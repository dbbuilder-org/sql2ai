"""AI agents with LangGraph for agentic SQL workflows."""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, TypedDict
from enum import Enum
from pydantic import BaseModel, Field
import structlog

from sql2ai_shared.ai.models import (
    ChatRequest,
    Message,
    Tool,
    ToolFunction,
    ToolCall,
    ToolResult,
)
from sql2ai_shared.ai.providers import get_ai_provider
from sql2ai_shared.tenancy.context import get_current_tenant

logger = structlog.get_logger()


class AgentStatus(str, Enum):
    """Agent execution status."""

    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentConfig(BaseModel):
    """Agent configuration."""

    name: str
    description: str
    model: str = "gpt-4"
    temperature: float = 0.7
    max_iterations: int = 10
    require_approval: bool = False
    approval_threshold: str = "high"  # low, medium, high
    tools: List[str] = Field(default_factory=list)
    system_prompt: Optional[str] = None


class AgentState(TypedDict, total=False):
    """State passed between agent nodes."""

    messages: List[Dict[str, Any]]
    current_step: int
    status: str
    result: Any
    error: Optional[str]
    tool_calls: List[Dict[str, Any]]
    pending_approvals: List[Dict[str, Any]]
    context: Dict[str, Any]


class AgentTool:
    """Wrapper for agent tools."""

    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        handler: Callable,
        requires_approval: bool = False,
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.handler = handler
        self.requires_approval = requires_approval

    def to_openai_tool(self) -> Tool:
        """Convert to OpenAI tool format."""
        return Tool(
            function=ToolFunction(
                name=self.name,
                description=self.description,
                parameters=self.parameters,
            )
        )

    async def execute(self, **kwargs) -> Any:
        """Execute the tool."""
        import asyncio
        import inspect

        if inspect.iscoroutinefunction(self.handler):
            return await self.handler(**kwargs)
        else:
            return await asyncio.to_thread(self.handler, **kwargs)


