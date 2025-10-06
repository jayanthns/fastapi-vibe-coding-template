"""
Date/Time Utilities

Comprehensive date and time utilities for FastAPI applications.
Provides timezone handling, formatting, business day calculations, and more.

Author: FastAPI Vibe Coding
Created: 2024
"""

from datetime import date, datetime, timedelta, timezone
from typing import Dict, List, Optional, Union
from zoneinfo import ZoneInfo

import pytz  # type: ignore
from dateutil import parser, relativedelta  # type: ignore

from src.core.logging import get_logger_for_trace_id


class DateTimeUtilsError(Exception):
    """Custom exception for date/time utility errors."""

    pass


class DateTimeUtils:
    """
    Comprehensive date and time utilities.

    Features:
    - Timezone conversion and handling
    - Date formatting and parsing
    - Business day calculations
    - Duration/interval calculations
    - Timestamp utilities
    - Date validation and manipulation
    """

    def __init__(self, trace_id: Optional[str] = None):
        """
        Initialize DateTimeUtils.

        Args:
            trace_id: Optional trace ID for logging
        """
        self.trace_id = trace_id or "datetime-utils"
        self.logger = get_logger_for_trace_id(self.trace_id, "src.datetime_utils")

        # Common timezone mappings
        self.timezone_mappings = {
            "utc": "UTC",
            "gmt": "GMT",
            "est": "US/Eastern",
            "pst": "US/Pacific",
            "cst": "US/Central",
            "mst": "US/Mountain",
            "ist": "Asia/Kolkata",
            "jst": "Asia/Tokyo",
            "cet": "Europe/Berlin",
            "aest": "Australia/Sydney",
        }

    def get_timezone(self, tz_name: str) -> timezone:
        """
        Get timezone object from name.

        Args:
            tz_name: Timezone name (e.g., 'UTC', 'US/Eastern', 'Asia/Kolkata')
                    Also supports common abbreviations like 'est', 'pst', 'ist'

        Returns:
            timezone object

        Raises:
            DateTimeUtilsError: If timezone is invalid

        Examples:
            >>> utils = DateTimeUtils()
            >>> tz = utils.get_timezone('UTC')
            >>> tz = utils.get_timezone('US/Eastern')
            >>> tz = utils.get_timezone('est')  # Abbreviation for US/Eastern
            >>> tz = utils.get_timezone('Asia/Kolkata')
        """
        try:
            # Check if it's a common abbreviation
            if tz_name.lower() in self.timezone_mappings:
                tz_name = self.timezone_mappings[tz_name.lower()]

            # Try zoneinfo first (Python 3.9+)
            try:
                return ZoneInfo(tz_name)  # type: ignore
            except Exception:
                # Fallback to pytz
                return pytz.timezone(tz_name)
        except Exception as e:
            self.logger.error(
                f"Invalid timezone: {tz_name}", extra={"trace_id": self.trace_id}
            )
            raise DateTimeUtilsError(f"Invalid timezone: {tz_name}") from e

    def now(self, tz: Optional[str] = None) -> datetime:
        """
        Get current datetime in specified timezone.

        Args:
            tz: Timezone name (default: UTC)

        Returns:
            Current datetime in specified timezone

        Examples:
            >>> utils = DateTimeUtils()
            >>> now_utc = utils.now()  # Returns: datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC)
            >>> now_est = utils.now('US/Eastern')  # Returns: datetime(2024, 1, 15, 5, 30, 0, tzinfo=EST)
            >>> now_ist = utils.now('Asia/Kolkata')  # Returns: datetime(2024, 1, 15, 16, 0, 0, tzinfo=IST)
        """
        if tz:
            timezone_obj = self.get_timezone(tz)
            return datetime.now(timezone_obj)
        return datetime.now(timezone.utc)

    def today(self, tz: Optional[str] = None) -> date:
        """
        Get current date in specified timezone.

        Args:
            tz: Timezone name (default: UTC)

        Returns:
            Current date in specified timezone

        Examples:
            >>> utils = DateTimeUtils()
            >>> today_utc = utils.today()  # Returns: date(2024, 1, 15)
            >>> today_est = utils.today('US/Eastern')  # Returns: date(2024, 1, 14) (if EST is behind UTC)
            >>> today_ist = utils.today('Asia/Kolkata')  # Returns: date(2024, 1, 15)
        """
        return self.now(tz).date()

    def convert_timezone(self, dt: datetime, from_tz: str, to_tz: str) -> datetime:
        """
        Convert datetime from one timezone to another.

        Args:
            dt: Datetime to convert (can be naive or timezone-aware)
            from_tz: Source timezone name
            to_tz: Target timezone name

        Returns:
            Converted datetime in target timezone

        Examples:
            >>> utils = DateTimeUtils()
            >>> dt_utc = datetime(2024, 1, 15, 10, 30, 0)
            >>> dt_est = utils.convert_timezone(dt_utc, 'UTC', 'US/Eastern')
            >>> # Returns: datetime(2024, 1, 15, 5, 30, 0, tzinfo=EST)

            >>> dt_aware = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
            >>> dt_ist = utils.convert_timezone(dt_aware, 'UTC', 'Asia/Kolkata')
            >>> # Returns: datetime(2024, 1, 15, 16, 0, 0, tzinfo=IST)
        """
        try:
            from_tz_obj = self.get_timezone(from_tz)
            to_tz_obj = self.get_timezone(to_tz)

            # If datetime is naive, assume it's in the source timezone
            if dt.tzinfo is None:
                # Handle both pytz and zoneinfo timezone objects
                if hasattr(from_tz_obj, "localize"):
                    # pytz timezone object
                    dt = from_tz_obj.localize(dt)
                else:
                    # zoneinfo timezone object
                    dt = dt.replace(tzinfo=from_tz_obj)

            # Convert to target timezone
            return dt.astimezone(to_tz_obj)
        except Exception as e:
            self.logger.error(
                f"Timezone conversion failed: {e}", extra={"trace_id": self.trace_id}
            )
            raise DateTimeUtilsError(f"Timezone conversion failed: {e}") from e

    def format_datetime(
        self,
        dt: datetime,
        format_str: str = "%Y-%m-%d %H:%M:%S",
        tz: Optional[str] = None,
    ) -> str:
        """
        Format datetime with specified format.

        Args:
            dt: Datetime to format
            format_str: Format string (default: "%Y-%m-%d %H:%M:%S")
            tz: Timezone to convert to before formatting

        Returns:
            Formatted datetime string

        Examples:
            >>> utils = DateTimeUtils()
            >>> dt = datetime(2024, 1, 15, 10, 30, 0)
            >>> formatted = utils.format_datetime(dt)
            >>> # Returns: "2024-01-15 10:30:00"

            >>> formatted = utils.format_datetime(dt, "%Y-%m-%d")
            >>> # Returns: "2024-01-15"

            >>> formatted = utils.format_datetime(dt, "%B %d, %Y at %I:%M %p", "US/Eastern")
            >>> # Returns: "January 15, 2024 at 05:30 AM"
        """
        try:
            if tz:
                dt = self.convert_timezone(
                    dt, dt.tzinfo.zone if dt.tzinfo else "UTC", tz  # type: ignore
                )

            return dt.strftime(format_str)
        except Exception as e:
            self.logger.error(
                f"Datetime formatting failed: {e}", extra={"trace_id": self.trace_id}
            )
            raise DateTimeUtilsError(f"Datetime formatting failed: {e}") from e

    def parse_datetime(
        self, date_str: str, format_str: Optional[str] = None, tz: Optional[str] = None
    ) -> datetime:
        """
        Parse datetime string.

        Args:
            date_str: Date string to parse
            format_str: Format string (if None, auto-detect using dateutil)
            tz: Timezone to assign if datetime is naive

        Returns:
            Parsed datetime

        Examples:
            >>> utils = DateTimeUtils()
            >>> dt = utils.parse_datetime("2024-01-15 10:30:00")
            >>> # Returns: datetime(2024, 1, 15, 10, 30, 0)

            >>> dt = utils.parse_datetime("2024-01-15", "%Y-%m-%d")
            >>> # Returns: datetime(2024, 1, 15, 0, 0, 0)

            >>> dt = utils.parse_datetime("Jan 15, 2024 10:30 AM", tz="US/Eastern")
            >>> # Returns: datetime(2024, 1, 15, 10, 30, 0, tzinfo=EST)

            >>> dt = utils.parse_datetime("2024-01-15T10:30:00Z")  # ISO format
            >>> # Returns: datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC)
        """
        try:
            if format_str:
                dt = datetime.strptime(date_str, format_str)
            else:
                # Use dateutil for auto-detection
                dt = parser.parse(date_str)

            # If naive and timezone specified, localize
            if dt.tzinfo is None and tz:
                tz_obj = self.get_timezone(tz)
                # Handle both pytz and zoneinfo timezone objects
                if hasattr(tz_obj, "localize"):
                    # pytz timezone object
                    dt = tz_obj.localize(dt)
                else:
                    # zoneinfo timezone object
                    dt = dt.replace(tzinfo=tz_obj)

            return dt
        except Exception as e:
            self.logger.error(
                f"Datetime parsing failed: {e}", extra={"trace_id": self.trace_id}
            )
            raise DateTimeUtilsError(f"Datetime parsing failed: {e}") from e

    def add_days(self, dt: datetime, days: int) -> datetime:
        """
        Add days to datetime.

        Args:
            dt: Base datetime
            days: Number of days to add (can be negative for subtraction)

        Returns:
            New datetime with days added

        Examples:
            >>> utils = DateTimeUtils()
            >>> dt = datetime(2024, 1, 15, 10, 30, 0)
            >>> new_dt = utils.add_days(dt, 5)
            >>> # Returns: datetime(2024, 1, 20, 10, 30, 0)

            >>> new_dt = utils.add_days(dt, -3)
            >>> # Returns: datetime(2024, 1, 12, 10, 30, 0)
        """
        return dt + timedelta(days=days)

    def add_hours(self, dt: datetime, hours: int) -> datetime:
        """
        Add hours to datetime.

        Args:
            dt: Base datetime
            hours: Number of hours to add (can be negative for subtraction)

        Returns:
            New datetime with hours added

        Examples:
            >>> utils = DateTimeUtils()
            >>> dt = datetime(2024, 1, 15, 10, 30, 0)
            >>> new_dt = utils.add_hours(dt, 3)
            >>> # Returns: datetime(2024, 1, 15, 13, 30, 0)

            >>> new_dt = utils.add_hours(dt, -2)
            >>> # Returns: datetime(2024, 1, 15, 8, 30, 0)
        """
        return dt + timedelta(hours=hours)

    def add_minutes(self, dt: datetime, minutes: int) -> datetime:
        """
        Add minutes to datetime.

        Args:
            dt: Base datetime
            minutes: Number of minutes to add (can be negative for subtraction)

        Returns:
            New datetime with minutes added

        Examples:
            >>> utils = DateTimeUtils()
            >>> dt = datetime(2024, 1, 15, 10, 30, 0)
            >>> new_dt = utils.add_minutes(dt, 45)
            >>> # Returns: datetime(2024, 1, 15, 11, 15, 0)

            >>> new_dt = utils.add_minutes(dt, -15)
            >>> # Returns: datetime(2024, 1, 15, 10, 15, 0)
        """
        return dt + timedelta(minutes=minutes)

    def add_months(self, dt: datetime, months: int) -> datetime:
        """
        Add months to datetime.

        Args:
            dt: Base datetime
            months: Number of months to add (can be negative for subtraction)

        Returns:
            New datetime with months added

        Examples:
            >>> utils = DateTimeUtils()
            >>> dt = datetime(2024, 1, 15, 10, 30, 0)
            >>> new_dt = utils.add_months(dt, 2)
            >>> # Returns: datetime(2024, 3, 15, 10, 30, 0)

            >>> new_dt = utils.add_months(dt, -1)
            >>> # Returns: datetime(2023, 12, 15, 10, 30, 0)

            >>> dt = datetime(2024, 1, 31, 10, 30, 0)
            >>> new_dt = utils.add_months(dt, 1)  # February doesn't have 31 days
            >>> # Returns: datetime(2024, 2, 29, 10, 30, 0) (leap year)
        """
        return dt + relativedelta.relativedelta(months=months)

    def add_years(self, dt: datetime, years: int) -> datetime:
        """
        Add years to datetime.

        Args:
            dt: Base datetime
            years: Number of years to add (can be negative for subtraction)

        Returns:
            New datetime with years added

        Examples:
            >>> utils = DateTimeUtils()
            >>> dt = datetime(2024, 1, 15, 10, 30, 0)
            >>> new_dt = utils.add_years(dt, 1)
            >>> # Returns: datetime(2025, 1, 15, 10, 30, 0)

            >>> new_dt = utils.add_years(dt, -2)
            >>> # Returns: datetime(2022, 1, 15, 10, 30, 0)

            >>> dt = datetime(2024, 2, 29, 10, 30, 0)  # Leap year
            >>> new_dt = utils.add_years(dt, 1)  # 2025 is not a leap year
            >>> # Returns: datetime(2025, 2, 28, 10, 30, 0)
        """
        return dt + relativedelta.relativedelta(years=years)

    def get_business_days_between(
        self,
        start_date: date,
        end_date: date,
        exclude_weekends: bool = True,
        exclude_holidays: Optional[List[date]] = None,
    ) -> int:
        """
        Calculate business days between two dates.

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            exclude_weekends: Whether to exclude weekends (default: True)
            exclude_holidays: List of holidays to exclude

        Returns:
            Number of business days between the dates

        Examples:
            >>> utils = DateTimeUtils()
            >>> start = date(2024, 1, 15)  # Monday
            >>> end = date(2024, 1, 19)    # Friday
            >>> days = utils.get_business_days_between(start, end)
            >>> # Returns: 5 (Monday to Friday)

            >>> start = date(2024, 1, 15)  # Monday
            >>> end = date(2024, 1, 21)    # Sunday
            >>> days = utils.get_business_days_between(start, end)
            >>> # Returns: 5 (Monday to Friday, excluding weekend)

            >>> holidays = [date(2024, 1, 16)]  # Tuesday holiday
            >>> days = utils.get_business_days_between(start, end, exclude_holidays=holidays)
            >>> # Returns: 4 (Monday, Wed, Thu, Fri)
        """
        if exclude_holidays is None:
            exclude_holidays = []

        current_date = start_date
        business_days = 0

        while current_date <= end_date:
            # Check if it's a weekend
            if exclude_weekends and current_date.weekday() >= 5:
                current_date += timedelta(days=1)
                continue

            # Check if it's a holiday
            if current_date in exclude_holidays:
                current_date += timedelta(days=1)
                continue

            business_days += 1
            current_date += timedelta(days=1)

        return business_days

    def get_next_business_day(
        self,
        dt: date,
        exclude_weekends: bool = True,
        exclude_holidays: Optional[List[date]] = None,
    ) -> date:
        """
        Get next business day.

        Args:
            dt: Base date
            exclude_weekends: Whether to exclude weekends (default: True)
            exclude_holidays: List of holidays to exclude

        Returns:
            Next business day

        Examples:
            >>> utils = DateTimeUtils()
            >>> dt = date(2024, 1, 15)  # Monday
            >>> next_biz = utils.get_next_business_day(dt)
            >>> # Returns: date(2024, 1, 16) (Tuesday)

            >>> dt = date(2024, 1, 19)  # Friday
            >>> next_biz = utils.get_next_business_day(dt)
            >>> # Returns: date(2024, 1, 22) (Monday, skipping weekend)

            >>> holidays = [date(2024, 1, 16)]  # Tuesday holiday
            >>> next_biz = utils.get_next_business_day(dt, exclude_holidays=holidays)
            >>> # Returns: date(2024, 1, 17) (Wednesday, skipping holiday)
        """
        if exclude_holidays is None:
            exclude_holidays = []

        next_day = dt + timedelta(days=1)

        while True:
            # Check if it's a weekend
            if exclude_weekends and next_day.weekday() >= 5:
                next_day += timedelta(days=1)
                continue

            # Check if it's a holiday
            if next_day in exclude_holidays:
                next_day += timedelta(days=1)
                continue

            return next_day

    def get_previous_business_day(
        self,
        dt: date,
        exclude_weekends: bool = True,
        exclude_holidays: Optional[List[date]] = None,
    ) -> date:
        """
        Get previous business day.

        Args:
            dt: Base date
            exclude_weekends: Whether to exclude weekends (default: True)
            exclude_holidays: List of holidays to exclude

        Returns:
            Previous business day
        """
        if exclude_holidays is None:
            exclude_holidays = []

        prev_day = dt - timedelta(days=1)

        while True:
            # Check if it's a weekend
            if exclude_weekends and prev_day.weekday() >= 5:
                prev_day -= timedelta(days=1)
                continue

            # Check if it's a holiday
            if prev_day in exclude_holidays:
                prev_day -= timedelta(days=1)
                continue

            return prev_day

    def get_duration_between(
        self, start_dt: datetime, end_dt: datetime
    ) -> Dict[str, int]:
        """
        Get duration between two datetimes.

        Args:
            start_dt: Start datetime
            end_dt: End datetime

        Returns:
            Dictionary with duration components (total_seconds, days, hours, minutes, seconds, microseconds)

        Examples:
            >>> utils = DateTimeUtils()
            >>> start = datetime(2024, 1, 15, 10, 30, 0)
            >>> end = datetime(2024, 1, 15, 12, 45, 30)
            >>> duration = utils.get_duration_between(start, end)
            >>> # Returns: {
            >>> #     'total_seconds': 8130,
            >>> #     'days': 0,
            >>> #     'hours': 2,
            >>> #     'minutes': 15,
            >>> #     'seconds': 30,
            >>> #     'microseconds': 0
            >>> # }

            >>> start = datetime(2024, 1, 15, 10, 30, 0)
            >>> end = datetime(2024, 1, 17, 14, 20, 15)
            >>> duration = utils.get_duration_between(start, end)
            >>> # Returns: {
            >>> #     'total_seconds': 190815,
            >>> #     'days': 2,
            >>> #     'hours': 3,
            >>> #     'minutes': 50,
            >>> #     'seconds': 15,
            >>> #     'microseconds': 0
            >>> # }
        """
        duration = end_dt - start_dt

        return {
            "total_seconds": int(duration.total_seconds()),
            "days": duration.days,
            "hours": duration.seconds // 3600,
            "minutes": (duration.seconds % 3600) // 60,
            "seconds": duration.seconds % 60,
            "microseconds": duration.microseconds,
        }

    def get_human_readable_duration(self, start_dt: datetime, end_dt: datetime) -> str:
        """
        Get human-readable duration between two datetimes.

        Args:
            start_dt: Start datetime
            end_dt: End datetime

        Returns:
            Human-readable duration string

        Examples:
            >>> utils = DateTimeUtils()
            >>> start = datetime(2024, 1, 15, 10, 30, 0)
            >>> end = datetime(2024, 1, 15, 12, 45, 30)
            >>> duration = utils.get_human_readable_duration(start, end)
            >>> # Returns: "2 hours, 15 minutes, 30 seconds"

            >>> start = datetime(2024, 1, 15, 10, 30, 0)
            >>> end = datetime(2024, 1, 17, 14, 20, 15)
            >>> duration = utils.get_human_readable_duration(start, end)
            >>> # Returns: "2 days, 3 hours, 50 minutes, 15 seconds"

            >>> start = datetime(2024, 1, 15, 10, 30, 0)
            >>> end = datetime(2024, 1, 15, 10, 30, 0)
            >>> duration = utils.get_human_readable_duration(start, end)
            >>> # Returns: "0 seconds"
        """
        duration = self.get_duration_between(start_dt, end_dt)

        parts = []

        if duration["days"] > 0:
            parts.append(
                f"{duration['days']} day{'s' if duration['days'] != 1 else ''}"
            )

        if duration["hours"] > 0:
            parts.append(
                f"{duration['hours']} hour{'s' if duration['hours'] != 1 else ''}"
            )

        if duration["minutes"] > 0:
            parts.append(
                f"{duration['minutes']} minute{'s' if duration['minutes'] != 1 else ''}"
            )

        if duration["seconds"] > 0:
            parts.append(
                f"{duration['seconds']} second{'s' if duration['seconds'] != 1 else ''}"
            )

        if not parts:
            return "0 seconds"

        return ", ".join(parts)

    def get_timestamp(self, dt: Optional[datetime] = None) -> int:
        """
        Get Unix timestamp.

        Args:
            dt: Datetime (default: current time)

        Returns:
            Unix timestamp (seconds since epoch)

        Examples:
            >>> utils = DateTimeUtils()
            >>> timestamp = utils.get_timestamp()  # Current time
            >>> # Returns: 1705312200 (example timestamp)

            >>> dt = datetime(2024, 1, 15, 10, 30, 0)
            >>> timestamp = utils.get_timestamp(dt)
            >>> # Returns: 1705312200
        """
        if dt is None:
            dt = self.now()

        return int(dt.timestamp())

    def from_timestamp(
        self, timestamp: Union[int, float], tz: Optional[str] = None
    ) -> datetime:
        """
        Convert Unix timestamp to datetime.

        Args:
            timestamp: Unix timestamp (seconds since epoch)
            tz: Timezone (default: UTC)

        Returns:
            Datetime object

        Examples:
            >>> utils = DateTimeUtils()
            >>> dt = utils.from_timestamp(1705312200)
            >>> # Returns: datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC)

            >>> dt = utils.from_timestamp(1705312200, 'US/Eastern')
            >>> # Returns: datetime(2024, 1, 15, 5, 30, 0, tzinfo=EST)
        """
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)

        if tz:
            dt = self.convert_timezone(dt, "UTC", tz)

        return dt

    def get_iso_format(self, dt: datetime) -> str:
        """
        Get ISO format string.

        Args:
            dt: Datetime to format

        Returns:
            ISO format string

        Examples:
            >>> utils = DateTimeUtils()
            >>> dt = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
            >>> iso_str = utils.get_iso_format(dt)
            >>> # Returns: "2024-01-15T10:30:00+00:00"

            >>> dt = datetime(2024, 1, 15, 10, 30, 0)
            >>> iso_str = utils.get_iso_format(dt)
            >>> # Returns: "2024-01-15T10:30:00"
        """
        return dt.isoformat()

    def from_iso_format(self, iso_str: str) -> datetime:
        """
        Parse ISO format string.

        Args:
            iso_str: ISO format string

        Returns:
            Parsed datetime

        Examples:
            >>> utils = DateTimeUtils()
            >>> dt = utils.from_iso_format("2024-01-15T10:30:00+00:00")
            >>> # Returns: datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC)

            >>> dt = utils.from_iso_format("2024-01-15T10:30:00")
            >>> # Returns: datetime(2024, 1, 15, 10, 30, 0)

            >>> dt = utils.from_iso_format("2024-01-15T10:30:00Z")
            >>> # Returns: datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC)
        """
        return datetime.fromisoformat(iso_str.replace("Z", "+00:00"))

    def get_week_start(self, dt: date, week_start_day: int = 0) -> date:
        """
        Get start of week for given date.

        Args:
            dt: Date
            week_start_day: Day of week to start (0=Monday, 6=Sunday)

        Returns:
            Start of week date

        Examples:
            >>> utils = DateTimeUtils()
            >>> dt = date(2024, 1, 17)  # Wednesday
            >>> week_start = utils.get_week_start(dt)  # Monday start
            >>> # Returns: date(2024, 1, 15) (Monday)

            >>> week_start = utils.get_week_start(dt, 6)  # Sunday start
            >>> # Returns: date(2024, 1, 14) (Sunday)
        """
        days_since_start = (dt.weekday() - week_start_day) % 7
        return dt - timedelta(days=days_since_start)

    def get_week_end(self, dt: date, week_start_day: int = 0) -> date:
        """
        Get end of week for given date.

        Args:
            dt: Date
            week_start_day: Day of week to start (0=Monday, 6=Sunday)

        Returns:
            End of week date
        """
        week_start = self.get_week_start(dt, week_start_day)
        return week_start + timedelta(days=6)

    def get_month_start(self, dt: date) -> date:
        """
        Get start of month for given date.

        Args:
            dt: Date

        Returns:
            Start of month date
        """
        return dt.replace(day=1)

    def get_month_end(self, dt: date) -> date:
        """
        Get end of month for given date.

        Args:
            dt: Date

        Returns:
            End of month date
        """
        next_month = dt.replace(day=28) + timedelta(days=4)
        return next_month - timedelta(days=next_month.day)

    def get_year_start(self, dt: date) -> date:
        """
        Get start of year for given date.

        Args:
            dt: Date

        Returns:
            Start of year date
        """
        return dt.replace(month=1, day=1)

    def get_year_end(self, dt: date) -> date:
        """
        Get end of year for given date.

        Args:
            dt: Date

        Returns:
            End of year date
        """
        return dt.replace(month=12, day=31)

    def is_weekend(self, dt: date) -> bool:
        """
        Check if date is weekend.

        Args:
            dt: Date to check

        Returns:
            True if weekend (Saturday or Sunday), False otherwise

        Examples:
            >>> utils = DateTimeUtils()
            >>> dt = date(2024, 1, 15)  # Monday
            >>> is_weekend = utils.is_weekend(dt)
            >>> # Returns: False

            >>> dt = date(2024, 1, 20)  # Saturday
            >>> is_weekend = utils.is_weekend(dt)
            >>> # Returns: True
        """
        return dt.weekday() >= 5

    def is_holiday(self, dt: date, holidays: List[date]) -> bool:
        """
        Check if date is holiday.

        Args:
            dt: Date to check
            holidays: List of holiday dates

        Returns:
            True if holiday, False otherwise
        """
        return dt in holidays

    def get_age(self, birth_date: date, reference_date: Optional[date] = None) -> int:
        """
        Calculate age in years.

        Args:
            birth_date: Birth date
            reference_date: Reference date (default: today)

        Returns:
            Age in years

        Examples:
            >>> utils = DateTimeUtils()
            >>> birth = date(1990, 5, 15)
            >>> age = utils.get_age(birth)  # Using today as reference
            >>> # Returns: 33 (example age)

            >>> birth = date(1990, 5, 15)
            >>> ref = date(2024, 1, 15)
            >>> age = utils.get_age(birth, ref)
            >>> # Returns: 33

            >>> birth = date(1990, 5, 15)
            >>> ref = date(2024, 3, 10)  # Before birthday
            >>> age = utils.get_age(birth, ref)
            >>> # Returns: 33

            >>> birth = date(1990, 5, 15)
            >>> ref = date(2024, 6, 1)  # After birthday
            >>> age = utils.get_age(birth, ref)
            >>> # Returns: 34
        """
        if reference_date is None:
            reference_date = self.today()

        return relativedelta.relativedelta(reference_date, birth_date).years

    def get_quarter(self, dt: date) -> int:
        """
        Get quarter for given date.

        Args:
            dt: Date

        Returns:
            Quarter number (1-4)
        """
        return (dt.month - 1) // 3 + 1

    def get_quarter_start(self, dt: date) -> date:
        """
        Get start of quarter for given date.

        Args:
            dt: Date

        Returns:
            Start of quarter date
        """
        quarter = self.get_quarter(dt)
        month = (quarter - 1) * 3 + 1
        return dt.replace(month=month, day=1)

    def get_quarter_end(self, dt: date) -> date:
        """
        Get end of quarter for given date.

        Args:
            dt: Date

        Returns:
            End of quarter date
        """
        quarter = self.get_quarter(dt)
        month = quarter * 3
        return self.get_month_end(dt.replace(month=month))

    def validate_date_range(
        self, start_date: date, end_date: date, max_days: Optional[int] = None
    ) -> bool:
        """
        Validate date range.

        Args:
            start_date: Start date
            end_date: End date
            max_days: Maximum allowed days between dates

        Returns:
            True if valid, False otherwise
        """
        if start_date > end_date:
            return False

        if max_days:
            days_diff = (end_date - start_date).days
            if days_diff >= max_days:
                return False

        return True

    def get_common_formats(self) -> Dict[str, str]:
        """
        Get common datetime format strings.

        Returns:
            Dictionary of format names and format strings
        """
        return {
            "iso": "%Y-%m-%dT%H:%M:%S.%fZ",
            "iso_date": "%Y-%m-%d",
            "iso_time": "%H:%M:%S",
            "us_date": "%m/%d/%Y",
            "us_datetime": "%m/%d/%Y %H:%M:%S",
            "eu_date": "%d/%m/%Y",
            "eu_datetime": "%d/%m/%Y %H:%M:%S",
            "readable": "%B %d, %Y at %I:%M %p",
            "short_readable": "%b %d, %Y",
            "time_only": "%I:%M %p",
            "date_only": "%B %d, %Y",
            "filename_safe": "%Y%m%d_%H%M%S",
            "log_format": "%Y-%m-%d %H:%M:%S",
        }


