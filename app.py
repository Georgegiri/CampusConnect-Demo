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


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="CampusConnect",
    page_icon="🎓",
    layout="wide",
)


# =========================================================
# FIXED DEMONSTRATION USERS
# =========================================================

STUDENTS = [
    "Alex Tan",
    "Jamie Lim",
    "Priya Rao",
    "Sam Lee",
    "Mei Chen",
    "Arjun Nair",
]


# =========================================================
# CONSULTATION SESSIONS
# =========================================================

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


# =========================================================
# INITIAL SYSTEM STATE
# =========================================================

if "bookings" not in st.session_state:
    st.session_state.bookings = []

if "waitlist" not in st.session_state:
    st.session_state.waitlist = []

if "event_log" not in st.session_state:
    st.session_state.event_log = []

if "last_message" not in st.session_state:
    st.session_state.last_message = None


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def add_event(message):
    st.session_state.event_log.insert(0, message)


def reset_system():
    st.session_state.bookings = []
    st.session_state.waitlist = []
    st.session_state.event_log = []
    st.session_state.last_message = (
        "info",
        "CampusConnect has been reset. "
        "There are no bookings or waitlist entries.",
    )


def student_has_booking(student, session_id):
    return any(
        booking.student == student
        and booking.session_id == session_id
        for booking in st.session_state.bookings
    )


def student_is_waitlisted(student, session_id):
    return any(
        entry.student == student
        and entry.session_id == session_id
        for entry in st.session_state.waitlist
    )


# =========================================================
# HEADER
# =========================================================

st.title("🎓 CampusConnect")

st.caption(
    "University Consultation Booking System — "
    "Software Quality Engineering Demonstration"
)

