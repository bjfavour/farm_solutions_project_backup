const BASE_URL = "http://127.0.0.1:8000/api";
let activeBatchId = null;

/* ================= REGISTER USER ================= */
async function registerUser() {
    const email = document.getElementById("regEmail")?.value;
    const username = document.getElementById("regUsername")?.value;
    const password = document.getElementById("regPassword")?.value;
    const msg = document.getElementById("regMsg");

    if (msg && (!email || !username || !password)) {
        msg.innerHTML = "All fields are required.";
        return;
    }

    if (!msg) return;

    try {
        const response = await fetch(`${BASE_URL}/register/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, username, password })
        });

        const data = await response.json();

        if (response.status === 201 || data.success) {
            msg.style.color = "green";
            msg.innerHTML = "Registration successful! Redirecting...";
            setTimeout(() => {
                window.location.href = "login.html";
            }, 1500);
        } else {
            msg.innerHTML = data.error || "Registration failed.";
        }

    } catch (error) {
        msg.innerHTML = "Network error. Try again.";
    }
}

/* ================= LOGIN ================= */
async function login() {
    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");
    const msg = document.getElementById("msg");

    if (!usernameInput || !passwordInput || !msg) return;

    const username = usernameInput.value;
    const password = passwordInput.value;

    if (!username || !password) {
        msg.innerHTML = "Username and password required";
        return;
    }

    try {
        const response = await fetch(`${BASE_URL}/token/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (data.access) {
            localStorage.setItem("farm_token", data.access);
            window.location.href = "dashboard.html";
        } else {
            msg.innerHTML = "Invalid login credentials";
        }

    } catch (error) {
        msg.innerHTML = "Network error";
    }
}

/* ================= LOAD BATCHES ================= */
async function loadBatches() {
    const token = localStorage.getItem("farm_token");
    if (!token) {
        window.location.href = "login.html";
        return;
    }

    const batchList = document.getElementById("batchList");
    if (!batchList) return;

    try {
        const response = await fetch(`${BASE_URL}/batches/`, {
            headers: { "Authorization": `Bearer ${token}` }
        });

        const data = await response.json();
        const list = data.results || data;

        batchList.innerHTML = "";

        list.forEach(batch => {
            batchList.innerHTML += `
                <div class="batch">
                    <h3>Batch ${batch.serial_number}</h3>
                    <p><b>Animal:</b> ${batch.animal_name}</p>
                    <p><b>Quantity:</b> ${batch.current_quantity}</p>

                    <button class="btn-small" onclick="openFeedingModal(${batch.id})">Add Feeding</button>
                    <button class="btn-small" onclick="openExpenseModal(${batch.id})">Add Expense</button>
                    <button class="btn-small" onclick="openMortalityModal(${batch.id})">Report Mortality</button>
                </div>
            `;
        });

    } catch (err) {
        batchList.innerHTML = "Failed to load batches.";
    }
}

/* ================= MODAL HANDLING ================= */
function showModal(id) {
    const backdrop = document.getElementById("modalBackdrop");
    const modal = document.getElementById(id);

    if (backdrop) backdrop.style.display = "block";
    if (modal) modal.style.display = "block";
}

function closeModals() {
    ["modalBackdrop", "feedingModal", "expenseModal", "mortalityModal"]
        .forEach(id => {
            const el = document.getElementById(id);
            if (el) el.style.display = "none";
        });
}

function openFeedingModal(id) {
    activeBatchId = id;
    showModal("feedingModal");
}

function openExpenseModal(id) {
    activeBatchId = id;
    showModal("expenseModal");
}

function openMortalityModal(id) {
    activeBatchId = id;
    showModal("mortalityModal");
}

/* ================= FEEDING (UPDATED) ================= */
async function submitFeeding() {
    const token = localStorage.getItem("farm_token");

    const bagsInput = document.getElementById("feedingBags");
    const amountInput = document.getElementById("feedingAmount");
    const noteInput = document.getElementById("feedingNote");

    if (!bagsInput || !amountInput) return;

    const bags = bagsInput.value;
    const amount = amountInput.value;
    const note = noteInput?.value || "";

    if (!bags || !amount) {
        alert("Please enter bags and amount.");
        return;
    }

    await fetch(`${BASE_URL}/batches/${activeBatchId}/feeding/`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ bags, amount, note })
    });

    alert("Feeding added!");
    closeModals();
    loadBatches();
}

/* ================= EXPENSE ================= */
async function submitExpense() {
    const token = localStorage.getItem("farm_token");

    const descInput = document.getElementById("expenseDesc");
    const amountInput = document.getElementById("expenseAmount");

    const description = descInput.value;
    const amount = amountInput.value;

    await fetch(`${BASE_URL}/batches/${activeBatchId}/expense/`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ description, amount })
    });

    alert("Expense added!");
    closeModals();
    loadBatches();
}

/* ================= MORTALITY ================= */
async function submitMortality() {
    const token = localStorage.getItem("farm_token");
    const countInput = document.getElementById("mortalityCount");

    const count = countInput.value;

    await fetch(`${BASE_URL}/batches/${activeBatchId}/mortality/`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ count })
    });

    alert("Mortality recorded!");
    closeModals();
    loadBatches();
}

/* ================= LOGOUT ================= */
function logout() {
    localStorage.removeItem("farm_token");
    window.location.href = "login.html";
}

/* ================= ON PAGE LOAD ================= */
document.addEventListener("DOMContentLoaded", () => {
    const path = window.location.pathname;

    if (path.endsWith("dashboard.html")) {
        loadBatches();
    }
});
