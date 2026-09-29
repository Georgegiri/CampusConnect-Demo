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
    page_title="CampusConnect Teaching Edition",
    page_icon="🎓",
    layout="wide",
)


# =========================================================
# FIXED DEMONSTRATION DATA
# =========================================================

STUDENTS = [
    "Alex Tan",
    "Jamie Lim",
    "Priya Rao",
    "Sam Lee",
    "Mei Chen",
    "Arjun Nair",
]


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


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def log_event(message):
    st.session_state.event_log.insert(0, message)


def reset_demo():
    st.session_state.bookings = []
    st.session_state.waitlist = []
    st.session_state.event_log = [
        "Demo reset. All bookings and waitlists cleared."
    ]


def load_waitlist_scenario():
    st.session_state.bookings = [
        Booking("Alex Tan", "SQE-1000"),
        Booking("Jamie Lim", "SQE-1000"),
        Booking("Mei Chen", "CB-1130"),
    ]

    st.session_state.waitlist = [
        WaitlistEntry("Priya Rao", "SQE-1000"),
        WaitlistEntry("Sam Lee", "SQE-1000"),
    ]

    st.session_state.event_log = [
        "Priya Rao joined SQE waitlist at position 1.",
        "Sam Lee joined SQE waitlist at position 2.",
        "Jamie Lim booked Software Quality Engineering.",
        "Alex Tan booked Software Quality Engineering.",
        "Teaching scenario loaded.",
    ]


# =========================================================
# HEADER
# =========================================================

st.title("🎓 CampusConnect")

st.caption(
    "Software Quality Engineering — Teaching Edition"
)

st.info(
    "Current version demonstrates baseline booking rules, "
    "waitlisting, automatic promotion and regression protection."
)


# =========================================================
# SIDEBAR DEMO CONTROLS
# =========================================================

with st.sidebar:

    st.header("🎬 Demo Controls")

    current_student = st.selectbox(
        "Current student",
        STUDENTS,
    )

    st.divider()

    if st.button(
        "Load Waitlist Scenario",
        use_container_width=True,
    ):
        load_waitlist_scenario()
        st.rerun()

    if st.button(
        "Reset Demo",
        use_container_width=True,
    ):
        reset_demo()
        st.rerun()

    st.divider()

    st.subheader("Current Version")
    st.write("**CampusConnect V1.1**")

    st.write("Change Request:")
    st.code("CR-001 — Waitlist Support")

    st.write("Automated tests:")
    st.success("10 tests passed")


# =========================================================
# STUDENT VIEW
# =========================================================

st.header(f"Student View — {current_student}")

student_bookings = [
    booking
    for booking in st.session_state.bookings
    if booking.student == current_student
]

student_waitlist = [
    entry
    for entry in st.session_state.waitlist
    if entry.student == current_student
]


metric1, metric2, metric3 = st.columns(3)

metric1.metric(
    "Confirmed bookings",
    len(student_bookings),
)

metric2.metric(
    "Waitlist entries",
    len(student_waitlist),
)

metric3.metric(
    "Available sessions",
    len(SESSIONS),
)


# =========================================================
# CONSULTATION CARDS
# =========================================================

st.subheader("Available Consultations")

cols = st.columns(len(SESSIONS))


for col, session in zip(cols, SESSIONS):

    with col:

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

        used = len(confirmed)
        places_left = session.capacity - used

        st.markdown(f"### {session.subject}")

        st.write(f"**Lecturer:** {session.lecturer}")

        st.write(
            f"**Time:** "
            f"{session.start.strftime('%H:%M')}–"
            f"{session.end.strftime('%H:%M')}"
        )

        if places_left > 0:
            st.success(
                f"{places_left} of {session.capacity} places available"
            )
        else:
            st.error(
                f"FULL — {session.capacity}/{session.capacity}"
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
                current_student,
                session.session_id,
                SESSIONS,
                st.session_state.bookings,
                st.session_state.waitlist,
            )

            st.session_state.bookings = updated_bookings
            st.session_state.waitlist = updated_waitlist

            if ok:

                if status == "booked":
                    log_event(
                        f"{current_student} booked "
                        f"{session.subject}."
                    )

                elif status == "waitlisted":
                    position = waitlist_position(
                        current_student,
                        session.session_id,
                        updated_waitlist,
                    )

                    log_event(
                        f"{current_student} joined "
                        f"{session.subject} waitlist "
                        f"at position {position}."
                    )

            else:

                log_event(
                    f"{current_student}: {message}"
                )

            st.session_state["last_message"] = (
                ok,
                message,
                status,
            )

            st.rerun()


