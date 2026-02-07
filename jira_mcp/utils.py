#!/usr/bin/env python3.12
"""
Utility functions for Jira MCP server.

Common helper functions shared across modules.
"""

from typing import Any


def get_user_attribute(
    user_obj: Any,
    cloud_attr: str,
    server_attr: str,
    default: Any = None
) -> Any:
    """
    Safely get user attribute that may differ between Cloud and Server.

    Args:
        user_obj: User object from Jira API
        cloud_attr: Attribute name in Jira Cloud
        server_attr: Attribute name in Jira Server/Data Center
        default: Default value if attribute not found

    Returns:
        Attribute value or default
    """
    if user_obj is None:
        return default
    # Try Cloud attribute first
    if hasattr(user_obj, cloud_attr):
        return getattr(user_obj, cloud_attr)
    # Try Server attribute
    if hasattr(user_obj, server_attr):
        return getattr(user_obj, server_attr)
    # Return default
    return default
