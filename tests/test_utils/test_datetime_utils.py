"""
Tests for DateTime Utilities

Comprehensive test suite for date/time utility functions.
"""

from datetime import date, datetime, timedelta, timezone
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

import pytest

from src.utils.datetime_utils import (
    DateTimeUtils,
    DateTimeUtilsError,
    convert_timezone,
    format_datetime,
    from_timestamp,
    get_business_days_between,
    get_duration_between,
    get_timestamp,
    now,
    parse_datetime,
    today,
)


class TestDateTimeUtils:
    """Test cases for DateTimeUtils class."""

    def test_init(self):
        """Test DateTimeUtils initialization."""
        utils = DateTimeUtils()
        assert utils.trace_id == "datetime-utils"
        assert utils.logger is not None

        utils_with_trace = DateTimeUtils("test-trace-123")
        assert utils_with_trace.trace_id == "test-trace-123"

    def test_get_timezone_valid(self):
        """Test getting valid timezone."""
        utils = DateTimeUtils()

        # Test common abbreviations
        assert utils.get_timezone("utc") is not None
        assert utils.get_timezone("est") is not None
        assert utils.get_timezone("ist") is not None

        # Test full timezone names
        assert utils.get_timezone("UTC") is not None
        assert utils.get_timezone("US/Eastern") is not None
        assert utils.get_timezone("Asia/Kolkata") is not None

    def test_get_timezone_invalid(self):
        """Test getting invalid timezone."""
        utils = DateTimeUtils()

        with pytest.raises(DateTimeUtilsError):
            utils.get_timezone("invalid_timezone")

    def test_now(self):
        """Test getting current datetime."""
        utils = DateTimeUtils()

        # Test with UTC
        utc_now = utils.now()
        assert isinstance(utc_now, datetime)
        assert utc_now.tzinfo is not None

        # Test with specific timezone
        est_now = utils.now("US/Eastern")
        assert isinstance(est_now, datetime)
        assert est_now.tzinfo is not None

    def test_today(self):
        """Test getting current date."""
        utils = DateTimeUtils()

        # Test with UTC
        utc_today = utils.today()
        assert isinstance(utc_today, date)

        # Test with specific timezone
        est_today = utils.today("US/Eastern")
        assert isinstance(est_today, date)

    def test_convert_timezone(self):
        """Test timezone conversion."""
        utils = DateTimeUtils()

        # Create a UTC datetime
        utc_dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        # Convert to EST
        est_dt = utils.convert_timezone(utc_dt, "UTC", "US/Eastern")
        assert est_dt.tzinfo is not None
        assert est_dt.hour != utc_dt.hour  # Different timezone

    def test_format_datetime(self):
        """Test datetime formatting."""
        utils = DateTimeUtils()

        dt = datetime(2024, 1, 1, 12, 30, 45)

        # Test default format
        formatted = utils.format_datetime(dt)
        assert formatted == "2024-01-01 12:30:45"

        # Test custom format
        formatted = utils.format_datetime(dt, "%Y-%m-%d")
        assert formatted == "2024-01-01"

        # Test with timezone
        formatted = utils.format_datetime(dt, "%Y-%m-%d %H:%M:%S", "US/Eastern")
        assert "2024-01-01" in formatted

    def test_parse_datetime(self):
        """Test datetime parsing."""
        utils = DateTimeUtils()

        # Test with format string
        parsed = utils.parse_datetime("2024-01-01 12:30:45", "%Y-%m-%d %H:%M:%S")
        assert parsed.year == 2024
        assert parsed.month == 1
        assert parsed.day == 1

        # Test auto-detection
        parsed = utils.parse_datetime("2024-01-01T12:30:45")
        assert parsed.year == 2024

        # Test with timezone
        parsed = utils.parse_datetime("2024-01-01 12:30:45", tz="US/Eastern")
        assert parsed.tzinfo is not None

    def test_add_days(self):
        """Test adding days to datetime."""
        utils = DateTimeUtils()

        dt = datetime(2024, 1, 1, 12, 0, 0)

        # Add positive days
        result = utils.add_days(dt, 5)
        assert result.day == 6

        # Add negative days
        result = utils.add_days(dt, -5)
        assert result.day == 27  # Previous month

    def test_add_hours(self):
        """Test adding hours to datetime."""
        utils = DateTimeUtils()

        dt = datetime(2024, 1, 1, 12, 0, 0)

        # Add positive hours
        result = utils.add_hours(dt, 5)
        assert result.hour == 17

        # Add negative hours
        result = utils.add_hours(dt, -5)
        assert result.hour == 7

    def test_add_minutes(self):
        """Test adding minutes to datetime."""
        utils = DateTimeUtils()

        dt = datetime(2024, 1, 1, 12, 0, 0)

        # Add positive minutes
        result = utils.add_minutes(dt, 30)
        assert result.minute == 30

        # Add negative minutes
        result = utils.add_minutes(dt, -30)
        assert result.minute == 30  # Previous hour

    def test_add_months(self):
        """Test adding months to datetime."""
        utils = DateTimeUtils()

        dt = datetime(2024, 1, 1, 12, 0, 0)

        # Add positive months
        result = utils.add_months(dt, 3)
        assert result.month == 4

        # Add negative months
        result = utils.add_months(dt, -3)
        assert result.month == 10  # Previous year

    def test_add_years(self):
        """Test adding years to datetime."""
        utils = DateTimeUtils()

        dt = datetime(2024, 1, 1, 12, 0, 0)

        # Add positive years
        result = utils.add_years(dt, 2)
        assert result.year == 2026

        # Add negative years
        result = utils.add_years(dt, -2)
        assert result.year == 2022

    def test_get_business_days_between(self):
        """Test business days calculation."""
        utils = DateTimeUtils()

        start_date = date(2024, 1, 1)  # Monday
        end_date = date(2024, 1, 7)  # Sunday

        # Test with weekends excluded
        business_days = utils.get_business_days_between(start_date, end_date)
        assert business_days == 5  # Monday to Friday

        # Test with weekends included
        business_days = utils.get_business_days_between(
            start_date, end_date, exclude_weekends=False
        )
        assert business_days == 7  # All days

    def test_get_business_days_between_with_holidays(self):
        """Test business days calculation with holidays."""
        utils = DateTimeUtils()

        start_date = date(2024, 1, 1)  # Monday
        end_date = date(2024, 1, 5)  # Friday
        holidays = [date(2024, 1, 2)]  # Tuesday holiday

        business_days = utils.get_business_days_between(
            start_date, end_date, exclude_holidays=holidays
        )
        assert business_days == 4  # Monday, Wednesday, Thursday, Friday

    def test_get_next_business_day(self):
        """Test getting next business day."""
        utils = DateTimeUtils()

        # Friday to Monday
        friday = date(2024, 1, 5)  # Friday
        next_business = utils.get_next_business_day(friday)
        assert next_business.weekday() == 0  # Monday

        # Monday to Tuesday
        monday = date(2024, 1, 1)  # Monday
        next_business = utils.get_next_business_day(monday)
        assert next_business.weekday() == 1  # Tuesday

    def test_get_previous_business_day(self):
        """Test getting previous business day."""
        utils = DateTimeUtils()

        # Monday to Friday
        monday = date(2024, 1, 1)  # Monday
        prev_business = utils.get_previous_business_day(monday)
        assert prev_business.weekday() == 4  # Friday (previous week)

        # Tuesday to Monday
        tuesday = date(2024, 1, 2)  # Tuesday
        prev_business = utils.get_previous_business_day(tuesday)
        assert prev_business.weekday() == 0  # Monday

    def test_get_duration_between(self):
        """Test duration calculation."""
        utils = DateTimeUtils()

        start_dt = datetime(2024, 1, 1, 12, 0, 0)
        end_dt = datetime(2024, 1, 2, 14, 30, 45)

        duration = utils.get_duration_between(start_dt, end_dt)

        assert duration["days"] == 1
        assert duration["hours"] == 2
        assert duration["minutes"] == 30
        assert duration["seconds"] == 45

    def test_get_human_readable_duration(self):
        """Test human-readable duration."""
        utils = DateTimeUtils()

        start_dt = datetime(2024, 1, 1, 12, 0, 0)
        end_dt = datetime(2024, 1, 3, 14, 30, 45)

        duration = utils.get_human_readable_duration(start_dt, end_dt)

        assert "2 days" in duration
        assert "2 hours" in duration
        assert "30 minutes" in duration
        assert "45 seconds" in duration

    def test_get_timestamp(self):
        """Test timestamp conversion."""
        utils = DateTimeUtils()

        # Test with current time
        timestamp = utils.get_timestamp()
        assert isinstance(timestamp, int)
        assert timestamp > 0

        # Test with specific datetime
        dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        timestamp = utils.get_timestamp(dt)
        assert isinstance(timestamp, int)

    def test_from_timestamp(self):
        """Test converting timestamp to datetime."""
        utils = DateTimeUtils()

        timestamp = 1704110400  # 2024-01-01 12:00:00 UTC
        dt = utils.from_timestamp(timestamp)

        assert dt.year == 2024
        assert dt.month == 1
        assert dt.day == 1

    def test_get_iso_format(self):
        """Test ISO format conversion."""
        utils = DateTimeUtils()

        dt = datetime(2024, 1, 1, 12, 30, 45, tzinfo=timezone.utc)
        iso_str = utils.get_iso_format(dt)

        assert "2024-01-01T12:30:45" in iso_str

    def test_from_iso_format(self):
        """Test parsing ISO format."""
        utils = DateTimeUtils()

        iso_str = "2024-01-01T12:30:45Z"
        dt = utils.from_iso_format(iso_str)

        assert dt.year == 2024
        assert dt.month == 1
        assert dt.day == 1

    def test_get_week_start(self):
        """Test getting week start."""
        utils = DateTimeUtils()

        # Monday
        monday = date(2024, 1, 1)
        week_start = utils.get_week_start(monday)
        assert week_start.weekday() == 0  # Monday

        # Friday
        friday = date(2024, 1, 5)
        week_start = utils.get_week_start(friday)
        assert week_start.weekday() == 0  # Monday of same week

    def test_get_week_end(self):
        """Test getting week end."""
        utils = DateTimeUtils()

        # Monday
        monday = date(2024, 1, 1)
        week_end = utils.get_week_end(monday)
        assert week_end.weekday() == 6  # Sunday

        # Friday
        friday = date(2024, 1, 5)
        week_end = utils.get_week_end(friday)
        assert week_end.weekday() == 6  # Sunday of same week

    def test_get_month_start(self):
        """Test getting month start."""
        utils = DateTimeUtils()

        dt = date(2024, 1, 15)
        month_start = utils.get_month_start(dt)
        assert month_start.day == 1
        assert month_start.month == 1

    def test_get_month_end(self):
        """Test getting month end."""
        utils = DateTimeUtils()

        dt = date(2024, 1, 15)
        month_end = utils.get_month_end(dt)
        assert month_end.day == 31
        assert month_end.month == 1

    def test_get_year_start(self):
        """Test getting year start."""
        utils = DateTimeUtils()

        dt = date(2024, 6, 15)
        year_start = utils.get_year_start(dt)
        assert year_start.month == 1
        assert year_start.day == 1

    def test_get_year_end(self):
        """Test getting year end."""
        utils = DateTimeUtils()

        dt = date(2024, 6, 15)
        year_end = utils.get_year_end(dt)
        assert year_end.month == 12
        assert year_end.day == 31

    def test_is_weekend(self):
        """Test weekend detection."""
        utils = DateTimeUtils()

        # Monday
        monday = date(2024, 1, 1)
        assert not utils.is_weekend(monday)

        # Saturday
        saturday = date(2024, 1, 6)
        assert utils.is_weekend(saturday)

        # Sunday
        sunday = date(2024, 1, 7)
        assert utils.is_weekend(sunday)

    def test_is_holiday(self):
        """Test holiday detection."""
        utils = DateTimeUtils()

        holidays = [date(2024, 1, 1), date(2024, 12, 25)]

        # New Year's Day
        assert utils.is_holiday(date(2024, 1, 1), holidays)

        # Christmas
        assert utils.is_holiday(date(2024, 12, 25), holidays)

        # Regular day
        assert not utils.is_holiday(date(2024, 1, 2), holidays)

    def test_get_age(self):
        """Test age calculation."""
        utils = DateTimeUtils()

        birth_date = date(1990, 1, 1)
        reference_date = date(2024, 1, 1)

        age = utils.get_age(birth_date, reference_date)
        assert age == 34

    def test_get_quarter(self):
        """Test quarter calculation."""
        utils = DateTimeUtils()

        # Q1
        assert utils.get_quarter(date(2024, 1, 1)) == 1
        assert utils.get_quarter(date(2024, 3, 31)) == 1

        # Q2
        assert utils.get_quarter(date(2024, 4, 1)) == 2
        assert utils.get_quarter(date(2024, 6, 30)) == 2

        # Q3
        assert utils.get_quarter(date(2024, 7, 1)) == 3
        assert utils.get_quarter(date(2024, 9, 30)) == 3

        # Q4
        assert utils.get_quarter(date(2024, 10, 1)) == 4
        assert utils.get_quarter(date(2024, 12, 31)) == 4

    def test_get_quarter_start(self):
        """Test getting quarter start."""
        utils = DateTimeUtils()

        # Q1
        q1_start = utils.get_quarter_start(date(2024, 2, 15))
        assert q1_start.month == 1
        assert q1_start.day == 1

        # Q2
        q2_start = utils.get_quarter_start(date(2024, 5, 15))
        assert q2_start.month == 4
        assert q2_start.day == 1

    def test_get_quarter_end(self):
        """Test getting quarter end."""
        utils = DateTimeUtils()

        # Q1
        q1_end = utils.get_quarter_end(date(2024, 2, 15))
        assert q1_end.month == 3
        assert q1_end.day == 31

        # Q2
        q2_end = utils.get_quarter_end(date(2024, 5, 15))
        assert q2_end.month == 6
        assert q2_end.day == 30

    def test_validate_date_range(self):
        """Test date range validation."""
        utils = DateTimeUtils()

        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)

        # Valid range
        assert utils.validate_date_range(start_date, end_date)

        # Invalid range (start > end)
        assert not utils.validate_date_range(end_date, start_date)

        # Valid range with max days
        assert utils.validate_date_range(start_date, end_date, max_days=31)

        # Invalid range with max days
        assert not utils.validate_date_range(start_date, end_date, max_days=30)

    def test_get_common_formats(self):
        """Test getting common formats."""
        utils = DateTimeUtils()

        formats = utils.get_common_formats()

        assert "iso" in formats
        assert "us_date" in formats
        assert "eu_date" in formats
        assert "readable" in formats
        assert "filename_safe" in formats