st.info(
    "Select a student and create the booking scenario live. "
    "The system starts with no bookings and no waitlists."
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("CampusConnect")

    st.subheader("Current Student")

    current_student = st.selectbox(
        "Select student",
        STUDENTS,
        index=0,
    )

    st.success(
        f"Logged in as: **{current_student}**"
    )

    st.divider()

    if st.button(
        "🔄 Reset System",
        use_container_width=True,
    ):
        reset_system()
        st.rerun()

    st.divider()

    st.caption("Teaching Demo")
    st.write("Version: **V1.1**")
    st.write("Change: **CR-001 Waitlist**")
    st.write("Automated tests: **10 passed**")


# =========================================================
# LAST SYSTEM MESSAGE
# =========================================================

if st.session_state.last_message:

    message_type, message = (
        st.session_state.last_message
    )

    if message_type == "success":
        st.success(message)

    elif message_type == "warning":
        st.warning(message)

    elif message_type == "error":
        st.error(message)

    else:
        st.info(message)

    st.session_state.last_message = None


# =========================================================
# STUDENT DASHBOARD
# =========================================================

st.header(f"Student Dashboard — {current_student}")


current_bookings = [
    booking
    for booking in st.session_state.bookings
    if booking.student == current_student
]

current_waitlist = [
    entry
    for entry in st.session_state.waitlist
    if entry.student == current_student
]


m1, m2, m3 = st.columns(3)

m1.metric(
    "Confirmed Bookings",
    len(current_bookings),
)

m2.metric(
    "Waitlist Entries",
    len(current_waitlist),
)

m3.metric(
    "Consultation Sessions",
    len(SESSIONS),
)


# =========================================================
# CONSULTATIONS
# =========================================================

st.divider()
st.header("Available Consultations")

columns = st.columns(len(SESSIONS))


for column, session in zip(columns, SESSIONS):

    with column:

        confirmed_students = [
            booking.student
            for booking in st.session_state.bookings
            if booking.session_id == session.session_id
        ]

        waitlisted_students = [
            entry.student
            for entry in st.session_state.waitlist
            if entry.session_id == session.session_id
        ]

        places_used = len(confirmed_students)

        places_remaining = (
            session.capacity - places_used
        )

        already_booked = student_has_booking(
            current_student,
            session.session_id,
        )

        already_waitlisted = student_is_waitlisted(
            current_student,
            session.session_id,
        )


        st.subheader(session.subject)

        st.write(
            f"**Lecturer:** {session.lecturer}"
        )

        st.write(
            f"**Time:** "
            f"{session.start.strftime('%H:%M')}"
            f"–"
            f"{session.end.strftime('%H:%M')}"
        )

        st.write(
            f"**Capacity:** "
            f"{places_used}/{session.capacity}"
        )


        if places_remaining > 0:

            st.success(
                f"{places_remaining} place(s) available"
            )

        else:

            st.error("SESSION FULL")


        if waitlisted_students:

            st.warning(
                f"Waitlist: "
                f"{len(waitlisted_students)} student(s)"
            )

        else:

            st.write("Waitlist: 0")


        # ---------------------------------------------
        # STUDENT ALREADY BOOKED
        # ---------------------------------------------

        if already_booked:

            st.success("✓ You are booked")

            st.button(
                "Already booked",
                key=f"already-{session.session_id}",
                disabled=True,
                use_container_width=True,
            )


        # ---------------------------------------------
        # STUDENT ALREADY WAITLISTED
        # ---------------------------------------------

        elif already_waitlisted:

            position = waitlist_position(
                current_student,
                session.session_id,
                st.session_state.waitlist,
            )

            st.warning(
                f"You are waitlisted — "
                f"position {position}"
            )

            st.button(
                f"Waitlist position {position}",
                key=f"waiting-{session.session_id}",
                disabled=True,
                use_container_width=True,
            )


        # ---------------------------------------------
        # BOOKING AVAILABLE
        # ---------------------------------------------

        elif places_remaining > 0:

            if st.button(
                "Book Appointment",
                key=f"book-{session.session_id}",
                use_container_width=True,
            ):

                (
                    updated_bookings,
                    updated_waitlist,
                    ok,
                    message,
                    status,
                ) = request_booking(
                    current_student,
                    session.session_id,
                    SESSIONS,
                    st.session_state.bookings,
                    st.session_state.waitlist,
                )

                st.session_state.bookings = (
                    updated_bookings
                )

                st.session_state.waitlist = (
                    updated_waitlist
                )

                if ok:

                    add_event(
                        f"{current_student} booked "
                        f"{session.subject}."
                    )

                    st.session_state.last_message = (
                        "success",
                        message,
                    )

                else:

                    add_event(
                        f"Booking rejected for "
                        f"{current_student}: {message}"
                    )

                    st.session_state.last_message = (
                        "error",
                        message,
                    )

                st.rerun()


        # ---------------------------------------------
        # SESSION FULL → WAITLIST
        # ---------------------------------------------

        else:

            if st.button(
                "Join Waitlist",
                key=f"waitlist-{session.session_id}",
                use_container_width=True,
            ):

                (
                    updated_bookings,
                    updated_waitlist,
                    ok,
                    message,
                    status,
                ) = request_booking(
                    current_student,
                    session.session_id,
                    SESSIONS,
                    st.session_state.bookings,
                    st.session_state.waitlist,
                )

                st.session_state.bookings = (
                    updated_bookings
                )

                st.session_state.waitlist = (
                    updated_waitlist
                )

                if ok:

                    position = waitlist_position(
                        current_student,
                        session.session_id,
                        updated_waitlist,
                    )

                    add_event(
                        f"{current_student} joined "
                        f"{session.subject} waitlist "
                        f"at position {position}."
                    )

                    st.session_state.last_message = (
                        "warning",
                        message,
                    )

                else:

                    st.session_state.last_message = (
                        "error",
                        message,
                    )

                st.rerun()


# =========================================================
# MY CONFIRMED BOOKINGS
# =========================================================

st.divider()
st.header("My Confirmed Bookings")


if not current_bookings:

    st.write(
        f"{current_student} currently has "
        f"no confirmed bookings."
    )

else:

    session_lookup = {
        session.session_id: session
        for session in SESSIONS
    }


    for booking in current_bookings:

        session = session_lookup[
            booking.session_id
        ]

        left, right = st.columns(
            [4, 1]
        )

        with left:

            st.markdown(
                f"### {session.subject}"
            )

            st.write(
                f"{session.lecturer} | "
                f"{session.start.strftime('%H:%M')}"
                f"–"
                f"{session.end.strftime('%H:%M')}"
            )

        with right:

            if st.button(
                "Cancel Booking",
                key=(
                    f"cancel-"
                    f"{current_student}-"
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
                    current_student,
                    session.session_id,
                    SESSIONS,
                    st.session_state.bookings,
                    st.session_state.waitlist,
                )

                st.session_state.bookings = (
                    updated_bookings
                )

                st.session_state.waitlist = (
                    updated_waitlist
                )


                if ok:

                    add_event(
                        f"{current_student} cancelled "
                        f"{session.subject}."
                    )

                    if promoted_student:

                        add_event(
                            f"{promoted_student} was "
                            f"automatically promoted "
                            f"from the waitlist."
                        )

                    st.session_state.last_message = (
                        "success",
                        message,
                    )

                else:

                    st.session_state.last_message = (
                        "error",
                        message,
                    )

                st.rerun()


# =========================================================
# MY WAITLIST ENTRIES
# =========================================================

st.divider()
st.header("My Waitlist Entries")


if not current_waitlist:

    st.write(
        f"{current_student} is not currently "
        f"on any waitlist."
    )

else:

    session_lookup = {
        session.session_id: session
        for session in SESSIONS
    }


    for entry in current_waitlist:

        session = session_lookup[
            entry.session_id
        ]

        position = waitlist_position(
            current_student,
            entry.session_id,
            st.session_state.waitlist,
        )

        st.warning(
            f"**{session.subject}** — "
            f"Waitlist position **{position}**"
        )


# =========================================================
# LIVE SYSTEM STATE
# =========================================================

st.divider()
st.header("🔍 Live System State")

st.caption(
    "This view shows all confirmed bookings "
    "and waitlists in the system."
)


for session in SESSIONS:

    confirmed = [
        booking.student
        for booking in st.session_state.bookings
        if booking.session_id == session.session_id
    ]

    waiting = [
        entry.student
        for entry in st.session_state.waitlist
        if entry.session_id == session.session_id
    ]


    with st.expander(
        f"{session.subject} | "
        f"{session.start.strftime('%H:%M')}"
        f"–"
        f"{session.end.strftime('%H:%M')}",
        expanded=True,
    ):

        col1, col2 = st.columns(2)

        with col1:

            st.markdown(
                f"#### Confirmed "
                f"({len(confirmed)}/{session.capacity})"
            )

            if confirmed:

                for student in confirmed:

                    st.write(
                        f"✅ {student}"
                    )

            else:

                st.write("No bookings")


        with col2:

            st.markdown(
                f"#### Waitlist "
                f"({len(waiting)})"
            )

            if waiting:

                for number, student in enumerate(
                    waiting,
                    start=1,
                ):

                    st.write(
                        f"⏳ {number}. {student}"
                    )

            else:

                st.write("No waitlist")


# =========================================================
# EVENT LOG
# =========================================================

st.divider()
st.header("📋 Activity Log")


if not st.session_state.event_log:

    st.write(
        "No activity yet. "
        "Start by selecting a student and making a booking."
    )

else:

    for event in st.session_state.event_log:

        st.write(
            f"• {event}"
        )


# =========================================================
# TEACHING INFORMATION
# =========================================================

st.divider()

with st.expander(
    "🧪 Software Quality Lifecycle"
):

    st.markdown(
        """
### Baseline V1.0

The original system provided:

- student bookings
- overlap prevention
- capacity control
- cancellation
- multiple non-overlapping bookings

### Change Request CR-001

A new requirement was introduced:

> When a consultation session becomes full,
> additional students should be able to join a
> waitlist.

When a confirmed student cancels, the first
eligible waitlisted student should automatically
receive the available place.

### Verification

The system currently has:

- 5 original baseline regression tests
- 5 new CR-001 waitlist tests
- 10 automated tests in total

All tests passed before CR-001 was merged.
"""
    )
