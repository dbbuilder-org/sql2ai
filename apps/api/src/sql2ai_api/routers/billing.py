"""Billing API router for SQL2.AI - Stripe integration."""

from fastapi import APIRouter, Depends, HTTPException, Request, Header
from pydantic import BaseModel
from typing import Optional
import stripe
import structlog

from sql2ai_api.config import settings
from sql2ai_api.dependencies.auth import get_current_user, get_tenant_id

router = APIRouter()
logger = structlog.get_logger()

# Initialize Stripe
stripe.api_key = settings.stripe_secret_key.get_secret_value() if settings.stripe_secret_key else None

# =============================================================================
# Models
# =============================================================================

class PricingTier(BaseModel):
    """Pricing tier information."""
    id: str
    name: str
    price_monthly: int
    price_yearly: int
    features: list[str]
    limits: dict


class CreateCheckoutRequest(BaseModel):
    """Request to create a checkout session."""
    price_id: str
    success_url: str
    cancel_url: str


class CreateCheckoutResponse(BaseModel):
    """Response with checkout session URL."""
    checkout_url: str
    session_id: str


class SubscriptionStatus(BaseModel):
    """Current subscription status."""
    plan: str
    status: str
    current_period_end: Optional[str]
    cancel_at_period_end: bool


class CreatePortalRequest(BaseModel):
    """Request to create a billing portal session."""
    return_url: str


# =============================================================================
# Pricing Tiers
# =============================================================================

PRICING_TIERS = [
    PricingTier(
        id="free",
        name="Free",
        price_monthly=0,
        price_yearly=0,
        features=[
            "1 database connection",
            "100 AI queries/month",
            "Basic schema explorer",
            "Community support",
        ],
        limits={
            "connections": 1,
            "ai_queries": 100,
            "team_members": 1,
        },
    ),
    PricingTier(
        id="team",
        name="Team",
        price_monthly=4900,  # $49.00
        price_yearly=47000,  # $470.00 (2 months free)
        features=[
            "5 database connections",
            "1,000 AI queries/month",
            "Schema comparison & versioning",
            "Query optimization",
            "Email support",
            "5 team members",
        ],
        limits={
            "connections": 5,
            "ai_queries": 1000,
            "team_members": 5,
        },
    ),
    PricingTier(
        id="professional",
        name="Professional",
        price_monthly=14900,  # $149.00
        price_yearly=143000,  # $1,430.00 (2 months free)
        features=[
            "25 database connections",
            "10,000 AI queries/month",
            "All Team features",
            "Compliance scanning",
            "Code review automation",
            "Priority support",
            "25 team members",
        ],
        limits={
            "connections": 25,
            "ai_queries": 10000,
            "team_members": 25,
        },
    ),
    PricingTier(
        id="enterprise",
        name="Enterprise",
        price_monthly=0,  # Custom pricing
        price_yearly=0,
        features=[
            "Unlimited connections",
            "Unlimited AI queries",
            "All Professional features",
            "SSO & SAML",
            "Dedicated support",
            "Custom integrations",
            "SLA guarantees",
        ],
        limits={
            "connections": -1,  # Unlimited
            "ai_queries": -1,
            "team_members": -1,
        },
    ),
]


# =============================================================================
# Endpoints
# =============================================================================

@router.get("/pricing", response_model=list[PricingTier])
async def get_pricing_tiers():
    """Get all available pricing tiers."""
    return PRICING_TIERS


@router.get("/subscription", response_model=SubscriptionStatus)
async def get_subscription_status(
    tenant_id: str = Depends(get_tenant_id),
):
    """Get current subscription status for the tenant."""
    # TODO: Look up subscription from database
    # For now, return mock data
    return SubscriptionStatus(
        plan="free",
        status="active",
        current_period_end=None,
        cancel_at_period_end=False,
    )


@router.post("/checkout", response_model=CreateCheckoutResponse)
async def create_checkout_session(
    request: CreateCheckoutRequest,
    tenant_id: str = Depends(get_tenant_id),
):
    """Create a Stripe checkout session for subscription."""
    if not stripe.api_key:
        raise HTTPException(
            status_code=503,
            detail="Payment processing is not configured",
        )

    try:
        # TODO: Look up or create Stripe customer for tenant
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[
                {
                    "price": request.price_id,
                    "quantity": 1,
                },
            ],
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            metadata={
                "tenant_id": tenant_id,
            },
        )

        return CreateCheckoutResponse(
            checkout_url=session.url,
            session_id=session.id,
        )

    except stripe.error.StripeError as e:
        logger.error("stripe_checkout_error", error=str(e))
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create checkout session: {str(e)}",
        )


@router.post("/portal")
async def create_billing_portal(
    request: CreatePortalRequest,
    tenant_id: str = Depends(get_tenant_id),
):
    """Create a Stripe billing portal session for managing subscription."""
    if not stripe.api_key:
        raise HTTPException(
            status_code=503,
            detail="Payment processing is not configured",
        )

    try:
        # TODO: Look up Stripe customer ID from database
        # For now, return error
        raise HTTPException(
            status_code=404,
            detail="No subscription found for this account",
        )

    except stripe.error.StripeError as e:
        logger.error("stripe_portal_error", error=str(e))
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create portal session: {str(e)}",
        )


# =============================================================================
# Webhooks
# =============================================================================

@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature"),
):
    """Handle Stripe webhook events."""
    if not stripe.api_key:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    webhook_secret = settings.stripe_webhook_secret.get_secret_value() if settings.stripe_webhook_secret else None
    if not webhook_secret:
        raise HTTPException(status_code=503, detail="Webhook secret not configured")

    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    event_type = event["type"]
    event_data = event["data"]["object"]

    logger.info("stripe_webhook_received", event_type=event_type)

    if event_type == "checkout.session.completed":
        await handle_checkout_completed(event_data)
    elif event_type == "customer.subscription.updated":
        await handle_subscription_updated(event_data)
    elif event_type == "customer.subscription.deleted":
        await handle_subscription_deleted(event_data)
    elif event_type == "invoice.payment_succeeded":
        await handle_payment_succeeded(event_data)
    elif event_type == "invoice.payment_failed":
        await handle_payment_failed(event_data)

    return {"status": "ok"}


async def handle_checkout_completed(session: dict):
    """Handle successful checkout."""
    tenant_id = session.get("metadata", {}).get("tenant_id")
    subscription_id = session.get("subscription")

    logger.info(
        "checkout_completed",
        tenant_id=tenant_id,
        subscription_id=subscription_id,
    )

    # TODO: Update tenant subscription in database


async def handle_subscription_updated(subscription: dict):
    """Handle subscription update."""
    logger.info(
        "subscription_updated",
        subscription_id=subscription.get("id"),
        status=subscription.get("status"),
    )

    # TODO: Update subscription status in database


async def handle_subscription_deleted(subscription: dict):
    """Handle subscription cancellation."""
    logger.info(
        "subscription_deleted",
        subscription_id=subscription.get("id"),
    )

    # TODO: Downgrade tenant to free tier


async def handle_payment_succeeded(invoice: dict):
    """Handle successful payment."""
    logger.info(
        "payment_succeeded",
        invoice_id=invoice.get("id"),
        amount=invoice.get("amount_paid"),
    )


async def handle_payment_failed(invoice: dict):
    """Handle failed payment."""
    logger.warning(
        "payment_failed",
        invoice_id=invoice.get("id"),
        customer=invoice.get("customer"),
    )

    # TODO: Send payment failed notification
