# Quickroll V2 - Web Frontend

## 🚀 Getting Started (For Web Team)

This is the web interface for Quickroll V2. The backend API is already running, and you'll build the frontend to connect to it.

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

### Setup Instructions

1. **Initialize Next.js Project** (First time only):
   ```bash
   cd web
   npx create-next-app@latest . --typescript --tailwind --app --no-src-dir
   ```

2. **Install Dependencies**:
   ```bash
   npm install
   ```

3. **Start Development Server**:
   ```bash
   npm run dev
   ```

4. **Access the App**:
   Open [http://localhost:3000](http://localhost:3000)

### Project Structure

```
web/
├── app/                    # Next.js 14 App Router
│   ├── page.tsx           # Home page
│   ├── register/          # Student registration page
│   ├── attendance/        # Attendance tracking page
│   ├── dashboard/         # Dashboard page
│   └── layout.tsx         # Root layout
├── components/            # Reusable React components
│   ├── FaceCapture.tsx   # Webcam capture component
│   ├── StudentCard.tsx   # Student display card
│   └── AttendanceTable.tsx
├── services/              # API communication
│   └── api.ts            # Backend API client
├── public/               # Static assets
└── package.json
```

### Backend API Endpoints

Your web app should call these endpoints (all at `http://localhost:8000`):

#### Students
- `POST /api/students/register` - Register new student
- `GET /api/students/list` - Get all students
- `DELETE /api/students/{id}` - Delete student

#### Recognition
- `POST /api/recognition/recognize` - Recognize face
- `POST /api/recognition/top-matches` - Get top matches

#### Attendance
- `POST /api/attendance/mark` - Mark attendance
- `GET /api/attendance/history?date=YYYY-MM-DD` - Get history
- `GET /api/attendance/today` - Get today's records

#### Camera
- `GET /api/camera/list` - List available cameras

### Tech Stack Recommendations

- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS (already configured)
- **State Management**: React Context or Zustand
- **API Calls**: Native fetch or axios
- **Webcam**: `react-webcam` package
- **UI Components**: shadcn/ui or custom components

### Sample API Service (services/api.ts)

```typescript
const API_BASE = 'http://localhost:8000';

export async function getStudents() {
  const response = await fetch(`${API_BASE}/api/students/list`);
  return response.json();
}

export async function registerStudent(formData: FormData) {
  const response = await fetch(`${API_BASE}/api/students/register`, {
    method: 'POST',
    body: formData,
  });
  return response.json();
}

export async function recognizeFace(imageBlob: Blob) {
  const formData = new FormData();
  formData.append('image', imageBlob);
  
  const response = await fetch(`${API_BASE}/api/recognition/recognize`, {
    method: 'POST',
    body: formData,
  });
  return response.json();
}
```

### Key Features to Implement

1. **Student Registration Page**
   - Form for student ID and name
   - Webcam capture for 3 face poses
   - Upload to backend API

2. **Attendance Mode Page**
   - Live webcam feed
   - Face recognition on capture
   - Display recognized student with confidence
   - Mark attendance automatically for high confidence

3. **Dashboard/Management Page**
   - View all registered students
   - View attendance history
   - Filter by date
   - Delete students

4. **Responsive Design**
   - Mobile-friendly layouts
   - Works on tablets and desktops

### Design Guidelines

- Use modern, clean UI with good color contrast
- Follow the desktop app's color scheme if possible
- Add animations for better UX
- Show loading states for API calls
- Handle errors gracefully with user-friendly messages

### Testing Checklist

- [ ] Can register new student with photos
- [ ] Can view list of students
- [ ] Can take attendance with webcam
- [ ] Attendance shows in history
- [ ] Can filter attendance by date
- [ ] Can delete students
- [ ] Mobile responsive
- [ ] Error handling works

### Need Help?

- Check `../docs/API.md` for complete API documentation
- Desktop app is in `../desktop/ui/` for reference
- Backend code is in `../backend/`

### Team Collaboration

- Work in feature branches
- Test against local backend before committing
- Document any new components you create
- Keep commits focused and atomic

---

**Happy Coding! 🎉**

For questions, refer to the main README or contact the backend team.
