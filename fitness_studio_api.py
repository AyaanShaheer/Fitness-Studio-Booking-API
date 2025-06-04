import sqlite3
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import pytz
from uuid import uuid4
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Fitness Studio Booking API")

# Initialize SQLite in-memory database
def init_db():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE classes (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            datetime TEXT NOT NULL,
            instructor TEXT NOT NULL,
            available_slots INTEGER NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE bookings (
            id TEXT PRIMARY KEY,
            class_id TEXT NOT NULL,
            client_name TEXT NOT NULL,
            client_email TEXT NOT NULL,
            FOREIGN KEY (class_id) REFERENCES classes(id)
        )
    """)
    # Seed data
    seed_data = [
        (str(uuid4()), "Yoga", "2025-06-05 10:00:00", "Alice", 10),
        (str(uuid4()), "Zumba", "2025-06-05 12:00:00", "Bob", 15),
        (str(uuid4()), "HIIT", "2025-06-06 08:00:00", "Charlie", 8)
    ]
    cursor.executemany("INSERT INTO classes VALUES (?, ?, ?, ?, ?)", seed_data)
    conn.commit()
    return conn

conn = init_db()

# Pydantic models for request/response validation
class ClassResponse(BaseModel):
    id: str
    name: str
    datetime: str
    instructor: str
    available_slots: int

class BookingRequest(BaseModel):
    class_id: str
    client_name: str
    client_email: EmailStr

class BookingResponse(BaseModel):
    id: str
    class_id: str
    client_name: str
    client_email: str

# Helper function for timezone conversion
def convert_timezone(dt_str: str, target_tz: str) -> str:
    try:
        ist = pytz.timezone("Asia/Kolkata")
        target = pytz.timezone(target_tz)
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        dt_ist = ist.localize(dt)
        dt_target = dt_ist.astimezone(target)
        return dt_target.isoformat()
    except Exception as e:
        logger.error(f"Timezone conversion error: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid timezone or datetime format")

# API Endpoints
@app.get("/classes", response_model=List[ClassResponse])
async def get_classes(timezone: Optional[str] = Query("Asia/Kolkata")):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM classes WHERE datetime > ?", (datetime.now().isoformat(),))
        classes = []
        for row in cursor.fetchall():
            dt = convert_timezone(row[2], timezone)
            classes.append(ClassResponse(
                id=row[0], name=row[1], datetime=dt, instructor=row[3], available_slots=row[4]
            ))
        logger.info(f"Retrieved {len(classes)} classes")
        return classes
    except Exception as e:
        logger.error(f"Error retrieving classes: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/book", response_model=BookingResponse)
async def book_class(booking: BookingRequest):
    try:
        cursor = conn.cursor()
        # Check if class exists and has available slots
        cursor.execute("SELECT available_slots FROM classes WHERE id = ?", (booking.class_id,))
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Class not found")
        if result[0] <= 0:
            raise HTTPException(status_code=400, detail="No available slots")

        # Create booking
        booking_id = str(uuid4())
        cursor.execute(
            "INSERT INTO bookings (id, class_id, client_name, client_email) VALUES (?, ?, ?, ?)",
            (booking_id, booking.class_id, booking.client_name, booking.client_email)
        )
        # Reduce available slots
        cursor.execute("UPDATE classes SET available_slots = available_slots - 1 WHERE id = ?", (booking.class_id,))
        conn.commit()

        logger.info(f"Booking created: {booking_id}")
        return BookingResponse(
            id=booking_id,
            class_id=booking.class_id,
            client_name=booking.client_name,
            client_email=booking.client_email
        )
    except Exception as e:
        logger.error(f"Error creating booking: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/bookings", response_model=List[BookingResponse])
async def get_bookings(client_email: str):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bookings WHERE client_email = ?", (client_email,))
        bookings = [
            BookingResponse(id=row[0], class_id=row[1], client_name=row[2], client_email=row[3])
            for row in cursor.fetchall()
        ]
        logger.info(f"Retrieved {len(bookings)} bookings for {client_email}")
        return bookings
    except Exception as e:
        logger.error(f"Error retrieving bookings: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")