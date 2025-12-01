"""
Notification System with OOP Design

Base notification classes and implementations for email and SMS notifications.
Uses abstract base classes to enforce consistent interface across different
notification types.
"""

import smtplib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from typing import Any
from uuid import uuid4

from src.core.config import settings
from src.core.logging import get_logger_for_trace_id


class NotificationStatus(Enum):
    """Notification delivery status."""

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"
    BOUNCED = "bounced"


class NotificationType(Enum):
    """Types of notifications supported."""

    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


@dataclass
class NotificationResult:
    """Result of notification sending attempt."""

    success: bool
    message: str
    notification_id: str
    status: NotificationStatus
    sent_at: datetime | None = None
    error_details: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class NotificationRecipient:
    """Notification recipient information."""

    id: str
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    metadata: dict[str, Any] | None = None


class BaseNotification(ABC):
    """
    Abstract base class for all notification types.

    This class defines the interface that all notification implementations
    must follow, ensuring consistency across different notification channels.
    """

    def __init__(self, trace_id: str = None):
        """
        Initialize base notification.

        Args:
            trace_id: Optional trace ID for logging and tracking
        """
        self.trace_id = trace_id or str(uuid4())
        self.logger = get_logger_for_trace_id(self.trace_id, "src.notifications")
        self.notification_id = str(uuid4())
        self.created_at = datetime.now(timezone.utc)
        self.status = NotificationStatus.PENDING

    @property
    @abstractmethod
    def notification_type(self) -> NotificationType:
        """Return the type of notification."""
        pass

    @abstractmethod
    async def send(
        self,
        recipients: NotificationRecipient | list[NotificationRecipient],
        subject: str,
        content: str,
        **kwargs,
    ) -> NotificationResult | list[NotificationResult]:
        """
        Send notification to recipients.

        Args:
            recipients: Single recipient or list of recipients
            subject: Notification subject/title
            content: Notification content/body
            **kwargs: Additional notification-specific parameters

        Returns:
            NotificationResult or list of results for multiple recipients
        """
        pass

    @abstractmethod
    def validate_recipient(self, recipient: NotificationRecipient) -> bool:
        """
        Validate if recipient is valid for this notification type.

        Args:
            recipient: Recipient to validate

        Returns:
            True if recipient is valid, False otherwise
        """
        pass

    def _create_result(
        self,
        success: bool,
        message: str,
        status: NotificationStatus,
        error_details: str = None,
        metadata: dict[str, Any] = None,
    ) -> NotificationResult:
        """Create a notification result."""
        return NotificationResult(
            success=success,
            message=message,
            notification_id=self.notification_id,
            status=status,
            sent_at=datetime.now(timezone.utc) if success else None,
            error_details=error_details,
            metadata=metadata or {},
        )

    def _log_attempt(self, recipient: NotificationRecipient, action: str):
        """Log notification attempt."""
        recipient_info = recipient.email or recipient.phone or recipient.id
        self.logger.info(
            f"{action} {self.notification_type.value} notification "
            f"(ID: {self.notification_id}) to {recipient_info}"
        )

    def _log_result(self, result: NotificationResult, recipient: NotificationRecipient):
        """Log notification result."""
        recipient_info = recipient.email or recipient.phone or recipient.id
        if result.success:
            self.logger.info(
                f"Successfully sent {self.notification_type.value} notification "
                f"(ID: {result.notification_id}) to {recipient_info}"
            )
        else:
            self.logger.error(
                f"Failed to send {self.notification_type.value} notification "
                f"(ID: {result.notification_id}) to {recipient_info}: {result.message}"
            )


