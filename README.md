## Project Structure

```
llm-agent/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── tools.py             # AI tools (game type, parameters, search)
│   ├── utils.py             # Utility functions and generation logic
│   ├── embeddings.py        # Vector embeddings for semantic search
│   ├── game_context.py      # Game parameter definitions
│   ├── state.py             # Application state management
│   ├── params.json          # Game parameter database
│   ├── system_prompt.md     # AI system prompt
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Main React component
│   │   └── main.tsx         # React entry point
│   ├── package.json         # Node.js dependencies
│   └── index.html           # HTML template
└── README.md                # This file
```

## Setup

### Backend Setup

   GEMINI_API_KEY=your_gemini_api_key_here
   and then
   uvicorn main:app --reload

### Frontend Setup

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**:
   ```bash
   npm run dev
   ```
