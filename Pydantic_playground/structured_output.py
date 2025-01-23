"""
Introduction to PydanticAI.

This module demonstrates how PydanticAI makes it easier to build
production-grade LLM-powered systems with type safety and structured responses.
"""

from typing import Dict, List, Optional
import nest_asyncio
from pydantic import BaseModel, Field
from pydantic_ai import Agent, ModelRetry, RunContext, Tool
from pydantic_ai.models.openai import OpenAIModel

from markdown import to_markdown


nest_asyncio.apply()

DeepSeek_MODEL = "deepseek-chat"
DeepSeek_API_KEY = "sk-be34b6c3d96f416b86a097987ac9b1fe"
DeepSeek_BASE_URL = "https://api.deepseek.com"

model = OpenAIModel(
        model_name=DeepSeek_MODEL,
        api_key=DeepSeek_API_KEY,
        base_url=DeepSeek_BASE_URL,
        )



# --------------------------------------------------------------
# 2. Agent with Structured Response
# --------------------------------------------------------------
"""
This example shows how to get structured, type-safe responses from the agent.
Key concepts:
- Using Pydantic models to define response structure
- Type validation and safety
- Field descriptions for better model understanding
"""


class ResponseModel(BaseModel):
    """Structured response with metadata."""

    response: str
    needs_escalation: bool
    follow_up_required: bool
    sentiment: str = Field(description="Customer sentiment analysis")


agent2 = Agent(
    model=model,
    result_type=ResponseModel,
    system_prompt=(
        "You are an intelligent customer support agent. "
        "Analyze queries carefully and provide structured responses."
    ),
)

response = agent2.run_sync("How can I track my order #12345?")
print(response.data.model_dump_json(indent=2))


# --------------------------------------------------------------
# 3. Agent with Structured Response & Dependencies
# --------------------------------------------------------------
"""
This example demonstrates how to use dependencies and context in agents.
Key concepts:
- Defining complex data models with Pydantic
- Injecting runtime dependencies
- Using dynamic system prompts
"""


# Define order schema
class Order(BaseModel):
    """Structure for order details."""

    order_id: str
    status: str
    items: List[str]


# Define customer schema
class CustomerDetails(BaseModel):
    """Structure for incoming customer queries."""

    customer_id: str
    name: str
    email: str
    orders: Optional[List[Order]] = None


# Agent with structured output and dependencies
agent5 = Agent(
    model=model,
    result_type=ResponseModel,
    deps_type=CustomerDetails,
    retries=3,
    system_prompt=(
        "You are an intelligent customer support agent. "
        "Analyze queries carefully and provide structured responses. "
        "Always great the customer and provide a helpful response."
    ),  # These are known when writing the code
)


# Add dynamic system prompt based on dependencies
@agent5.system_prompt
async def add_customer_name(ctx: RunContext[CustomerDetails]) -> str:
    return f"Customer details: {to_markdown(ctx.deps)}"  # These depend in some way on context that isn't known until runtime


customer = CustomerDetails(
    customer_id="1",
    name="John Doe",
    email="john.doe@example.com",
    orders=[
        Order(order_id="12345", status="shipped", items=["Blue Jeans", "T-Shirt"]),
    ],
)

response = agent5.run_sync(user_prompt="What did I order?", deps=customer)

response.all_messages()
print(response.data.model_dump_json(indent=2))

print(
    "Customer Details:\n"
    f"Name: {customer.name}\n"
    f"Email: {customer.email}\n\n"
    "Response Details:\n"
    f"{response.data.response}\n\n"
    "Status:\n"
    f"Follow-up Required: {response.data.follow_up_required}\n"
    f"Needs Escalation: {response.data.needs_escalation}"
)

