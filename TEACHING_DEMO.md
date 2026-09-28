# 10-minute CampusConnect teaching demo

## Working application
Book SQE at 10:00-11:00. Then try LLM at 10:30-11:30. The second booking must be rejected. Book Consumer Behaviour at 11:30-12:30; it should pass.

## Explain the pieces
- `app.py`: user interface
- `booking.py`: business rules
- `test_booking.py`: automated tests
- GitHub: stores the files
- GitHub Actions YAML: tells GitHub how to run the tests
- Ubuntu runner: executes the testing commands

## Continuous Integration
Every push to `main` triggers the automated test workflow.

## Deliberate defect
Temporarily change the `overlaps()` function in `booking.py` to `return False`, commit and push. The overlap test should fail. Restore the correct rule and push again.
