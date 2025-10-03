# Notification System Documentation

## Overview

The FastAPI Vibe Coding notification system provides a comprehensive, OOP-based solution for sending notifications through various channels. Currently supports email notifications with a foundation for SMS and other notification types.

## Architecture

### OOP Design Pattern

The notification system follows object-oriented programming principles with:

- **Abstract Base Class**: `BaseNotification` defines the common interface
- **Derived Classes**: `EmailNotification`, `SMSNotification` implement specific channels
- **Factory Pattern**: `create_notification()` for creating notification instances
- **Data Classes**: `NotificationRecipient`, `NotificationResult` for structured data

### Key Components

```python
# Base Classes
BaseNotification          # Abstract base class
├── EmailNotification     # SMTP email implementation
└── SMSNotification      # SMS placeholder (Twilio, AWS SNS ready)

# Supporting Classes
NotificationRecipient    # Recipient data structure
NotificationResult      # Result tracking with success/failure
NotificationStatus      # Enum: PENDING, SENT, FAILED, DELIVERED, BOUNCED
NotificationType       # Enum: EMAIL, SMS, PUSH
```

## Installation & Setup

### Dependencies

The notification system uses standard Python libraries:

```python
# Core dependencies (already in requirements.txt)
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
```

### Configuration

Configure email settings in your environment or `src/core/config.py`:

```python
# Environment variables (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourcompany.com
FROM_NAME=Your Company Name
```

## Usage Examples

### 1. Simple Email Sending

```python
from src.utils.notifications import send_email

# Send a simple email
result = await send_email(
    to_email="user@example.com",
    to_name="John Doe",
    subject="Welcome to Our Service!",
    content="Hello John, welcome to our amazing service!",
    html_content="<h1>Welcome!</h1><p>Hello John, welcome to our <strong>amazing</strong> service!</p>",
    trace_id="welcome-001"
)

print(f"Email sent: {result.success}")
print(f"Message: {result.message}")
print(f"Status: {result.status.value}")
```

### 2. Bulk Email Sending

```python
from src.utils.notifications import send_bulk_email

# Send emails to multiple recipients
recipients = [
    {"email": "user1@example.com", "name": "Alice Smith"},
    {"email": "user2@example.com", "name": "Bob Johnson"},
    {"email": "user3@example.com"},  # No name provided
]

results = await send_bulk_email(
    recipients=recipients,
    subject="Monthly Newsletter",
    content="Here's your monthly newsletter with updates and news.",
    html_content="""
    <h2>Monthly Newsletter</h2>
    <p>Here's your monthly newsletter with updates and news.</p>
    <ul>
        <li>Feature Update: New dashboard</li>
        <li>Bug Fix: Login issues resolved</li>
        <li>Coming Soon: Mobile app</li>
    </ul>
    """,
    trace_id="newsletter-001"
)

for i, result in enumerate(results):
    print(f"Email {i+1}: {result.success} - {result.message}")
```

### 3. Using EmailNotification Class Directly

```python
from src.utils.notifications import EmailNotification, NotificationRecipient

# Create email notification instance
email_notifier = EmailNotification(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    username="your-email@gmail.com",
    password="your-app-password",
    from_email="noreply@mycompany.com",
    from_name="My Company",
    trace_id="system-alert-001"
)

# Create recipients
recipients = [
    NotificationRecipient(id="user1", email="admin@example.com", name="Admin User"),
    NotificationRecipient(id="user2", email="manager@example.com", name="Manager"),
]

# Send notification
results = await email_notifier.send(
    recipients=recipients,
    subject="System Alert",
    content="This is an important system alert that requires your attention.",
    html_content="""
    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px;">
        <h3 style="color: #dc3545;">🚨 System Alert</h3>
        <p>This is an important system alert that requires your attention.</p>
        <p><strong>Action Required:</strong> Please check the system dashboard.</p>
    </div>
    """
)

for result in results:
    print(f"{result.metadata.get('recipient_email', 'Unknown')}: {result.success}")
```

### 4. Factory Pattern Usage

```python
from src.utils.notifications import create_notification, NotificationType, NotificationRecipient

# Create email notification using factory
email_notifier = create_notification(
    NotificationType.EMAIL,
    trace_id="support-001",
    smtp_server="smtp.gmail.com",
    from_email="support@example.com",
    from_name="Support Team"
)

recipient = NotificationRecipient(
    id="support-ticket-123",
    email="customer@example.com",
    name="Valued Customer"
)

result = await email_notifier.send(
    recipients=recipient,
    subject="Support Ticket Update",
    content="Your support ticket has been updated. Please check your account for details."
)

print(f"Support notification: {result.success}")
print(f"Notification type: {email_notifier.notification_type.value}")
```

