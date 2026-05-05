"""
Data structure for representing issue links in TiraJira.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class IssueLink:
    """Represents a link between Jira issues.

    Attributes:
        target_key: The key of the target issue to link to.
        link_type: The type of link between issues (e.g., 'relates to', 'blocks').
    """

    target_key: Optional[str] = None
    link_type: Optional[str] = None
