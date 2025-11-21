#!/usr/bin/env python3.12
"""
Issue Manager Module

Handles Jira issue operations including search, create, read, update, and transitions.
"""

import logging
from typing import Any, Dict, List, Optional
from jira import JIRA
from jira.exceptions import JIRAError

# Configure logging
logger = logging.getLogger(__name__)


class IssueManagerError(Exception):
    """Custom exception for issue manager errors."""


class IssueManager:
    """
    Manager for Jira issue operations.

    Handles issue lifecycle: search, create, read, update, assign, transition.
    """

    def __init__(self, jira_client: JIRA, site_url: str):
        """
        Initialize issue manager.

        Args:
            jira_client: Authenticated JIRA client instance
            site_url: Jira site URL for generating links
        """
        self.jira = jira_client
        self.site_url = site_url.rstrip('/')

    def search_issues(
        self,
        jql: str,
        max_results: int = 50,
        fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for issues using JQL.

        Args:
            jql: JQL query string
            max_results: Maximum number of results to return
            fields: Optional list of fields to retrieve

        Returns:
            List of issue dictionaries

        Raises:
            IssueManagerError: If search fails
        """
        try:
            logger.info("Searching issues with JQL: %s", jql)

            # Default fields if not specified
            if fields is None:
                fields = [
                    'summary', 'status', 'assignee', 'reporter',
                    'priority', 'created', 'updated', 'issuetype',
                    'project', 'description'
                ]

            issues = self.jira.search_issues(
                jql,
                maxResults=max_results,
                fields=','.join(fields)
            )

            issue_list = []
            for issue in issues:
                issue_data = self._format_issue(issue)
                issue_list.append(issue_data)

            logger.info("Found %d issues", len(issue_list))
            return issue_list

        except JIRAError as e:
            error_msg = f"Failed to search issues: {e.text if hasattr(e, 'text') else str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error searching issues: {str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e

    def get_issue(self, issue_key: str) -> Dict[str, Any]:
        """
        Get full details of a specific issue.

        Args:
            issue_key: Issue key (e.g., 'PROJ-123')

        Returns:
            Issue dictionary with full details

        Raises:
            IssueManagerError: If issue not found or access denied
        """
        try:
            logger.info("Getting issue: %s", issue_key)

            issue = self.jira.issue(issue_key)
            issue_data = self._format_issue(issue, full_details=True)

            return issue_data

        except JIRAError as e:
            error_msg = f"Failed to get issue {issue_key}: {e.text if hasattr(e, 'text') else str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error getting issue: {str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e

    def create_issue(  # pylint: disable=too-many-positional-arguments
        self,
        project_key: str,
        summary: str,
        issue_type: str,
        description: Optional[str] = None,
        assignee: Optional[str] = None,
        priority: Optional[str] = None,
        labels: Optional[List[str]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Create a new issue.

        Args:
            project_key: Project key (e.g., 'PROJ')
            summary: Issue summary/title
            issue_type: Issue type name (e.g., 'Task', 'Bug')
            description: Optional issue description
            assignee: Optional assignee account ID or username
            priority: Optional priority name
            labels: Optional list of labels
            **kwargs: Additional custom fields

        Returns:
            Created issue dictionary

        Raises:
            IssueManagerError: If creation fails
        """
        try:
            logger.info("Creating issue in project %s: %s", project_key, summary)

            # Build issue fields
            fields = {
                'project': {'key': project_key},
                'summary': summary,
                'issuetype': {'name': issue_type}
            }

            if description:
                fields['description'] = description

            if assignee:
                fields['assignee'] = {'accountId': assignee}

            if priority:
                fields['priority'] = {'name': priority}

            if labels:
                fields['labels'] = labels

            # Add any additional custom fields
            fields.update(kwargs)

            # Create the issue
            issue = self.jira.create_issue(fields=fields)

            logger.info("✅ Created issue: %s", issue.key)
            return self._format_issue(issue, full_details=True)

        except JIRAError as e:
            error_msg = f"Failed to create issue: {e.text if hasattr(e, 'text') else str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error creating issue: {str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e

    def update_issue(  # pylint: disable=too-many-positional-arguments
        self,
        issue_key: str,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        assignee: Optional[str] = None,
        priority: Optional[str] = None,
        labels: Optional[List[str]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Update an existing issue.

        Args:
            issue_key: Issue key (e.g., 'PROJ-123')
            summary: Optional new summary
            description: Optional new description
            assignee: Optional new assignee account ID
            priority: Optional new priority
            labels: Optional new labels list
            **kwargs: Additional custom fields to update

        Returns:
            Updated issue dictionary

        Raises:
            IssueManagerError: If update fails
        """
        try:
            logger.info("Updating issue: %s", issue_key)

            issue = self.jira.issue(issue_key)
            fields = {}

            if summary is not None:
                fields['summary'] = summary

            if description is not None:
                fields['description'] = description

            if assignee is not None:
                fields['assignee'] = {'accountId': assignee}

            if priority is not None:
                fields['priority'] = {'name': priority}

            if labels is not None:
                fields['labels'] = labels

            # Add any additional custom fields
            fields.update(kwargs)

            # Update the issue
            issue.update(fields=fields)

            logger.info("✅ Updated issue: %s", issue_key)
            return self._format_issue(issue, full_details=True)

        except JIRAError as e:
            error_msg = f"Failed to update issue {issue_key}: {e.text if hasattr(e, 'text') else str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error updating issue: {str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e

    def assign_issue(self, issue_key: str, assignee: str) -> Dict[str, Any]:
        """
        Assign an issue to a user.

        Args:
            issue_key: Issue key (e.g., 'PROJ-123')
            assignee: User account ID or username

        Returns:
            Updated issue dictionary

        Raises:
            IssueManagerError: If assignment fails
        """
        try:
            logger.info("Assigning issue %s to %s", issue_key, assignee)

            issue = self.jira.issue(issue_key)
            self.jira.assign_issue(issue, assignee)

            logger.info("✅ Assigned issue %s to %s", issue_key, assignee)
            return self._format_issue(issue, full_details=True)

        except JIRAError as e:
            error_msg = f"Failed to assign issue {issue_key}: {e.text if hasattr(e, 'text') else str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error assigning issue: {str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e

    def transition_issue(
        self,
        issue_key: str,
        transition: str,
        comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transition an issue to a new status.

        Args:
            issue_key: Issue key (e.g., 'PROJ-123')
            transition: Transition name or ID
            comment: Optional comment to add with transition

        Returns:
            Updated issue dictionary

        Raises:
            IssueManagerError: If transition fails
        """
        try:
            logger.info("Transitioning issue %s: %s", issue_key, transition)

            issue = self.jira.issue(issue_key)

            # Get available transitions
            transitions = self.jira.transitions(issue)
            transition_id = None

            # Find transition by name or ID
            for trans in transitions:
                if trans['name'].lower() == transition.lower() or trans['id'] == transition:
                    transition_id = trans['id']
                    break

            if not transition_id:
                available = [t['name'] for t in transitions]
                raise IssueManagerError(
                    f"Transition '{transition}' not found. Available: {', '.join(available)}"
                )

            # Perform transition
            if comment:
                self.jira.transition_issue(
                    issue,
                    transition_id,
                    comment=comment
                )
            else:
                self.jira.transition_issue(issue, transition_id)

            logger.info("✅ Transitioned issue %s", issue_key)

            # Refresh issue to get updated status
            issue = self.jira.issue(issue_key)
            return self._format_issue(issue, full_details=True)

        except JIRAError as e:
            error_msg = f"Failed to transition issue {issue_key}: {e.text if hasattr(e, 'text') else str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e
        except IssueManagerError:
            raise
        except Exception as e:
            error_msg = f"Unexpected error transitioning issue: {str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e

    def get_transitions(self, issue_key: str) -> List[Dict[str, str]]:
        """
        Get available transitions for an issue.

        Args:
            issue_key: Issue key (e.g., 'PROJ-123')

        Returns:
            List of transition dictionaries with id and name

        Raises:
            IssueManagerError: If retrieval fails
        """
        try:
            issue = self.jira.issue(issue_key)
            transitions = self.jira.transitions(issue)

            return [
                {'id': t['id'], 'name': t['name']}
                for t in transitions
            ]

        except JIRAError as e:
            error_msg = f"Failed to get transitions for {issue_key}: {e.text if hasattr(e, 'text') else str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error getting transitions: {str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e

    def _format_issue(self, issue: Any, full_details: bool = False) -> Dict[str, Any]:
        """
        Format issue data into a dictionary.

        Args:
            issue: JIRA issue object
            full_details: Whether to include full details

        Returns:
            Formatted issue dictionary
        """
        fields = issue.fields

        # Basic issue data
        issue_data = {
            'key': issue.key,
            'id': issue.id,
            'summary': fields.summary,
            'status': fields.status.name,
            'issue_type': fields.issuetype.name,
            'project': fields.project.key,
            'url': f"{self.site_url}/browse/{issue.key}",
            'created': str(fields.created),
            'updated': str(fields.updated)
        }

        # Add assignee info
        if hasattr(fields, 'assignee') and fields.assignee:
            issue_data['assignee'] = {
                'name': fields.assignee.displayName,
                'account_id': fields.assignee.accountId
            }
        else:
            issue_data['assignee'] = None

        # Add reporter info
        if hasattr(fields, 'reporter') and fields.reporter:
            issue_data['reporter'] = {
                'name': fields.reporter.displayName,
                'account_id': fields.reporter.accountId
            }
        else:
            issue_data['reporter'] = None

        # Add priority
        if hasattr(fields, 'priority') and fields.priority:
            issue_data['priority'] = fields.priority.name
        else:
            issue_data['priority'] = None

        # Add full details if requested
        if full_details:
            issue_data['description'] = getattr(fields, 'description', None) or ''

            # Add labels
            issue_data['labels'] = getattr(fields, 'labels', [])

            # Add components
            if hasattr(fields, 'components') and fields.components:
                issue_data['components'] = [c.name for c in fields.components]
            else:
                issue_data['components'] = []

            # Add fix versions
            if hasattr(fields, 'fixVersions') and fields.fixVersions:
                issue_data['fix_versions'] = [v.name for v in fields.fixVersions]
            else:
                issue_data['fix_versions'] = []

        return issue_data

    def __repr__(self) -> str:
        """String representation of IssueManager."""
        return f"IssueManager(site_url='{self.site_url}')"
