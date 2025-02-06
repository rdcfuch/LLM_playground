import os
from typing import List
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from microsoft_graph.client import GraphClient

# Define email structure and summary result
class Email(BaseModel):
    subject: str
    sender: str
    body: str

class SummaryResult(BaseModel):
    focus_items: List[str]
    summary: str

# Agent setup
email_agent = Agent(
    model='openai:gpt-4o',
    result_type=SummaryResult,
    system_prompt=(
        "You are an assistant that helps summarize daily emails. "
        "Focus on highlighting key action items and providing a concise summary."
    ),
)

# Tool to fetch emails from Outlook
@email_agent.tool_plain
def fetch_emails_from_outlook() -> List[Email]:
    """Fetches today's emails from Outlook."""
    # Authenticate with Microsoft Graph API
    client = GraphClient(
        client_id=os.getenv("MS_CLIENT_ID"),
        client_secret=os.getenv("MS_CLIENT_SECRET"),
        tenant_id=os.getenv("MS_TENANT_ID"),
    )

    # Fetch the last 10 emails
    emails_data = client.get(
        "/me/messages",
        params={"$top": 10, "$select": "subject,from,bodyPreview"},
    )

    emails = []
    for item in emails_data["value"]:
        emails.append(
            Email(
                subject=item.get("subject", "No Subject"),
                sender=item["from"]["emailAddress"]["address"],
                body=item.get("bodyPreview", "No Content"),
            )
        )

    return emails

# Run the agent to summarize emails
if __name__ == '__main__':
    # Fetch emails using the tool
    emails = fetch_emails_from_outlook()

    # Run the agent with fetched emails
    result = email_agent.run_sync("Summarize my emails and tell me what to focus on.", deps=emails)
    print("Daily Summary:")
    print(result.data.summary)
    print("\nFocus Items:")
    for item in result.data.focus_items:
        print(f"- {item}")