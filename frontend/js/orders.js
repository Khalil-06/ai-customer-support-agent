const token =
    localStorage.getItem("access_token");

if (!token) {
    window.location.href = "login.html";
}


const ordersTableBody =
    document.getElementById("ordersTableBody");

const searchInput =
    document.getElementById("searchInput");

const statusFilter =
    document.getElementById("statusFilter");

const refreshButton =
    document.getElementById("refreshButton");

const openOrderModalButton =
    document.getElementById("openOrderModal");

const orderModal =
    document.getElementById("orderModal");

const orderForm =
    document.getElementById("orderForm");

const orderIdInput =
    document.getElementById("orderId");

const customerIdInput =
    document.getElementById("customerId");

const orderStatus =
    document.getElementById("orderStatus");

const cancelOrderButton =
    document.getElementById("cancelOrder");

const formMessage =
    document.getElementById("formMessage");

const modalTitle =
    document.getElementById("modalTitle");

const saveOrderButton =
    document.getElementById("saveOrder");

const deleteModal =
    document.getElementById("deleteModal");

const cancelDelete =
    document.getElementById("cancelDelete");

const confirmDelete =
    document.getElementById("confirmDelete");

const logoutButton =
    document.getElementById("logoutButton");


let orders = [];

let editingOrderId = null;

let deletingOrderId = null;


/* =========================
   USER INFO
========================= */

function loadUserInfo() {

    const userData =
        localStorage.getItem("user");

    if (!userData) {
        return;
    }

    try {

        const user =
            JSON.parse(userData);

        document.getElementById(
            "userName"
        ).textContent =
            user.email || "User";

        document.getElementById(
            "userRole"
        ).textContent =
            user.role || "User";

    } catch (error) {

        console.error(error);

    }
}


/* =========================
   LOAD ORDERS
========================= */

async function loadOrders() {

    try {

        const data =
            await apiRequest("/orders");

        if (Array.isArray(data)) {

            orders = data;

        } else if (
            Array.isArray(data.orders)
        ) {

            orders = data.orders;

        } else {

            orders = [];

        }

        renderOrders();

        updateSummary();

    } catch (error) {

        console.error(
            "Failed to load orders:",
            error
        );

        ordersTableBody.innerHTML = `
            <tr>
                <td colspan="4">
                    <div class="empty-state">
                        <div class="empty-state-icon">
                            ⚠️
                        </div>

                        <h4>
                            Unable to load orders
                        </h4>

                        <p>
                            ${escapeHtml(error.message)}
                        </p>
                    </div>
                </td>
            </tr>
        `;

    }
}


/* =========================
   FILTER
========================= */

function getFilteredOrders() {

    const search =
        searchInput.value
            .trim()
            .toLowerCase();

    const status =
        statusFilter.value;


    return orders.filter(order => {

        const matchesSearch =
            !search ||
            String(order.order_id)
                .includes(search) ||
            String(order.customer_id)
                .includes(search);


        const matchesStatus =
            status === "all" ||
            String(order.status)
                .toLowerCase() ===
            status.toLowerCase();


        return (
            matchesSearch &&
            matchesStatus
        );

    });

}


/* =========================
   RENDER
========================= */

function renderOrders() {

    const filteredOrders =
        getFilteredOrders();


    ordersTableBody.innerHTML = "";


    if (!filteredOrders.length) {

        ordersTableBody.innerHTML = `
            <tr>
                <td colspan="4">

                    <div class="empty-state">

                        <div class="empty-state-icon">
                            🛒
                        </div>

                        <h4>
                            No orders found
                        </h4>

                        <p>
                            Add an order or change your search/filter.
                        </p>

                    </div>

                </td>
            </tr>
        `;

        return;
    }


    filteredOrders.forEach(order => {

        const row =
            document.createElement("tr");


        row.innerHTML = `

            <td>

                <span class="order-id">
                    #${escapeHtml(order.order_id)}
                </span>

            </td>


            <td>

                <span class="customer-id">
                    Customer #${escapeHtml(order.customer_id)}
                </span>

            </td>


            <td>

                <span class="status ${getStatusClass(order.status)}">
                    ${escapeHtml(order.status)}
                </span>

            </td>


            <td>

                <button
                    class="action-btn edit-btn"
                >
                    Edit
                </button>


                <button
                    class="action-btn delete-btn"
                >
                    Delete
                </button>

            </td>

        `;


        row.querySelector(
            ".edit-btn"
        ).addEventListener(
            "click",
            () => openEditModal(order)
        );


        row.querySelector(
            ".delete-btn"
        ).addEventListener(
            "click",
            () => openDeleteModal(
                order.order_id
            )
        );


        ordersTableBody.appendChild(row);

    });

}


/* =========================
   SUMMARY
========================= */

function updateSummary() {

    document.getElementById(
        "totalOrders"
    ).textContent =
        orders.length;


    document.getElementById(
        "processingOrders"
    ).textContent =
        countStatus("Processing");


    document.getElementById(
        "shippedOrders"
    ).textContent =
        countStatus("Shipped");


    document.getElementById(
        "deliveredOrders"
    ).textContent =
        countStatus("Delivered");

}


