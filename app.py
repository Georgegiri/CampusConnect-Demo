import streamlit as st
from datetime import time

from booking import (
    Session,
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
# FIXED USERS
# =========================================================

STUDENTS = [
    "Alex Tan",
    "Jamie Lim",
    "Priya Rao",
    "Sam Lee",
    "Mei Chen",
    "Arjun Nair",
]

LECTURERS = [
    "Dr. Lee",
    "Dr. Tan",
    "Dr. Wong",
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
# SESSION STATE
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
        "All bookings and waitlists are empty.",
    )


def has_booking(student, session_id):
    return any(
        booking.student == student
        and booking.session_id == session_id
        for booking in st.session_state.bookings
    )


def is_waitlisted(student, session_id):
    return any(
        entry.student == student
        and entry.session_id == session_id
        for entry in st.session_state.waitlist
    )


def confirmed_students(session_id):
    return [
        booking.student
        for booking in st.session_state.bookings
        if booking.session_id == session_id
    ]


def waitlisted_students(session_id):
    return [
        entry.student
        for entry in st.session_state.waitlist
        if entry.session_id == session_id
    ]


# =========================================================
# HEADER
# =========================================================

st.title("🎓 CampusConnect")

st.caption(
    "University Consultation Booking System — "
    "Software Quality Engineering Demonstration"
)


# =========================================================
# SIDEBAR - ROLE SELECTION
# =========================================================

with st.sidebar:

    st.header("CampusConnect")

    role = st.radio(
        "Select role",
        [
            "Student",
            "Lecturer",
            "Administrator",
        ],
    )

    st.divider()

    if role == "Student":

        current_student = st.selectbox(
            "Select student",
            STUDENTS,
        )

        st.success(
            f"Student view: **{current_student}**"
        )

    elif role == "Lecturer":

        current_lecturer = st.selectbox(
            "Select lecturer",
            LECTURERS,
        )

        st.success(
            f"Lecturer view: **{current_lecturer}**"
        )

    else:

        st.success(
            "Administrator view"
        )

        if st.button(
            "🔄 Reset Entire System",
            use_container_width=True,
        ):
            reset_system()
            st.rerun()

    st.divider()

    st.caption("System Version")
    st.write("**CampusConnect V1.1**")
    st.write("CR-001: **Waitlist Support**")


# =========================================================
# LAST MESSAGE
# =========================================================

if st.session_state.last_message:

    message_type, message = st.session_state.last_message

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
# STUDENT VIEW
# =========================================================

if role == "Student":

    st.header(
        f"👨‍🎓 Student Portal — {current_student}"
    )

    st.info(
        "Students can view consultation sessions, "
        "make bookings, join waitlists and cancel "
        "their own bookings."
    )

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
        "Available Subjects",
        len(SESSIONS),
    )

    st.divider()
    st.subheader("Available Consultations")

    columns = st.columns(len(SESSIONS))

    for column, session in zip(
        columns,
        SESSIONS,
    ):

        with column:

            confirmed = confirmed_students(
                session.session_id
            )

            waiting = waitlisted_students(
                session.session_id
            )

            confirmed_count = len(confirmed)

            places_remaining = (
                session.capacity
                - confirmed_count
            )

            already_booked = has_booking(
                current_student,
                session.session_id,
            )

            already_waitlisted = is_waitlisted(
                current_student,
                session.session_id,
            )

            st.subheader(
                session.subject
            )

            st.write(
                f"**Lecturer:** "
                f"{session.lecturer}"
            )

            st.write(
                f"**Time:** "
                f"{session.start.strftime('%H:%M')}–"
                f"{session.end.strftime('%H:%M')}"
            )

            st.write(
                f"**Confirmed:** "
                f"{confirmed_count} / "
                f"{session.capacity}"
            )

            st.write(
                f"**Places remaining:** "
                f"{places_remaining}"
            )

            if places_remaining > 0:

                st.success(
                    f"{places_remaining} "
                    f"place(s) available"
                )

            else:

                st.error(
                    "SESSION FULL"
                )

            st.write(
                f"**Waitlist:** "
                f"{len(waiting)}"
            )

            if already_booked:

                st.success(
                    "✓ You are booked"
                )

            elif already_waitlisted:

                position = waitlist_position(
                    current_student,
                    session.session_id,
                    st.session_state.waitlist,
                )

                st.warning(
                    f"Waitlist position "
                    f"{position}"
                )

            elif places_remaining > 0:

                if st.button(
                    "Book Appointment",
                    key=(
                        f"book-"
                        f"{session.session_id}"
                    ),
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
                            f"{current_student} "
                            f"booked "
                            f"{session.subject}."
                        )

                        st.session_state.last_message = (
                            "success",
                            message,
                        )

                    else:

                        add_event(
                            f"Booking rejected for "
                            f"{current_student}: "
                            f"{message}"
                        )

                        st.session_state.last_message = (
                            "error",
                            message,
                        )

                    st.rerun()

            else:

                if st.button(
                    "Join Waitlist",
                    key=(
                        f"waitlist-"
                        f"{session.session_id}"
                    ),
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
                            f"{current_student} "
                            f"joined "
                            f"{session.subject} "
                            f"waitlist at "
                            f"position {position}."
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

    # -----------------------------------------------------
    # STUDENT CONFIRMED BOOKINGS
    # -----------------------------------------------------

    st.divider()
    st.subheader("My Confirmed Bookings")

    current_bookings = [
        booking
        for booking in st.session_state.bookings
        if booking.student == current_student
    ]

    if not current_bookings:

        st.write(
            "No confirmed bookings."
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

                st.write(
                    f"**{session.subject}**"
                )

                st.write(
                    f"{session.lecturer} | "
                    f"{session.start.strftime('%H:%M')}–"
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
                            f"{current_student} "
                            f"cancelled "
                            f"{session.subject}."
                        )

                        if promoted_student:

                            add_event(
                                f"{promoted_student} "
                                f"was automatically "
                                f"promoted from "
                                f"the waitlist."
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

    # -----------------------------------------------------
    # STUDENT WAITLIST
    # -----------------------------------------------------

    st.divider()
    st.subheader("My Waitlist Entries")

    current_waitlist = [
        entry
        for entry in st.session_state.waitlist
        if entry.student == current_student
    ]

    if not current_waitlist:

        st.write(
            "Not currently on any waitlist."
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
                f"Waitlist position "
                f"**{position}**"
            )


# =========================================================
# LECTURER VIEW
# =========================================================

elif role == "Lecturer":

    st.header(
        f"👩‍🏫 Lecturer Portal — "
        f"{current_lecturer}"
    )

    st.info(
        "Lecturers can view their own consultation "
        "sessions, confirmed students, capacity "
        "and waitlists."
    )

    lecturer_sessions = [
        session
        for session in SESSIONS
        if session.lecturer
        == current_lecturer
    ]

    if not lecturer_sessions:

        st.warning(
            "No consultation sessions assigned."
        )

    for session in lecturer_sessions:

        confirmed = confirmed_students(
            session.session_id
        )

        waiting = waitlisted_students(
            session.session_id
        )

        places_remaining = (
            session.capacity
            - len(confirmed)
        )

        st.subheader(
            session.subject
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Capacity",
            session.capacity,
        )

        c2.metric(
            "Confirmed",
            len(confirmed),
        )

        c3.metric(
            "Waitlisted",
            len(waiting),
        )

        st.write(
            f"**Consultation time:** "
            f"{session.start.strftime('%H:%M')}–"
            f"{session.end.strftime('%H:%M')}"
        )

        if places_remaining == 0:

            st.error(
                "Session is currently full."
            )

        else:

            st.success(
                f"{places_remaining} "
                f"place(s) available."
            )

        left, right = st.columns(2)

        with left:

            st.markdown(
                "### Confirmed Students"
            )

            if confirmed:

                for number, student in enumerate(
                    confirmed,
                    start=1,
                ):

                    st.write(
                        f"{number}. {student}"
                    )

            else:

                st.write(
                    "No confirmed students."
                )

        with right:

            st.markdown(
                "### Waitlist"
            )

            if waiting:

                for number, student in enumerate(
                    waiting,
                    start=1,
                ):

                    st.write(
                        f"{number}. {student}"
                    )

            else:

                st.write(
                    "No students on waitlist."
                )


# =========================================================
# ADMINISTRATOR VIEW
# =========================================================

else:

    st.header(
        "🛠️ Administrator Portal"
    )

    st.info(
        "Administrators can view the complete "
        "system state, activity history and "
        "software quality information."
    )

    total_capacity = sum(
        session.capacity
        for session in SESSIONS
    )

    total_bookings = len(
        st.session_state.bookings
    )

    total_waitlist = len(
        st.session_state.waitlist
    )

    a1, a2, a3, a4 = st.columns(4)

    a1.metric(
        "Students",
        len(STUDENTS),
    )

    a2.metric(
        "Sessions",
        len(SESSIONS),
    )

    a3.metric(
        "Confirmed Bookings",
        total_bookings,
    )

    a4.metric(
        "Waitlist Entries",
        total_waitlist,
    )

    st.divider()
    st.subheader("Live System State")

    for session in SESSIONS:

        confirmed = confirmed_students(
            session.session_id
        )

        waiting = waitlisted_students(
            session.session_id
        )

        with st.expander(
            f"{session.subject} | "
            f"{session.lecturer} | "
            f"{session.start.strftime('%H:%M')}–"
            f"{session.end.strftime('%H:%M')}",
            expanded=True,
        ):

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Capacity",
                session.capacity,
            )

            c2.metric(
                "Confirmed",
                len(confirmed),
            )

            c3.metric(
                "Waitlist",
                len(waiting),
            )

            left, right = st.columns(2)

            with left:

                st.markdown(
                    "### Confirmed Students"
                )

                if confirmed:

                    for student in confirmed:

                        st.write(
                            f"✅ {student}"
                        )

                else:

                    st.write(
                        "No confirmed bookings"
                    )

            with right:

                st.markdown(
                    "### Waitlist"
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

                    st.write(
                        "No waitlist"
                    )

    # -----------------------------------------------------
    # ACTIVITY LOG
    # -----------------------------------------------------

    st.divider()
    st.subheader("📋 Activity Log")

    if not st.session_state.event_log:

        st.write(
            "No system activity yet."
        )

    else:

        for event in (
            st.session_state.event_log
        ):

            st.write(
                f"• {event}"
            )

    # -----------------------------------------------------
    # QUALITY VIEW
    # -----------------------------------------------------

    st.divider()
    st.subheader(
        "🧪 Software Quality & Lifecycle"
    )

    q1, q2, q3 = st.columns(3)

    q1.metric(
        "Current Version",
        "V1.1",
    )

    q2.metric(
        "Automated Tests",
        "10 / 10",
    )

    q3.metric(
        "Open Change",
        "CR-001",
    )

    st.markdown(
        """
### Baseline V1.0

Original approved requirements:

- R1 — Book an available consultation
- R2 — Prevent overlapping bookings
- R3 — Enforce session capacity
- R4 — Allow cancellation
- R5 — Allow non-overlapping bookings

### Change Request CR-001

**Waitlist functionality**

When a consultation session is full:

- another student may join the waitlist
- waitlist order must be preserved
- a cancellation creates an available place
- the first eligible waitlisted student is promoted
- promotion must not create an overlapping booking

### Verification

Before CR-001 was merged:

- impact analysis was performed
- development occurred on a separate branch
- 5 baseline regression tests were retained
- 5 new CR-001 tests were added
- all 10 tests passed in GitHub Actions
- the Pull Request was approved and merged
- Streamlit deployed the updated version
"""
    )
