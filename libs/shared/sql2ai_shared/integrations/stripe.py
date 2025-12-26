"""Stripe billing and subscription integration."""

from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel
import structlog

logger = structlog.get_logger()


class StripeConfig(BaseModel):
    """Stripe configuration."""

    secret_key: str
    publishable_key: str
    webhook_secret: str

    # Price IDs (set in environment)
    price_pro_monthly: str = ""
    price_pro_yearly: str = ""
    price_enterprise_monthly: str = ""
    price_ai_tokens: str = ""  # Metered usage

    disabled: bool = False


class SubscriptionStatus:
    """Stripe subscription statuses."""

    ACTIVE = "active"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    CANCELED = "canceled"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    TRIALING = "trialing"
    PAUSED = "paused"


class StripeBilling:
    """Stripe billing integration for SQL2.AI."""

    def __init__(self, config: StripeConfig):
        self.config = config
        self._stripe = None

        if not config.disabled:
            self._init_client()

    def _init_client(self):
        """Initialize Stripe client."""
        try:
            import stripe

            stripe.api_key = self.config.secret_key
            self._stripe = stripe
            logger.info("stripe_initialized")
        except ImportError:
            logger.warning("stripe_not_installed")
        except Exception as e:
            logger.error("stripe_init_failed", error=str(e))

    async def create_customer(
        self,
        email: str,
        name: str,
        tenant_id: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Optional[str]:
        """Create a Stripe customer for a tenant."""
        if not self._stripe:
            return None

        try:
            customer_metadata = {
                "tenant_id": tenant_id,
                "source": "sql2ai",
            }
            if metadata:
                customer_metadata.update(metadata)

            customer = self._stripe.Customer.create(
                email=email,
                name=name,
                metadata=customer_metadata,
            )

            logger.info(
                "stripe_customer_created",
                customer_id=customer.id,
                tenant_id=tenant_id,
            )

            return customer.id

        except Exception as e:
            logger.error(
                "stripe_customer_create_failed",
                tenant_id=tenant_id,
                error=str(e),
            )
            return None

    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        trial_days: int = 14,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Create a subscription for a customer."""
        if not self._stripe:
            return None

        try:
            subscription = self._stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                trial_period_days=trial_days if trial_days > 0 else None,
                payment_behavior="default_incomplete",
                expand=["latest_invoice.payment_intent"],
                metadata=metadata or {},
            )

            result = {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "current_period_end": datetime.fromtimestamp(
                    subscription.current_period_end
                ),
            }

            # Include client secret for Stripe Elements
            if subscription.latest_invoice and subscription.latest_invoice.payment_intent:
                result["client_secret"] = (
                    subscription.latest_invoice.payment_intent.client_secret
                )

            logger.info(
                "stripe_subscription_created",
                subscription_id=subscription.id,
                customer_id=customer_id,
            )

            return result

        except Exception as e:
            logger.error(
                "stripe_subscription_create_failed",
                customer_id=customer_id,
                error=str(e),
            )
            return None

    async def cancel_subscription(
        self,
        subscription_id: str,
        at_period_end: bool = True,
    ) -> bool:
        """Cancel a subscription."""
        if not self._stripe:
            return False

        try:
            if at_period_end:
                self._stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True,
                )
            else:
                self._stripe.Subscription.delete(subscription_id)

            logger.info(
                "stripe_subscription_cancelled",
                subscription_id=subscription_id,
                at_period_end=at_period_end,
            )

            return True

        except Exception as e:
            logger.error(
                "stripe_subscription_cancel_failed",
                subscription_id=subscription_id,
                error=str(e),
            )
            return False

    async def create_checkout_session(
        self,
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        mode: str = "subscription",
        trial_days: int = 0,
    ) -> Optional[str]:
        """Create a Stripe Checkout session."""
        if not self._stripe:
            return None

        try:
            params = {
                "customer": customer_id,
                "mode": mode,
                "line_items": [{"price": price_id, "quantity": 1}],
                "success_url": success_url,
                "cancel_url": cancel_url,
                "allow_promotion_codes": True,
            }

            if trial_days > 0 and mode == "subscription":
                params["subscription_data"] = {
                    "trial_period_days": trial_days,
                }

            session = self._stripe.checkout.Session.create(**params)

            logger.info(
                "stripe_checkout_session_created",
                session_id=session.id,
                customer_id=customer_id,
            )

            return session.url

        except Exception as e:
            logger.error(
                "stripe_checkout_create_failed",
                customer_id=customer_id,
                error=str(e),
            )
            return None

    async def create_billing_portal(
        self,
        customer_id: str,
        return_url: str,
    ) -> Optional[str]:
        """Create a customer billing portal session."""
        if not self._stripe:
            return None

        try:
            session = self._stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )

            return session.url

        except Exception as e:
            logger.error(
                "stripe_portal_create_failed",
                customer_id=customer_id,
                error=str(e),
            )
            return None

    async def report_usage(
        self,
        subscription_item_id: str,
        quantity: int,
        timestamp: Optional[int] = None,
        action: str = "increment",
    ) -> bool:
        """Report metered usage (e.g., AI tokens)."""
        if not self._stripe:
            return False

        try:
            import time

            self._stripe.SubscriptionItem.create_usage_record(
                subscription_item_id,
                quantity=quantity,
                timestamp=timestamp or int(time.time()),
                action=action,
            )

            logger.debug(
                "stripe_usage_reported",
                subscription_item_id=subscription_item_id,
                quantity=quantity,
            )

            return True

        except Exception as e:
            logger.error(
                "stripe_usage_report_failed",
                subscription_item_id=subscription_item_id,
                error=str(e),
            )
            return False

    async def get_subscription(
        self,
        subscription_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get subscription details."""
        if not self._stripe:
            return None

        try:
            subscription = self._stripe.Subscription.retrieve(subscription_id)

            return {
                "id": subscription.id,
                "status": subscription.status,
                "current_period_start": datetime.fromtimestamp(
                    subscription.current_period_start
                ),
                "current_period_end": datetime.fromtimestamp(
                    subscription.current_period_end
                ),
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "canceled_at": (
                    datetime.fromtimestamp(subscription.canceled_at)
                    if subscription.canceled_at
                    else None
                ),
                "trial_end": (
                    datetime.fromtimestamp(subscription.trial_end)
                    if subscription.trial_end
                    else None
                ),
            }

        except Exception as e:
            logger.error(
                "stripe_subscription_get_failed",
                subscription_id=subscription_id,
                error=str(e),
            )
            return None

    def verify_webhook(
        self,
        payload: bytes,
        signature: str,
    ) -> Optional[Dict[str, Any]]:
        """Verify and parse a Stripe webhook event."""
        if not self._stripe:
            return None

        try:
            event = self._stripe.Webhook.construct_event(
                payload,
                signature,
                self.config.webhook_secret,
            )

            return {
                "id": event.id,
                "type": event.type,
                "data": event.data.object,
                "created": datetime.fromtimestamp(event.created),
            }

        except self._stripe.error.SignatureVerificationError as e:
            logger.warning("stripe_webhook_signature_invalid", error=str(e))
            return None
        except Exception as e:
            logger.error("stripe_webhook_verify_failed", error=str(e))
            return None


class StripeWebhookHandler:
    """Handler for Stripe webhook events."""

    def __init__(self):
        self._handlers: Dict[str, callable] = {}

    def on(self, event_type: str):
        """Decorator to register a webhook handler."""
        def decorator(func):
            self._handlers[event_type] = func
            return func
        return decorator

    async def handle(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a webhook event."""
        event_type = event.get("type")
        handler = self._handlers.get(event_type)

        if handler:
            try:
                result = await handler(event["data"])
                logger.info(
                    "stripe_webhook_handled",
                    event_type=event_type,
                    event_id=event.get("id"),
                )
                return {"status": "handled", "result": result}
            except Exception as e:
                logger.error(
                    "stripe_webhook_handler_failed",
                    event_type=event_type,
                    error=str(e),
                )
                return {"status": "error", "error": str(e)}

        logger.debug("stripe_webhook_ignored", event_type=event_type)
        return {"status": "ignored"}


# Pre-configured webhook handler
webhook_handler = StripeWebhookHandler()


# Example event handlers (to be implemented in app)
@webhook_handler.on("customer.subscription.created")
async def on_subscription_created(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle new subscription creation."""
    # Update tenant tier in database
    return {"subscription_id": data.get("id")}


@webhook_handler.on("customer.subscription.updated")
async def on_subscription_updated(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle subscription updates."""
    # Update tenant tier/limits based on new subscription
    return {"subscription_id": data.get("id"), "status": data.get("status")}


@webhook_handler.on("customer.subscription.deleted")
async def on_subscription_deleted(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle subscription cancellation."""
    # Downgrade tenant to free tier
    return {"subscription_id": data.get("id")}


@webhook_handler.on("invoice.payment_failed")
async def on_payment_failed(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle failed payment."""
    # Send notification, maybe restrict access
    return {"invoice_id": data.get("id")}