# =========================================================
# DISPLAY LAST ACTION
# =========================================================

if "last_message" in st.session_state:

    ok, message, status = st.session_state.pop(
        "last_message"
    )

    if ok and status == "booked":
        st.success(message)

    elif ok and status == "waitlisted":
        st.warning(message)

    else:
        st.error(message)


# =========================================================
# CURRENT STUDENT BOOKINGS
# =========================================================

st.divider()
st.subheader(f"{current_student}'s Confirmed Bookings")


if not student_bookings:

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
                f"**{session.subject}** "
                f"({session.start.strftime('%H:%M')}–"
                f"{session.end.strftime('%H:%M')})"
            )

        with right:

            if st.button(
                "Cancel",
                key=f"cancel-{current_student}-{session.session_id}",
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

                st.session_state.bookings = updated_bookings
                st.session_state.waitlist = updated_waitlist

                log_event(
                    f"{current_student} cancelled "
                    f"{session.subject}."
                )

                if promoted_student:

                    log_event(
                        f"{promoted_student} automatically "
                        f"promoted from the waitlist."
                    )

                st.session_state["last_message"] = (
                    True,
                    message,
                    "booked",
                )

                st.rerun()


# =========================================================
# WAITLIST STATUS
# =========================================================

st.subheader(f"{current_student}'s Waitlist Status")


if not student_waitlist:

    st.write("Not currently on a waitlist.")

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
            current_student,
            entry.session_id,
            st.session_state.waitlist,
        )

        st.warning(
            f"{session.subject} — "
            f"Waitlist position {position}"
        )


# =========================================================
# SYSTEM STATE
# =========================================================

st.divider()
st.header("🔍 System State")

st.caption(
    "This section lets students see what is happening "
    "behind the user interface."
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
        f"{session.subject} "
        f"({session.start.strftime('%H:%M')}–"
        f"{session.end.strftime('%H:%M')})",
        expanded=True,
    ):

        left, right = st.columns(2)

        with left:

            st.markdown("#### Confirmed Students")

            if confirmed:

                for student in confirmed:
                    st.write(f"✅ {student}")

            else:
                st.write("None")

        with right:

            st.markdown("#### Waitlist")

            if waiting:

                for number, student in enumerate(
                    waiting,
                    start=1,
                ):
                    st.write(
                        f"⏳ {number}. {student}"
                    )

            else:
                st.write("None")


# =========================================================
# EVENT LOG
# =========================================================

st.divider()
st.header("📋 System Event Log")

if not st.session_state.event_log:

    st.write("No events recorded yet.")

else:

    for event in st.session_state.event_log:
        st.write(f"• {event}")


# =========================================================
# QUALITY / LIFECYCLE VIEW
# =========================================================

st.divider()

with st.expander(
    "🧪 Software Quality & Lifecycle View"
):

    st.markdown(
        """
### Baseline V1.0

Original approved requirements:

- R1 — Create an available booking
- R2 — Prevent overlapping bookings
- R3 — Enforce capacity
- R4 — Allow cancellation
- R5 — Allow non-overlapping bookings

### Change Request CR-001

**Requested change:**

When a session is full, students should be able to
join a waitlist.

When a confirmed booking is cancelled, the first
eligible waitlisted student should automatically
receive the available place.

### Quality controls

Before CR-001 was merged:

- impact analysis was performed
- development occurred on a separate branch
- five new waitlist tests were added
- five original baseline regression tests were retained
- all ten automated tests passed
- the change was reviewed through a Pull Request
- the change was merged into `main`
- Streamlit automatically deployed the new version

### Result

V1.1 became the new approved baseline.
"""
    )
