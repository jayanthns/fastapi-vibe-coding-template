"""
Tests for the notification system.

Tests the OOP notification system including base classes,
email notifications, and error handling.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.utils.notifications import (
    BaseNotification,
    EmailNotification,
    NotificationRecipient,
    NotificationStatus,
    NotificationType,
    SMSNotification,
    create_notification,
    send_email,
)


class TestNotificationRecipient:
    """Test NotificationRecipient dataclass."""

    def test_create_recipient_with_email(self):
        """Test creating recipient with email."""
        recipient = NotificationRecipient(
            id="user1", email="user@example.com", name="Test User"
        )

        assert recipient.id == "user1"
        assert recipient.email == "user@example.com"
        assert recipient.name == "Test User"
        assert recipient.phone is None

    def test_create_recipient_with_phone(self):
        """Test creating recipient with phone."""
        recipient = NotificationRecipient(
            id="user2", phone="+1234567890", name="Mobile User"
        )

        assert recipient.id == "user2"
        assert recipient.phone == "+1234567890"
        assert recipient.name == "Mobile User"
        assert recipient.email is None


class TestEmailNotification:
    """Test EmailNotification class."""

    def test_initialization(self):
        """Test EmailNotification initialization."""
        email_notifier = EmailNotification(
            smtp_server="smtp.example.com",
            smtp_port=587,
            from_email="test@example.com",
            trace_id="test-trace",
        )

        assert email_notifier.notification_type == NotificationType.EMAIL
        assert email_notifier.smtp_server == "smtp.example.com"
        assert email_notifier.smtp_port == 587
        assert email_notifier.from_email == "test@example.com"
        assert email_notifier.trace_id == "test-trace"

    def test_validate_recipient_valid_email(self):
        """Test email validation with valid email."""
        email_notifier = EmailNotification()
        recipient = NotificationRecipient(id="user1", email="valid@example.com")

        assert email_notifier.validate_recipient(recipient) is True

    def test_validate_recipient_invalid_email(self):
        """Test email validation with invalid email."""
        email_notifier = EmailNotification()
        recipient = NotificationRecipient(id="user1", email="invalid-email")

        assert email_notifier.validate_recipient(recipient) is False

    def test_validate_recipient_no_email(self):
        """Test email validation with no email."""
        email_notifier = EmailNotification()
        recipient = NotificationRecipient(
            id="user1", phone="+1234567890"  # No email provided
        )

        assert email_notifier.validate_recipient(recipient) is False

    @patch("smtplib.SMTP")
    async def test_send_single_email_success(self, mock_smtp):
        """Test sending single email successfully."""
        # Mock SMTP server
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        email_notifier = EmailNotification(
            smtp_server="smtp.example.com",
            from_email="test@example.com",
            trace_id="test-trace",
        )

        recipient = NotificationRecipient(
            id="user1", email="recipient@example.com", name="Test User"
        )

        result = await email_notifier.send(
            recipients=recipient, subject="Test Subject", content="Test content"
        )

        assert result.success is True
        assert result.status == NotificationStatus.SENT
        assert result.message == "Email sent successfully"
        assert "recipient_email" in result.metadata
        assert result.metadata["recipient_email"] == "recipient@example.com"

        # Verify SMTP was called
        mock_smtp.assert_called_once_with("smtp.example.com", 587)
        mock_server.send_message.assert_called_once()

    async def test_send_single_email_invalid_recipient(self):
        """Test sending email to invalid recipient."""
        email_notifier = EmailNotification(trace_id="test-trace")

        recipient = NotificationRecipient(
            id="user1", email="invalid-email"  # Invalid email format
        )

        result = await email_notifier.send(
            recipients=recipient, subject="Test Subject", content="Test content"
        )

        assert result.success is False
        assert result.status == NotificationStatus.FAILED
        assert "Invalid email recipient" in result.message
        assert result.error_details == "Invalid email address"

    @patch("smtplib.SMTP")
    async def test_send_multiple_emails(self, mock_smtp):
        """Test sending emails to multiple recipients."""
        # Mock SMTP server
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        email_notifier = EmailNotification(trace_id="test-trace")

        recipients = [
            NotificationRecipient(id="user1", email="user1@example.com"),
            NotificationRecipient(id="user2", email="user2@example.com"),
        ]

        results = await email_notifier.send(
            recipients=recipients, subject="Test Subject", content="Test content"
        )

        assert len(results) == 2
        assert all(result.success for result in results)
        assert all(result.status == NotificationStatus.SENT for result in results)

        # Verify SMTP was called for each recipient
        assert mock_smtp.call_count == 2

    @patch("smtplib.SMTP")
    async def test_send_email_with_html_content(self, mock_smtp):
        """Test sending email with HTML content."""
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        email_notifier = EmailNotification(trace_id="test-trace")
        recipient = NotificationRecipient(id="user1", email="user@example.com")

        result = await email_notifier.send(
            recipients=recipient,
            subject="Test Subject",
            content="Plain text content",
            html_content="<h1>HTML content</h1>",
        )

        assert result.success is True
        assert result.metadata["has_html"] is True

    @patch("smtplib.SMTP")
    async def test_send_email_smtp_error(self, mock_smtp):
        """Test handling SMTP errors."""
        # Mock SMTP to raise an exception
        mock_smtp.side_effect = Exception("SMTP connection failed")

        email_notifier = EmailNotification(trace_id="test-trace")
        recipient = NotificationRecipient(id="user1", email="user@example.com")

        result = await email_notifier.send(
            recipients=recipient, subject="Test Subject", content="Test content"
        )

        assert result.success is False
        assert result.status == NotificationStatus.FAILED
        assert "Failed to send email" in result.message
        assert "SMTP connection failed" in result.error_details


class TestSMSNotification:
    """Test SMSNotification class."""

    def test_initialization(self):
        """Test SMSNotification initialization."""
        sms_notifier = SMSNotification(
            provider="twilio", trace_id="test-trace", account_sid="test_sid"
        )

        assert sms_notifier.notification_type == NotificationType.SMS
        assert sms_notifier.provider == "twilio"
        assert sms_notifier.config["account_sid"] == "test_sid"

    def test_validate_recipient_valid_phone(self):
        """Test phone validation with valid phone number."""
        sms_notifier = SMSNotification()
        recipient = NotificationRecipient(id="user1", phone="+1234567890")

        assert sms_notifier.validate_recipient(recipient) is True

    def test_validate_recipient_invalid_phone(self):
        """Test phone validation with invalid phone number."""
        sms_notifier = SMSNotification()
        recipient = NotificationRecipient(id="user1", phone="123")  # Too short

        assert sms_notifier.validate_recipient(recipient) is False

    def test_validate_recipient_no_phone(self):
        """Test phone validation with no phone number."""
        sms_notifier = SMSNotification()
        recipient = NotificationRecipient(
            id="user1", email="user@example.com"  # No phone provided
        )

        assert sms_notifier.validate_recipient(recipient) is False

    async def test_send_sms_placeholder(self):
        """Test SMS sending (placeholder implementation)."""
        sms_notifier = SMSNotification(trace_id="test-trace")
        recipient = NotificationRecipient(id="user1", phone="+1234567890")

        result = await sms_notifier.send(
            recipients=recipient, subject="Test", content="Test SMS content"
        )

        # Since it's a placeholder, it should fail gracefully
        assert result.success is False
        assert "not yet implemented" in result.message
        assert result.status == NotificationStatus.FAILED


class TestNotificationFactory:
    """Test notification factory function."""

    def test_create_email_notification(self):
        """Test creating email notification via factory."""
        notifier = create_notification(
            NotificationType.EMAIL, trace_id="test-trace", from_email="test@example.com"
        )

        assert isinstance(notifier, EmailNotification)
        assert notifier.notification_type == NotificationType.EMAIL
        assert notifier.from_email == "test@example.com"

    def test_create_sms_notification(self):
        """Test creating SMS notification via factory."""
        notifier = create_notification(
            NotificationType.SMS, trace_id="test-trace", provider="twilio"
        )

        assert isinstance(notifier, SMSNotification)
        assert notifier.notification_type == NotificationType.SMS
        assert notifier.provider == "twilio"

    def test_create_unsupported_notification(self):
        """Test creating unsupported notification type."""
        with pytest.raises(ValueError, match="Unsupported notification type"):
            create_notification(NotificationType.PUSH)


class TestConvenienceFunctions:
    """Test convenience functions."""

    @patch("src.utils.notifications.EmailNotification.send")
    async def test_send_email_convenience(self, mock_send):
        """Test send_email convenience function."""
        # Mock the send method
        mock_result = Mock()
        mock_result.success = True
        mock_send.return_value = mock_result

        result = await send_email(
            to_email="user@example.com",
            subject="Test",
            content="Test content",
            trace_id="test-trace",
        )

        assert result.success is True
        mock_send.assert_called_once()

        # Check that the recipient was created correctly
        call_args = mock_send.call_args
        recipients = call_args[1]["recipients"]
        assert recipients.email == "user@example.com"
        assert recipients.id == "user@example.com"


class TestErrorHandling:
    """Test error handling scenarios."""

    async def test_base_notification_abstract_methods(self):
        """Test that BaseNotification cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseNotification()

    def test_notification_result_creation(self):
        """Test NotificationResult creation."""
        email_notifier = EmailNotification()

        result = email_notifier._create_result(
            success=True,
            message="Test message",
            status=NotificationStatus.SENT,
            metadata={"test": "data"},
        )

        assert result.success is True
        assert result.message == "Test message"
        assert result.status == NotificationStatus.SENT
        assert result.metadata["test"] == "data"
        assert result.notification_id == email_notifier.notification_id