function countStatus(status) {

    return orders.filter(
        order =>
            String(order.status)
                .toLowerCase() ===
            status.toLowerCase()
    ).length;

}


/* =========================
   STATUS CLASS
========================= */

function getStatusClass(status) {

    const normalized =
        String(status)
            .toLowerCase();

    if (normalized === "shipped") {
        return "status-shipped";
    }

    if (normalized === "delivered") {
        return "status-delivered";
    }

    if (normalized === "processing") {
        return "status-processing";
    }

    if (normalized === "cancelled") {
        return "status-cancelled";
    }

    return "status-default";

}


/* =========================
   OPEN ADD MODAL
========================= */

openOrderModalButton.addEventListener(
    "click",
    function () {

        editingOrderId = null;

        modalTitle.textContent =
            "Add Order";

        saveOrderButton.textContent =
            "Save Order";

        orderForm.reset();

        formMessage.textContent = "";

        orderModal.classList.add(
            "show"
        );

    }
);


/* =========================
   OPEN EDIT MODAL
========================= */

function openEditModal(order) {

    editingOrderId =
        order.order_id;


    modalTitle.textContent =
        `Edit Order #${order.order_id}`;


    saveOrderButton.textContent =
        "Update Order";


    orderIdInput.value =
        order.order_id;


    customerIdInput.value =
        order.customer_id;


    orderStatus.value =
        order.status;


    formMessage.textContent = "";


    /*
     * Order ID and customer ID
     * cannot be changed during update.
     */

    orderIdInput.disabled = true;

    customerIdInput.disabled = true;


    orderModal.classList.add(
        "show"
    );

}


/* =========================
   ADD / UPDATE
========================= */

orderForm.addEventListener(
    "submit",
    async function (event) {

        event.preventDefault();


        formMessage.textContent = "";


        saveOrderButton.disabled =
            true;


        saveOrderButton.textContent =
            editingOrderId
                ? "Updating..."
                : "Saving...";


        try {

            if (editingOrderId) {

                await apiRequest(
                    `/orders/${editingOrderId}`,
                    {
                        method: "PUT",

                        body: JSON.stringify({
                            status:
                                orderStatus.value
                        })
                    }
                );


            } else {

                await apiRequest(
                    "/orders",
                    {
                        method: "POST",

                        body: JSON.stringify({

                            order_id:
                                Number(
                                    orderIdInput.value
                                ),

                            customer_id:
                                Number(
                                    customerIdInput.value
                                ),

                            status:
                                orderStatus.value

                        })
                    }
                );

            }


            closeOrderModal();

            await loadOrders();


        } catch (error) {

            console.error(error);

            formMessage.textContent =
                error.message;

        } finally {

            saveOrderButton.disabled =
                false;

            saveOrderButton.textContent =
                editingOrderId
                    ? "Update Order"
                    : "Save Order";

        }

    }
);


/* =========================
   CLOSE ORDER MODAL
========================= */

cancelOrderButton.addEventListener(
    "click",
    closeOrderModal
);


function closeOrderModal() {

    orderModal.classList.remove(
        "show"
    );

    editingOrderId = null;

    orderIdInput.disabled = false;

    customerIdInput.disabled = false;

}


/* =========================
   DELETE
========================= */

function openDeleteModal(orderId) {

    deletingOrderId =
        orderId;

    deleteModal.classList.add(
        "show"
    );

}


cancelDelete.addEventListener(
    "click",
    function () {

        deletingOrderId = null;

        deleteModal.classList.remove(
            "show"
        );

    }
);


confirmDelete.addEventListener(
    "click",
    async function () {

        if (!deletingOrderId) {
            return;
        }


        confirmDelete.disabled =
            true;

        confirmDelete.textContent =
            "Deleting...";


        try {

            await apiRequest(
                `/orders/${deletingOrderId}`,
                {
                    method: "DELETE"
                }
            );


            deleteModal.classList.remove(
                "show"
            );


            deletingOrderId = null;


            await loadOrders();


        } catch (error) {

            alert(
                error.message
            );

        } finally {

            confirmDelete.disabled =
                false;

            confirmDelete.textContent =
                "Delete";

        }

    }
);


/* =========================
   SEARCH / FILTER
========================= */

searchInput.addEventListener(
    "input",
    renderOrders
);


statusFilter.addEventListener(
    "change",
    renderOrders
);


/* =========================
   REFRESH
========================= */

refreshButton.addEventListener(
    "click",
    async function () {

        refreshButton.disabled =
            true;

        refreshButton.textContent =
            "Refreshing...";


        try {

            await loadOrders();

        } finally {

            refreshButton.disabled =
                false;

            refreshButton.textContent =
                "↻ Refresh";

        }

    }
);


/* =========================
   LOGOUT
========================= */

logoutButton.addEventListener(
    "click",
    function () {

        localStorage.removeItem(
            "access_token"
        );

        localStorage.removeItem(
            "user"
        );

        window.location.href =
            "login.html";

    }
);


/* =========================
   ESCAPE HTML
========================= */

function escapeHtml(value) {

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");

}


/* =========================
   INITIALIZE
========================= */

loadUserInfo();

loadOrders();