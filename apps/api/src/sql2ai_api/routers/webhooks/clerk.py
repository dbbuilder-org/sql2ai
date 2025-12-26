"""Clerk webhook handlers for user and organization events."""

import hashlib
import hmac
from typing import Any, Dict

import structlog
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from sql2ai_api.config import settings
from sql2ai_api.db.session import get_db

logger = structlog.get_logger()

router = APIRouter()


class WebhookEvent(BaseModel):
    """Clerk webhook event structure."""

    type: str
    data: Dict[str, Any]
    object: str = "event"


def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verify Clerk webhook signature using HMAC-SHA256."""
    if not settings.clerk_webhook_secret:
        logger.warning("clerk_webhook_secret_not_configured")
        return False

    expected_signature = hmac.new(
        settings.clerk_webhook_secret.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(signature, expected_signature)


async def handle_user_created(data: Dict[str, Any], db: AsyncSession) -> None:
    """Handle user.created event from Clerk."""
    user_id = data.get("id")
    email = data.get("email_addresses", [{}])[0].get("email_address")
    first_name = data.get("first_name")
    last_name = data.get("last_name")

    logger.info(
        "user_created",
        user_id=user_id,
        email=email,
    )

    # Sync user to local database
    # This creates a local user record for faster lookups and RLS
    from sql2ai_api.models.user import User

    user = User(
        id=user_id,
        email=email,
        first_name=first_name,
        last_name=last_name,
        status="active",
    )

    db.add(user)
    await db.commit()

    logger.info("user_synced_to_db", user_id=user_id)


async def handle_user_updated(data: Dict[str, Any], db: AsyncSession) -> None:
    """Handle user.updated event from Clerk."""
    user_id = data.get("id")
    email = data.get("email_addresses", [{}])[0].get("email_address")
    first_name = data.get("first_name")
    last_name = data.get("last_name")

    logger.info(
        "user_updated",
        user_id=user_id,
    )

    # Update user in local database
    from sqlalchemy import update
    from sql2ai_api.models.user import User

    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
    )

    await db.execute(stmt)
    await db.commit()

    logger.info("user_updated_in_db", user_id=user_id)


async def handle_user_deleted(data: Dict[str, Any], db: AsyncSession) -> None:
    """Handle user.deleted event from Clerk."""
    user_id = data.get("id")

    logger.info("user_deleted", user_id=user_id)

    # Soft delete user in local database
    from sqlalchemy import update
    from sql2ai_api.models.user import User

    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(status="deleted")
    )

    await db.execute(stmt)
    await db.commit()

    logger.info("user_soft_deleted_in_db", user_id=user_id)


async def handle_organization_created(data: Dict[str, Any], db: AsyncSession) -> None:
    """Handle organization.created event from Clerk."""
    org_id = data.get("id")
    name = data.get("name")
    slug = data.get("slug")

    logger.info(
        "organization_created",
        org_id=org_id,
        name=name,
        slug=slug,
    )

    # Create tenant in local database
    from sql2ai_api.models.tenant import Tenant

    tenant = Tenant(
        id=org_id,
        name=name,
        slug=slug,
        status="active",
        tier="free",
    )

    db.add(tenant)
    await db.commit()

    logger.info("tenant_created_in_db", org_id=org_id)


async def handle_organization_updated(data: Dict[str, Any], db: AsyncSession) -> None:
    """Handle organization.updated event from Clerk."""
    org_id = data.get("id")
    name = data.get("name")
    slug = data.get("slug")

    logger.info(
        "organization_updated",
        org_id=org_id,
    )

    # Update tenant in local database
    from sqlalchemy import update
    from sql2ai_api.models.tenant import Tenant

    stmt = (
        update(Tenant)
        .where(Tenant.id == org_id)
        .values(
            name=name,
            slug=slug,
        )
    )

    await db.execute(stmt)
    await db.commit()

    logger.info("tenant_updated_in_db", org_id=org_id)


async def handle_organization_deleted(data: Dict[str, Any], db: AsyncSession) -> None:
    """Handle organization.deleted event from Clerk."""
    org_id = data.get("id")

    logger.info("organization_deleted", org_id=org_id)

    # Soft delete tenant in local database
    from sqlalchemy import update
    from sql2ai_api.models.tenant import Tenant

    stmt = (
        update(Tenant)
        .where(Tenant.id == org_id)
        .values(status="deleted")
    )

    await db.execute(stmt)
    await db.commit()

    logger.info("tenant_soft_deleted_in_db", org_id=org_id)


async def handle_organization_membership_created(
    data: Dict[str, Any], db: AsyncSession
) -> None:
    """Handle organizationMembership.created event from Clerk."""
    org_id = data.get("organization", {}).get("id")
    user_id = data.get("public_user_data", {}).get("user_id")
    role = data.get("role")

    logger.info(
        "organization_membership_created",
        org_id=org_id,
        user_id=user_id,
        role=role,
    )

    # Update user's tenant association
    from sqlalchemy import update
    from sql2ai_api.models.user import User

    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(
            tenant_id=org_id,
            role=role,
        )
    )

    await db.execute(stmt)
    await db.commit()

    logger.info(
        "user_tenant_updated",
        user_id=user_id,
        tenant_id=org_id,
    )


async def handle_organization_membership_deleted(
    data: Dict[str, Any], db: AsyncSession
) -> None:
    """Handle organizationMembership.deleted event from Clerk."""
    org_id = data.get("organization", {}).get("id")
    user_id = data.get("public_user_data", {}).get("user_id")

    logger.info(
        "organization_membership_deleted",
        org_id=org_id,
        user_id=user_id,
    )

    # Remove user's tenant association
    from sqlalchemy import update
    from sql2ai_api.models.user import User

    stmt = (
        update(User)
        .where(User.id == user_id)
        .where(User.tenant_id == org_id)
        .values(
            tenant_id=None,
            role=None,
        )
    )

    await db.execute(stmt)
    await db.commit()

    logger.info(
        "user_tenant_removed",
        user_id=user_id,
        org_id=org_id,
    )


# Event handlers mapping
EVENT_HANDLERS = {
    "user.created": handle_user_created,
    "user.updated": handle_user_updated,
    "user.deleted": handle_user_deleted,
    "organization.created": handle_organization_created,
    "organization.updated": handle_organization_updated,
    "organization.deleted": handle_organization_deleted,
    "organizationMembership.created": handle_organization_membership_created,
    "organizationMembership.deleted": handle_organization_membership_deleted,
}


@router.post("/clerk")
async def handle_clerk_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, str]:
    """Handle incoming Clerk webhook events.

    Verifies the webhook signature and dispatches to appropriate handler.
    """
    # Get raw body for signature verification
    body = await request.body()

    # Verify signature
    signature = request.headers.get("svix-signature", "")
    if not verify_webhook_signature(body, signature):
        logger.warning("webhook_signature_invalid")
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    # Parse event
    try:
        event_data = await request.json()
        event = WebhookEvent(**event_data)
    except Exception as e:
        logger.error("webhook_parse_error", error=str(e))
        raise HTTPException(status_code=400, detail="Invalid webhook payload")

    logger.info(
        "webhook_received",
        event_type=event.type,
    )

    # Get handler for event type
    handler = EVENT_HANDLERS.get(event.type)

    if handler:
        try:
            await handler(event.data, db)
            logger.info("webhook_processed", event_type=event.type)
        except Exception as e:
            logger.error(
                "webhook_handler_error",
                event_type=event.type,
                error=str(e),
            )
            # Don't raise - return 200 to prevent Clerk from retrying
            # Log the error and investigate manually

    else:
        logger.info("webhook_event_ignored", event_type=event.type)

    return {"status": "received"}
