# SQL Send

**Unified Database Messaging Platform**

## Overview

SQL Send provides database-native email and SMS connectivity through a unified outbox pattern. It integrates with SendGrid, Resend, Twilio, and other providers while maintaining full SQL Server and PostgreSQL compatibility. Messages are queued reliably using the transactional outbox pattern, ensuring delivery even during failures.

## The Problem

### Current Database Messaging Challenges

| Challenge | Traditional Approach | Risk |
|-----------|---------------------|------|
| sp_send_dbmail limitations | SQL Server only | No cloud support |
| Provider lock-in | Direct API calls | Vendor dependency |
| Delivery reliability | Fire and forget | Lost messages |
| Transaction coupling | Sync API calls | Partial failures |
| No SMS support | Separate systems | Fragmented notifications |
| Audit trail | Manual logging | Compliance gaps |

## SQL Send Solution

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION/DATABASE                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  -- Send email from stored procedure                       │ │
│  │  EXEC sql2ai.SendEmail                                     │ │
│  │      @To = 'customer@example.com',                         │ │
│  │      @Subject = 'Order Confirmation',                      │ │
│  │      @Body = @EmailBody;                                   │ │
│  │                                                            │ │
│  │  -- Send SMS notification                                  │ │
│  │  EXEC sql2ai.SendSMS                                       │ │
│  │      @Phone = '+1234567890',                               │ │
│  │      @Message = 'Your order has shipped!';                 │ │
│  └────────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OUTBOX TABLE                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  MessageId | Type  | Provider | Status  | Payload          │ │
│  │  ──────────┼───────┼──────────┼─────────┼────────────────  │ │
│  │  msg-001   │ email │ sendgrid │ pending │ {to, subject...} │ │
│  │  msg-002   │ sms   │ twilio   │ pending │ {phone, msg...}  │ │
│  └────────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SQL SEND PROCESSOR                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  1. Poll outbox for pending messages                       │ │
│  │  2. Route to appropriate provider                          │ │
│  │  3. Deliver via provider API                               │ │
│  │  4. Update status (sent/failed)                            │ │
│  │  5. Handle retries with exponential backoff                │ │
│  └────────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
   │  SendGrid   │   │   Resend    │   │   Twilio    │
   │  (Email)    │   │   (Email)   │   │  (SMS/Voice)│
   └─────────────┘   └─────────────┘   └─────────────┘
```

## Supported Providers

### Email Providers
- **SendGrid** - Enterprise email delivery
- **Resend** - Modern developer-focused email
- **Amazon SES** - AWS email service
- **Mailgun** - Email API service
- **Postmark** - Transactional email
- **SMTP** - Any SMTP server

### SMS/Voice Providers
- **Twilio** - SMS, MMS, and Voice
- **AWS SNS** - Simple Notification Service
- **Vonage (Nexmo)** - Messaging API
- **MessageBird** - Communication platform

## Usage Examples

### SQL Server

```sql
-- Simple email
EXEC sql2ai.SendEmail
    @To = 'customer@example.com',
    @Subject = 'Welcome!',
    @Body = 'Thank you for signing up.';

-- HTML email with attachments
EXEC sql2ai.SendEmail
    @To = 'customer@example.com',
    @Cc = 'support@company.com',
    @Subject = 'Your Invoice',
    @BodyHtml = @InvoiceHtml,
    @Attachments = '[{"name": "invoice.pdf", "content": "base64..."}]',
    @Provider = 'sendgrid';  -- Optional: override default

-- Template-based email
EXEC sql2ai.SendEmailTemplate
    @To = 'customer@example.com',
    @TemplateName = 'order_confirmation',
    @TemplateData = '{"orderId": "12345", "total": "$99.99"}';

-- SMS notification
EXEC sql2ai.SendSMS
    @Phone = '+15551234567',
    @Message = 'Your verification code is: 123456';

-- Bulk send (efficient batch processing)
EXEC sql2ai.SendBulkEmail
    @Recipients = '[
        {"email": "user1@example.com", "name": "User 1"},
        {"email": "user2@example.com", "name": "User 2"}
    ]',
    @Subject = 'Monthly Newsletter',
    @BodyHtml = @NewsletterHtml;
```

### PostgreSQL

```sql
-- Simple email
SELECT sql2ai.send_email(
    _to := 'customer@example.com',
    _subject := 'Welcome!',
    _body := 'Thank you for signing up.'
);

-- HTML email with template
SELECT sql2ai.send_email_template(
    _to := 'customer@example.com',
    _template_name := 'order_confirmation',
    _template_data := '{"orderId": "12345", "total": "$99.99"}'::jsonb
);

-- SMS
SELECT sql2ai.send_sms(
    _phone := '+15551234567',
    _message := 'Your order has shipped!'
);
```

## Transactional Outbox Pattern

Messages are queued within the same transaction as your business logic:

```sql
BEGIN TRANSACTION;

    -- Business logic
    INSERT INTO Orders (CustomerId, Total)
    VALUES (@CustomerId, @Total);

    -- Queue confirmation email (same transaction)
    EXEC sql2ai.SendEmail
        @To = @CustomerEmail,
        @Subject = 'Order Confirmed',
        @Body = @ConfirmationBody;

    -- Queue SMS notification (same transaction)
    EXEC sql2ai.SendSMS
        @Phone = @CustomerPhone,
        @Message = 'Order #' + @OrderId + ' confirmed!';

