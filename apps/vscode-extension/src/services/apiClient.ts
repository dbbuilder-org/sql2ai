import axios, { AxiosInstance } from 'axios';

export interface OptimizeResult {
    original_query: string;
    optimized_query: string;
    suggestions: string[];
    estimated_improvement: string;
}

export interface ExplainResult {
    explanation: string;
    steps: string[];
    complexity: string;
    estimated_rows?: number;
}

export interface ReviewResult {
    issues: ReviewIssue[];
    score: number;
    summary: string;
}

export interface ReviewIssue {
    severity: 'error' | 'warning' | 'info';
    rule: string;
    message: string;
    line?: number;
    suggestion?: string;
}

export interface GenerateResult {
    sql: string;
    explanation: string;
}

export interface Connection {
    id: string;
    name: string;
    db_type: 'postgresql' | 'sqlserver';
    host: string;
    database: string;
    status: string;
}

export class Sql2AiApiClient {
    private client: AxiosInstance;
    private apiKey: string;

    constructor(baseUrl: string, apiKey: string) {
        this.apiKey = apiKey;
        this.client = axios.create({
            baseURL: baseUrl,
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json',
            },
        });

        this.setupInterceptors();
    }

    private setupInterceptors() {
        this.client.interceptors.request.use(config => {
            if (this.apiKey) {
                config.headers.Authorization = `Bearer ${this.apiKey}`;
            }
            return config;
        });

        this.client.interceptors.response.use(
            response => response,
            error => {
                if (error.response?.status === 401) {
                    throw new Error('Invalid API key. Please check your SQL2.AI settings.');
                }
                throw error;
            }
        );
    }

    updateConfig(baseUrl: string, apiKey: string) {
        this.apiKey = apiKey;
        this.client.defaults.baseURL = baseUrl;
    }

    async optimizeQuery(sql: string, dbType: string = 'postgresql'): Promise<OptimizeResult> {
        const response = await this.client.post('/api/optimize/query', {
            sql,
            db_type: dbType,
        });
        return response.data;
    }

    async explainQuery(sql: string, dbType: string = 'postgresql'): Promise<ExplainResult> {
        const response = await this.client.post('/api/writer/explain', {
            sql,
            db_type: dbType,
        });
        return response.data;
    }

    async reviewCode(sql: string, dbType: string = 'postgresql'): Promise<ReviewResult> {
        const response = await this.client.post('/api/codereview/analyze', {
            sql,
            db_type: dbType,
        });
        return response.data;
    }

    async generateSql(prompt: string, dbType: string = 'postgresql', context?: string): Promise<GenerateResult> {
        const response = await this.client.post('/api/writer/generate', {
            prompt,
            db_type: dbType,
            context,
        });
        return response.data;
    }

    async generateCrud(
        tableName: string,
        schema: string,
        dbType: string = 'postgresql'
    ): Promise<GenerateResult> {
        const response = await this.client.post('/api/writer/crud', {
            table_name: tableName,
            schema,
            db_type: dbType,
        });
        return response.data;
    }

    async analyzeExecutionPlan(plan: string, dbType: string = 'postgresql'): Promise<ExplainResult> {
        const response = await this.client.post('/api/optimize/plan', {
            execution_plan: plan,
            db_type: dbType,
        });
        return response.data;
    }

    async formatSql(sql: string, dbType: string = 'postgresql'): Promise<string> {
        const response = await this.client.post('/api/writer/format', {
            sql,
            db_type: dbType,
        });
        return response.data.formatted_sql;
    }

    async listConnections(): Promise<Connection[]> {
        const response = await this.client.get('/api/connections');
        return response.data.connections;
    }

    async testConnection(connectionId: string): Promise<{ success: boolean; message: string }> {
        const response = await this.client.post(`/api/connections/${connectionId}/test`);
        return response.data;
    }

    async healthCheck(): Promise<boolean> {
        try {
            const response = await this.client.get('/health');
            return response.data.status === 'healthy';
        } catch {
            return false;
        }
    }
}
