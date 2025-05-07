import os
from typing import List, Dict, Any
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Import functions from your existing gmail_reader module
# Assuming these functions exist based on the context provided earlier
from gmail_reader import (
    list_unread_subjects,
    get_email_body_by_subject,
    # search_recent_emails_by_keyword, # Remove this line
    mark_mail_as_read_with_subject,
    get_gmail_service # Needed if functions require the service object directly
)

# Load environment variables (for Gmail credentials)
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("gmail", log_level="INFO") # Use INFO for better debugging initially

# --- Helper Function to Format Email Details ---
def format_email_details(emails: List[Dict[str, Any]]) -> str:
    """Formats a list of email details (subject, timestamp) into a readable string."""
    if not emails:
        return "No matching emails found."
    
    formatted_list = []
    for email in emails:
        subject = email.get('subject', 'No Subject')
        timestamp = email.get('timestamp', 'No Date')
        formatted_list.append(f"Subject: {subject}\nDate: {timestamp}")
    
    return "\n---\n".join(formatted_list)

# --- MCP Tools ---

@mcp.tool()
async def list_unread(max_results: int = 10, keyword: str | None = None) -> str:
    """Lists subjects of unread emails.

    Args:
        max_results: Maximum number of emails to list. Defaults to 10.
        keyword: Optional keyword to filter subjects.
    """
    try:
        subjects = list_unread_subjects(max_results=max_results, keyword=keyword)
        if not subjects:
            return "No unread emails found." if not keyword else f"No unread emails matching '{keyword}' found."
        return "\n".join(subjects)
    except Exception as e:
        mcp.logger.error(f"Error listing unread emails: {e}")
        return f"Error listing unread emails: {e}"

@mcp.tool()
async def get_email_content(subject: str) -> str:
    """Gets the full body content of an email by its exact subject.

    Args:
        subject: The exact subject of the email to retrieve.
    """
    if not subject:
        return "Error: Subject cannot be empty."
    try:
        body = get_email_body_by_subject(subject)
        return body if body else f"Email with subject '{subject}' not found or has no body."
    except Exception as e:
        mcp.logger.error(f"Error getting email content for subject '{subject}': {e}")
        return f"Error getting email content: {e}"

# Remove the entire search_emails tool function
# @mcp.tool()
# async def search_emails(keyword: str, max_results: int = 10) -> str:
#     """Searches recent emails for a keyword in the subject and returns subjects and timestamps.
#
#     Args:
#         keyword: The keyword to search for in email subjects.
#         max_results: Maximum number of recent emails to check. Defaults to 10.
#     """
#     if not keyword:
#         return "Error: Search keyword cannot be empty."
#     try:
#         # Assuming search_recent_emails_by_keyword exists and returns List[Dict[str, Any]]
#         # You might need to adjust this based on your actual gmail_reader implementation
#         matching_emails = search_recent_emails_by_keyword(keyword=keyword, number_of_latest_email_to_check=max_results)
#         return format_email_details(matching_emails)
#     except Exception as e:
#         mcp.logger.error(f"Error searching emails for keyword '{keyword}': {e}")
#         return f"Error searching emails: {e}"

@mcp.tool()
async def mark_email_read(subject: str) -> str:
    """Marks an email as read based on its exact subject.

    Args:
        subject: The exact subject of the email to mark as read.
    """
    if not subject:
        return "Error: Subject cannot be empty."
    try:
        result = mark_mail_as_read_with_subject(subject)
        return result.get("message", "Completed mark as read operation.")
    except Exception as e:
        mcp.logger.error(f"Error marking email '{subject}' as read: {e}")
        return f"Error marking email as read: {e}"

# --- Run the server ---
if __name__ == "__main__":
    # Ensure .env file with GOOGLE_REFRESH_TOKEN, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET is accessible
    print("Starting Gmail MCP Server...")
    print("Ensure your Gmail API credentials are set in a .env file.")
    mcp.run(transport='stdio')