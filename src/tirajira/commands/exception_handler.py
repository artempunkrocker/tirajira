"""Standardized exception handler for TiraJira commands."""

from functools import wraps
from typing import Any, Callable

from ..logger import get_logger


def handle_exceptions(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator for standardized exception handling in commands.

    Args:
        func: Function to wrap

    Returns:
        Wrapped function with exception handling

    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        logger = get_logger()

        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error executing command: {e}")

            if func.__name__ == "execute":
                if (
                    args
                    and hasattr(args[0], "args")
                    and hasattr(args[0].args, "verbose")
                    and args[0].args.verbose
                ):
                    logger.debug(f"Error details: {str(e)}")
                return 1

            raise

    return wrapper
