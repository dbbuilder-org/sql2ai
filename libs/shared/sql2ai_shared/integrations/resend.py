"""Resend transactional email integration."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, EmailStr
import structlog

logger = structlog.get_logger()


class ResendConfig(BaseModel):
    """Resend configuration."""

    api_key: str
    from_email: str = "SQL2.AI <notifications@sql2.ai>"
    reply_to: str = "support@sql2.ai"
    disabled: bool = False


class EmailTemplate:
    """Email template names."""

    WELCOME = "welcome"
    VERIFY_EMAIL = "verify_email"
    PASSWORD_RESET = "password_reset"
    INVITATION = "invitation"
    ALERT = "alert"
    COMPLIANCE_REPORT = "compliance_report"
    MIGRATION_COMPLETE = "migration_complete"
    USAGE_WARNING = "usage_warning"
    UPGRADE_CONFIRMATION = "upgrade_confirmation"
    INVOICE = "invoice"


class EmailService:
    """Resend email service for transactional emails."""

    def __init__(self, config: ResendConfig):
        self.config = config
        self._client = None

        if not config.disabled:
            self._init_client()

    def _init_client(self):
        """Initialize Resend client."""
        try:
            import resend

            resend.api_key = self.config.api_key
            self._client = resend
            logger.info("resend_initialized")
        except ImportError:
            logger.warning("resend_not_installed")
        except Exception as e:
            logger.error("resend_init_failed", error=str(e))

    async def send(
        self,
        to: str | List[str],
        subject: str,
        html: str,
        text: Optional[str] = None,
        reply_to: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[Dict]] = None,
        tags: Optional[List[Dict[str, str]]] = None,
    ) -> Optional[str]:
        """Send an email."""
        if not self._client:
            logger.warning("resend_not_configured")
            return None

        try:
            params = {
                "from": self.config.from_email,
                "to": to if isinstance(to, list) else [to],
                "subject": subject,
                "html": html,
            }

            if text:
                params["text"] = text
            if reply_to:
                params["reply_to"] = reply_to
            elif self.config.reply_to:
                params["reply_to"] = self.config.reply_to
            if cc:
                params["cc"] = cc
            if bcc:
                params["bcc"] = bcc
            if attachments:
                params["attachments"] = attachments
            if tags:
                params["tags"] = tags

            result = self._client.Emails.send(params)

            logger.info(
                "email_sent",
                to=to,
                subject=subject,
                email_id=result.get("id"),
            )

            return result.get("id")

        except Exception as e:
            logger.error(
                "email_send_failed",
                to=to,
                subject=subject,
                error=str(e),
            )
            return None

    async def send_welcome(
        self,
        to: str,
        name: str,
        login_url: str = "https://app.sql2.ai",
    ) -> Optional[str]:
        """Send welcome email to new user."""
        html = f"""
        <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #2563eb;">Welcome to SQL2.AI!</h1>
            <p>Hi {name},</p>
            <p>Thank you for signing up for SQL2.AI. We're excited to have you on board!</p>
            <p>SQL2.AI helps you manage your SQL Server and PostgreSQL databases with AI-powered tools for:</p>
            <ul>
                <li><strong>Query Optimization</strong> - Get AI suggestions to improve query performance</li>
                <li><strong>Database Monitoring</strong> - Real-time insights into database health</li>
                <li><strong>Migration Management</strong> - Safe, versioned database migrations</li>
                <li><strong>Compliance Scanning</strong> - Automated SOC2, HIPAA, and GDPR checks</li>
            </ul>
            <p>
                <a href="{login_url}" style="display: inline-block; background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                    Get Started
                </a>
            </p>
            <p>If you have any questions, reply to this email or reach out to our support team.</p>
            <p>Best,<br>The SQL2.AI Team</p>
        </div>
        """

        return await self.send(
            to=to,
            subject="Welcome to SQL2.AI!",
            html=html,
            tags=[{"name": "template", "value": EmailTemplate.WELCOME}],
        )

    async def send_alert(
        self,
        to: str | List[str],
        alert_name: str,
        severity: str,
        database: str,
        details: Dict[str, Any],
        dashboard_url: str = "https://app.sql2.ai/alerts",
    ) -> Optional[str]:
        """Send database alert notification."""
        severity_colors = {
            "info": "#3b82f6",
            "warning": "#f59e0b",
            "error": "#ef4444",
            "critical": "#dc2626",
        }

        color = severity_colors.get(severity.lower(), "#6b7280")

        details_html = "\n".join(
            f"<li><strong>{k}:</strong> {v}</li>"
            for k, v in details.items()
        )

        html = f"""
        <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: {color}; color: white; padding: 16px; border-radius: 6px 6px 0 0;">
                <h2 style="margin: 0;">[{severity.upper()}] {alert_name}</h2>
            </div>
            <div style="border: 1px solid #e5e7eb; border-top: none; padding: 16px; border-radius: 0 0 6px 6px;">
                <p><strong>Database:</strong> {database}</p>
                <h3>Details:</h3>
                <ul>{details_html}</ul>
                <p>
                    <a href="{dashboard_url}" style="display: inline-block; background-color: #2563eb; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">
                        View in Dashboard
                    </a>
                </p>
            </div>
        </div>
        """

        return await self.send(
            to=to,
            subject=f"[{severity.upper()}] {alert_name} - {database}",
            html=html,
            tags=[
                {"name": "template", "value": EmailTemplate.ALERT},
                {"name": "severity", "value": severity},
            ],
        )

    async def send_compliance_report(
        self,
        to: str | List[str],
        report_type: str,
        framework: str,
        summary: Dict[str, Any],
        report_url: str,
    ) -> Optional[str]:
        """Send compliance scan report."""
        passed = summary.get("passed", 0)
        failed = summary.get("failed", 0)
        warnings = summary.get("warnings", 0)
        total = passed + failed + warnings

        html = f"""
        <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #2563eb;">Compliance Report: {framework}</h1>
            <p>Your {report_type} compliance scan has completed.</p>

            <div style="background-color: #f3f4f6; padding: 16px; border-radius: 6px; margin: 16px 0;">
                <h3 style="margin-top: 0;">Summary</h3>
                <table style="width: 100%;">
                    <tr>
                        <td style="color: #22c55e;">✓ Passed</td>
                        <td style="text-align: right; font-weight: bold;">{passed}</td>
                    </tr>
                    <tr>
                        <td style="color: #ef4444;">✗ Failed</td>
                        <td style="text-align: right; font-weight: bold;">{failed}</td>
                    </tr>
                    <tr>
                        <td style="color: #f59e0b;">⚠ Warnings</td>
                        <td style="text-align: right; font-weight: bold;">{warnings}</td>
                    </tr>
                    <tr style="border-top: 1px solid #d1d5db;">
                        <td><strong>Total Checks</strong></td>
                        <td style="text-align: right; font-weight: bold;">{total}</td>
                    </tr>
                </table>
            </div>

            <p>
                <a href="{report_url}" style="display: inline-block; background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                    View Full Report
                </a>
            </p>
        </div>
        """

        return await self.send(
            to=to,
            subject=f"SQL2.AI Compliance Report: {framework}",
            html=html,
            tags=[
                {"name": "template", "value": EmailTemplate.COMPLIANCE_REPORT},
                {"name": "framework", "value": framework},
            ],
        )

    async def send_usage_warning(
        self,
        to: str,
        resource: str,
        current_usage: int,
        limit: int,
        percentage: int,
        upgrade_url: str = "https://app.sql2.ai/settings/billing",
    ) -> Optional[str]:
        """Send usage limit warning."""
        html = f"""
        <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #f59e0b;">Usage Warning</h1>
            <p>You're approaching your {resource} limit.</p>

            <div style="background-color: #fef3c7; padding: 16px; border-radius: 6px; margin: 16px 0;">
                <p style="margin: 0;">
                    <strong>{current_usage:,}</strong> of <strong>{limit:,}</strong> {resource} used ({percentage}%)
                </p>
                <div style="background-color: #fbbf24; height: 8px; border-radius: 4px; margin-top: 8px;">
                    <div style="background-color: #f59e0b; height: 100%; width: {percentage}%; border-radius: 4px;"></div>
                </div>
            </div>

            <p>Upgrade your plan to increase your limits and unlock additional features.</p>

            <p>
                <a href="{upgrade_url}" style="display: inline-block; background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                    Upgrade Plan
                </a>
            </p>
        </div>
        """

        return await self.send(
            to=to,
            subject=f"SQL2.AI: {resource} Usage Warning ({percentage}%)",
            html=html,
            tags=[
                {"name": "template", "value": EmailTemplate.USAGE_WARNING},
                {"name": "resource", "value": resource},
            ],
        )
