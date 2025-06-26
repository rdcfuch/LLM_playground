from fastapi import FastAPI
from src.config.settings import load_settings
from src.api.routes import api_router
from src.mcp.server import start_mcp_server

app = FastAPI()

# Load configuration settings
settings = load_settings()

# Include API routes
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    # Start the MCP server in a separate thread
    start_mcp_server(settings.mcp_config)
    
    # Run the FastAPI application
    uvicorn.run(app, host=settings.host, port=settings.port)