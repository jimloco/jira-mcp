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

    def _get_user_attribute(self, user_obj: Any, cloud_attr: str, server_attr: str, default: Any = None) -> Any:
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
                'name': self._get_user_attribute(fields.assignee, 'displayName', 'displayName', 'Unknown'),
                'account_id': self._get_user_attribute(fields.assignee, 'accountId', 'name', 'N/A')
            }
        else:
            issue_data['assignee'] = None

        # Add reporter info
        if hasattr(fields, 'reporter') and fields.reporter:
            issue_data['reporter'] = {
                'name': self._get_user_attribute(fields.reporter, 'displayName', 'displayName', 'Unknown'),
                'account_id': self._get_user_attribute(fields.reporter, 'accountId', 'name', 'N/A')
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

    def list_comments(self, issue_key: str) -> List[Dict[str, Any]]:
        """
        Get all comments for an issue.

        Args:
            issue_key: Issue key (e.g., 'PROJ-123')

        Returns:
            List of comment dictionaries

        Raises:
            IssueManagerError: If retrieval fails
        """
        try:
            logger.info("Getting comments for issue: %s", issue_key)

            issue = self.jira.issue(issue_key)
            comments = issue.fields.comment.comments

            comment_list = []
            for comment in comments:
                comment_data = {
                    'id': comment.id,
                    'body': comment.body,
                    'author': {
                        'name': self._get_user_attribute(comment.author, 'displayName', 'displayName', 'Unknown'),
                        'account_id': self._get_user_attribute(comment.author, 'accountId', 'name', 'N/A')
                    },
                    'created': str(comment.created),
                    'updated': str(comment.updated)
                }
                comment_list.append(comment_data)

            logger.info("Found %d comments", len(comment_list))
            return comment_list

        except JIRAError as e:
            error_msg = f"Failed to get comments for {issue_key}: {e.text if hasattr(e, 'text') else str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error getting comments: {str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e

    def add_comment(self, issue_key: str, body: str) -> Dict[str, Any]:
        """
        Add a comment to an issue.

        Args:
            issue_key: Issue key (e.g., 'PROJ-123')
            body: Comment text

        Returns:
            Created comment dictionary

        Raises:
            IssueManagerError: If comment creation fails
        """
        try:
            logger.info("Adding comment to issue: %s", issue_key)

            issue = self.jira.issue(issue_key)
            comment = self.jira.add_comment(issue, body)

            comment_data = {
                'id': comment.id,
                'body': comment.body,
                'author': {
                    'name': self._get_user_attribute(comment.author, 'displayName', 'displayName', 'Unknown'),
                    'account_id': self._get_user_attribute(comment.author, 'accountId', 'name', 'N/A')
                },
                'created': str(comment.created),
                'updated': str(comment.updated)
            }

            logger.info("✅ Added comment to %s", issue_key)
            return comment_data

        except JIRAError as e:
            error_msg = f"Failed to add comment to {issue_key}: {e.text if hasattr(e, 'text') else str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error adding comment: {str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e

    def update_comment(
        self,
        issue_key: str,
        comment_id: str,
        body: str
    ) -> Dict[str, Any]:
        """
        Update an existing comment.

        Args:
            issue_key: Issue key (e.g., 'PROJ-123')
            comment_id: Comment ID to update
            body: New comment text

        Returns:
            Updated comment dictionary

        Raises:
            IssueManagerError: If comment update fails
        """
        try:
            logger.info("Updating comment %s on issue %s", comment_id, issue_key)

            comment = self.jira.comment(issue_key, comment_id)
            comment.update(body=body)

            # Refresh comment to get updated data
            comment = self.jira.comment(issue_key, comment_id)

            comment_data = {
                'id': comment.id,
                'body': comment.body,
                'author': {
                    'name': self._get_user_attribute(comment.author, 'displayName', 'displayName', 'Unknown'),
                    'account_id': self._get_user_attribute(comment.author, 'accountId', 'name', 'N/A')
                },
                'created': str(comment.created),
                'updated': str(comment.updated)
            }

            logger.info("✅ Updated comment %s", comment_id)
            return comment_data

        except JIRAError as e:
            error_msg = f"Failed to update comment {comment_id}: {e.text if hasattr(e, 'text') else str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error updating comment: {str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e

    def delete_comment(self, issue_key: str, comment_id: str) -> None:
        """
        Delete a comment from an issue.

        Args:
            issue_key: Issue key (e.g., 'PROJ-123')
            comment_id: Comment ID to delete

        Raises:
            IssueManagerError: If comment deletion fails
        """
        try:
            logger.info("Deleting comment %s from issue %s", comment_id, issue_key)

            comment = self.jira.comment(issue_key, comment_id)
            comment.delete()

            logger.info("✅ Deleted comment %s", comment_id)

        except JIRAError as e:
            error_msg = f"Failed to delete comment {comment_id}: {e.text if hasattr(e, 'text') else str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error deleting comment: {str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e

    def list_attachments(self, issue_key: str) -> List[Dict[str, Any]]:
        """
        Get all attachments for an issue.

        Args:
            issue_key: Issue key (e.g., 'PROJ-123')

        Returns:
            List of attachment dictionaries

        Raises:
            IssueManagerError: If retrieval fails
        """
        try:
            logger.info("Getting attachments for issue: %s", issue_key)

            issue = self.jira.issue(issue_key)
            attachments = issue.fields.attachment

            attachment_list = []
            for attachment in attachments:
                attachment_data = {
                    'id': attachment.id,
                    'filename': attachment.filename,
                    'size': attachment.size,
                    'mime_type': getattr(attachment, 'mimeType', 'unknown'),
                    'created': str(attachment.created),
                    'author': {
                        'name': self._get_user_attribute(attachment.author, 'displayName', 'displayName', 'Unknown'),
                        'account_id': self._get_user_attribute(attachment.author, 'accountId', 'name', 'N/A')
                    },
                    'content_url': attachment.content
                }
                attachment_list.append(attachment_data)

            logger.info("Found %d attachments", len(attachment_list))
            return attachment_list

        except JIRAError as e:
            error_msg = f"Failed to get attachments for {issue_key}: {e.text if hasattr(e, 'text') else str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error getting attachments: {str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e

    def add_attachment(self, issue_key: str, filepath: str) -> Dict[str, Any]:
        """
        Upload an attachment to an issue.

        Args:
            issue_key: Issue key (e.g., 'PROJ-123')
            filepath: Path to file to upload

        Returns:
            Created attachment dictionary

        Raises:
            IssueManagerError: If upload fails
        """
        try:
            logger.info("Adding attachment to issue %s: %s", issue_key, filepath)

            issue = self.jira.issue(issue_key)

            # Upload the attachment
            with open(filepath, 'rb') as file:
                attachment = self.jira.add_attachment(issue, file)

            attachment_data = {
                'id': attachment.id,
                'filename': attachment.filename,
                'size': attachment.size,
                'mime_type': getattr(attachment, 'mimeType', 'unknown'),
                'created': str(attachment.created),
                'author': {
                    'name': self._get_user_attribute(attachment.author, 'displayName', 'displayName', 'Unknown'),
                    'account_id': self._get_user_attribute(attachment.author, 'accountId', 'name', 'N/A')
                },
                'content_url': attachment.content
            }

            logger.info("✅ Added attachment to %s", issue_key)
            return attachment_data

        except FileNotFoundError as e:
            error_msg = f"File not found: {filepath}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e
        except JIRAError as e:
            error_msg = f"Failed to add attachment to {issue_key}: {e.text if hasattr(e, 'text') else str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error adding attachment: {str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e

    def delete_attachment(self, attachment_id: str) -> None:
        """
        Delete an attachment.

        Args:
            attachment_id: Attachment ID to delete

        Raises:
            IssueManagerError: If deletion fails
        """
        try:
            logger.info("Deleting attachment: %s", attachment_id)

            attachment = self.jira.attachment(attachment_id)
            attachment.delete()

            logger.info("✅ Deleted attachment %s", attachment_id)

        except JIRAError as e:
            error_msg = f"Failed to delete attachment {attachment_id}: {e.text if hasattr(e, 'text') else str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error deleting attachment: {str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e

    def create_link(
        self,
        inward_issue: str,
        outward_issue: str,
        link_type: str = "Relates"
    ) -> Dict[str, Any]:
        """
        Create a link between two issues.

        Args:
            inward_issue: Inward issue key (e.g., 'PROJ-123')
            outward_issue: Outward issue key (e.g., 'PROJ-456')
            link_type: Link type name (e.g., 'Relates', 'Blocks', 'Duplicate')

        Returns:
            Link creation result

        Raises:
            IssueManagerError: If link creation fails
        """
        try:
            logger.info("Creating link: %s %s %s", inward_issue, link_type, outward_issue)

            self.jira.create_issue_link(
                type=link_type,
                inwardIssue=inward_issue,
                outwardIssue=outward_issue
            )

            result = {
                'inward_issue': inward_issue,
                'outward_issue': outward_issue,
                'link_type': link_type
            }

            logger.info("✅ Created link between %s and %s", inward_issue, outward_issue)
            return result

        except JIRAError as e:
            error_msg = f"Failed to create link: {e.text if hasattr(e, 'text') else str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error creating link: {str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e

    def delete_link(self, link_id: str) -> None:
        """
        Delete an issue link.

        Args:
            link_id: Link ID to delete

        Raises:
            IssueManagerError: If link deletion fails
        """
        try:
            logger.info("Deleting link: %s", link_id)

            link = self.jira.issue_link(link_id)
            link.delete()

            logger.info("✅ Deleted link %s", link_id)

        except JIRAError as e:
            error_msg = f"Failed to delete link {link_id}: {e.text if hasattr(e, 'text') else str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error deleting link: {str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e

    def list_links(self, issue_key: str) -> List[Dict[str, Any]]:
        """
        Get all issue links for an issue.

        Args:
            issue_key: Issue key (e.g., 'PROJ-123')

        Returns:
            List of link dictionaries

        Raises:
            IssueManagerError: If retrieval fails
        """
        try:
            logger.info("Getting links for issue: %s", issue_key)

            issue = self.jira.issue(issue_key)
            issue_links = issue.fields.issuelinks

            link_list = []
            for link in issue_links:
                link_data = {
                    'id': link.id,
                    'type': link.type.name
                }

                # Determine if this is an inward or outward link
                if hasattr(link, 'outwardIssue'):
                    link_data['direction'] = 'outward'
                    link_data['related_issue'] = link.outwardIssue.key
                    link_data['related_summary'] = link.outwardIssue.fields.summary
                elif hasattr(link, 'inwardIssue'):
                    link_data['direction'] = 'inward'
                    link_data['related_issue'] = link.inwardIssue.key
                    link_data['related_summary'] = link.inwardIssue.fields.summary

                link_list.append(link_data)

            logger.info("Found %d links", len(link_list))
            return link_list

        except JIRAError as e:
            error_msg = f"Failed to get links for {issue_key}: {e.text if hasattr(e, 'text') else str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error getting links: {str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e

    def create_subtask(
        self,
        parent_key: str,
        summary: str,
        description: Optional[str] = None,
        assignee: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a subtask under a parent issue.

        Args:
            parent_key: Parent issue key (e.g., 'PROJ-123')
            summary: Subtask summary/title
            description: Optional subtask description
            assignee: Optional assignee account ID

        Returns:
            Created subtask dictionary

        Raises:
            IssueManagerError: If subtask creation fails
        """
        try:
            logger.info("Creating subtask under %s: %s", parent_key, summary)

            # Get parent issue to extract project
            parent_issue = self.jira.issue(parent_key)
            project_key = parent_issue.fields.project.key

            # Build subtask fields
            fields = {
                'project': {'key': project_key},
                'summary': summary,
                'issuetype': {'name': 'Sub-task'},
                'parent': {'key': parent_key}
            }

            if description:
                fields['description'] = description

            if assignee:
                fields['assignee'] = {'accountId': assignee}

            # Create the subtask
            subtask = self.jira.create_issue(fields=fields)

            logger.info("✅ Created subtask: %s", subtask.key)
            return self._format_issue(subtask, full_details=True)

        except JIRAError as e:
            error_msg = f"Failed to create subtask: {e.text if hasattr(e, 'text') else str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error creating subtask: {str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e

    def list_subtasks(self, issue_key: str) -> List[Dict[str, Any]]:
        """
        Get all subtasks for an issue.

        Args:
            issue_key: Parent issue key (e.g., 'PROJ-123')

        Returns:
            List of subtask dictionaries

        Raises:
            IssueManagerError: If retrieval fails
        """
        try:
            logger.info("Getting subtasks for issue: %s", issue_key)

            issue = self.jira.issue(issue_key)
            subtasks = getattr(issue.fields, 'subtasks', [])

            subtask_list = []
            for subtask in subtasks:
                subtask_data = {
                    'key': subtask.key,
                    'id': subtask.id,
                    'summary': subtask.fields.summary,
                    'status': subtask.fields.status.name,
                    'url': f"{self.site_url}/browse/{subtask.key}"
                }

                # Add assignee if present
                if hasattr(subtask.fields, 'assignee') and subtask.fields.assignee:
                    subtask_data['assignee'] = {
                        'name': self._get_user_attribute(subtask.fields.assignee, 'displayName', 'displayName', 'Unknown'),
                        'account_id': self._get_user_attribute(subtask.fields.assignee, 'accountId', 'name', 'N/A')
                    }
                else:
                    subtask_data['assignee'] = None

                subtask_list.append(subtask_data)

            logger.info("Found %d subtasks", len(subtask_list))
            return subtask_list

        except JIRAError as e:
            error_msg = f"Failed to get subtasks for {issue_key}: {e.text if hasattr(e, 'text') else str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error getting subtasks: {str(e)}"
            logger.error("❌ %s", error_msg)
            raise IssueManagerError(error_msg) from e

    def __repr__(self) -> str:
        """String representation of IssueManager."""
        return f"IssueManager(site_url='{self.site_url}')"