### 5. SMS Notifications (Placeholder)

```python
from src.utils.notifications import SMSNotification, NotificationRecipient

# SMS notification (ready for Twilio, AWS SNS, etc.)
sms_notifier = SMSNotification(
    provider="twilio",
    trace_id="sms-001",
    account_sid="your-twilio-sid",
    auth_token="your-twilio-token"
)

recipient = NotificationRecipient(
    id="mobile-user",
    phone="+1234567890",
    name="Mobile User"
)

result = await sms_notifier.send(
    recipients=recipient,
    subject="Alert",
    content="Your verification code is: 123456"
)

print(f"SMS sent: {result.success}")
print(f"Message: {result.message}")
```

### 6. Error Handling

```python
from src.utils.notifications import EmailNotification, NotificationRecipient

email_notifier = EmailNotification(trace_id="error-handling-001")

# Invalid email recipient
invalid_recipient = NotificationRecipient(
    id="invalid-user",
    email="not-an-email",  # Invalid email format
    name="Invalid User"
)

result = await email_notifier.send(
    recipients=invalid_recipient,
    subject="Test Email",
    content="This should fail due to invalid email."
)

print(f"Success: {result.success}")
print(f"Message: {result.message}")
print(f"Status: {result.status.value}")
print(f"Error details: {result.error_details}")
```

## Common Email Templates

### Welcome Email Template

```python
async def send_welcome_email(user_email: str, user_name: str, trace_id: str = None):
    return await send_email(
        to_email=user_email,
        to_name=user_name,
        subject=f"Welcome to our platform, {user_name}!",
        content=f"""
Hello {user_name},

Welcome to our platform! We're excited to have you on board.

Here are some quick links to get you started:
- Complete your profile: https://example.com/profile
- Browse our features: https://example.com/features
- Contact support: support@example.com

Best regards,
The Team
        """.strip(),
        html_content=f"""
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <h1 style="color: #2c3e50;">Welcome to our platform, {user_name}! 🎉</h1>
    <p>We're excited to have you on board.</p>
    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
        <h3>Quick Links to Get Started:</h3>
        <ul>
            <li><a href="https://example.com/profile">Complete your profile</a></li>
            <li><a href="https://example.com/features">Browse our features</a></li>
            <li><a href="mailto:support@example.com">Contact support</a></li>
        </ul>
    </div>
    <p>Best regards,<br>The Team</p>
</div>
        """.strip(),
        trace_id=trace_id
    )
```

### Password Reset Email Template

```python
async def send_password_reset_email(user_email: str, reset_token: str, trace_id: str = None):
    reset_url = f"https://example.com/reset-password?token={reset_token}"
    return await send_email(
        to_email=user_email,
        subject="Reset Your Password",
        content=f"""
You requested a password reset for your account.

Click the link below to reset your password:
{reset_url}

This link will expire in 1 hour.

If you didn't request this reset, please ignore this email.

Best regards,
The Security Team
        """.strip(),
        html_content=f"""
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <h2 style="color: #e74c3c;">🔒 Password Reset Request</h2>
    <p>You requested a password reset for your account.</p>
    <div style="text-align: center; margin: 30px 0;">
        <a href="{reset_url}"
           style="background-color: #3498db; color: white; padding: 12px 24px;
                  text-decoration: none; border-radius: 5px; display: inline-block;">
            Reset Your Password
        </a>
    </div>
    <p><strong>Important:</strong> This link will expire in 1 hour.</p>
    <p>If you didn't request this reset, please ignore this email.</p>
    <p>Best regards,<br>The Security Team</p>
</div>
        """.strip(),
        trace_id=trace_id
    )
```

## Integration with FastAPI

### Using in API Endpoints

```python
from fastapi import APIRouter, HTTPException
from src.utils.notifications import send_email

router = APIRouter()

@router.post("/send-welcome-email")
async def send_welcome_email_endpoint(user_email: str, user_name: str):
    try:
        result = await send_email(
            to_email=user_email,
            to_name=user_name,
            subject="Welcome!",
            content=f"Hello {user_name}, welcome to our service!",
            trace_id=f"welcome-{user_email}"
        )

        if result.success:
            return {"message": "Welcome email sent successfully"}
        else:
            raise HTTPException(status_code=500, detail=result.message)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Background Task Integration

```python
from fastapi import BackgroundTasks
from src.utils.notifications import send_email

