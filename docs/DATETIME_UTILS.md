# Date/Time Utilities Documentation

Comprehensive date and time utilities for FastAPI applications with timezone handling, formatting, business day calculations, and more.

## Table of Contents

- [Overview](#overview)
- [Installation & Dependencies](#installation--dependencies)
- [Quick Start](#quick-start)
- [Core Features](#core-features)
- [API Reference](#api-reference)
- [Usage Examples](#usage-examples)
- [Timezone Handling](#timezone-handling)
- [Business Day Calculations](#business-day-calculations)
- [Date Formatting & Parsing](#date-formatting--parsing)
- [Duration Calculations](#duration-calculations)
- [Date Range Operations](#date-range-operations)
- [FastAPI Integration](#fastapi-integration)
- [Error Handling](#error-handling)
- [Performance Considerations](#performance-considerations)
- [Troubleshooting](#troubleshooting)

## Overview

The DateTime Utilities module provides a comprehensive set of date and time operations for FastAPI applications. It includes timezone handling, business day calculations, date formatting, duration calculations, and more.

### Key Features

- **Timezone Conversion**: Convert between different timezones
- **Business Day Calculations**: Calculate business days excluding weekends and holidays
- **Date Formatting**: Format dates in various formats
- **Date Parsing**: Parse date strings with auto-detection
- **Duration Calculations**: Calculate and format durations between dates
- **Date Range Operations**: Work with date ranges and periods
- **Validation**: Validate date ranges and formats
- **Convenience Functions**: Simple functions for common operations

## Installation & Dependencies

The datetime utilities require the following dependencies:

```bash
pip install python-dateutil pytz
```

### Dependencies

- `python-dateutil`: Advanced date parsing and manipulation
- `pytz`: Timezone database and utilities
- `zoneinfo`: Built-in timezone support (Python 3.9+)

## Quick Start

### Basic Usage

```python
from src.utils.datetime_utils import DateTimeUtils, now, today, format_datetime

# Initialize utilities
utils = DateTimeUtils(trace_id="user-123")

# Get current datetime
current_time = now()  # UTC by default
current_time_est = now('US/Eastern')

# Get current date
today_date = today()
today_est = today('US/Eastern')

# Format datetime
formatted = format_datetime(current_time, "%Y-%m-%d %H:%M:%S")
```

### Timezone Conversion

```python
from src.utils.datetime_utils import convert_timezone

# Convert from UTC to EST
utc_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
est_time = convert_timezone(utc_time, 'UTC', 'US/Eastern')
```

### Business Day Calculations

```python
from src.utils.datetime_utils import get_business_days_between
from datetime import date

# Calculate business days between dates
start_date = date(2024, 1, 1)  # Monday
end_date = date(2024, 1, 7)    # Sunday
business_days = get_business_days_between(start_date, end_date)
print(f"Business days: {business_days}")  # 5 days
```

## Core Features

### 1. Timezone Handling

- Convert between different timezones
- Support for common timezone abbreviations
- Handle both naive and aware datetime objects
- Automatic timezone detection

### 2. Date Formatting & Parsing

- Multiple format options
- Auto-detection of date formats
- ISO format support
- Custom format strings

### 3. Business Day Calculations

- Exclude weekends and holidays
- Calculate business days between dates
- Find next/previous business days
- Support for custom holiday lists

### 4. Duration Calculations

- Calculate duration between dates
- Human-readable duration strings
- Support for different time units
- Timestamp conversion

### 5. Date Range Operations

- Get week/month/quarter/year boundaries
- Validate date ranges
- Calculate quarters
- Age calculations

## API Reference

### DateTimeUtils Class

#### Constructor

```python
DateTimeUtils(trace_id: Optional[str] = None)
```

**Parameters:**
- `trace_id`: Optional trace ID for logging

#### Core Methods

##### Timezone Operations

```python
def get_timezone(self, tz_name: str) -> timezone
def now(self, tz: Optional[str] = None) -> datetime
def today(self, tz: Optional[str] = None) -> date
def convert_timezone(self, dt: datetime, from_tz: str, to_tz: str) -> datetime
```

##### Date Formatting & Parsing

```python
def format_datetime(self, dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S", tz: Optional[str] = None) -> str
def parse_datetime(self, date_str: str, format_str: Optional[str] = None, tz: Optional[str] = None) -> datetime
def get_iso_format(self, dt: datetime) -> str
def from_iso_format(self, iso_str: str) -> datetime
```

##### Date Arithmetic

```python
def add_days(self, dt: datetime, days: int) -> datetime
def add_hours(self, dt: datetime, hours: int) -> datetime
def add_minutes(self, dt: datetime, minutes: int) -> datetime
def add_months(self, dt: datetime, months: int) -> datetime
def add_years(self, dt: datetime, years: int) -> datetime
```

##### Business Day Calculations

```python
def get_business_days_between(self, start_date: date, end_date: date, exclude_weekends: bool = True, exclude_holidays: Optional[List[date]] = None) -> int
def get_next_business_day(self, dt: date, exclude_weekends: bool = True, exclude_holidays: Optional[List[date]] = None) -> date
def get_previous_business_day(self, dt: date, exclude_weekends: bool = True, exclude_holidays: Optional[List[date]] = None) -> date
```

##### Duration Calculations

```python
def get_duration_between(self, start_dt: datetime, end_dt: datetime) -> Dict[str, int]
def get_human_readable_duration(self, start_dt: datetime, end_dt: datetime) -> str
def get_timestamp(self, dt: Optional[datetime] = None) -> int
def from_timestamp(self, timestamp: Union[int, float], tz: Optional[str] = None) -> datetime
```

##### Date Range Operations

```python
def get_week_start(self, dt: date, week_start_day: int = 0) -> date
def get_week_end(self, dt: date, week_start_day: int = 0) -> date
def get_month_start(self, dt: date) -> date
def get_month_end(self, dt: date) -> date
def get_year_start(self, dt: date) -> date
def get_year_end(self, dt: date) -> date
def get_quarter(self, dt: date) -> int
def get_quarter_start(self, dt: date) -> date
def get_quarter_end(self, dt: date) -> date
```

##### Validation & Utilities

```python
def is_weekend(self, dt: date) -> bool
def is_holiday(self, dt: date, holidays: List[date]) -> bool
def get_age(self, birth_date: date, reference_date: Optional[date] = None) -> int
def validate_date_range(self, start_date: date, end_date: date, max_days: Optional[int] = None) -> bool
def get_common_formats(self) -> Dict[str, str]
```

### Convenience Functions

```python
# Current time/date
now(tz: Optional[str] = None, trace_id: Optional[str] = None) -> datetime
today(tz: Optional[str] = None, trace_id: Optional[str] = None) -> date

# Timezone conversion
convert_timezone(dt: datetime, from_tz: str, to_tz: str, trace_id: Optional[str] = None) -> datetime

# Formatting
format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S", tz: Optional[str] = None, trace_id: Optional[str] = None) -> str
parse_datetime(date_str: str, format_str: Optional[str] = None, tz: Optional[str] = None, trace_id: Optional[str] = None) -> datetime

# Business days
get_business_days_between(start_date: date, end_date: date, exclude_weekends: bool = True, exclude_holidays: Optional[List[date]] = None, trace_id: Optional[str] = None) -> int

# Duration
get_duration_between(start_dt: datetime, end_dt: datetime, trace_id: Optional[str] = None) -> Dict[str, int]

# Timestamps
get_timestamp(dt: Optional[datetime] = None, trace_id: Optional[str] = None) -> int
from_timestamp(timestamp: Union[int, float], tz: Optional[str] = None, trace_id: Optional[str] = None) -> datetime
```

## Usage Examples

### 1. Basic Timezone Operations

```python
from src.utils.datetime_utils import DateTimeUtils, now, convert_timezone

# Initialize utilities
utils = DateTimeUtils(trace_id="user-123")

# Get current time in different timezones
utc_now = now()
est_now = now('US/Eastern')
ist_now = now('Asia/Kolkata')

# Convert between timezones
utc_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
est_time = convert_timezone(utc_time, 'UTC', 'US/Eastern')
ist_time = convert_timezone(utc_time, 'UTC', 'Asia/Kolkata')

print(f"UTC: {utc_time}")
print(f"EST: {est_time}")
print(f"IST: {ist_time}")
```

### 2. Date Formatting

```python
from src.utils.datetime_utils import format_datetime, parse_datetime

# Format datetime
dt = datetime(2024, 1, 1, 12, 30, 45)

# Different formats
iso_format = format_datetime(dt, "%Y-%m-%dT%H:%M:%S")
us_format = format_datetime(dt, "%m/%d/%Y %I:%M %p")
readable_format = format_datetime(dt, "%B %d, %Y at %I:%M %p")

print(f"ISO: {iso_format}")
print(f"US: {us_format}")
print(f"Readable: {readable_format}")

# Parse datetime
parsed = parse_datetime("2024-01-01 12:30:45", "%Y-%m-%d %H:%M:%S")
auto_parsed = parse_datetime("2024-01-01T12:30:45Z")
```

### 3. Business Day Calculations

```python
from src.utils.datetime_utils import get_business_days_between, DateTimeUtils
from datetime import date

# Calculate business days
start_date = date(2024, 1, 1)  # Monday
end_date = date(2024, 1, 31)   # Wednesday

# Basic calculation
business_days = get_business_days_between(start_date, end_date)
print(f"Business days: {business_days}")

# With holidays
holidays = [date(2024, 1, 1), date(2024, 1, 15)]  # New Year's Day, MLK Day
business_days_with_holidays = get_business_days_between(
    start_date, end_date, holidays=holidays
)
print(f"Business days (with holidays): {business_days_with_holidays}")

# Find next business day
utils = DateTimeUtils()
next_business = utils.get_next_business_day(date(2024, 1, 5))  # Friday
print(f"Next business day: {next_business}")  # Monday
```

### 4. Duration Calculations

```python
from src.utils.datetime_utils import get_duration_between, DateTimeUtils

# Calculate duration
start_dt = datetime(2024, 1, 1, 12, 0, 0)
end_dt = datetime(2024, 1, 3, 14, 30, 45)

# Get duration components
duration = get_duration_between(start_dt, end_dt)
print(f"Duration: {duration}")

# Human-readable duration
utils = DateTimeUtils()
human_duration = utils.get_human_readable_duration(start_dt, end_dt)
print(f"Human readable: {human_duration}")  # "2 days, 2 hours, 30 minutes, 45 seconds"
```

### 5. Date Range Operations

```python
from src.utils.datetime_utils import DateTimeUtils
from datetime import date

utils = DateTimeUtils()

# Get week boundaries
dt = date(2024, 1, 15)  # Monday
week_start = utils.get_week_start(dt)
week_end = utils.get_week_end(dt)
print(f"Week: {week_start} to {week_end}")

# Get month boundaries
month_start = utils.get_month_start(dt)
month_end = utils.get_month_end(dt)
print(f"Month: {month_start} to {month_end}")

# Get quarter
quarter = utils.get_quarter(dt)
quarter_start = utils.get_quarter_start(dt)
quarter_end = utils.get_quarter_end(dt)
print(f"Quarter {quarter}: {quarter_start} to {quarter_end}")

# Calculate age
birth_date = date(1990, 1, 1)
age = utils.get_age(birth_date)
print(f"Age: {age} years")
```

### 6. Date Validation

```python
from src.utils.datetime_utils import DateTimeUtils

utils = DateTimeUtils()

# Validate date range
start_date = date(2024, 1, 1)
end_date = date(2024, 1, 31)

# Basic validation
is_valid = utils.validate_date_range(start_date, end_date)
print(f"Valid range: {is_valid}")

# With maximum days
is_valid_limited = utils.validate_date_range(start_date, end_date, max_days=30)
print(f"Valid range (max 30 days): {is_valid_limited}")

# Check if weekend
is_weekend = utils.is_weekend(date(2024, 1, 6))  # Saturday
print(f"Is weekend: {is_weekend}")

# Check if holiday
holidays = [date(2024, 1, 1), date(2024, 12, 25)]
is_holiday = utils.is_holiday(date(2024, 1, 1), holidays)
print(f"Is holiday: {is_holiday}")
```

## Timezone Handling

### Supported Timezones

The utilities support all timezones available in the `zoneinfo` and `pytz` libraries:

```python
# Common abbreviations
'utc', 'gmt', 'est', 'pst', 'cst', 'mst', 'ist', 'jst', 'cet', 'aest'

# Full timezone names
'UTC', 'US/Eastern', 'US/Pacific', 'Asia/Kolkata', 'Europe/Berlin'
```

### Timezone Conversion Examples

```python
from src.utils.datetime_utils import convert_timezone

# Convert UTC to different timezones
utc_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

# Convert to EST (UTC-5)
est_time = convert_timezone(utc_time, 'UTC', 'US/Eastern')
print(f"EST: {est_time}")  # 2024-01-01 07:00:00-05:00

# Convert to IST (UTC+5:30)
ist_time = convert_timezone(utc_time, 'UTC', 'Asia/Kolkata')
print(f"IST: {ist_time}")  # 2024-01-01 17:30:00+05:30

# Convert to PST (UTC-8)
pst_time = convert_timezone(utc_time, 'UTC', 'US/Pacific')
print(f"PST: {pst_time}")  # 2024-01-01 04:00:00-08:00
```

## Business Day Calculations

### Basic Business Day Calculation

```python
from src.utils.datetime_utils import get_business_days_between
from datetime import date

# Calculate business days between two dates
start_date = date(2024, 1, 1)  # Monday
end_date = date(2024, 1, 7)    # Sunday

# Exclude weekends (default)
business_days = get_business_days_between(start_date, end_date)
print(f"Business days: {business_days}")  # 5 days (Mon-Fri)

# Include weekends
all_days = get_business_days_between(start_date, end_date, exclude_weekends=False)
print(f"All days: {all_days}")  # 7 days
```

### Business Days with Holidays

```python
from src.utils.datetime_utils import get_business_days_between
from datetime import date

# Define holidays
holidays = [
    date(2024, 1, 1),   # New Year's Day
    date(2024, 1, 15),  # Martin Luther King Jr. Day
    date(2024, 2, 19),  # Presidents' Day
    date(2024, 5, 27),  # Memorial Day
    date(2024, 7, 4),   # Independence Day
    date(2024, 9, 2),   # Labor Day
    date(2024, 10, 14), # Columbus Day
    date(2024, 11, 11), # Veterans Day
    date(2024, 11, 28), # Thanksgiving
    date(2024, 12, 25), # Christmas Day
]

# Calculate business days excluding weekends and holidays
start_date = date(2024, 1, 1)
end_date = date(2024, 1, 31)

business_days = get_business_days_between(
    start_date, end_date, holidays=holidays
)
print(f"Business days (with holidays): {business_days}")
```

### Next/Previous Business Days

```python
from src.utils.datetime_utils import DateTimeUtils
from datetime import date

utils = DateTimeUtils()

# Find next business day
friday = date(2024, 1, 5)  # Friday
next_business = utils.get_next_business_day(friday)
print(f"Next business day after {friday}: {next_business}")  # Monday

# Find previous business day
monday = date(2024, 1, 1)  # Monday
prev_business = utils.get_previous_business_day(monday)
print(f"Previous business day before {monday}: {prev_business}")  # Friday (previous week)
```

## Date Formatting & Parsing

### Common Formats

```python
from src.utils.datetime_utils import DateTimeUtils

utils = DateTimeUtils()
formats = utils.get_common_formats()

print("Available formats:")
for name, format_str in formats.items():
    print(f"{name}: {format_str}")
```

### Formatting Examples

```python
from src.utils.datetime_utils import format_datetime
from datetime import datetime

dt = datetime(2024, 1, 1, 12, 30, 45)

# ISO format
iso = format_datetime(dt, "%Y-%m-%dT%H:%M:%S")
print(f"ISO: {iso}")  # 2024-01-01T12:30:45

# US format
us = format_datetime(dt, "%m/%d/%Y %I:%M %p")
print(f"US: {us}")  # 01/01/2024 12:30 PM

# European format
eu = format_datetime(dt, "%d/%m/%Y %H:%M:%S")
print(f"EU: {eu}")  # 01/01/2024 12:30:45

# Readable format
readable = format_datetime(dt, "%B %d, %Y at %I:%M %p")
print(f"Readable: {readable}")  # January 01, 2024 at 12:30 PM

# Filename safe
filename = format_datetime(dt, "%Y%m%d_%H%M%S")
print(f"Filename: {filename}")  # 20240101_123045
```

### Parsing Examples

```python
from src.utils.datetime_utils import parse_datetime

# Parse with format string
dt1 = parse_datetime("2024-01-01 12:30:45", "%Y-%m-%d %H:%M:%S")
print(f"Parsed: {dt1}")

# Auto-detect format
dt2 = parse_datetime("2024-01-01T12:30:45Z")
print(f"Auto-parsed: {dt2}")

# Parse with timezone
dt3 = parse_datetime("2024-01-01 12:30:45", tz="US/Eastern")
print(f"With timezone: {dt3}")
```

## Duration Calculations

### Duration Components

```python
from src.utils.datetime_utils import get_duration_between
from datetime import datetime

start_dt = datetime(2024, 1, 1, 12, 0, 0)
end_dt = datetime(2024, 1, 3, 14, 30, 45)

duration = get_duration_between(start_dt, end_dt)
print(f"Duration components: {duration}")
# {
#     'total_seconds': 189045,
#     'days': 2,
#     'hours': 2,
#     'minutes': 30,
#     'seconds': 45,
#     'microseconds': 0
# }
```

### Human-Readable Duration

```python
from src.utils.datetime_utils import DateTimeUtils
from datetime import datetime

utils = DateTimeUtils()

start_dt = datetime(2024, 1, 1, 12, 0, 0)
end_dt = datetime(2024, 1, 3, 14, 30, 45)

human_duration = utils.get_human_readable_duration(start_dt, end_dt)
print(f"Human readable: {human_duration}")  # "2 days, 2 hours, 30 minutes, 45 seconds"
```

### Timestamp Operations

```python
from src.utils.datetime_utils import get_timestamp, from_timestamp

# Get current timestamp
timestamp = get_timestamp()
print(f"Current timestamp: {timestamp}")

# Convert timestamp to datetime
dt = from_timestamp(timestamp)
print(f"From timestamp: {dt}")

# Convert specific timestamp
specific_timestamp = 1704110400  # 2024-01-01 12:00:00 UTC
dt = from_timestamp(specific_timestamp)
print(f"Specific timestamp: {dt}")
```

## Date Range Operations

### Week Operations

```python
from src.utils.datetime_utils import DateTimeUtils
from datetime import date

utils = DateTimeUtils()

dt = date(2024, 1, 15)  # Monday

# Get week start (Monday)
week_start = utils.get_week_start(dt)
print(f"Week start: {week_start}")  # 2024-01-15

# Get week end (Sunday)
week_end = utils.get_week_end(dt)
print(f"Week end: {week_end}")  # 2024-01-21

# Custom week start day (Sunday)
week_start_sunday = utils.get_week_start(dt, week_start_day=6)
print(f"Week start (Sunday): {week_start_sunday}")  # 2024-01-14
```

### Month Operations

```python
from src.utils.datetime_utils import DateTimeUtils
from datetime import date

utils = DateTimeUtils()

dt = date(2024, 1, 15)

# Get month start
month_start = utils.get_month_start(dt)
print(f"Month start: {month_start}")  # 2024-01-01

# Get month end
month_end = utils.get_month_end(dt)
print(f"Month end: {month_end}")  # 2024-01-31
```

### Quarter Operations

```python
from src.utils.datetime_utils import DateTimeUtils
from datetime import date

utils = DateTimeUtils()

dt = date(2024, 6, 15)

# Get quarter
quarter = utils.get_quarter(dt)
print(f"Quarter: {quarter}")  # 2

# Get quarter start
quarter_start = utils.get_quarter_start(dt)
print(f"Quarter start: {quarter_start}")  # 2024-04-01

# Get quarter end
quarter_end = utils.get_quarter_end(dt)
print(f"Quarter end: {quarter_end}")  # 2024-06-30
```

### Year Operations

```python
from src.utils.datetime_utils import DateTimeUtils
from datetime import date

utils = DateTimeUtils()

dt = date(2024, 6, 15)

# Get year start
year_start = utils.get_year_start(dt)
print(f"Year start: {year_start}")  # 2024-01-01

# Get year end
year_end = utils.get_year_end(dt)
print(f"Year end: {year_end}")  # 2024-12-31
```

## FastAPI Integration

### Using in FastAPI Endpoints

```python
from fastapi import FastAPI, HTTPException
from src.utils.datetime_utils import DateTimeUtils, get_business_days_between
from datetime import date
from pydantic import BaseModel

app = FastAPI()

class DateRangeRequest(BaseModel):
    start_date: date
    end_date: date
    exclude_weekends: bool = True
    holidays: list[date] = []

@app.post("/calculate-business-days")
async def calculate_business_days(request: DateRangeRequest):
    """Calculate business days between two dates."""
    try:
        utils = DateTimeUtils(trace_id="api-request")

        # Validate date range
        if not utils.validate_date_range(request.start_date, request.end_date):
            raise HTTPException(status_code=400, detail="Invalid date range")

        # Calculate business days
        business_days = get_business_days_between(
            request.start_date,
            request.end_date,
            exclude_weekends=request.exclude_weekends,
            exclude_holidays=request.holidays
        )

        return {
            "start_date": request.start_date,
            "end_date": request.end_date,
            "business_days": business_days,
            "total_days": (request.end_date - request.start_date).days + 1
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Using in Background Tasks

```python
from fastapi import BackgroundTasks
from src.utils.datetime_utils import DateTimeUtils
from datetime import datetime, timedelta

async def process_scheduled_task(task_id: str):
    """Process a scheduled task."""
    utils = DateTimeUtils(trace_id=f"task-{task_id}")

    # Get current time
    current_time = utils.now()

    # Calculate next run time
    next_run = utils.add_hours(current_time, 24)

    # Log the scheduling
    utils.logger.info(f"Task {task_id} scheduled for {next_run}")

    # Process the task
    # ... task logic here ...

@app.post("/schedule-task")
async def schedule_task(background_tasks: BackgroundTasks):
    """Schedule a background task."""
    background_tasks.add_task(process_scheduled_task, "task-123")
    return {"message": "Task scheduled"}
```

### Using in Data Models

```python
from pydantic import BaseModel, validator
from src.utils.datetime_utils import DateTimeUtils
from datetime import date

class UserProfile(BaseModel):
    name: str
    birth_date: date
    timezone: str = "UTC"

    @validator('birth_date')
    def validate_birth_date(cls, v):
        utils = DateTimeUtils()
        today = utils.today()

        # Check if birth date is in the future
        if v > today:
            raise ValueError('Birth date cannot be in the future')

        # Check if age is reasonable
        age = utils.get_age(v, today)
        if age > 150:
            raise ValueError('Age cannot exceed 150 years')

        return v

    @property
    def age(self) -> int:
        """Calculate user's age."""
        utils = DateTimeUtils()
        return utils.get_age(self.birth_date)
```

## Error Handling

### Common Exceptions

```python
from src.utils.datetime_utils import DateTimeUtils, DateTimeUtilsError

utils = DateTimeUtils()

try:
    # This will raise DateTimeUtilsError
    invalid_tz = utils.get_timezone('invalid_timezone')
except DateTimeUtilsError as e:
    print(f"Timezone error: {e}")
```

### Error Handling Patterns

```python
from src.utils.datetime_utils import DateTimeUtils, DateTimeUtilsError
from fastapi import HTTPException

def safe_timezone_conversion(dt: datetime, from_tz: str, to_tz: str):
    """Safely convert timezone with error handling."""
    try:
        utils = DateTimeUtils()
        return utils.convert_timezone(dt, from_tz, to_tz)
    except DateTimeUtilsError as e:
        # Log the error
        utils.logger.error(f"Timezone conversion failed: {e}")
        # Return original datetime or raise HTTP exception
        raise HTTPException(status_code=400, detail=f"Invalid timezone: {e}")
    except Exception as e:
        # Handle unexpected errors
        utils.logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

## Performance Considerations

### Caching Timezone Objects

```python
from src.utils.datetime_utils import DateTimeUtils
from functools import lru_cache

class CachedDateTimeUtils(DateTimeUtils):
    """DateTimeUtils with timezone caching."""

    @lru_cache(maxsize=128)
    def get_timezone(self, tz_name: str):
        """Cached timezone retrieval."""
        return super().get_timezone(tz_name)

# Use cached version for better performance
utils = CachedDateTimeUtils()
```

### Batch Operations

```python
from src.utils.datetime_utils import DateTimeUtils
from datetime import date, timedelta

def calculate_business_days_batch(date_ranges: list[tuple[date, date]]):
    """Calculate business days for multiple date ranges efficiently."""
    utils = DateTimeUtils()

    results = []
    for start_date, end_date in date_ranges:
        business_days = utils.get_business_days_between(start_date, end_date)
        results.append({
            'start_date': start_date,
            'end_date': end_date,
            'business_days': business_days
        })

    return results
```

## Troubleshooting

### Common Issues

#### 1. Timezone Not Found

**Error:** `DateTimeUtilsError: Invalid timezone: 'invalid_timezone'`

**Solution:** Use valid timezone names or abbreviations:

```python
# Valid timezone names
'UTC', 'US/Eastern', 'US/Pacific', 'Asia/Kolkata'

# Valid abbreviations
'utc', 'est', 'pst', 'ist'
```

#### 2. Naive Datetime Warning

**Warning:** `RuntimeWarning: DateTime received a naive datetime`

**Solution:** Always use timezone-aware datetimes or specify timezone:

```python
from datetime import datetime, timezone

# Create timezone-aware datetime
dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

# Or specify timezone when parsing
parsed = parse_datetime("2024-01-01 12:00:00", tz="UTC")
```

#### 3. Date Range Validation

**Error:** `Invalid date range`

**Solution:** Ensure start date is before end date:

```python
# Valid range
start_date = date(2024, 1, 1)
end_date = date(2024, 1, 31)

# Invalid range
start_date = date(2024, 1, 31)
end_date = date(2024, 1, 1)  # This will fail validation
```

### Debugging Tips

#### 1. Enable Debug Logging

```python
import logging
from src.utils.datetime_utils import DateTimeUtils

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

utils = DateTimeUtils(trace_id="debug-session")
# Operations will now log debug information
```

#### 2. Validate Inputs

```python
from src.utils.datetime_utils import DateTimeUtils

def safe_parse_datetime(date_str: str):
    """Safely parse datetime with validation."""
    utils = DateTimeUtils()

    try:
        # Try parsing
        dt = utils.parse_datetime(date_str)

        # Validate reasonable date range
        if dt.year < 1900 or dt.year > 2100:
            raise ValueError("Date out of reasonable range")

        return dt

    except Exception as e:
        utils.logger.error(f"Date parsing failed: {e}")
        return None
```

#### 3. Test Timezone Conversions

```python
from src.utils.datetime_utils import DateTimeUtils

def test_timezone_conversion():
    """Test timezone conversion functionality."""
    utils = DateTimeUtils()

    # Test common timezones
    test_timezones = ['UTC', 'US/Eastern', 'US/Pacific', 'Asia/Kolkata']

    for tz in test_timezones:
        try:
            tz_obj = utils.get_timezone(tz)
            print(f"✓ {tz}: {tz_obj}")
        except Exception as e:
            print(f"✗ {tz}: {e}")
```

### Performance Optimization

#### 1. Reuse DateTimeUtils Instance

```python
# Good: Reuse instance
utils = DateTimeUtils(trace_id="session-123")
for i in range(1000):
    result = utils.now()

# Bad: Create new instance each time
for i in range(1000):
    utils = DateTimeUtils(trace_id="session-123")
    result = utils.now()
```

#### 2. Use Convenience Functions for Simple Operations

```python
# Good: Use convenience functions for simple operations
from src.utils.datetime_utils import now, today

current_time = now()
current_date = today()

# Bad: Create instance for simple operations
utils = DateTimeUtils()
current_time = utils.now()
current_date = utils.today()
```

#### 3. Batch Operations

```python
# Good: Batch operations
def process_dates_batch(dates: list[date]):
    utils = DateTimeUtils()
    results = []

    for date_obj in dates:
        # Process multiple operations at once
        week_start = utils.get_week_start(date_obj)
        week_end = utils.get_week_end(date_obj)
        is_weekend = utils.is_weekend(date_obj)

        results.append({
            'date': date_obj,
            'week_start': week_start,
            'week_end': week_end,
            'is_weekend': is_weekend
        })

    return results
```

---

## Summary

The DateTime Utilities module provides comprehensive date and time operations for FastAPI applications. It includes timezone handling, business day calculations, date formatting, duration calculations, and more. The module is designed to be easy to use with both class-based and convenience function APIs, and includes comprehensive error handling and logging.

For more examples and advanced usage, see the test files in `tests/test_utils/test_datetime_utils.py`.
