from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List
import sqlite3
import os

app = FastAPI()

# Set up static files and templates
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Database setup
def init_db():
    conn = sqlite3.connect('energy_management.db')
    cursor = conn.cursor()
    # Create tables
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT NOT NULL,
                        password_hash TEXT NOT NULL
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS devices (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        status TEXT NOT NULL,
                        energy_usage REAL NOT NULL
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS energy_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        device_id INTEGER NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        usage REAL NOT NULL,
                        FOREIGN KEY(device_id) REFERENCES devices(id)
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS recommendations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        description TEXT NOT NULL
                    )''')
    # Seed data
    cursor.execute("INSERT INTO users (name, email, password_hash) VALUES ('John Doe', 'john@example.com', 'hashedpassword')")
    cursor.execute("INSERT INTO devices (name, status, energy_usage) VALUES ('Light Bulb', 'off', 0.0)")
    cursor.execute("INSERT INTO recommendations (title, description) VALUES ('Turn off lights', 'Save energy by turning off lights when not in use.')")
    conn.commit()
    conn.close()

# Initialize database
if not os.path.exists('energy_management.db'):
    init_db()

# Models
class Device(BaseModel):
    id: int
    name: str
    status: str
    energy_usage: float

class EnergyRecord(BaseModel):
    id: int
    device_id: int
    timestamp: str
    usage: float

class Recommendation(BaseModel):
    id: int
    title: str
    description: str

# API Endpoints
@app.get("/api/devices", response_model=List[Device])
async def get_devices():
    conn = sqlite3.connect('energy_management.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM devices")
    devices = cursor.fetchall()
    conn.close()
    return [Device(id=row[0], name=row[1], status=row[2], energy_usage=row[3]) for row in devices]

@app.get("/api/energy-usage")
async def get_energy_usage():
    conn = sqlite3.connect('energy_management.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM energy_records ORDER BY timestamp DESC LIMIT 1")
    record = cursor.fetchone()
    conn.close()
    if record:
        return EnergyRecord(id=record[0], device_id=record[1], timestamp=record[2], usage=record[3])
    else:
        raise HTTPException(status_code=404, detail="No energy usage data found")

@app.get("/api/energy-history", response_model=List[EnergyRecord])
async def get_energy_history():
    conn = sqlite3.connect('energy_management.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM energy_records")
    records = cursor.fetchall()
    conn.close()
    return [EnergyRecord(id=row[0], device_id=row[1], timestamp=row[2], usage=row[3]) for row in records]

@app.post("/api/device-control")
async def control_device(device_id: int, status: str):
    conn = sqlite3.connect('energy_management.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE devices SET status = ? WHERE id = ?", (status, device_id))
    conn.commit()
    conn.close()
    return {"message": "Device status updated"}

@app.get("/api/recommendations", response_model=List[Recommendation])
async def get_recommendations():
    conn = sqlite3.connect('energy_management.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recommendations")
    recommendations = cursor.fetchall()
    conn.close()
    return [Recommendation(id=row[0], title=row[1], description=row[2]) for row in recommendations]

# HTML Endpoints
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/history", response_class=HTMLResponse)
async def history(request: Request):
    return templates.TemplateResponse("history.html", {"request": request})

@app.get("/devices", response_class=HTMLResponse)
async def devices(request: Request):
    return templates.TemplateResponse("devices.html", {"request": request})

@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})

@app.get("/recommendations", response_class=HTMLResponse)
async def recommendations(request: Request):
    return templates.TemplateResponse("recommendations.html", {"request": request})
