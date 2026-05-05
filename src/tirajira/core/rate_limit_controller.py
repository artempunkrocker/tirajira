"""
Module for managing rate limiting of requests to the Jira API.
"""

import threading
import time

from ..logger import get_logger


class RateLimitController:
    """Rate limit controller that provides timing delays."""

    def __init__(self, min_request_interval: float = 1.0) -> None:
        """
        Initializes the rate limit controller.

        Args:
            min_request_interval: Minimum interval between requests in seconds.
        """
        self.min_request_interval = min_request_interval
        self._last_request_time = 0.0
        self._lock = threading.Lock()
        self.logger = get_logger()

    def wait_if_needed(self) -> None:
        """
        Waits, if necessary, to comply with the minimum interval between requests.

        The method is thread-safe and uses a lock to synchronize access
        to the last request time.
        """
        if self.min_request_interval <= 0:
            return

        with self._lock:
            current_time = time.time()
            time_since_last_request = current_time - self._last_request_time
            time_to_wait = self.min_request_interval - time_since_last_request

            if time_to_wait > 0:
                self.logger.debug(
                    f"Waiting {time_to_wait:.2f} seconds to comply with "
                    f"request rate limiting"
                )
                time.sleep(time_to_wait)
                self.logger.debug("Waiting completed")

            # Update the last request time
            self._last_request_time = time.time()

    def update_min_request_interval(self, interval: float) -> None:
        """
        Updates the minimum interval between requests.

        Args:
            interval: New minimum interval between requests in seconds.
        """
        with self._lock:
            self.min_request_interval = interval
            self.logger.debug(f"Minimum request interval updated to {interval} seconds")
