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


@dataclass(frozen=True)
class WaitlistEntry:
    student: str
    session_id: str


def overlaps(start_a: time, end_a: time, start_b: time, end_b: time) -> bool:
    """Return True when two time intervals overlap."""
    return start_a < end_b and start_b < end_a


def booking_count(bookings: List[Booking], session_id: str) -> int:
    return sum(1 for booking in bookings if booking.session_id == session_id)


def can_book(
    student: str,
    new_session: Session,
    sessions: List[Session],
    bookings: List[Booking],
) -> Tuple[bool, str]:

    student = student.strip()

    if not student:
        return False, "Please enter a student name."

    if booking_count(bookings, new_session.session_id) >= new_session.capacity:
        return False, "This consultation session is already full."

    session_by_id = {
        session.session_id: session
        for session in sessions
    }

    for booking in bookings:

        if booking.student.casefold() != student.casefold():
            continue

        existing = session_by_id[booking.session_id]

        if existing.session_id == new_session.session_id:
            return False, "You have already booked this consultation."

        if overlaps(
            existing.start,
            existing.end,
            new_session.start,
            new_session.end,
        ):
            return (
                False,
                f"Booking rejected: this overlaps with "
                f"{existing.subject} "
                f"({existing.start.strftime('%H:%M')}–"
                f"{existing.end.strftime('%H:%M')}).",
            )

    return True, "Booking accepted."


def add_booking(
    student: str,
    session_id: str,
    sessions: List[Session],
    bookings: List[Booking],
) -> Tuple[List[Booking], bool, str]:

    session_by_id = {
        session.session_id: session
        for session in sessions
    }

    if session_id not in session_by_id:
        return bookings, False, "Unknown consultation session."

    new_session = session_by_id[session_id]

    allowed, message = can_book(
        student,
        new_session,
        sessions,
        bookings,
    )

    if not allowed:
        return bookings, False, message

    return (
        bookings
        + [
            Booking(
                student=student.strip(),
                session_id=session_id,
            )
        ],
        True,
        message,
    )


def cancel_booking(
    student: str,
    session_id: str,
    bookings: List[Booking],
) -> Tuple[List[Booking], bool, str]:

    for index, booking in enumerate(bookings):

        if (
            booking.student.casefold()
            == student.strip().casefold()
            and booking.session_id == session_id
        ):
            updated = (
                bookings[:index]
                + bookings[index + 1:]
            )

            return updated, True, "Booking cancelled."

    return bookings, False, "No matching booking was found."


# ---------------------------------------------------------
# CR-001 WAITLIST FUNCTIONALITY
# ---------------------------------------------------------


def waitlist_position(
    student: str,
    session_id: str,
    waitlist: List[WaitlistEntry],
):

    relevant_entries = [
        entry
        for entry in waitlist
        if entry.session_id == session_id
    ]

    for position, entry in enumerate(relevant_entries, start=1):

        if entry.student.casefold() == student.strip().casefold():
            return position

    return None


def join_waitlist(
    student: str,
    session_id: str,
    waitlist: List[WaitlistEntry],
) -> Tuple[List[WaitlistEntry], bool, str]:

    student = student.strip()

    if not student:
        return waitlist, False, "Please enter a student name."

    existing_position = waitlist_position(
        student,
        session_id,
        waitlist,
    )

    if existing_position is not None:
        return (
            waitlist,
            False,
            f"You are already on the waitlist at position "
            f"{existing_position}.",
        )

    updated = waitlist + [
        WaitlistEntry(
            student=student,
            session_id=session_id,
        )
    ]

    position = waitlist_position(
        student,
        session_id,
        updated,
    )

    return (
        updated,
        True,
        f"Session full. Added to waitlist at position {position}.",
    )


def request_booking(
    student: str,
    session_id: str,
    sessions: List[Session],
    bookings: List[Booking],
    waitlist: List[WaitlistEntry],
):
    """
    Attempt to book a consultation.

    If there is capacity, create the booking.
    If the session is full, place the student on the waitlist.
    """

    session_by_id = {
        session.session_id: session
        for session in sessions
    }

    if session_id not in session_by_id:
        return (
            bookings,
            waitlist,
            False,
            "Unknown consultation session.",
            "error",
        )

    session = session_by_id[session_id]

    # If a space is available, use the normal booking rules.
    if booking_count(bookings, session_id) < session.capacity:

        updated_bookings, success, message = add_booking(
            student,
            session_id,
            sessions,
            bookings,
        )

        return (
            updated_bookings,
            waitlist,
            success,
            message,
            "booked" if success else "rejected",
        )

    # Session is full: offer the waitlist.
    updated_waitlist, success, message = join_waitlist(
        student,
        session_id,
        waitlist,
    )

    return (
        bookings,
        updated_waitlist,
        success,
        message,
        "waitlisted" if success else "rejected",
    )


def cancel_and_promote(
    student: str,
    session_id: str,
    sessions: List[Session],
    bookings: List[Booking],
    waitlist: List[WaitlistEntry],
):
    """
    Cancel a confirmed booking.

    If a place becomes available, promote the first eligible
    student from the waitlist.

    A student is only eligible if promotion does not create
    an overlapping booking.
    """

    updated_bookings, cancelled, message = cancel_booking(
        student,
        session_id,
        bookings,
    )

    if not cancelled:
        return (
            bookings,
            waitlist,
            False,
            message,
            None,
        )

    updated_waitlist = list(waitlist)

    # Examine waitlisted students in FIFO order.
    for index, entry in enumerate(updated_waitlist):

        if entry.session_id != session_id:
            continue

        candidate_bookings, allowed, candidate_message = add_booking(
            entry.student,
            session_id,
            sessions,
            updated_bookings,
        )

        if allowed:

            promoted_student = entry.student

            updated_bookings = candidate_bookings
            del updated_waitlist[index]

            return (
                updated_bookings,
                updated_waitlist,
                True,
                f"Booking cancelled. "
                f"{promoted_student} was promoted from the waitlist.",
                promoted_student,
            )

    return (
        updated_bookings,
        updated_waitlist,
        True,
        "Booking cancelled. No eligible waitlisted student was available.",
        None,
    )
