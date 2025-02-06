from typing import Dict, Any
from pydantic import BaseModel
from fc_pydantic_agent.agent import DynamicAgent
from httpx import Client
from dataclasses import dataclass
from pydantic_ai import Agent, ModelRetry, RunContext
from dataclasses import asdict

# Define the custom result type using Pydantic
class CountryResponse(BaseModel):
    country_name: str
    country_capital: str
    capital_location: str  # Format: "latitude,longitude"
    weather_api_key: str | None

@dataclass
class Deps:
    client: Client
    weather_api_key: str | None
    chat_history: list[Dict[str, str]]

def get_weather_api_key(ctx: RunContext) -> str:
    """Get the weather API key from dependencies."""
    print("get_weather_api_key called:", ctx.deps.weather_api_key)
    return ctx.deps.weather_api_key

def main():
    # Define a system prompt that explains the task to the agent
    system_prompt = """
    You are a helpful assistant that provides information about countries.
    When asked about a country, respond with its name, capital city, and the capital's coordinates. you will also use get_weather_api_key to get the weather API key.
    Your response should be structured with:
    - country_name: The name of the country
    - country_capital: The capital city name
    - capital_location: The coordinates of the capital city in "latitude,longitude" format
    - weather_api_key: The API key for the weather API by using tool "get_weather_api_key"
    """

    # Create a DynamicAgent instance with the custom result type
    agent = DynamicAgent(
        model_type="kimi",  # You can change this to your preferred model, for function call, use "kimi" or "chatgpt-4o-mini"
        system_prompt=system_prompt,
        result_type=CountryResponse,
        deps_type=Deps
    )

    # Register the tool using add_tool method
    agent.add_tool(get_weather_api_key, tool_type="tool")

    try:
        # Initialize the dependencies
        with Client() as client:
            myDeps = Deps(
                client=client,
                weather_api_key="123123",
                chat_history=agent.get_chat_history().copy()  # add the chat_history attribute
            )
            
            # Test with a sample query
            user_input = "Tell me about Argentina"
            
            response = agent.interact_with_model(user_input, deps=myDeps)

            # The response will be automatically validated against CountryResponse model
            print(f"Response for {user_input}:")
            print(f"Country Name: {response.country_name}")
            print(f"Capital: {response.country_capital}")
            print(f"Capital location: {response.capital_location}")
            print(f"Weather API Key: {response.weather_api_key}")

    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()
