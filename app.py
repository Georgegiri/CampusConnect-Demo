import streamlit as st
from datetime import time
from booking import Session, add_booking, booking_count, cancel_booking

st.set_page_config(page_title='CampusConnect Demo', page_icon='🎓', layout='wide')

SESSIONS = [
    Session('SQE-1000', 'Software Quality Engineering', 'Dr. Lee', time(10, 0), time(11, 0), 2),
    Session('LLM-1030', 'Large Language Models', 'Dr. Tan', time(10, 30), time(11, 30), 2),
    Session('CB-1130', 'Consumer Behaviour', 'Dr. Wong', time(11, 30), time(12, 30), 3),
]

if 'bookings' not in st.session_state:
    st.session_state.bookings = []

st.title('🎓 CampusConnect')
st.caption('Software Quality Engineering teaching demonstration')
st.info('Key quality rule: a student must not be allowed to hold overlapping consultation bookings.')
student = st.text_input('Student name', placeholder='e.g. Alex Tan')

st.subheader('Available consultations')
cols = st.columns(len(SESSIONS))
for col, session in zip(cols, SESSIONS):
    with col:
        used = booking_count(st.session_state.bookings, session.session_id)
        remaining = session.capacity - used
        st.markdown(f'### {session.subject}')
        st.write(f'**Lecturer:** {session.lecturer}')
        st.write(f'**Time:** {session.start.strftime("%H:%M")}-{session.end.strftime("%H:%M")}')
        st.write(f'**Places remaining:** {remaining}/{session.capacity}')
        if st.button('Book appointment', key=f'book-{session.session_id}', disabled=remaining <= 0, use_container_width=True):
            updated, ok, message = add_booking(student, session.session_id, SESSIONS, st.session_state.bookings)
            st.session_state.bookings = updated
            if ok:
                st.success(message)
            else:
                st.error(message)

st.divider()
st.subheader('My bookings')
if not student.strip():
    st.write('Enter a student name above to view bookings.')
else:
    mine = [b for b in st.session_state.bookings if b.student.casefold() == student.strip().casefold()]
    session_by_id = {s.session_id: s for s in SESSIONS}
    if not mine:
        st.write('No bookings yet.')
    for b in mine:
        s = session_by_id[b.session_id]
        left, right = st.columns([4, 1])
        with left:
            st.write(f'**{s.subject}** - {s.start.strftime("%H:%M")}-{s.end.strftime("%H:%M")}')
        with right:
            if st.button('Cancel', key=f'cancel-{student}-{s.session_id}', use_container_width=True):
                updated, ok, message = cancel_booking(student, s.session_id, st.session_state.bookings)
                st.session_state.bookings = updated
                if ok:
                    st.rerun()
                else:
                    st.error(message)

with st.expander('Teaching notes'):
    st.markdown('''
1. Book **Software Quality Engineering (10:00-11:00)**.
2. Try **Large Language Models (10:30-11:30)**. It should be rejected because it overlaps.
3. Book **Consumer Behaviour (11:30-12:30)**. It should be accepted.
4. Then open GitHub Actions and show the automated tests.
''')
