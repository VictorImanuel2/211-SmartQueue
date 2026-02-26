# SmartQueue Web App (IS-211 Spring 2026)

A prototype digital queue management system for public offices, featuring a Python backend (`deque`, `heapq`) and a simple web frontend (`Flask`, `JS`, `CSS`).

## Features

- **Customer Kiosk**: Simple form to fetch a ticket (Normal or Priority).
- **Live Status**: Check your position and estimated wait time by Ticket ID.
- **Admin Desk**: Serve the next customer (Priority First logic).
- **Analytics**: Real-time average wait time stats sorted by service ($O(n \log n)$).

## Project Structure

- `app.py`: Flask web server and API endpoints.
- `smartqueue/`: Core backend logic (QueueManager, Models).
- `templates/`: HTML frontend.
- `static/`: CSS and JS assets.
- `tests/`: Unit tests for backend logic.

## Prerequisites

You need Python 3 and Flask installed.

```bash
pip install flask
```

## How to Run

1. Start the server:
   ```bash
   python3 app.py
   ```
2. Open your browser and go to:
   [http://127.0.0.1:5000](http://127.0.0.1:5000)

## How to Run Tests

Run the backend unit tests:

```bash
python3 -m unittest discover tests
```
