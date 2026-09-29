from datetime import time

from booking import (
    Booking,
    Session,
    WaitlistEntry,
    add_booking,
    cancel_and_promote,
    cancel_booking,
    request_booking,
)


SESSIONS = [
    Session(
        "SQE-1000",
        "Software Quality Engineering",
        "Dr. Lee",
        time(10, 0),
        time(11, 0),
        2,
    ),
    Session(
        "LLM-1030",
        "Large Language Models",
        "Dr. Tan",
        time(10, 30),
        time(11, 30),
        2,
    ),
    Session(
        "CB-1130",
        "Consumer Behaviour",
        "Dr. Wong",
        time(11, 30),
        time(12, 30),
        3,
    ),
]


# ---------------------------------------------------------
# BASELINE V1.0 REGRESSION TESTS
# ---------------------------------------------------------


def test_first_booking_is_accepted():
    bookings, ok, message = add_booking(
        "Alex",
        "SQE-1000",
        SESSIONS,
        [],
    )

    assert ok is True
    assert len(bookings) == 1
    assert message == "Booking accepted."


def test_overlapping_booking_is_rejected():
    bookings, ok, _ = add_booking(
        "Alex",
        "SQE-1000",
        SESSIONS,
        [],
    )

    assert ok is True

    bookings_after, ok, message = add_booking(
        "Alex",
        "LLM-1030",
        SESSIONS,
        bookings,
    )

    assert ok is False
    assert len(bookings_after) == 1
    assert "overlaps" in message.lower()


def test_non_overlapping_booking_is_accepted():
    bookings, ok, _ = add_booking(
        "Alex",
        "SQE-1000",
        SESSIONS,
        [],
    )

    assert ok is True

    bookings, ok, _ = add_booking(
        "Alex",
        "CB-1130",
        SESSIONS,
        bookings,
    )

    assert ok is True
    assert len(bookings) == 2


def test_capacity_is_enforced():
    bookings = [
        Booking("Alex", "SQE-1000"),
        Booking("Jamie", "SQE-1000"),
    ]

    bookings_after, ok, message = add_booking(
        "Priya",
        "SQE-1000",
        SESSIONS,
        bookings,
    )

    assert ok is False
    assert len(bookings_after) == 2
    assert "full" in message.lower()


def test_cancellation_releases_booking():
    bookings = [
        Booking("Alex", "SQE-1000"),
    ]

    bookings_after, ok, message = cancel_booking(
        "Alex",
        "SQE-1000",
        bookings,
    )

    assert ok is True
    assert bookings_after == []
    assert message == "Booking cancelled."


# ---------------------------------------------------------
# CR-001 WAITLIST TESTS
# ---------------------------------------------------------


def test_full_session_adds_student_to_waitlist():
    bookings = [
        Booking("Alex", "SQE-1000"),
        Booking("Jamie", "SQE-1000"),
    ]

    bookings_after, waitlist, ok, message, status = request_booking(
        "Priya",
        "SQE-1000",
        SESSIONS,
        bookings,
        [],
    )

    assert ok is True
    assert status == "waitlisted"
    assert len(bookings_after) == 2
    assert len(waitlist) == 1
    assert waitlist[0] == WaitlistEntry("Priya", "SQE-1000")
    assert "position 1" in message.lower()


def test_waitlist_order_is_preserved():
    bookings = [
        Booking("Alex", "SQE-1000"),
        Booking("Jamie", "SQE-1000"),
    ]

    waitlist = []

    _, waitlist, ok, _, _ = request_booking(
        "Priya",
        "SQE-1000",
        SESSIONS,
        bookings,
        waitlist,
    )

    assert ok is True

    _, waitlist, ok, _, _ = request_booking(
        "Sam",
        "SQE-1000",
        SESSIONS,
        bookings,
        waitlist,
    )

    assert ok is True

    assert waitlist == [
        WaitlistEntry("Priya", "SQE-1000"),
        WaitlistEntry("Sam", "SQE-1000"),
    ]


def test_cancellation_promotes_first_waitlisted_student():
    bookings = [
        Booking("Alex", "SQE-1000"),
        Booking("Jamie", "SQE-1000"),
    ]

    waitlist = [
        WaitlistEntry("Priya", "SQE-1000"),
        WaitlistEntry("Sam", "SQE-1000"),
    ]

    bookings_after, waitlist_after, ok, message, promoted = cancel_and_promote(
        "Alex",
        "SQE-1000",
        SESSIONS,
        bookings,
        waitlist,
    )

    assert ok is True
    assert promoted == "Priya"
    assert Booking("Priya", "SQE-1000") in bookings_after
    assert len(bookings_after) == 2
    assert waitlist_after == [
        WaitlistEntry("Sam", "SQE-1000"),
    ]
    assert "Priya" in message


def test_waitlist_promotion_does_not_exceed_capacity():
    bookings = [
        Booking("Alex", "SQE-1000"),
        Booking("Jamie", "SQE-1000"),
    ]

    waitlist = [
        WaitlistEntry("Priya", "SQE-1000"),
    ]

    bookings_after, waitlist_after, ok, _, promoted = cancel_and_promote(
        "Alex",
        "SQE-1000",
        SESSIONS,
        bookings,
        waitlist,
    )

    assert ok is True
    assert promoted == "Priya"
    assert len(bookings_after) == 2
    assert waitlist_after == []


def test_ineligible_waitlisted_student_is_skipped():
    bookings = [
        Booking("Alex", "SQE-1000"),
        Booking("Jamie", "SQE-1000"),

        # Priya already has an overlapping session.
        Booking("Priya", "LLM-1030"),
    ]

    waitlist = [
        WaitlistEntry("Priya", "SQE-1000"),
        WaitlistEntry("Sam", "SQE-1000"),
    ]

    bookings_after, waitlist_after, ok, message, promoted = cancel_and_promote(
        "Alex",
        "SQE-1000",
        SESSIONS,
        bookings,
        waitlist,
    )

    assert ok is True
    assert promoted == "Sam"

    assert Booking("Sam", "SQE-1000") in bookings_after
    assert Booking("Priya", "SQE-1000") not in bookings_after

    # Priya remains on the waitlist because she is currently ineligible.
    assert waitlist_after == [
        WaitlistEntry("Priya", "SQE-1000"),
    ]

    assert "Sam" in message
