document.addEventListener('DOMContentLoaded', () => {
    console.log("SmartQueue Loaded");
    
    // Attach event listeners explicitly to avoid inline HTML onclick issues if CSP strict
    document.querySelector('.kiosk .btn.primary').addEventListener('click', takeTicket);
    document.querySelector('.status .btn.secondary').addEventListener('click', checkStatus);
    document.querySelector('.admin .btn.success').addEventListener('click', serveNext);
    document.querySelector('.analytics-preview .btn.text-btn').addEventListener('click', refreshStats);

    // Initial Load
    refreshStats();
});

async function takeTicket() {
    const nameInput = document.getElementById('custName');
    const name = nameInput.value.trim() || "Guest";
    const service = document.getElementById('custService').value;
    const priority = document.getElementById('custPriority').checked ? 5 : 0;

    try {
        const res = await fetch('/api/ticket', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                name: name,
                service: service,
                priority: priority
            })
        });
        const data = await res.json();

        if(data.success) {
            document.getElementById('displayTicketId').textContent = data.ticket_id;
            document.getElementById('displayPos').textContent = data.position;
            document.getElementById('displayWait').textContent = data.wait_time;
            
            const result = document.getElementById('ticketResult');
            result.classList.remove('hidden');
            result.style.display = 'block';
            
            // Clear inputs
            nameInput.value = "";
            document.getElementById('custPriority').checked = false;
        } else {
            alert("Error: " + data.error);
        }
    } catch(e) {
        console.error(e);
        alert("Server error");
    }
}

async function checkStatus() {
    const id = document.getElementById('checkId').value.trim();
    if(!id) return alert("Please enter a Ticket ID");

    try {
        const res = await fetch(`/api/status/${id}`);
        if(res.status === 404) {
            alert("Ticket not found or already served.");
            return;
        }
        
        const data = await res.json();
        if(data.success) {
            document.getElementById('statusPos').textContent = data.position;
            document.getElementById('statusWait').textContent = data.wait_time;
            
            const result = document.getElementById('statusResult');
            result.classList.remove('hidden');
            result.style.display = 'block';
        }
    } catch(e) {
        console.error(e);
    }
}

async function serveNext() {
    const service = document.getElementById('adminService').value;

    try {
        const res = await fetch('/api/serve', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ service: service })
        });
        
        const data = await res.json();
        
        if(data.success) {
            const t = data.ticket;
            document.getElementById('servingTicket').textContent = t.id;
            document.getElementById('servingName').textContent = t.customer;
            
            const result = document.getElementById('serveResult');
            result.classList.remove('hidden');
            result.style.display = 'block';
            
            // Auto refresh stats
            refreshStats();
        } else {
            alert(data.message || "Queue is empty!");
        }
    } catch(e) {
        console.error(e);
    }
}

async function refreshStats() {
    try {
        const res = await fetch('/api/analytics');
        const data = await res.json();
        
        const list = document.getElementById('statsList');
        list.innerHTML = "";
        
        if(data.success && data.stats.length > 0) {
            data.stats.forEach(s => {
                const li = document.createElement('li');
                li.innerHTML = `<span>${s.service.toUpperCase()}</span> <span>Avg Wait: <strong>${s.avg_wait.toFixed(1)} m</strong></span>`;
                list.appendChild(li);
            });
        } else {
            list.innerHTML = "<li>No served customers yet.</li>";
        }
    } catch(e) {
        console.error(e);
    }
}
