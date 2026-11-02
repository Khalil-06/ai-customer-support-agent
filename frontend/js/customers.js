let customers = [];

document.addEventListener("DOMContentLoaded", () => {

    checkAuthentication();

    loadUser();

    loadCustomers();

    setupEvents();

});


function checkAuthentication() {

    const token =
        localStorage.getItem("access_token");

    if (!token) {
        window.location.href = "login.html";
    }

}


function loadUser() {

    const storedUser =
        localStorage.getItem("user");

    if (!storedUser) {
        return;
    }

    const user =
        JSON.parse(storedUser);

    const email =
        user.email || "User";

    const name =
        email.split("@")[0];

    document.getElementById("userName")
        .textContent = name;

    document.getElementById("userRole")
        .textContent = user.role || "User";

    document.getElementById("workspaceName")
        .textContent = name;

    document.getElementById("userAvatar")
        .textContent =
        name.charAt(0).toUpperCase();

    document.getElementById("workspaceAvatar")
        .textContent =
        name.charAt(0).toUpperCase();

}


async function loadCustomers() {

    const tableBody =
        document.getElementById(
            "customerTableBody"
        );

    tableBody.innerHTML = `
        <tr>
            <td colspan="5" class="loading-cell">
                Loading customers...
            </td>
        </tr>
    `;

    try {

        const data =
            await apiRequest("/customers");

        customers =
            data.customers || [];

        document.getElementById(
            "customerCount"
        ).textContent =
            data.count ?? customers.length;

        await loadCustomerLimit();

        renderCustomers(customers);

    } catch (error) {

        tableBody.innerHTML = "";

        showMessage(
            error.message,
            true
        );

    }

}


async function loadCustomerLimit() {

    try {

        const data =
            await apiRequest("/saas/usage");

        const limit =
            data.limits?.customers ?? "--";

        document.getElementById(
            "customerLimit"
        ).textContent =
            limit;

    } catch (error) {

        document.getElementById(
            "customerLimit"
        ).textContent = "--";

    }

}


function renderCustomers(list) {

    const tableBody =
        document.getElementById(
            "customerTableBody"
        );

    const emptyState =
        document.getElementById(
            "emptyCustomers"
        );


    if (!list.length) {

        tableBody.innerHTML = "";

        emptyState.style.display = "block";

        return;

    }


    emptyState.style.display = "none";


    tableBody.innerHTML =
        list.map(customer => {

            const initial =
                customer.name
                    .charAt(0)
                    .toUpperCase();

            return `

                <tr>

                    <td>

                        <div class="customer-name">

                            <div class="customer-avatar">
                                ${initial}
                            </div>

                            <div>
                                <strong>
                                    ${escapeHtml(customer.name)}
                                </strong>

                                <span>
                                    Customer
                                </span>
                            </div>

                        </div>

                    </td>


                    <td>
                        ${escapeHtml(customer.email)}
                    </td>


                    <td>
                        ${escapeHtml(customer.phone)}
                    </td>


                    <td>
                        <span class="customer-id">
                            #${customer.id}
                        </span>
                    </td>


                    <td>

                        <button
                            class="view-customer"
                            onclick="viewCustomer(${customer.id})"
                        >
                            View
                        </button>

                    </td>

                </tr>

            `;

        }).join("");

}


function setupEvents() {

    const search =
        document.getElementById(
            "customerSearch"
        );

    search.addEventListener(
        "input",
        function () {

            const query =
                this.value
                    .toLowerCase()
                    .trim();

            const filtered =
                customers.filter(customer =>

                    customer.name
                        .toLowerCase()
                        .includes(query)

                    ||

                    customer.email
                        .toLowerCase()
                        .includes(query)

                    ||

                    customer.phone
                        .toLowerCase()
                        .includes(query)

                );

            renderCustomers(filtered);

        }
    );


    document.getElementById(
        "openCustomerModal"
    ).addEventListener(
        "click",
        openModal
    );


    document.getElementById(
        "closeCustomerModal"
    ).addEventListener(
        "click",
        closeModal
    );


    document.getElementById(
        "cancelCustomer"
    ).addEventListener(
        "click",
        closeModal
    );


    document.getElementById(
        "customerForm"
    ).addEventListener(
        "submit",
        addCustomer
    );


    document.getElementById(
        "logoutButton"
    ).addEventListener(
        "click",
        logout
    );

}


function openModal() {

    document
        .getElementById("customerModal")
        .classList.add("show");

}


function closeModal() {

    document
        .getElementById("customerModal")
        .classList.remove("show");

    document
        .getElementById("customerForm")
        .reset();

    document
        .getElementById("formMessage")
        .textContent = "";

}