@router.post("/register")
async def register_user(user_data: UserCreate, background_tasks: BackgroundTasks):
    # Create user logic here...
    user = create_user(user_data)

    # Send welcome email in background
    background_tasks.add_task(
        send_welcome_email_background,
        user.email,
        user.name,
        f"welcome-{user.id}"
    )

    return {"message": "User registered successfully"}

async def send_welcome_email_background(email: str, name: str, trace_id: str):
    await send_email(
        to_email=email,
        to_name=name,
        subject="Welcome to our platform!",
        content=f"Hello {name}, welcome to our platform!",
        trace_id=trace_id
    )
```

## Advanced Features

### Logging and Tracing

All notifications include comprehensive logging with trace IDs:

```python
# Logs are automatically generated with trace IDs
# Example log output:
# 2024-01-01 10:00:00,123 | INFO | welcome-001 | src.notifications |
# Sending email notification (ID: abc123) to user@example.com

# 2024-01-01 10:00:01,456 | INFO | welcome-001 | src.notifications |
# Successfully sent email notification (ID: abc123) to user@example.com
```

### Result Tracking

Every notification returns detailed results:

```python
result = await send_email(...)

# Access result properties
print(f"Success: {result.success}")
print(f"Message: {result.message}")
print(f"Notification ID: {result.notification_id}")
print(f"Status: {result.status.value}")
print(f"Sent at: {result.sent_at}")
print(f"Error details: {result.error_details}")
print(f"Metadata: {result.metadata}")
```

### Validation

Built-in validation for recipients:

```python
# Email validation
email_notifier = EmailNotification()
recipient = NotificationRecipient(id="1", email="invalid-email")
is_valid = email_notifier.validate_recipient(recipient)  # Returns False

# Phone validation (for SMS)
sms_notifier = SMSNotification()
recipient = NotificationRecipient(id="1", phone="+1234567890")
is_valid = sms_notifier.validate_recipient(recipient)  # Returns True
```

## Extending the System

### Adding New Notification Types

To add a new notification type (e.g., Slack, Push notifications):

1. **Add to NotificationType enum**:
```python
class NotificationType(Enum):
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"  # New type
    PUSH = "push"    # New type
```

2. **Create new notification class**:
```python
class SlackNotification(BaseNotification):
    def __init__(self, webhook_url: str, trace_id: str = None):
        super().__init__(trace_id)
        self.webhook_url = webhook_url

    @property
    def notification_type(self) -> NotificationType:
        return NotificationType.SLACK

    def validate_recipient(self, recipient: NotificationRecipient) -> bool:
        # Validate Slack recipient (e.g., channel, user ID)
        return bool(recipient.metadata and recipient.metadata.get('slack_channel'))

    async def send(self, recipients, subject, content, **kwargs):
        # Implement Slack API integration
        pass
```

3. **Update factory function**:
```python
def create_notification(notification_type: NotificationType, **config):
    if notification_type == NotificationType.EMAIL:
        return EmailNotification(**config)
    elif notification_type == NotificationType.SMS:
        return SMSNotification(**config)
    elif notification_type == NotificationType.SLACK:
        return SlackNotification(**config)
    # ... etc
```

### SMS Provider Integration

To implement SMS with Twilio:

```python
# Update SMSNotification._send_single method
async def _send_single(self, recipient, subject, content, **kwargs):
    if self.provider == "twilio":
        from twilio.rest import Client

        client = Client(self.config['account_sid'], self.config['auth_token'])

        try:
            message = client.messages.create(
                body=content,
                from_=self.config['from_phone'],
                to=recipient.phone
            )

            return self._create_result(
                success=True,
                message="SMS sent successfully",
                status=NotificationStatus.SENT,
                metadata={"twilio_sid": message.sid}
            )
        except Exception as e:
            return self._create_result(
                success=False,
                message=f"SMS failed: {str(e)}",
                status=NotificationStatus.FAILED,
                error_details=str(e)
            )
```

## Testing

### Unit Testing

```python
import pytest
from unittest.mock import patch
from src.utils.notifications import EmailNotification, NotificationRecipient

@patch('smtplib.SMTP')
async def test_send_email_success(mock_smtp):
    # Mock SMTP server
    mock_server = Mock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    email_notifier = EmailNotification()
    recipient = NotificationRecipient(id="1", email="test@example.com")

    result = await email_notifier.send(
        recipients=recipient,
        subject="Test",
        content="Test content"
    )

    assert result.success is True
    assert result.status == NotificationStatus.SENT
    mock_smtp.assert_called_once()
