from pydantic_ai import Agent, RunContext
from httpx import AsyncClient
import os

class Dependencies:
    client: AsyncClient
    weather_api_key: str

# Define the agent
agent = Agent(
    'openai:gpt-4o',
    deps_type=Dependencies
)

# Add tools
@agent.tool
async def get_lat_lng(ctx: RunContext, location: str) -> dict[str, float]:
    """Get latitude and longitude of a location."""
    if not ctx.deps.weather_api_key:
        return {"lat": 51.5074, "lng": -0.1278}  # Default to London
    response = await ctx.deps.client.get(f"https://api.example.com/geocode?q={location}")
    return response.json()

@agent.tool
async def get_weather(ctx: RunContext, lat: float, lng: float) -> dict:
    """Get weather data for a location."""
    response = await ctx.deps.client.get(
        f"https://api.example.com/weather?lat={lat}&lng={lng}&key={ctx.deps.weather_api_key}"
    )
    return response.json()

# Run the agent
if __name__ == '__main__':
    async with AsyncClient() as client:
        deps = Dependencies(client=client, weather_api_key=os.getenv("WEATHER_API_KEY"))
        result = await agent.run("What’s the weather in Boston?", deps=deps)
        print(result.data)