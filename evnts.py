from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

DB_PATH = "events.db"

class RSVPRequest(BaseModel):
    email: str

class EventResponse(BaseModel):
    name: str
    description: str | None
    remaining_seats: int
    registration_deadline: str
    registeredUsers: list[str]
    waitlistUsers: list[str]

class MessageResponse(BaseModel):
    message: str

def get_db():
    return sqlite3.connect(DB_PATH)

def initialize_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            remaining_seats INTEGER NOT NULL,
            registration_deadline TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rsvps (
            event_id INTEGER,
            email TEXT,
            status TEXT CHECK(status IN ('registered', 'waitlist')),
            PRIMARY KEY (event_id, email),
            FOREIGN KEY (event_id) REFERENCES events(id)
        )
    """)
    conn.commit()
    conn.close()



from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_db()
    add_sample_event()

    yield

app = FastAPI(lifespan=lifespan)

@app.get("/events/{event_id}", response_model=EventResponse)
def get_event(event_id: int):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT name, description, remaining_seats, registration_deadline FROM events WHERE id=?", (event_id,))
    event_row = cur.fetchone()
    if not event_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Event not found")

    cur.execute("SELECT email FROM rsvps WHERE event_id=? AND status='registered'", (event_id,))
    registered = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT email FROM rsvps WHERE event_id=? AND status='waitlist'", (event_id,))
    waitlist = [row[0] for row in cur.fetchall()]

    conn.close()
    return EventResponse(
        name=event_row[0],
        description=event_row[1],
        remaining_seats=event_row[2],
        registration_deadline=event_row[3],
        registeredUsers=registered,
        waitlistUsers=waitlist
    )

@app.post("/events/{event_id}/rsvp", response_model=MessageResponse)
def rsvp_event(event_id: int, req: RSVPRequest):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT status FROM rsvps WHERE event_id=? AND email=?", (event_id, req.email))
    if cur.fetchone():
        conn.close()
        return {"message": f"{req.email} already RSVPed."}

    cur.execute("SELECT remaining_seats FROM events WHERE id=?", (event_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Event not found")

    remaining_seats = row[0]
    if remaining_seats > 0:
        cur.execute("INSERT INTO rsvps VALUES (?, ?, 'registered')", (event_id, req.email))
        cur.execute("UPDATE events SET remaining_seats = remaining_seats - 1 WHERE id=?", (event_id,))
        msg = f"{req.email} registered successfully."
    else:
        cur.execute("INSERT INTO rsvps VALUES (?, ?, 'waitlist')", (event_id, req.email))
        msg = f"{req.email} added to waitlist."

    conn.commit()
    conn.close()
    return {"message": msg}

@app.post("/events/{event_id}/cancel", response_model=MessageResponse)
def cancel_rsvp(event_id: int, req: RSVPRequest):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT status FROM rsvps WHERE event_id=? AND email=?", (event_id, req.email))
    result = cur.fetchone()
    if not result:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    status = result[0]
    cur.execute("DELETE FROM rsvps WHERE event_id=? AND email=?", (event_id, req.email))
    promoted_msg = ""

    if status == "registered":
        cur.execute("UPDATE events SET remaining_seats = remaining_seats + 1 WHERE id=?", (event_id,))
        cur.execute("SELECT email FROM rsvps WHERE event_id=? AND status='waitlist' ORDER BY rowid ASC LIMIT 1", (event_id,))
        waitlisted = cur.fetchone()
        if waitlisted:
            promoted_email = waitlisted[0]
            cur.execute("UPDATE rsvps SET status='registered' WHERE event_id=? AND email=?", (event_id, promoted_email))
            cur.execute("UPDATE events SET remaining_seats = remaining_seats - 1 WHERE id=?", (event_id,))
            promoted_msg = f"{promoted_email} promoted from waitlist."

    conn.commit()
    conn.close()
    return {"message": f"{req.email} RSVP canceled. {promoted_msg}".strip()}
def add_sample_event():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Check if the event already exists
    cur.execute("SELECT COUNT(*) FROM events")
    if cur.fetchone()[0] == 0:
        cur.execute("""
            INSERT INTO events (name, description, remaining_seats, registration_deadline)
            VALUES (?, ?, ?, ?)
        """, ("IoT Workshop", "Learn about sensors and microcontrollers", 3, "2025-07-31"))
        conn.commit()

    conn.close()