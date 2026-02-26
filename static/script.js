document.addEventListener('DOMContentLoaded', () => {
    console.log("NoQ Loaded");
    
    // Attach event listeners if the elements exist on the current page
    // This prevents errors when switching between customer and admin views
    
    // Customer page elements
    const getTicketBtn = document.getElementById('getTicketBtn');
    if (getTicketBtn) {
        getTicketBtn.addEventListener('click', takeTicket);
    }
    
    const checkStatusBtn = document.getElementById('checkStatusBtn');
    if (checkStatusBtn) {
        checkStatusBtn.addEventListener('click', checkStatus);
    }

    // Admin page elements
    const serveNextBtn = document.getElementById('serveNextBtn');
    if (serveNextBtn) {
        serveNextBtn.addEventListener('click', serveNext);
    }

    const refreshStatsBtn = document.getElementById('refreshStatsBtn');
    if (refreshStatsBtn) {
        refreshStatsBtn.addEventListener('click', refreshStats);
        // Initial Load for admin page
        refreshStats();
    }
});

async function takeTicket() {
    const nameInput = document.getElementById('custName');
    const name = nameInput.value.trim() || "Guest";
    const service = document.getElementById('custService').value;
    const isPriority = document.getElementById('custPriority').checked;
    const priority = isPriority ? 5 : 0; // Assign a default priority level of 5 if checked

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
        
        if (!res.ok) {
            const errorData = await res.json();
            throw new Error(errorData.error || `HTTP error! status: ${res.status}`);
        }

        const data = await res.json();

        document.getElementById('displayTicketId').textContent = data.ticket_id;
        document.getElementById('displayPos').textContent = data.position;
        document.getElementById('displayWait').textContent = data.wait_time;
        
        const result = document.getElementById('ticketResult');
        result.classList.remove('hidden');
        
        // Clear inputs
        nameInput.value = "";
        document.getElementById('custPriority').checked = false;

    } catch(e) {
        console.error("Error taking ticket:", e);
        alert("Error: " + e.message);
    }
}

async function checkStatus() {
    const idInput = document.getElementById('checkId');
    const id = idInput.value.trim();
    if (!id) return alert("Please enter a Ticket ID");

    try {
        const res = await fetch(`/api/status/${id}`);
        
        if (res.status === 404) {
            alert("Ticket not found or already served.");
            return;
        }

        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        
        const data = await res.json();
        
        document.getElementById('statusPos').textContent = data.position;
        document.getElementById('statusWait').textContent = data.wait_time;
        
        const result = document.getElementById('statusResult');
        result.classList.remove('hidden');

    } catch(e) {
        console.error("Error checking status:", e);
        alert("An error occurred while checking the status.");
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
        
        if (data.success) {
            const t = data.ticket;
            document.getElementById('servingTicket').textContent = t.id;
            document.getElementById('servingName').textContent = t.customer;
            
            const result = document.getElementById('serveResult');
            result.classList.remove('hidden');
            
            // Auto refresh stats
            refreshStats();
        } else {
            alert(data.message || "Queue is empty for this service!");
            // Optionally hide the serving box if queue is empty
            document.getElementById('serveResult').classList.add('hidden');
}
    } catch(e) {
        console.error("Error serving next:", e);
        alert("An error occurred while serving the next customer.");
    }
}

async function refreshStats() {
    try {
        const res = await fetch('/api/analytics');
        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        const data = await res.json();
        
        const list = document.getElementById('statsList');
        if (!list) return; // In case we're on a page without this element
        
        list.innerHTML = ""; // Clear current stats
        
        if (data.success && data.stats.length > 0) {
            data.stats.forEach(s => {
                const li = document.createElement('li');
                li.innerHTML = `<span>${s.service.charAt(0).toUpperCase() + s.service.slice(1)}</span> <strong>${s.avg_wait.toFixed(1)} min</strong>`;
                list.appendChild(li);
            });
        } else {
            list.innerHTML = "<li>No served customers yet.</li>";
        }
    } catch(e) {
        console.error("Error refreshing stats:", e);
        const list = document.getElementById('statsList');
        if(list) list.innerHTML = "<li>Error loading stats.</li>";
    }
}