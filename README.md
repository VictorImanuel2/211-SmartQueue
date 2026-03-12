# NoQ Web App (IS-211 Spring 2026)

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

---

## Where AI Was Used

We used AI assistants (GitHub Copilot and ChatGPT) during development in the following areas:

| Where | What AI helped with | How we used it |
|-------|--------------------|-----------------|
| `smartqueue/queues.py` — `issue_ticket()` | Designing the dual deque + heap approach and the `(-priority, counter)` max-heap trick | Asked Copilot to suggest a data structure that supports both FIFO and priority ordering; adopted the pattern and wrote the surrounding logic by hand |
| `smartqueue/queues.py` — `serve_next()` | The "drain priority heap first, fall back to deque" serving pattern | Described the requirement to ChatGPT and used the suggested control flow |
| `smartqueue/analytics.py` — `rank_services_by_avg_wait()` | Generating the initial function body | Prompted Copilot with the function signature and a one-line description; reviewed and adjusted the output |
| `tests/test_queue_manager.py` | Scaffolding the unit test cases | Described the expected behaviors (FIFO, priority skip, position calculation) and let Copilot generate the test methods, then refined assertions |
| `static/script.js` | Async fetch boilerplate for all four API calls | Gave ChatGPT the API endpoint specs and had it produce the `async/await` fetch functions; adapted element IDs and error handling |
| `static/style.css` | Initial card/grid layout and CSS custom properties | Used Copilot to generate a minimal design-system (variables, card styles, responsive grid) as a starting point |

In every case, the AI output was **reviewed, tested, and modified** before being committed. AI was not used to write the core algorithmic logic from scratch — it served as a productivity tool for boilerplate, patterns, and scaffolding.

---

## Using AI with This Project

This codebase is documented with AI-friendly comments in the key source files. Each module header explains what the file does, how it fits into the architecture, and the design decisions behind it. Below is a quick map and a set of representative prompts you can feed to an AI assistant (GitHub Copilot, ChatGPT, etc.) to get useful help.

### Architecture at a Glance

| Layer | Files | Purpose |
|-------|-------|---------|
| HTTP / API | `app.py` | Flask routes, JSON endpoints |
| Core engine | `smartqueue/queues.py` | `QueueManager` — dual deque + heap queuing |
| Domain models | `smartqueue/models.py` | `Ticket`, `Customer`, `ServiceType` dataclasses |
| Analytics | `smartqueue/analytics.py` | Average wait-time ranking per service |
| Utilities | `smartqueue/utils.py` | ID generation, timestamp helpers |
| CLI | `smartqueue/cli.py` | Terminal-based interface (same backend) |
| Frontend | `static/script.js`, `templates/` | JS fetch calls + Jinja2 HTML |
| Tests | `tests/test_queue_manager.py` | Unit tests for FIFO, priority, and position logic |

All state is **in-memory** (no database). The `QueueManager` is the single source of truth.

### Representative Prompts

These prompts are written so an AI assistant can understand the project context and give targeted answers. Feel free to copy, tweak, or combine them.

**Understanding the codebase**
> "Explain how QueueManager in smartqueue/queues.py decides serving order between priority and normal customers."

> "Walk me through the data flow when a customer clicks 'Get My Ticket' on the frontend — from script.js through app.py to QueueManager."

**Adding features**
> "Add a new ServiceType called 'health' to the system. What files need to change?"

> "I want to add a /api/cancel endpoint that lets a customer cancel their ticket by ticket_id. Implement it in app.py and add the cleanup logic in QueueManager."

> "Add a 'transfer ticket to a different service' feature. The ticket should keep its original issue time but move to the new service queue."

**Fixing bugs / refactoring**
> "The get_position method is O(n). Can you refactor it to be faster while keeping the same interface?"

> "When I restart the server I lose all data. How would I add SQLite persistence to QueueManager without changing the API?"

**Testing**
> "Write a test that verifies a cancelled ticket is no longer served by serve_next."

> "Add a test for the analytics endpoint that serves a few tickets and checks the JSON response."

**Frontend**
> "Add a live-refreshing queue display to the admin page that polls /api/analytics every 5 seconds."

> "The customer kiosk doesn't show an error when the service type is invalid. Add client-side validation in script.js."
