import dramatiq


@dramatiq.actor
def test_background_task(duration: int = 1):
    """
    A simple test task that sleeps for a specified duration.
    Used for verifying the background jobs system.
    """
    import time

    time.sleep(duration)
    return {"status": "success", "duration": duration}


@dramatiq.actor
def test_failing_task():
    """
    A test task that always fails.
    """
    raise ValueError("This is a simulated failure")
