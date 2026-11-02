document.addEventListener("DOMContentLoaded", loadDashboard);

async function loadDashboard() {

    const token = localStorage.getItem("access_token");
    const storedUser = localStorage.getItem("user");

    if (!token) {
        window.location.href = "login.html";
        return;
    }

    try {

        const user = storedUser
            ? JSON.parse(storedUser)
            : null;

        if (user) {
            displayUser(user);
        }

        const data = await apiRequest("/saas/usage");

        displayUsage(data);

    } catch (error) {

        console.error(error);

        const message =
            document.getElementById("dashboardMessage");

        message.textContent =
            "Unable to load dashboard data: " + error.message;

        if (
            error.message.toLowerCase().includes("token") ||
            error.message.toLowerCase().includes("unauthorized")
        ) {
            logout();
        }
    }
}


/* =========================
   USER
========================= */

function displayUser(user) {

    const email = user.email || "User";
    const role = user.role || "User";

    const userName =
        email.split("@")[0];

    document.getElementById("userName").textContent =
        userName;

    document.getElementById("userRole").textContent =
        role;

    document.getElementById("welcomeMessage").textContent =
        `Welcome back, ${userName} 👋`;

    document.getElementById("accountEmail").textContent =
        email;

    document.getElementById("accountRole").textContent =
        role;

    document.getElementById("companyId").textContent =
        user.company_id ?? "--";

    document.getElementById("userAvatar").textContent =
        userName.charAt(0).toUpperCase();
}


/* =========================
   USAGE
========================= */

function displayUsage(data) {

    const usage = data.usage;
    const limits = data.limits;
    const plan = data.plan;

    const customersUsed =
        usage.customers ?? 0;

    const customersLimit =
        limits.customers ?? 0;

    const aiMessagesUsed =
        usage.ai_messages ?? 0;

    const aiMessagesLimit =
        limits.ai_messages ?? 0;

    const documentsUsed =
        usage.documents ?? 0;

    const documentsLimit =
        limits.documents ?? 0;


    document.getElementById("customersUsed")
        .textContent = customersUsed;

    document.getElementById("customersLimit")
        .textContent = `/ ${customersLimit} limit`;


    document.getElementById("aiMessagesUsed")
        .textContent = aiMessagesUsed;

    document.getElementById("aiMessagesLimit")
        .textContent = `/ ${aiMessagesLimit} limit`;


    document.getElementById("documentsUsed")
        .textContent = documentsUsed;

    document.getElementById("documentsLimit")
        .textContent = `/ ${documentsLimit} limit`;


    const planName =
        plan.name
            ? plan.name.toUpperCase()
            : "FREE";

    document.getElementById("currentPlan")
        .textContent = planName;

    document.getElementById("planBadge")
        .textContent = `${planName} PLAN`;


    const price =
        Number(plan.price_monthly || 0);

    document.getElementById("planPrice")
        .textContent = `₹${price} / month`;


    /* AI progress */

    const aiPercentage =
        calculatePercentage(
            aiMessagesUsed,
            aiMessagesLimit
        );

    document.getElementById("aiUsagePercentage")
        .textContent = `${aiPercentage}%`;

    document.getElementById("aiUsageProgress")
        .style.width = `${aiPercentage}%`;


    /* Customer progress */

    const customerPercentage =
        calculatePercentage(
            customersUsed,
            customersLimit
        );

    document.getElementById("customerUsagePercentage")
        .textContent = `${customerPercentage}%`;

    document.getElementById("customerUsageProgress")
        .style.width = `${customerPercentage}%`;
}


/* =========================
   HELPERS
========================= */

function calculatePercentage(used, limit) {

    if (!limit || limit <= 0) {
        return 0;
    }

    return Math.min(
        100,
        Math.round((used / limit) * 100)
    );
}


/* =========================
   LOGOUT
========================= */

function logout() {

    localStorage.removeItem("access_token");
    localStorage.removeItem("user");

    window.location.href = "login.html";
}


document
    .getElementById("logoutButton")
    .addEventListener("click", logout);