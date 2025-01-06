import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",  # Only allow local connections
        port=8080,
        reload=True,
        log_level="debug",
        timeout_keep_alive=65,
    )
