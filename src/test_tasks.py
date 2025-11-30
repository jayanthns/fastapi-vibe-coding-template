"""Simple test tasks for debugging Dramatiq."""

import dramatiq


@dramatiq.actor
def hello_world(name: str = "World"):
    """
    Simple hello world task for testing Dramatiq.

    Args:
        name: Name to greet
    """
    message = f"Hello, {name}! Dramatiq is working!"
    print(message)  # Print to stdout for easy debugging
    return message


@dramatiq.actor
def test_task_with_args(x: int, y: int):
    """
    Test task with arguments.

    Args:
        x: First number
        y: Second number

    Returns:
        Sum of x and y
    """
    result = x + y
    print(f"Test task: {x} + {y} = {result}")
    return result
