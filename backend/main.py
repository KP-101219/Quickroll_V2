"""
Quickroll V2 Backend API Server
FastAPI server providing RESTful endpoints for face recognition and attendance management.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import routes
from api import students, recognition, attendance, camera

app = FastAPI(
    title="Quickroll V2 API",
    description="Face Recognition Attendance System Backend",
    version="2.0.0"
)

# CORS middleware for web client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(students.router, prefix="/api/students", tags=["Students"])
app.include_router(recognition.router, prefix="/api/recognition", tags=["Recognition"])
app.include_router(attendance.router, prefix="/api/attendance", tags=["Attendance"])
app.include_router(camera.router, prefix="/api/camera", tags=["Camera"])

@app.get("/")
async def root():
    """Root endpoint - API status check"""
    return {
        "message": "Quickroll V2 Backend API",
        "version": "2.0.0",
        "status": "online"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
