from dataclasses import dataclass
from datetime import time
from typing import List, Tuple

@dataclass(frozen=True)
class Session:
    session_id: str
    subject: str
    lecturer: str
    start: time
    end: time
    capacity: int

@dataclass(frozen=True)
class Booking:
    student: str
    session_id: str

def overlaps(start_a: time, end_a: time, start_b: time, end_b: time) -> bool:
    return start_a < end_b and start_b < end_a

def booking_count(bookings: List[Booking], session_id: str) -> int:
    return sum(1 for b in bookings if b.session_id == session_id)

def can_book(student: str, new_session: Session, sessions: List[Session], bookings: List[Booking]) -> Tuple[bool, str]:
    student = student.strip()
    if not student:
        return False, 'Please enter a student name.'
    if booking_count(bookings, new_session.session_id) >= new_session.capacity:
        return False, 'This consultation session is already full.'
    session_by_id = {s.session_id: s for s in sessions}
    for b in bookings:
        if b.student.casefold() != student.casefold():
            continue
        existing = session_by_id[b.session_id]
        if existing.session_id == new_session.session_id:
            return False, 'You have already booked this consultation.'
        if overlaps(existing.start, existing.end, new_session.start, new_session.end):
            return False, f'Booking rejected: this overlaps with {existing.subject} ({existing.start.strftime("%H:%M")}-{existing.end.strftime("%H:%M")}).'
    return True, 'Booking accepted.'

def add_booking(student: str, session_id: str, sessions: List[Session], bookings: List[Booking]):
    session_by_id = {s.session_id: s for s in sessions}
    if session_id not in session_by_id:
        return bookings, False, 'Unknown consultation session.'
    allowed, message = can_book(student, session_by_id[session_id], sessions, bookings)
    if not allowed:
        return bookings, False, message
    return bookings + [Booking(student.strip(), session_id)], True, message

def cancel_booking(student: str, session_id: str, bookings: List[Booking]):
    for i, b in enumerate(bookings):
        if b.student.casefold() == student.strip().casefold() and b.session_id == session_id:
            return bookings[:i] + bookings[i+1:], True, 'Booking cancelled.'
    return bookings, False, 'No matching booking was found.'
