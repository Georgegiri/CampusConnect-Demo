# CampusConnect Demo

A small browser-based application for demonstrating Software Quality Engineering concepts.

## Files
- `app.py` - Streamlit user interface
- `booking.py` - booking rules
- `test_booking.py` - automated regression tests
- `.github/workflows/quality-checks.yml` - GitHub Actions workflow

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Run tests
```bash
pytest -q
```

## Classroom demo
1. Enter `Alex`.
2. Book SQE 10:00-11:00.
3. Try LLM 10:30-11:30. It should be rejected.
4. Book Consumer Behaviour 11:30-12:30. It should be accepted.
5. Show the GitHub Actions test run.

Later, deliberately break the `overlaps()` rule in `booking.py` and push the change. The overlap test should fail. Restore the correct rule and the workflow should return to green.
