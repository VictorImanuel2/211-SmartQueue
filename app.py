from flask import Flask, render_template, request, jsonify
from smartqueue.queues import QueueManager
from smartqueue.analytics import rank_services_by_avg_wait
from smartqueue.models import ServiceType
import threading

app = Flask(__name__)

# Global In-Memory Queue Manager
manager = QueueManager()

# Pre-populate with more diverse data for a better demo
try:
    print("Pre-populating queue with mock data...")
    # Passport queue
    manager.issue_ticket("u1", "Alice", "passport", priority_level=0)
    manager.issue_ticket("u2", "Bob", "passport", priority_level=0)
    manager.issue_ticket("u3", "Charlie", "passport", priority_level=5) # Priority
    
    # Tax queue
    manager.issue_ticket("u4", "Diana", "tax", priority_level=8) # High Priority
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
    # Redirect to customer page by default
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

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    stats = rank_services_by_avg_wait(manager)
    return jsonify({
        'success': True,
        'stats': [{'service': s, 'avg_wait': w} for s, w in stats]
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)