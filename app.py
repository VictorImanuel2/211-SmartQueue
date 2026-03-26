# =============================================================================
# app.py — Flask web server for the NoQ queue management system.
#
# Architecture overview:
#   - This is the HTTP layer. All state lives in-memory in a single
#     QueueManager instance (see smartqueue/queues.py).
#   - Two user-facing pages: customer kiosk (/) and admin dashboard (/admin),
#     rendered via Jinja2 templates in templates/.
#   - JSON API endpoints under /api/ are consumed by static/script.js:
#       POST /api/ticket          — issue a new ticket (normal or priority)
#       GET  /api/status/<id>     — check position & estimated wait
#       POST /api/serve           — admin calls next customer from a queue
#       GET  /api/queue           — get queue details for a given service
#       GET  /api/queue-overview  — get current waiting counts by service
#   - Data models (Ticket, Customer, ServiceType) are in smartqueue/models.py.
#   - No database; everything resets on server restart.
# =============================================================================

from flask import Flask, render_template, request, jsonify
from smartqueue.queues import QueueManager

app = Flask(__name__)

# Global In-Memory Queue Manager
manager = QueueManager()

# Pre-populate with more diverse data for a better demo
try:
    print("Pre-populating queue with mock data...")
    
    # Passport queue
    manager.issue_ticket("u1", "Alice", "passport", priority_level=0)
    manager.issue_ticket("u2", "Bob", "passport", priority_level=0)
    manager.issue_ticket("u3", "Charlie", "passport", priority_level=5)  # Priority
    
    # Tax queue
    manager.issue_ticket("u4", "Diana", "tax", priority_level=8)  # High Priority
    manager.issue_ticket("u5", "Eve", "tax", priority_level=0)

    # Municipal queue
    manager.issue_ticket("u6", "Frank", "municipal", priority_level=0)
    
    # Support queue
    manager.issue_ticket("u7", "Grace", "support", priority_level=0)
    manager.issue_ticket("u8", "Henry", "support", priority_level=0)
    
    print("✅ 8 mock tickets created across different services.")
except Exception as e:
    print(f"⚠️ Pre-populating error: {e}")


@app.route('/')
def home():
    return render_template('customer.html')


@app.route('/admin')
def admin():
    return render_template('admin.html')


# --- API ENDPOINTS ---

@app.route('/api/ticket', methods=['POST'])
def create_ticket():
    data = request.json
    try:
        # Use a unique ID for guests to allow multiple guest tickets
        user_id = f"guest-{manager.counter}"
        name = data.get('name', 'Guest')
        service = data.get('service', 'passport')
        priority = int(data.get('priority', 0))
        
        ticket = manager.issue_ticket(user_id, name, service, priority_level=priority)
        position, wait = manager.get_position(ticket.ticket_id)
        
        return jsonify({
            'success': True,
            'ticket_id': ticket.ticket_id,
            'service': ticket.service.value,
            'priority': ticket.priority_level,
            'position': position,
            'wait_time': wait
        })
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/status/<ticket_id>', methods=['GET'])
def get_status(ticket_id):
    pos, wait = manager.get_position(ticket_id)
    if pos == -1:
        return jsonify({'success': False, 'status': 'not_found_or_served'}), 404
        
    ticket = manager.active_tickets_by_id.get(ticket_id)
    return jsonify({
        'success': True,
        'position': pos,
        'wait_time': wait,
        'customer': ticket.customer.name,
        'service': ticket.service.value
    })


@app.route('/api/serve', methods=['POST'])
def serve_next():
    data = request.json
    service = data.get('service', 'passport')
    office = data.get('office_id', 'default')
    
    ticket = manager.serve_next(office, service)
    
    if ticket:
        return jsonify({
            'success': True,
            'ticket': {
                'id': ticket.ticket_id,
                'customer': ticket.customer.name,
                'priority': ticket.priority_level
            }
        })
    else:
        return jsonify({'success': False, 'message': 'No customers waiting'}), 404


@app.route('/api/queue', methods=['GET'])
def get_queue():
    service = request.args.get('service', 'passport')
    try:
        queue = manager.get_queue(service)
        return jsonify({
            'success': True,
            'queue': [
                {
                    'ticket_id': t.ticket_id,
                    'name': t.customer.name,
                    'priority': t.priority_level
                }
                for t in queue
            ]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/queue-overview', methods=['GET'])
def get_queue_overview():
    services = ['passport', 'tax', 'municipal', 'support']
    queues = []

    for service in services:
        waiting_count = 0

        for ticket in manager.active_tickets_by_id.values():
            if ticket.service.value == service and ticket.status == "WAITING":
                waiting_count += 1

        queues.append({
            'service': service,
            'waiting_count': waiting_count
        })

    return jsonify({
        'success': True,
        'queues': queues
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)