```

### Integration Testing

```python
# Test with real SMTP server (use test credentials)
async def test_real_email_sending():
    email_notifier = EmailNotification(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        username="test@gmail.com",
        password="test-app-password",
        from_email="test@gmail.com"
    )

    recipient = NotificationRecipient(
        id="test",
        email="recipient@example.com"
    )

    result = await email_notifier.send(
        recipients=recipient,
        subject="Integration Test",
        content="This is a test email"
    )

    assert result.success is True
```

## Best Practices

### 1. Always Use Trace IDs
```python
# Good - with trace ID for debugging
result = await send_email(
    to_email="user@example.com",
    subject="Welcome",
    content="Welcome!",
    trace_id=f"welcome-{user_id}"
)

# Bad - no trace ID
result = await send_email(
    to_email="user@example.com",
    subject="Welcome",
    content="Welcome!"
)
```

### 2. Handle Errors Gracefully
```python
try:
    result = await send_email(...)
    if not result.success:
        logger.error(f"Email failed: {result.message}")
        # Handle failure (retry, alert admin, etc.)
except Exception as e:
    logger.error(f"Email system error: {e}")
    # Handle system-level errors
```

### 3. Use Templates for Consistency
```python
# Create reusable template functions
async def send_user_notification(user_id: str, template_type: str, **data):
    user = get_user(user_id)

    if template_type == "welcome":
        return await send_welcome_email(user.email, user.name, **data)
    elif template_type == "password_reset":
        return await send_password_reset_email(user.email, **data)
    # ... etc
```

### 4. Batch Operations for Performance
```python
# Good - bulk sending
recipients = [{"email": user.email, "name": user.name} for user in users]
results = await send_bulk_email(recipients, subject, content)

# Less efficient - individual sends
for user in users:
    await send_email(user.email, user.name, subject, content)
```

### 5. Environment-Based Configuration
```python
# Use environment variables for different stages
email_notifier = EmailNotification(
    smtp_server=settings.smtp_server,  # From environment
    from_email=settings.from_email,
    trace_id=trace_id
)
```

## Troubleshooting

### Common Issues

1. **SMTP Authentication Errors**
   - Verify SMTP credentials
   - Use app passwords for Gmail
   - Check firewall/network settings

2. **Email Not Delivered**
   - Check spam folders
   - Verify recipient email addresses
   - Review SMTP server logs

3. **Invalid Recipients**
   - Use validation before sending
   - Handle validation errors gracefully

4. **Performance Issues**
   - Use bulk sending for multiple recipients
   - Consider background tasks for large volumes
   - Implement rate limiting if needed

### Debugging

Enable detailed logging:

```python
import logging
logging.getLogger("src.notifications").setLevel(logging.DEBUG)
```

Check notification results:

```python
result = await send_email(...)
if not result.success:
    print(f"Error: {result.message}")
    print(f"Details: {result.error_details}")
    print(f"Metadata: {result.metadata}")
```

## Performance Considerations

- **Bulk Operations**: Use `send_bulk_email()` for multiple recipients
- **Background Tasks**: Use FastAPI background tasks for non-blocking sends
- **Connection Pooling**: SMTP connections are created per send (consider pooling for high volume)
- **Rate Limiting**: Implement rate limiting for high-volume scenarios
- **Async Operations**: All operations are async-compatible

## Security Considerations

- **Credentials**: Store SMTP credentials securely (environment variables, secrets management)
- **Validation**: Always validate recipient data before sending
- **Content Sanitization**: Sanitize HTML content to prevent injection
- **Rate Limiting**: Implement rate limiting to prevent abuse
- **Logging**: Be careful not to log sensitive information (passwords, tokens)

## API Reference

### Classes

#### `BaseNotification`
Abstract base class for all notification types.

#### `EmailNotification`
SMTP email notification implementation.

#### `SMSNotification`
SMS notification placeholder (ready for provider integration).

#### `NotificationRecipient`
Data class for recipient information.

#### `NotificationResult`
Data class for notification results.

### Functions

#### `send_email()`
Convenience function for sending single emails.

#### `send_bulk_email()`
Convenience function for sending bulk emails.

#### `create_notification()`
Factory function for creating notification instances.

### Enums

#### `NotificationType`
- EMAIL
- SMS
- PUSH

#### `NotificationStatus`
- PENDING
- SENT
- FAILED
- DELIVERED
- BOUNCED

---

## Contributing

To contribute to the notification system:

1. Follow the existing OOP patterns
2. Add comprehensive tests
3. Update documentation
4. Ensure backward compatibility
5. Add logging with trace IDs

## License

This notification system is part of the FastAPI Vibe Coding project.
