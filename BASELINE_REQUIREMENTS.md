# CampusConnect Baseline Requirements

## Version
Baseline V1.0

## Purpose
CampusConnect is a university consultation booking system used to demonstrate
Software Quality Engineering concepts.

## Baseline Functional Requirements

### R1 - Create Booking
A student shall be able to book an available consultation session.

### R2 - Prevent Overlapping Bookings
A student shall not be permitted to hold consultation bookings whose times overlap.

Example:

- Existing booking: 10:00-11:00
- Requested booking: 10:30-11:30

The requested booking shall be rejected.

### R3 - Session Capacity
The system shall not allow the number of confirmed bookings to exceed
the capacity of a consultation session.

### R4 - Cancel Booking
A student shall be able to cancel an existing consultation booking.

### R5 - Non-Overlapping Bookings
A student shall be able to book multiple consultation sessions provided
their times do not overlap.

## Verification

The baseline requirements are verified by automated tests contained in:

test_booking.py

The tests are executed automatically through GitHub Actions whenever
changes are pushed to the main branch.

## Baseline Status

All five automated tests passed when Baseline V1.0 was established.