class EmailNotification(BaseNotification):
    """
    Email notification implementation.

    Handles sending emails using SMTP with support for both plain text
    and HTML content.
    """

    def __init__(
        self,
        smtp_server: str = None,
        smtp_port: int = None,
        username: str = None,
        password: str = None,
        use_tls: bool = True,
        from_email: str = None,
        from_name: str = None,
        trace_id: str = None,
    ):
        """
        Initialize email notification.

        Args:
            smtp_server: SMTP server hostname
            smtp_port: SMTP server port
            username: SMTP username
            password: SMTP password
            use_tls: Whether to use TLS encryption
            from_email: Sender email address
            from_name: Sender display name
            trace_id: Optional trace ID for logging
        """
        super().__init__(trace_id)

        # Use provided values or fall back to settings/defaults
        self.smtp_server = smtp_server or getattr(settings, "smtp_server", "localhost")
        self.smtp_port = smtp_port or getattr(settings, "smtp_port", 587)
        self.username = username or getattr(settings, "smtp_username", None)
        self.password = password or getattr(settings, "smtp_password", None)
        self.use_tls = use_tls
        self.from_email = from_email or getattr(settings, "from_email", "noreply@example.com")
        self.from_name = from_name or getattr(settings, "from_name", "FastAPI App")

    @property
    def notification_type(self) -> NotificationType:
        """Return email notification type."""
        return NotificationType.EMAIL

    def validate_recipient(self, recipient: NotificationRecipient) -> bool:
        """
        Validate email recipient.

        Args:
            recipient: Recipient to validate

        Returns:
            True if recipient has valid email, False otherwise
        """
        if not recipient.email:
            return False

        # Basic email validation
        import re

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(email_pattern, recipient.email))

    async def send(
        self,
        recipients: NotificationRecipient | list[NotificationRecipient],
        subject: str,
        content: str,
        html_content: str = None,
        attachments: list[str] = None,
        **kwargs,
    ) -> NotificationResult | list[NotificationResult]:
        """
        Send email notification.

        Args:
            recipients: Single recipient or list of recipients
            subject: Email subject
            content: Plain text email content
            html_content: Optional HTML email content
            attachments: Optional list of file paths to attach
            **kwargs: Additional email parameters

        Returns:
            NotificationResult or list of results for multiple recipients
        """
        # Handle single recipient
        if isinstance(recipients, NotificationRecipient):
            return await self._send_single(
                recipients, subject, content, html_content, attachments, **kwargs
            )

        # Handle multiple recipients
        results = []
        for recipient in recipients:
            result = await self._send_single(
                recipient, subject, content, html_content, attachments, **kwargs
            )
            results.append(result)

        return results

    async def _send_single(
        self,
        recipient: NotificationRecipient,
        subject: str,
        content: str,
        html_content: str = None,
        attachments: list[str] = None,
        **kwargs,
    ) -> NotificationResult:
        """Send email to a single recipient."""
        self._log_attempt(recipient, "Sending")

        # Validate recipient
        if not self.validate_recipient(recipient):
            error_msg = f"Invalid email recipient: {recipient.email}"
            self.logger.error(error_msg)
            return self._create_result(
                success=False,
                message=error_msg,
                status=NotificationStatus.FAILED,
                error_details="Invalid email address",
            )

        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = recipient.email
            msg["Message-ID"] = f"<{self.notification_id}@{self.smtp_server}>"

            # Add plain text content
            text_part = MIMEText(content, "plain", "utf-8")
            msg.attach(text_part)

            # Add HTML content if provided
            if html_content:
                html_part = MIMEText(html_content, "html", "utf-8")
                msg.attach(html_part)

            # TODO: Handle attachments if needed
            if attachments:
                self.logger.warning("Email attachments not yet implemented")

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()

                if self.username and self.password:
                    server.login(self.username, self.password)

                server.send_message(msg)

            result = self._create_result(
                success=True,
                message="Email sent successfully",
                status=NotificationStatus.SENT,
                metadata={
                    "recipient_email": recipient.email,
                    "subject": subject,
                    "has_html": bool(html_content),
                    "smtp_server": self.smtp_server,
                },
            )

            self._log_result(result, recipient)
            return result

        except Exception as e:
            error_msg = f"Failed to send email: {str(e)}"
            result = self._create_result(
                success=False,
                message=error_msg,
                status=NotificationStatus.FAILED,
                error_details=str(e),
                metadata={
                    "recipient_email": recipient.email,
                    "smtp_server": self.smtp_server,
                },
            )

            self._log_result(result, recipient)
            return result


