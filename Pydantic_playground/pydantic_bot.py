from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import requests

# Define a User model
class User(BaseModel):
    user_id: int = Field(..., description="The unique identifier for the user")
    username: str = Field(..., description="The username of the user")
    email: Optional[str] = Field(None, description="The email address of the user")

# Define a Message model
class Message(BaseModel):
    message_id: int = Field(..., description="The unique identifier for the message")
    sender: User = Field(..., description="The user who sent the message")
    content: str = Field(..., description="The content of the message")
    timestamp: datetime = Field(default_factory=datetime.now, description="The timestamp when the message was sent")

# Define a ChatSession model
class ChatSession(BaseModel):
    session_id: int = Field(..., description="The unique identifier for the chat session")
    participants: List[User] = Field(..., description="The list of users participating in the chat session")
    messages: List[Message] = Field(default_factory=list, description="The list of messages in the chat session")

    def add_message(self, sender: User, content: str):
        """Add a new message to the chat session."""
        new_message = Message(
            message_id=len(self.messages) + 1,
            sender=sender,
            content=content
        )
        self.messages.append(new_message)

    def get_bot_response(self, user_input: str) -> str:
        """Get a response from the local Ollama service and clean it up."""
        ollama_url = "http://127.0.0.1:11434/api/generate"  # Ollama API endpoint
        payload = {
            "model": "deepseek-r1:14b",  # Replace with the model you're using
            "prompt": user_input,
            "stream": False
        }
        try:
            response = requests.post(ollama_url, json=payload)
            response.raise_for_status()
            bot_response = response.json().get("response", "Sorry, I couldn't generate a response.")

            # Remove <think> tags from the response
            bot_response = bot_response.replace("<think>", "").replace("</think>", "").strip()
            return bot_response
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with Ollama: {e}")
            return "Sorry, I encountered an error while generating a response."

# Example usage
if __name__ == "__main__":
    # Create some users
    user1 = User(user_id=1, username="Alice", email="alice@example.com")
    user2 = User(user_id=2, username="Bob", email="bob@example.com")

    # Create a chat session
    chat_session = ChatSession(
        session_id=1,
        participants=[user1, user2]
    )

    # Simulate a conversation
    while True:
        user_input = input("User:")
        chat_session.add_message(sender=user1, content=user_input)
        # print(f"User: {user_input}")

        # Get a response from the bot (Ollama)
        bot_response = chat_session.get_bot_response(user_input)
        chat_session.add_message(sender=user2, content=bot_response)
        print(f"Bot: {bot_response}")

        # Print the chat session using model_dump_json()
        # print("\nChat Session:")
        # print(chat_session.model_dump_json(indent=2))
