import streamlit as st
from datetime import time

from booking import (
    Booking,
    Session,
    WaitlistEntry,
    booking_count,
    cancel_and_promote,
    request_booking,
    waitlist_position,
)


st.set_page_config(
    page_title="CampusConnect Demo",
    page_icon="🎓",
    layout="wide",
)


SESSIONS = [
    Session(
        session_id="SQE-1000",
        subject="Software Quality Engineering",
        lecturer="Dr. Lee",
        start=time(10, 0),
        end=time(11, 0),
        capacity=2,
    ),
    Session(
        session_id="LLM-1030",
        subject="Large Language Models",
        lecturer="Dr. Tan",
        start=time(10, 30),
        end=time(11, 30),
        capacity=2,
    ),
    Session(
        session_id="CB-1130",
        subject="Consumer Behaviour",
        lecturer="Dr. Wong",
        start=time(11, 30),
        end=time(12, 30),
        capacity=3,
    ),
]


# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

if "bookings" not in st.session_state:
    st.session_state.bookings = []

if "waitlist" not in st.session_state:
    st.session_state.waitlist = []


# ---------------------------------------------------------
# PAGE HEADER
# ---------------------------------------------------------

st.title("🎓 CampusConnect")

st.caption(
    "Software Quality Engineering teaching demonstration — "
    "CR-001 Waitlist Version"
)

st.info(
    "Baseline quality rules remain active: "
    "booking capacity must be respected and students must not "
    "receive overlapping consultation bookings."
)


# ---------------------------------------------------------
# STUDENT
# ---------------------------------------------------------

student = st.text_input(
    "Student name",
    placeholder="e.g. Alex Tan",
    help="Enter a student name before making or cancelling a booking.",
)


# ---------------------------------------------------------
# AVAILABLE CONSULTATIONS
# ---------------------------------------------------------

st.subheader("Available consultations")

cols = st.columns(len(SESSIONS))

for col, session in zip(cols, SESSIONS):

    with col:

        used = booking_count(
            st.session_state.bookings,
            session.session_id,
        )

        places_left = session.capacity - used

        wait_count = sum(
            1
            for entry in st.session_state.waitlist
            if entry.session_id == session.session_id
        )

        st.markdown(f"### {session.subject}")

        st.write(f"**Lecturer:** {session.lecturer}")

        st.write(
            f"**Time:** "
            f"{session.start.strftime('%H:%M')}–"
            f"{session.end.strftime('%H:%M')}"
        )

        st.write(
            f"**Places remaining:** "
            f"{places_left}/{session.capacity}"
        )

        st.write(
            f"**Waitlist:** {wait_count}"
        )

        if places_left > 0:
            button_text = "Book appointment"
        else:
            button_text = "Join waitlist"

        if st.button(
            button_text,
            key=f"request-{session.session_id}",
            use_container_width=True,
        ):

            (
                updated_bookings,
                updated_waitlist,
                ok,
                message,
                status,
            ) = request_booking(
                student,
                session.session_id,
                SESSIONS,
                st.session_state.bookings,
                st.session_state.waitlist,
            )

            st.session_state.bookings = updated_bookings
            st.session_state.waitlist = updated_waitlist

            if ok:

                if status == "booked":
                    st.success(message)

                elif status == "waitlisted":
                    st.warning(message)

            else:
                st.error(message)


# ---------------------------------------------------------
# MY BOOKINGS
# ---------------------------------------------------------

st.divider()
st.subheader("My bookings")

student_bookings = [
    booking
    for booking in st.session_state.bookings
    if (
        student.strip()
        and booking.student.casefold()
        == student.strip().casefold()
    )
]

if not student.strip():

    st.write(
        "Enter a student name above to view bookings."
    )

elif not student_bookings:

    st.write("No confirmed bookings.")

else:

    session_by_id = {
        session.session_id: session
        for session in SESSIONS
    }

    for booking in student_bookings:

        session = session_by_id[
            booking.session_id
        ]

        left, right = st.columns([4, 1])

        with left:

            st.write(
                f"**{session.subject}** — "
                f"{session.start.strftime('%H:%M')}–"
                f"{session.end.strftime('%H:%M')}"
            )

        with right:

            if st.button(
                "Cancel",
                key=(
                    f"cancel-"
                    f"{student}-"
                    f"{session.session_id}"
                ),
                use_container_width=True,
            ):

                (
                    updated_bookings,
                    updated_waitlist,
                    ok,
                    message,
                    promoted_student,
                ) = cancel_and_promote(
                    student,
                    session.session_id,
                    SESSIONS,
                    st.session_state.bookings,
                    st.session_state.waitlist,
                )

                st.session_state.bookings = updated_bookings
                st.session_state.waitlist = updated_waitlist

                if ok:

                    if promoted_student:
                        st.success(
                            f"{message}"
                        )
                    else:
                        st.success(message)

                    st.rerun()

                else:
                    st.error(message)


# ---------------------------------------------------------
# MY WAITLIST STATUS
# ---------------------------------------------------------

st.divider()
st.subheader("My waitlist status")

if not student.strip():

    st.write(
        "Enter a student name above to view waitlist status."
    )

else:

    student_waitlist = [
        entry
        for entry in st.session_state.waitlist
        if (
            entry.student.casefold()
            == student.strip().casefold()
        )
    ]

    if not student_waitlist:

        st.write(
            "You are not currently on any waitlist."
        )

    else:

        session_by_id = {
            session.session_id: session
            for session in SESSIONS
        }

        for entry in student_waitlist:

            session = session_by_id[
                entry.session_id
            ]

            position = waitlist_position(
                student,
                entry.session_id,
                st.session_state.waitlist,
            )

            st.write(
                f"**{session.subject}** — "
                f"Waitlist position: **{position}**"
            )


# ---------------------------------------------------------
# DEMONSTRATION / TEACHING PANEL
# ---------------------------------------------------------

with st.expander(
    "Teaching demonstration"
):

    st.markdown(
        """
### Lifecycle demonstration

**Baseline V1.0**

The original system supported:

- normal bookings
- prevention of overlapping bookings
- capacity enforcement
- cancellation
- non-overlapping multiple bookings

---

### CR-001

A new requirement was introduced:

> When a consultation session is full, students should be
> able to join a waitlist.

The change also requires automatic promotion when a place
becomes available.

---

### Suggested classroom demonstration

1. Enter **Alex** and book Software Quality Engineering.
2. Enter **Jamie** and book the same session.
3. The session is now full.
4. Enter **Priya** and click **Join waitlist**.
5. Enter **Sam** and join the same waitlist.
6. Enter **Alex** and cancel the booking.
7. Priya should automatically be promoted.
8. View Priya's confirmed booking.
9. View Sam's waitlist position.

This demonstrates:

- baseline requirements
- controlled change
- impact analysis
- implementation
- regression testing
- deployment
- maintenance
"""
    )
