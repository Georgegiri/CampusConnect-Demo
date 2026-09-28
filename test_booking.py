from datetime import time
from booking import Booking, Session, add_booking, cancel_booking

SESSIONS = [
    Session('SQE-1000', 'Software Quality Engineering', 'Dr. Lee', time(10, 0), time(11, 0), 2),
    Session('LLM-1030', 'Large Language Models', 'Dr. Tan', time(10, 30), time(11, 30), 2),
    Session('CB-1130', 'Consumer Behaviour', 'Dr. Wong', time(11, 30), time(12, 30), 3),
]

def test_first_booking_is_accepted():
    bookings, ok, _ = add_booking('Alex', 'SQE-1000', SESSIONS, [])
    assert ok and len(bookings) == 1

def test_overlapping_booking_is_rejected():
    bookings, ok, _ = add_booking('Alex', 'SQE-1000', SESSIONS, [])
    assert ok
    after, ok, message = add_booking('Alex', 'LLM-1030', SESSIONS, bookings)
    assert not ok and len(after) == 1 and 'overlaps' in message.lower()

def test_non_overlapping_booking_is_accepted():
    bookings, ok, _ = add_booking('Alex', 'SQE-1000', SESSIONS, [])
    assert ok
    bookings, ok, _ = add_booking('Alex', 'CB-1130', SESSIONS, bookings)
    assert ok and len(bookings) == 2

def test_capacity_is_enforced():
    bookings = [Booking('Alex', 'SQE-1000'), Booking('Jamie', 'SQE-1000')]
    after, ok, message = add_booking('Priya', 'SQE-1000', SESSIONS, bookings)
    assert not ok and len(after) == 2 and 'full' in message.lower()

def test_cancellation_releases_booking():
    after, ok, message = cancel_booking('Alex', 'SQE-1000', [Booking('Alex', 'SQE-1000')])
    assert ok and after == [] and message == 'Booking cancelled.'