COMMIT TRANSACTION;
-- Messages only sent if transaction commits
```

**Benefits:**
- Messages guaranteed to be queued if transaction succeeds
- No orphaned messages if business logic fails
- Retry logic handles provider failures
- Audit trail for all messages

## Provider Configuration

```yaml
# sql2ai-send.yaml
providers:
  sendgrid:
    type: sendgrid
    api_key: ${SENDGRID_API_KEY}
    from_email: noreply@company.com
    from_name: Company Name

  resend:
    type: resend
    api_key: ${RESEND_API_KEY}
    from_email: hello@company.com

  twilio:
    type: twilio
    account_sid: ${TWILIO_SID}
    auth_token: ${TWILIO_TOKEN}
    from_phone: +15551234567

routing:
  email:
    default: sendgrid
    rules:
      - match: "@enterprise.com"
        provider: resend  # Use Resend for enterprise clients

  sms:
    default: twilio

processor:
  poll_interval: 1s
  batch_size: 100
  retry:
    max_attempts: 5
    backoff: exponential
    initial_delay: 1s
    max_delay: 5m
```

## Templates

```yaml
# templates/order_confirmation.yaml
name: order_confirmation
subject: "Order #{{orderId}} Confirmed"
body_html: |
  <html>
    <body>
      <h1>Thank you for your order!</h1>
      <p>Order ID: {{orderId}}</p>
      <p>Total: {{total}}</p>
      <p>Shipping to: {{shippingAddress}}</p>
    </body>
  </html>
body_text: |
  Thank you for your order!
  Order ID: {{orderId}}
  Total: {{total}}
```

## Message Status Tracking

```sql
-- Check message status
SELECT
    MessageId,
    MessageType,
    Provider,
    Status,
    SentAt,
    ErrorMessage,
    RetryCount
FROM sql2ai.MessageOutbox
WHERE CorrelationId = @OrderId;
```

```
╔══════════════════════════════════════════════════════════════════╗
║ MESSAGE STATUS                                                   ║
╠══════════════════════════════════════════════════════════════════╣
║ MessageId: msg-12345                                             ║
║ Type: email                                                      ║
║ Provider: sendgrid                                               ║
║ Status: delivered                                                ║
║ Sent At: 2024-01-15 10:23:45                                     ║
║ Delivered At: 2024-01-15 10:23:47                                ║
║ Opens: 3                                                         ║
║ Clicks: 1                                                        ║
╚══════════════════════════════════════════════════════════════════╝
```

## Webhook Integration

Track delivery, opens, and clicks:

```yaml
webhooks:
  sendgrid:
    endpoint: /webhooks/sendgrid
    events: [delivered, opened, clicked, bounced, spam]

  twilio:
    endpoint: /webhooks/twilio
    events: [delivered, failed]
```

## Rate Limiting & Throttling

```yaml
rate_limits:
  sendgrid:
    requests_per_second: 100
    daily_limit: 100000

  twilio:
    sms_per_second: 10

  burst_handling:
    queue_overflow: defer  # Queue for later
    notification: alert_on_threshold
```

## Dashboard

```
╔══════════════════════════════════════════════════════════════════╗
║                    SQL SEND DASHBOARD                            ║
╠══════════════════════════════════════════════════════════════════╣
║ TODAY'S ACTIVITY                                                 ║
║ ─────────────────────────────────────────────────────────────── ║
║ Emails Sent:        4,721 │ SMS Sent:           892             ║
║ Delivered:          4,698 │ Delivered:          889             ║
║ Failed:             23    │ Failed:             3               ║
║ Delivery Rate:      99.5% │ Delivery Rate:      99.7%           ║
╠══════════════════════════════════════════════════════════════════╣
║ QUEUE STATUS                                                     ║
║ ─────────────────────────────────────────────────────────────── ║
║ Pending:            12    │ Processing:         3               ║
║ Retry Queue:        7     │ Failed (permanent): 2               ║
╠══════════════════════════════════════════════════════════════════╣
║ PROVIDER HEALTH                                                  ║
║ ─────────────────────────────────────────────────────────────── ║
║ SendGrid:           ● Healthy (latency: 45ms)                    ║
║ Twilio:             ● Healthy (latency: 120ms)                   ║
╚══════════════════════════════════════════════════════════════════╝
```

## CLI Commands

```bash
# Initialize SQL Send
sql2ai send init --connection "..."

# Test provider connection
sql2ai send test --provider sendgrid

# Process outbox manually
sql2ai send process --batch-size 100

# View queue status
sql2ai send status

# Retry failed messages
sql2ai send retry --status failed --from 2024-01-01
```

## Integration Points

- **SQL Orchestrate**: Schedule bulk sends
- **SQL Audit**: Log all message activity
- **SQL Monitor**: Dashboard for message metrics
- **SQL Comply**: Ensure message content compliance
