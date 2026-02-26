import sys
import time
from datetime import datetime
from .queues import QueueManager
from .models import ServiceType
from .analytics import rank_services_by_avg_wait

def print_header():
    print("\n" + "="*50)
    print("   SMART QUEUE SYSTEM (IS-211 PROTOTYPE)   ")
    print("="*50 + "\n")

def print_menu():
    print("1. [User] Take a Ticket (Normal)")
    print("2. [User] Take a Ticket (Priority / Urgent)")
    print("3. [User] Check Status & Wait Time")
    print("4. [Admin] Serve Next Customer")
    print("5. [Admin] View Analytics (Avg Wait Time)")
    print("6. Exit")
    print("-" * 30)

def main():
    manager = QueueManager()
    print_header()

    # Pre-populate some data for demo
    print("[System] Pre-populating queue for demo...")
    try:
        t1 = manager.issue_ticket("u1", "Alice", "passport", priority_level=0)
        t2 = manager.issue_ticket("u2", "Bob", "passport", priority_level=0)
        t3 = manager.issue_ticket("u3", "Charlie", "passport", priority_level=5) # Priority
        print(f" -> Added 3 customers. {t3.customer.name} is priority.")
    except Exception as e:
        print(f"Error prepopulating: {e}")

    while True:
        print_menu()
        choice = input("Select an option: ").strip()

        if choice == "1":
            user_id = input("Enter User ID: ").strip() or "guest"
            name = input("Enter Name: ").strip() or "Guest"
            service = input("Service (passport/tax/support): ").strip().lower()
            if not service: service = "passport"
            
            try:
                ticket = manager.issue_ticket(user_id, name, service, priority_level=0)
                print(f"\n✅ Ticket Issued: {ticket.ticket_id}")
                print(f"   Name: {ticket.customer.name}")
                print(f"   Service: {ticket.service.value}")
                print(f"   Priority: Normal")
                pos, est = manager.get_position(ticket.ticket_id)
                print(f"   Current Position: {pos}")
                print(f"   Est. Wait: {est} mins\n")
            except ValueError as e:
                print(f"\n❌ Error: {e}\n")

        elif choice == "2":
            user_id = input("Enter User ID: ").strip() or "guest_p"
            name = input("Enter Name: ").strip() or "Guest"
            service = input("Service (passport/tax/support): ").strip().lower()
            if not service: service = "passport"
            
            try:
                # Priority level 5 for demo purposes
                ticket = manager.issue_ticket(user_id, name, service, priority_level=5)
                print(f"\n⚡️ PRIORITY Ticket Issued: {ticket.ticket_id}")
                print(f"   Name: {ticket.customer.name}")
                print(f"   Service: {ticket.service.value}")
                print(f"   Priority: HIGH (Level 5)")
                pos, est = manager.get_position(ticket.ticket_id)
                print(f"   Current Position: {pos}")
                print(f"   Est. Wait: {est} mins\n")
            except ValueError as e:
                print(f"\n❌ Error: {e}\n")

        elif choice == "3":
            tid = input("Enter Ticket ID: ").strip()
            pos, est = manager.get_position(tid)
            if pos == -1:
                print("\n❌ Ticket not found or already served.\n")
            else:
                print(f"\n📍 Status for Ticket {tid}:")
                print(f"   Position in Queue: {pos}")
                print(f"   Estimated Wait: {est} mins")
                # Also show details if possible
                if tid in manager.active_tickets_by_id:
                    t = manager.active_tickets_by_id[tid]
                    print(f"   Customer: {t.customer.name} ({t.service.value})")
                print("")

        elif choice == "4":
            office_id = "default"
            service = input("Service to serve (passport/tax/support): ").strip().lower()
            if not service: service = "passport"
            
            served = manager.serve_next(office_id, service)
            if served:
                print(f"\n📢 NOW SERVING: {served.ticket_id}")
                print(f"   Customer: {served.customer.name}")
                print(f"   Priority: {served.priority_level}")
                waited = (datetime.now() - served.issued_at).seconds / 60
                print(f"   Waited: {waited:.1f} mins\n")
            else:
                print(f"\n⚠️  No customers waiting for {service}.\n")

        elif choice == "5":
            print("\n📊 Service Analytics (Avg Wait Time):")
            stats = rank_services_by_avg_wait(manager)
            if not stats:
                print("   No data yet.")
            for s, avg in stats:
                print(f"   - {s}: {avg:.1f} mins")
            print("")

        elif choice == "6":
            print("Exiting...")
            break
        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    main()