class TestConvenienceFunctions:
    """Test cases for convenience functions."""

    def test_now(self):
        """Test now convenience function."""
        result = now()
        assert isinstance(result, datetime)

        result_with_tz = now("US/Eastern")
        assert isinstance(result_with_tz, datetime)

    def test_today(self):
        """Test today convenience function."""
        result = today()
        assert isinstance(result, date)

        result_with_tz = today("US/Eastern")
        assert isinstance(result_with_tz, date)

    def test_convert_timezone(self):
        """Test convert_timezone convenience function."""
        utc_dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        result = convert_timezone(utc_dt, "UTC", "US/Eastern")
        assert isinstance(result, datetime)

    def test_format_datetime(self):
        """Test format_datetime convenience function."""
        dt = datetime(2024, 1, 1, 12, 30, 45)
        result = format_datetime(dt)
        assert result == "2024-01-01 12:30:45"

    def test_parse_datetime(self):
        """Test parse_datetime convenience function."""
        result = parse_datetime("2024-01-01 12:30:45", "%Y-%m-%d %H:%M:%S")
        assert result.year == 2024

    def test_get_business_days_between(self):
        """Test get_business_days_between convenience function."""
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 7)
        result = get_business_days_between(start_date, end_date)
        assert result == 5

    def test_get_duration_between(self):
        """Test get_duration_between convenience function."""
        start_dt = datetime(2024, 1, 1, 12, 0, 0)
        end_dt = datetime(2024, 1, 2, 14, 30, 45)
        result = get_duration_between(start_dt, end_dt)
        assert result["days"] == 1

    def test_get_timestamp(self):
        """Test get_timestamp convenience function."""
        result = get_timestamp()
        assert isinstance(result, int)

    def test_from_timestamp(self):
        """Test from_timestamp convenience function."""
        timestamp = 1704110400
        result = from_timestamp(timestamp)
        assert result.year == 2024


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_invalid_timezone_error(self):
        """Test invalid timezone error handling."""
        utils = DateTimeUtils()

        with pytest.raises(DateTimeUtilsError):
            utils.get_timezone("invalid_timezone")

    def test_timezone_conversion_error(self):
        """Test timezone conversion error handling."""
        utils = DateTimeUtils()

        with patch.object(
            utils, "get_timezone", side_effect=Exception("Timezone error")
        ):
            with pytest.raises(DateTimeUtilsError):
                utils.convert_timezone(
                    datetime(2024, 1, 1, 12, 0, 0), "UTC", "US/Eastern"
                )

    def test_datetime_formatting_error(self):
        """Test datetime formatting error handling."""
        utils = DateTimeUtils()

        with patch.object(
            utils, "convert_timezone", side_effect=Exception("Conversion error")
        ):
            with pytest.raises(DateTimeUtilsError):
                utils.format_datetime(datetime(2024, 1, 1, 12, 0, 0), tz="US/Eastern")

    def test_datetime_parsing_error(self):
        """Test datetime parsing error handling."""
        utils = DateTimeUtils()

        with pytest.raises(DateTimeUtilsError):
            utils.parse_datetime("invalid_date_string")
