"""Webhook routers for SQL2.AI API."""

from sql2ai_api.routers.webhooks.clerk import router as clerk_router

__all__ = ["clerk_router"]