class BaseAgent(ABC):
    """Base class for AI agents."""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.tools: Dict[str, AgentTool] = {}
        self._setup_tools()

    @abstractmethod
    def _setup_tools(self) -> None:
        """Set up agent tools."""
        pass

    def register_tool(self, tool: AgentTool) -> None:
        """Register a tool with the agent."""
        self.tools[tool.name] = tool

    async def run(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentState:
        """Run the agent with a prompt."""
        provider = get_ai_provider()

        # Initialize state
        state: AgentState = {
            "messages": [],
            "current_step": 0,
            "status": AgentStatus.THINKING.value,
            "result": None,
            "error": None,
            "tool_calls": [],
            "pending_approvals": [],
            "context": context or {},
        }

        # Add system prompt
        system_prompt = self.config.system_prompt or self._default_system_prompt()
        state["messages"].append(Message.system(system_prompt).model_dump())
        state["messages"].append(Message.user(prompt).model_dump())

        # Agent loop
        while state["current_step"] < self.config.max_iterations:
            state["current_step"] += 1

            # Check for pending approvals
            if state["pending_approvals"]:
                state["status"] = AgentStatus.WAITING_APPROVAL.value
                return state

            # Get model response
            messages = [
                Message(**m) for m in state["messages"]
            ]

            request = ChatRequest(
                messages=messages,
                model=self.config.model,
                temperature=self.config.temperature,
                tools=[t.to_openai_tool() for t in self.tools.values()],
            )

            try:
                response = await provider.chat(request)
            except Exception as e:
                state["status"] = AgentStatus.FAILED.value
                state["error"] = str(e)
                return state

            # Add assistant response
            assistant_msg = response.choices[0].message
            state["messages"].append(assistant_msg.model_dump())

            # Check for tool calls
            if assistant_msg.tool_calls:
                state["status"] = AgentStatus.EXECUTING.value

                for tool_call in assistant_msg.tool_calls:
                    result = await self._execute_tool_call(tool_call, state)

                    # Add tool result to messages
                    state["messages"].append(
                        Message.tool(
                            content=str(result.result if result.result else result.error),
                            tool_call_id=tool_call.id,
                            name=tool_call.name,
                        ).model_dump()
                    )

                    state["tool_calls"].append({
                        "id": tool_call.id,
                        "name": tool_call.name,
                        "result": result.model_dump(),
                    })
            else:
                # No more tool calls, agent is done
                state["status"] = AgentStatus.COMPLETED.value
                state["result"] = assistant_msg.content
                break

        return state

    async def _execute_tool_call(
        self,
        tool_call: ToolCall,
        state: AgentState,
    ) -> ToolResult:
        """Execute a single tool call."""
        import json
        import time

        tool_name = tool_call.name
        start_time = time.perf_counter()

        if tool_name not in self.tools:
            return ToolResult(
                tool_call_id=tool_call.id,
                name=tool_name,
                result=None,
                error=f"Unknown tool: {tool_name}",
            )

        tool = self.tools[tool_name]

        # Check if approval is required
        if tool.requires_approval and self.config.require_approval:
            state["pending_approvals"].append({
                "tool_call_id": tool_call.id,
                "tool_name": tool_name,
                "arguments": tool_call.arguments,
            })
            return ToolResult(
                tool_call_id=tool_call.id,
                name=tool_name,
                result=None,
                error="Awaiting approval",
            )

        try:
            args = json.loads(tool_call.arguments)
            result = await tool.execute(**args)

            execution_time_ms = (time.perf_counter() - start_time) * 1000

            logger.info(
                "agent_tool_executed",
                tool=tool_name,
                execution_time_ms=execution_time_ms,
            )

            return ToolResult(
                tool_call_id=tool_call.id,
                name=tool_name,
                result=result,
                execution_time_ms=execution_time_ms,
            )

        except Exception as e:
            logger.error(
                "agent_tool_failed",
                tool=tool_name,
                error=str(e),
            )
            return ToolResult(
                tool_call_id=tool_call.id,
                name=tool_name,
                result=None,
                error=str(e),
            )

    def _default_system_prompt(self) -> str:
        """Generate default system prompt."""
        return f"""You are {self.config.name}, an AI assistant.
{self.config.description}

You have access to the following tools:
{chr(10).join(f"- {t.name}: {t.description}" for t in self.tools.values())}

Use these tools to help accomplish the user's request.
Think step by step and use tools when needed."""


class SQLAgent(BaseAgent):
    """SQL-focused agent for database operations."""

    def __init__(
        self,
        config: Optional[AgentConfig] = None,
        database_type: str = "sqlserver",
        connection_id: Optional[str] = None,
    ):
        self.database_type = database_type
        self.connection_id = connection_id

        if config is None:
            config = AgentConfig(
                name="SQL Agent",
                description="An AI agent specialized in SQL Server and PostgreSQL database operations.",
                model="gpt-4",
                temperature=0.3,
                require_approval=True,
            )

        super().__init__(config)

    def _setup_tools(self) -> None:
        """Set up SQL-specific tools."""

        # Query execution tool
        self.register_tool(AgentTool(
            name="execute_query",
            description="Execute a read-only SQL query against the database",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The SQL query to execute",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of rows to return",
                        "default": 100,
                    },
                },
                "required": ["query"],
            },
            handler=self._execute_query,
            requires_approval=False,
        ))

        # Schema exploration tool
        self.register_tool(AgentTool(
            name="get_schema",
            description="Get the schema information for a table or the entire database",
            parameters={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Table name to get schema for (optional)",
                    },
                },
            },
            handler=self._get_schema,
            requires_approval=False,
        ))

        # Query optimization tool
        self.register_tool(AgentTool(
            name="optimize_query",
            description="Analyze and suggest optimizations for a SQL query",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The SQL query to optimize",
                    },
                },
                "required": ["query"],
            },
            handler=self._optimize_query,
            requires_approval=False,
        ))

        # DDL execution tool (requires approval)
        self.register_tool(AgentTool(
            name="execute_ddl",
            description="Execute a DDL statement (CREATE, ALTER, DROP)",
            parameters={
                "type": "object",
                "properties": {
                    "statement": {
                        "type": "string",
                        "description": "The DDL statement to execute",
                    },
                },
                "required": ["statement"],
            },
            handler=self._execute_ddl,
            requires_approval=True,
        ))

    async def _execute_query(self, query: str, limit: int = 100) -> Dict[str, Any]:
        """Execute a read-only query."""
        # This would integrate with the database module
        logger.info(
            "sql_agent_query",
            query=query[:100],
            limit=limit,
            database_type=self.database_type,
        )

        # Placeholder - actual implementation would use database module
        return {
            "status": "success",
            "message": f"Query would be executed: {query[:50]}...",
            "row_count": 0,
        }

    async def _get_schema(self, table_name: Optional[str] = None) -> Dict[str, Any]:
        """Get database schema information."""
        logger.info(
            "sql_agent_schema",
            table_name=table_name,
            database_type=self.database_type,
        )

        # Placeholder
        return {
            "status": "success",
            "table": table_name,
            "columns": [],
        }

    async def _optimize_query(self, query: str) -> Dict[str, Any]:
        """Optimize a query using AI."""
        provider = get_ai_provider()

        result = await provider.optimize_query(
            query=query,
            database_type=self.database_type,
        )

        return result

    async def _execute_ddl(self, statement: str) -> Dict[str, Any]:
        """Execute a DDL statement (requires approval)."""
        logger.info(
            "sql_agent_ddl",
            statement=statement[:100],
            database_type=self.database_type,
        )

        # Placeholder
        return {
            "status": "success",
            "message": f"DDL would be executed: {statement[:50]}...",
        }

    def _default_system_prompt(self) -> str:
        """SQL-specific system prompt."""
        return f"""You are an expert {self.database_type} database assistant.

Your capabilities:
- Execute read-only queries to explore data
- Analyze table schemas and relationships
- Suggest query optimizations
- Generate DDL for schema changes (requires approval)

Important guidelines:
1. Always verify table names and column names before writing queries
2. Use appropriate query limits to avoid returning too much data
3. For any DDL operations, explain the impact before execution
4. Prioritize data safety - never execute destructive operations without approval

Database type: {self.database_type}
Connection ID: {self.connection_id or "Not connected"}"""