async function addCustomer(event) {

    event.preventDefault();


    const button =
        document.getElementById(
            "saveCustomer"
        );

    const message =
        document.getElementById(
            "formMessage"
        );


    const name =
        document.getElementById(
            "customerName"
        ).value.trim();

    const email =
        document.getElementById(
            "customerEmail"
        ).value.trim();

    const phone =
        document.getElementById(
            "customerPhone"
        ).value.trim();


    button.disabled = true;

    button.textContent =
        "Adding...";

    message.textContent = "";


    try {

        await apiRequest(
            "/customers",
            {
                method: "POST",

                body: JSON.stringify({
                    name,
                    email,
                    phone
                })
            }
        );


        closeModal();

        await loadCustomers();


        showMessage(
            "Customer added successfully."
        );


    } catch (error) {

        message.textContent =
            error.message;

    } finally {

        button.disabled = false;

        button.textContent =
            "Add customer";

    }

}


async function viewCustomer(customerId) {

    const customer =
        customers.find(
            item => item.id === customerId
        );

    if (!customer) {
        return;
    }


    // Open drawer
    document
        .getElementById("customerDrawer")
        .classList.add("show");


    // Basic customer information
    const initial =
        customer.name
            .charAt(0)
            .toUpperCase();


    document.getElementById(
        "drawerAvatar"
    ).textContent = initial;


    document.getElementById(
        "drawerCustomerName"
    ).textContent = customer.name;


    document.getElementById(
        "drawerCustomerEmail"
    ).textContent = customer.email;


    document.getElementById(
        "drawerEmail"
    ).textContent = customer.email;


    document.getElementById(
        "drawerPhone"
    ).textContent = customer.phone;


    document.getElementById(
        "drawerId"
    ).textContent = `#${customer.id}`;


    // Reset sections
    document.getElementById(
        "drawerOrders"
    ).innerHTML = `
        <div class="drawer-loading">
            Loading orders...
        </div>
    `;


    document.getElementById(
        "drawerConversations"
    ).innerHTML = `
        <div class="drawer-loading">
            Loading conversations...
        </div>
    `;


    document.getElementById(
        "drawerOrderCount"
    ).textContent = "0";


    document.getElementById(
        "drawerConversationCount"
    ).textContent = "0";


    // Load real backend data
    await Promise.all([
        loadCustomerOrders(customer.id),
        loadCustomerConversations(customer.id)
    ]);

}
async function loadCustomerOrders(customerId) {

    const container =
        document.getElementById(
            "drawerOrders"
        );

    try {

        const data =
            await apiRequest(
                `/customers/${customerId}/orders`
            );


        const orders =
            Array.isArray(data)
                ? data
                : data.orders || [];


        document.getElementById(
            "drawerOrderCount"
        ).textContent = orders.length;


        if (!orders.length) {

            container.innerHTML = `
                <div class="drawer-empty">
                    No orders found.
                </div>
            `;

            return;
        }


        container.innerHTML =
            orders.map(order => `

                <div class="drawer-card">

                    <div>

                        <strong>
                            #${order.order_id}
                        </strong>

                        <span>
                            Order
                        </span>

                    </div>

                    <span
                        class="status-badge ${getStatusClass(order.status)}"
                    >
                        ${escapeHtml(order.status)}
                    </span>

                </div>

            `).join("");


    } catch (error) {

        container.innerHTML = `
            <div class="drawer-empty error">
                Unable to load orders.
            </div>
        `;

    }

}


async function loadCustomerConversations(customerId) {

    const container =
        document.getElementById(
            "drawerConversations"
        );

    try {

        const data =
            await apiRequest(
                `/customers/${customerId}/conversations`
            );


        const conversations =
            Array.isArray(data)
                ? data
                : data.conversations || [];


        document.getElementById(
            "drawerConversationCount"
        ).textContent =
            conversations.length;


        if (!conversations.length) {

            container.innerHTML = `
                <div class="drawer-empty">
                    No conversations yet.
                </div>
            `;

            return;
        }


        container.innerHTML =
            conversations.map(conversation => `

                <div class="conversation-card">

                    <div class="conversation-icon">
                        ✦
                    </div>

                    <div class="conversation-content">

                        <strong>
                            ${escapeHtml(
                                conversation.title ||
                                "Support conversation"
                            )}
                        </strong>

                        <span>
                            Conversation #${conversation.id}
                        </span>

                    </div>

                </div>

            `).join("");


    } catch (error) {

        container.innerHTML = `
            <div class="drawer-empty error">
                Unable to load conversations.
            </div>
        `;

    }

}


function getStatusClass(status) {

    const value =
        String(status || "")
            .toLowerCase();


    if (
        value.includes("deliver")
    ) {
        return "status-success";
    }


    if (
        value.includes("ship")
    ) {
        return "status-info";
    }


    if (
        value.includes("cancel")
    ) {
        return "status-danger";
    }


    return "status-warning";

}