# DocuChat 🏴‍☠️

A modern document chat application that allows users to upload documents and have intelligent conversations with them using AI. Built with FastAPI backend and Next.js frontend.

## 🌐 Live Demo

- **Frontend (Vercel)**: [https://docu-chat-mu.vercel.app/](https://docu-chat-mu.vercel.app/)
- **Backend (Render)**: [https://docuchat-xurq.onrender.com/](https://docuchat-xurq.onrender.com/)
- **API Documentation**: [https://docuchat-xurq.onrender.com/docs](https://docuchat-xurq.onrender.com/docs)

## 🚀 Features

- **Document Upload**: Support for PDF files with intelligent text extraction
- **AI-Powered Chat**: Chat with your documents using Google Gemini AI
- **Session Management**: Persistent chat sessions with configurable TTL
- **Modern UI**: Beautiful, responsive interface built with Next.js and Tailwind CSS
- **Audio Support**: Speech-to-text capabilities with Sarvam AI integration
- **Real-time Processing**: Fast document processing and embedding generation

## 🏗️ Architecture

```
DocuChat/
├── backend/          # FastAPI Python backend
│   ├── app/         # Main application code
│   │   ├── routers/ # API endpoints
│   │   ├── services/ # Business logic
│   │   └── schemas/ # Pydantic models
│   └── requirements.txt
└── frontend/         # Next.js React frontend
    ├── app/         # Next.js app directory
    ├── components/  # React components
    └── package.json
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Google Gemini AI** - Large language model for chat
- **LangChain** - AI application framework
- **PyPDF2** - PDF text extraction
- **Uvicorn** - ASGI server

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS
- **Radix UI** - Accessible component primitives
- **React Hook Form** - Form handling

## 🚢 Getting Started

### Prerequisites

- **Python 3.11+** (for backend)
- **Node.js 18+** (for frontend)
- **Google Gemini API Key** (for AI chat)
- **Sarvam API Key** (optional, for audio features)

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   
   **Windows:**
   ```bash
   venv\Scripts\activate
   ```
   
   **macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**
   
   Create a `.env` file in the backend directory:
   ```env
   SESSION_TTL_SECONDS=3600
   MAX_FILE_MB=100
   EMBED_DIM=1024
   
   SARVAM_API_KEY=your_sarvam_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

6. **Start the backend server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:3000`

## 🔧 API Endpoints

### Core Endpoints
- `POST /upload` - Upload and process documents
- `POST /chat` - Send chat messages
- `GET /sessions` - List chat sessions
- `POST /sessions` - Create new session
- `GET /sessions/{session_id}` - Get session details
- `POST /summarize` - Generate document summaries

### Health Check
- `GET /health` - API health status

## 🐳 Docker Support

The project includes Docker configuration for easy deployment:

```bash
# Build and run with Docker Compose
docker-compose up --build
```

## 📝 Environment Variables

### Backend (.env)
| Variable | Description | Default |
|----------|-------------|---------|
| `SESSION_TTL_SECONDS` | Session timeout in seconds | `3600` |
| `MAX_FILE_MB` | Maximum file upload size | `100` |
| `EMBED_DIM` | Embedding dimensions | `1024` |
| `SARVAM_API_KEY` | Sarvam AI API key | Required for audio |
| `GEMINI_API_KEY` | Google Gemini API key | Required |

## 🧪 Development

### Backend Development
- The backend uses FastAPI with automatic API documentation
- Visit `http://localhost:8000/docs` for interactive API docs
- Code is organized with routers, services, and schemas

### Frontend Development
- Built with Next.js App Router
- Uses TypeScript for type safety
- Tailwind CSS for styling
- Radix UI components for accessibility

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Virtual environment not activating**
   - Ensure Python 3.11+ is installed
   - Check the activation script path

2. **API key errors**
   - Verify your Google Gemini API key is valid
   - Check environment variable names

3. **Port conflicts**
   - Backend runs on port 8000
   - Frontend runs on port 3000
   - Change ports if needed

4. **File upload issues**
   - Check file size limits
   - Ensure PDF files are not corrupted

---

**Ahoy! Welcome aboard the DocuChat ship! 🏴‍☠️**

For more help, check the API documentation or open an issue on GitHub.