class SMSNotification(BaseNotification):
    """
    SMS notification implementation (placeholder).

    This is a placeholder implementation that can be extended
    to integrate with SMS providers like Twilio, AWS SNS, etc.
    """

    def __init__(self, provider: str = "twilio", trace_id: str = None, **config):
        """
        Initialize SMS notification.

        Args:
            provider: SMS provider name
            trace_id: Optional trace ID for logging
            **config: Provider-specific configuration
        """
        super().__init__(trace_id)
        self.provider = provider
        self.config = config

    @property
    def notification_type(self) -> NotificationType:
        """Return SMS notification type."""
        return NotificationType.SMS

    def validate_recipient(self, recipient: NotificationRecipient) -> bool:
        """
        Validate SMS recipient.

        Args:
            recipient: Recipient to validate

        Returns:
            True if recipient has valid phone number, False otherwise
        """
        if not recipient.phone:
            return False

        # Basic phone number validation (can be enhanced)
        import re

        phone_pattern = r"^\+?[\d\s\-\(\)]{10,}$"
        return bool(re.match(phone_pattern, recipient.phone.replace(" ", "").replace("-", "")))

    async def send(
        self,
        recipients: NotificationRecipient | list[NotificationRecipient],
        subject: str,
        content: str,
        **kwargs,
    ) -> NotificationResult | list[NotificationResult]:
        """
        Send SMS notification (placeholder implementation).

        Args:
            recipients: Single recipient or list of recipients
            subject: SMS subject (may be ignored by some providers)
            content: SMS content
            **kwargs: Additional SMS parameters

        Returns:
            NotificationResult or list of results
        """
        # Handle single recipient
        if isinstance(recipients, NotificationRecipient):
            return await self._send_single(recipients, subject, content, **kwargs)

        # Handle multiple recipients
        results = []
        for recipient in recipients:
            result = await self._send_single(recipient, subject, content, **kwargs)
            results.append(result)

        return results

    async def _send_single(
        self, recipient: NotificationRecipient, subject: str, content: str, **kwargs
    ) -> NotificationResult:
        """Send SMS to a single recipient (placeholder)."""
        self._log_attempt(recipient, "Sending")

        # Validate recipient
        if not self.validate_recipient(recipient):
            error_msg = f"Invalid SMS recipient: {recipient.phone}"
            self.logger.error(error_msg)
            return self._create_result(
                success=False,
                message=error_msg,
                status=NotificationStatus.FAILED,
                error_details="Invalid phone number",
            )

        # TODO: Implement actual SMS sending logic based on provider
        self.logger.info(f"SMS sending not yet implemented for provider: {self.provider}")

        return self._create_result(
            success=False,
            message="SMS sending not yet implemented",
            status=NotificationStatus.FAILED,
            error_details="SMS functionality is placeholder",
            metadata={"recipient_phone": recipient.phone, "provider": self.provider},
        )


# Factory function for creating notifications
def create_notification(
    notification_type: NotificationType, trace_id: str = None, **config
) -> BaseNotification:
    """
    Factory function to create notification instances.

    Args:
        notification_type: Type of notification to create
        trace_id: Optional trace ID for logging
        **config: Configuration parameters for the notification

    Returns:
        Notification instance

    Raises:
        ValueError: If notification type is not supported
    """
    if notification_type == NotificationType.EMAIL:
        return EmailNotification(trace_id=trace_id, **config)
    elif notification_type == NotificationType.SMS:
        return SMSNotification(trace_id=trace_id, **config)
    else:
        raise ValueError(f"Unsupported notification type: {notification_type}")


# Convenience functions
async def send_email(
    to_email: str,
    subject: str,
    content: str,
    html_content: str = None,
    to_name: str = None,
    trace_id: str = None,
    **email_config,
) -> NotificationResult:
    """
    Convenience function to send a single email.

    Args:
        to_email: Recipient email address
        subject: Email subject
        content: Plain text email content
        html_content: Optional HTML email content
        to_name: Optional recipient name
        trace_id: Optional trace ID for logging
        **email_config: Additional email configuration

    Returns:
        NotificationResult
    """
    email_notification = EmailNotification(trace_id=trace_id, **email_config)
    recipient = NotificationRecipient(id=to_email, email=to_email, name=to_name)

    return await email_notification.send(
        recipients=recipient,
        subject=subject,
        content=content,
        html_content=html_content,
    )


async def send_bulk_email(
    recipients: list[dict[str, str]],
    subject: str,
    content: str,
    html_content: str = None,
    trace_id: str = None,
    **email_config,
) -> list[NotificationResult]:
    """
    Convenience function to send bulk emails.

    Args:
        recipients: List of recipient dicts with 'email' and optional 'name'
        subject: Email subject
        content: Plain text email content
        html_content: Optional HTML email content
        trace_id: Optional trace ID for logging
        **email_config: Additional email configuration

    Returns:
        List of NotificationResult
    """
    email_notification = EmailNotification(trace_id=trace_id, **email_config)

    notification_recipients = [
        NotificationRecipient(id=r["email"], email=r["email"], name=r.get("name"))
        for r in recipients
    ]

    return await email_notification.send(
        recipients=notification_recipients,
        subject=subject,
        content=content,
        html_content=html_content,
    )
