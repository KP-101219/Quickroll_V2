# Quickroll V2 - Face Recognition Attendance System

> **Modern attendance tracking using face recognition technology**

![Version](https://img.shields.io/badge/version-2.0-blue) ![Python](https://img.shields.io/badge/python-3.8+-green) ![License](https://img.shields.io/badge/license-MIT-orange)

## 🎯 Overview

Quickroll V2 is a distributed face recognition attendance system with:
- **Backend API** - FastAPI server with face recognition engine
- **Desktop App** - Python GUI for local deployment
- **Web Interface** - Browser-based client (in development)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     QUICKROLL V2                        │
└─────────────────────────────────────────────────────────┘

┌──────────────┐              ┌──────────────┐
│   Desktop    │◄────HTTP────►│   Backend    │
│   Client     │              │   API Server │
│  (Python UI) │              │  (FastAPI)   │
└──────────────┘              └──────┬───────┘
                                     │
┌──────────────┐                     │
│     Web      │◄────HTTP────────────┘
│   Client     │
│ (React/Next) │
└──────────────┘

         Backend Components:
    ┌──────────────────────────┐
    │ Face Recognition Engine  │
    │ (OpenCV + SFace Model)   │
    ├──────────────────────────┤
    │ SQLite Database          │
    │ (Students & Attendance)  │
    └──────────────────────────┘
```

## 📁 Project Structure

```
Quickroll_V2/
│
├── backend/              # Backend Team
│   ├── api/             # REST API endpoints
│   ├── core/            # Face recognition logic
│   ├── data/            # Database manager
│   ├── models/          # AI models (ONNX)
│   ├── main.py          # FastAPI server
│   ├── requirements.txt
│   └── run_server.bat   # Start backend
│
├── desktop/             # Desktop Team
│   ├── ui/              # UI components
│   ├── services/        # API client
│   ├── requirements.txt
│   └── run.bat          # Start desktop app
│
├── web/                 # Web Team
│   ├── app/             # Next.js pages
│   ├── components/      # React components
│   ├── services/        # API client
│   └── README.md        # Web team guide
│
└── docs/                # Documentation
    ├── API.md           # API reference
    ├── SETUP.md         # Setup guide
    └── ARCHITECTURE.md  # System design
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Node.js 18+ (for web interface)
- Webcam

### 1. Backend Setup (Required)

```bash
cd backend
pip install -r requirements.txt
run_server.bat
```

Backend will start on `http://localhost:8000`

### 2. Desktop App Setup

```bash
cd desktop
pip install -r requirements.txt
run.bat
```

### 3. Web Interface Setup (Optional)

```bash
cd web
npm install
npm run dev
```

Web app will be on `http://localhost:3000`

## 👥 Team Assignments

### 🔧 Backend Team
**Responsibilities:**
- Maintain FastAPI server
- Optimize face recognition accuracy
- Database management
- API endpoint development

**Files:** `backend/`

### 🖥️ Desktop Team
**Responsibilities:**
- Python UI improvements
- Desktop app bug fixes
- User experience enhancements
- API client updates

**Files:** `desktop/`

### 🌐 Web Team
**Responsibilities:**
- Build React/Next.js frontend
- Create responsive web UI
- Implement webcam capture
- Design modern interface

**Files:** `web/`

## 🔑 Key Features

- ✅ Real-time face detection and recognition
- ✅ Multi-pose face enrollment (front, left, right)
- ✅ Confidence-based attendance marking
- ✅ SQLite database for data persistence
- ✅ Attendance history and reporting
- ✅ RESTful API for integration
- ✅ Desktop and Web interfaces

## 📡 API Endpoints

### Students
- `POST /api/students/register` - Register new student
- `GET /api/students/list` - Get all students
- `DELETE /api/students/{id}` - Delete student

### Recognition
- `POST /api/recognition/recognize` - Recognize face
- `POST /api/recognition/top-matches` - Get top matches

### Attendance
- `POST /api/attendance/mark` - Mark attendance
- `GET /api/attendance/history` - Get attendance logs
- `GET /api/attendance/today` - Today's attendance

See [docs/API.md](docs/API.md) for detailed documentation.

## 🛠️ Development Workflow

### For All Teams

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd Quickroll_V2
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes**
   - Backend team: Work in `backend/`
   - Desktop team: Work in `desktop/`
   - Web team: Work in `web/`

4. **Test Your Changes**
   - Ensure backend is running
   - Test your component thoroughly
   - Verify no breaking changes

5. **Commit and Push**
   ```bash
   git add .
   git commit -m "Add: your feature description"
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request**
   - Request review from team lead
   - Address feedback
   - Merge when approved

### Branch Naming Convention

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation
- `refactor/` - Code refactoring

## 📊 Database Schema

### Students Table
- `student_id` (TEXT, PRIMARY KEY)
- `name` (TEXT)
- `created_at` (TIMESTAMP)

### Embeddings Table
- `id` (INTEGER, PRIMARY KEY)
- `student_id` (TEXT, FOREIGN KEY)
- `embedding` (BLOB) - 128D face vector
- `pose` (TEXT) - front/left/right
- `created_at` (TIMESTAMP)

### Attendance Logs Table
- `id` (INTEGER, PRIMARY KEY)
- `student_id` (TEXT, FOREIGN KEY)
- `date` (TEXT)
- `time` (TEXT)
- `confidence` (REAL)
- `marked_by` (TEXT)
- `status` (TEXT)

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/
```

### Desktop Tests
```bash
cd desktop
python -m unittest discover tests/
```

### Manual Testing Checklist
- [ ] Register new student
- [ ] Recognize registered student
- [ ] Mark attendance
- [ ] View attendance history
- [ ] Delete student

## 📝 Documentation

- [API Documentation](docs/API.md) - Complete API reference
- [Setup Guide](docs/SETUP.md) - Detailed setup instructions
- [Architecture](docs/ARCHITECTURE.md) - System design details
- [Web Team Guide](web/README.md) - Web development guide

## 🤝 Contributing

We welcome contributions from all team members!

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

### Code Style

- **Python**: Follow PEP 8
- **JavaScript/TypeScript**: Use ESLint + Prettier
- **Commits**: Use conventional commit messages

## 🐛 Troubleshooting

### Backend won't start
- Check if port 8000 is already in use
- Verify all dependencies are installed
- Check Python version (3.8+)

### Desktop app can't connect
- Ensure backend server is running
- Check `http://localhost:8000/health`
- Verify firewall settings

### Face recognition not working
- Check camera permissions
- Ensure good lighting
- Verify face is clearly visible
- Check AI models are in `backend/models/`

## 📄 License

MIT License - See LICENSE file for details

## 👨‍💻 Team

- **Backend Team**: API & Core Logic
- **Desktop Team**: Python UI
- **Web Team**: React Frontend

## 🔗 Links

- API Docs: http://localhost:8000/docs (when server running)
- Desktop App: Run `desktop/run.bat`
- Web Interface: http://localhost:3000

---

**Built with ❤️ by the Quickroll V2 Team**

For questions or issues, please create a GitHub issue or contact your team lead.