# Convenience functions for common operations
def now(tz: Optional[str] = None, trace_id: Optional[str] = None) -> datetime:
    """Get current datetime in specified timezone."""
    utils = DateTimeUtils(trace_id)
    return utils.now(tz)


def today(tz: Optional[str] = None, trace_id: Optional[str] = None) -> date:
    """Get current date in specified timezone."""
    utils = DateTimeUtils(trace_id)
    return utils.today(tz)


def convert_timezone(
    dt: datetime, from_tz: str, to_tz: str, trace_id: Optional[str] = None
) -> datetime:
    """Convert datetime from one timezone to another."""
    utils = DateTimeUtils(trace_id)
    return utils.convert_timezone(dt, from_tz, to_tz)


def format_datetime(
    dt: datetime,
    format_str: str = "%Y-%m-%d %H:%M:%S",
    tz: Optional[str] = None,
    trace_id: Optional[str] = None,
) -> str:
    """Format datetime with specified format."""
    utils = DateTimeUtils(trace_id)
    return utils.format_datetime(dt, format_str, tz)


def parse_datetime(
    date_str: str,
    format_str: Optional[str] = None,
    tz: Optional[str] = None,
    trace_id: Optional[str] = None,
) -> datetime:
    """Parse datetime string."""
    utils = DateTimeUtils(trace_id)
    return utils.parse_datetime(date_str, format_str, tz)


def get_business_days_between(
    start_date: date,
    end_date: date,
    exclude_weekends: bool = True,
    exclude_holidays: Optional[List[date]] = None,
    trace_id: Optional[str] = None,
) -> int:
    """Calculate business days between two dates."""
    utils = DateTimeUtils(trace_id)
    return utils.get_business_days_between(
        start_date, end_date, exclude_weekends, exclude_holidays
    )


def get_duration_between(
    start_dt: datetime, end_dt: datetime, trace_id: Optional[str] = None
) -> Dict[str, int]:
    """Get duration between two datetimes."""
    utils = DateTimeUtils(trace_id)
    return utils.get_duration_between(start_dt, end_dt)


def get_timestamp(dt: Optional[datetime] = None, trace_id: Optional[str] = None) -> int:
    """Get Unix timestamp."""
    utils = DateTimeUtils(trace_id)
    return utils.get_timestamp(dt)


def from_timestamp(
    timestamp: Union[int, float],
    tz: Optional[str] = None,
    trace_id: Optional[str] = None,
) -> datetime:
    """Convert Unix timestamp to datetime."""
    utils = DateTimeUtils(trace_id)
    return utils.from_timestamp(timestamp, tz)
