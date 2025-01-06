# Monica AI Assistant

A modern web application featuring a chat interface with various AI-powered generation capabilities.

## Features

- Interactive chat interface
- Multiple generation tools:
  - Translation
  - Calendar booking
  - Document generation
  - Mind map creation
  - Art generation
- Modern, responsive design
- FastAPI backend
- Real-time chat updates

## Project Structure

```
Monica_copy/
├── backend/
│   └── main.py
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── requirements.txt
└── README.md
```

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Start the backend server:
```bash
cd backend
uvicorn main:app --reload
```

3. Open the frontend:
Open `frontend/index.html` in your web browser or serve it using a local server.

## Development

- Backend runs on `http://localhost:8000`
- API documentation available at `http://localhost:8000/docs`
- Frontend communicates with backend via REST API

## API Endpoints

- `GET /`: Welcome message
- `POST /chat`: Send and receive chat messages
- `POST /generate/{type}`: Generate various types of content (document, mindmap, art, etc.)