class MigrationAgent(BaseAgent):
    """Agent for database migrations."""

    def __init__(self, config: Optional[AgentConfig] = None):
        if config is None:
            config = AgentConfig(
                name="Migration Agent",
                description="An AI agent for planning and executing database migrations.",
                model="gpt-4",
                temperature=0.2,
                require_approval=True,
            )

        super().__init__(config)

    def _setup_tools(self) -> None:
        """Set up migration tools."""

        self.register_tool(AgentTool(
            name="compare_schemas",
            description="Compare source and target database schemas",
            parameters={
                "type": "object",
                "properties": {
                    "source": {"type": "string", "description": "Source schema identifier"},
                    "target": {"type": "string", "description": "Target schema identifier"},
                },
                "required": ["source", "target"],
            },
            handler=self._compare_schemas,
            requires_approval=False,
        ))

        self.register_tool(AgentTool(
            name="generate_migration",
            description="Generate migration scripts for detected changes",
            parameters={
                "type": "object",
                "properties": {
                    "changes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of changes to include",
                    },
                },
                "required": ["changes"],
            },
            handler=self._generate_migration,
            requires_approval=False,
        ))

        self.register_tool(AgentTool(
            name="apply_migration",
            description="Apply a migration script to the target database",
            parameters={
                "type": "object",
                "properties": {
                    "migration_id": {"type": "string", "description": "Migration ID to apply"},
                },
                "required": ["migration_id"],
            },
            handler=self._apply_migration,
            requires_approval=True,
        ))

    async def _compare_schemas(self, source: str, target: str) -> Dict[str, Any]:
        """Compare two schemas."""
        return {
            "status": "success",
            "source": source,
            "target": target,
            "differences": [],
        }

    async def _generate_migration(self, changes: List[str]) -> Dict[str, Any]:
        """Generate migration scripts."""
        return {
            "status": "success",
            "migration_id": "mig_001",
            "scripts": [],
        }

    async def _apply_migration(self, migration_id: str) -> Dict[str, Any]:
        """Apply a migration."""
        return {
            "status": "pending_approval",
            "migration_id": migration_id,
        }
