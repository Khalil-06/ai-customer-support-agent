let tickets = [];

let editingTicketId = null;

let deletingTicketId = null;


// =========================================================
// INITIALIZATION
// =========================================================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        const token =
            localStorage.getItem(
                "access_token"
            );

        if (!token) {

            window.location.href =
                "login.html";

            return;
        }

        setupEvents();

        loadTickets();

    }
);


// =========================================================
// LOAD TICKETS
// =========================================================

async function loadTickets() {

    showMessage(
        "ticketsMessage",
        "Loading tickets...",
        ""
    );

    try {

        const data =
            await apiRequest(
                "/tickets"
            );

        tickets =
            Array.isArray(data)
                ? data
                : (
                    data.tickets ||
                    []
                );

        renderTickets(tickets);

        updateSummary(tickets);

        showMessage(
            "ticketsMessage",
            "",
            ""
        );

    } catch (error) {

        console.error(
            "Failed to load tickets:",
            error
        );

        showMessage(
            "ticketsMessage",
            error.message,
            "error"
        );

        tickets = [];

        renderTickets([]);

        updateSummary([]);

    }

}


// =========================================================
// RENDER
// =========================================================

function renderTickets(ticketList) {

    const tableBody =
        document.getElementById(
            "ticketsTableBody"
        );

    const emptyState =
        document.getElementById(
            "emptyState"
        );


    if (!ticketList.length) {

        tableBody.innerHTML = "";

        emptyState.style.display =
            "block";

        return;
    }


    emptyState.style.display =
        "none";


    tableBody.innerHTML =
        ticketList
            .map(ticket => {

                const statusClass =
                    getStatusClass(
                        ticket.status
                    );


                return `
                    <tr>

                        <td>
                            <span class="ticket-id">
                                #${escapeHtml(
                                    ticket.ticket_id
                                )}
                            </span>
                        </td>


                        <td>
                            Customer #${escapeHtml(
                                ticket.customer_id
                            )}
                        </td>


                        <td class="subject-cell">

                            <div class="subject-title">
                                ${escapeHtml(
                                    ticket.subject
                                )}
                            </div>

                            <div class="subject-description">
                                ${escapeHtml(
                                    ticket.description
                                )}
                            </div>

                        </td>


                        <td>

                            <span
                                class="status-badge ${statusClass}"
                            >
                                ${escapeHtml(
                                    ticket.status
                                )}
                            </span>

                        </td>


                        <td>

                            <div class="action-buttons">

                                <button
                                    class="action-btn"
                                    onclick="editTicket(
                                        ${Number(
                                            ticket.ticket_id
                                        )}
                                    )"
                                >
                                    Edit
                                </button>


                                <button
                                    class="action-btn delete-btn"
                                    onclick="openDeleteModal(
                                        ${Number(
                                            ticket.ticket_id
                                        )}
                                    )"
                                >
                                    Delete
                                </button>

                            </div>

                        </td>

                    </tr>
                `;

            })
            .join("");

}


// =========================================================
// SUMMARY
// =========================================================

function updateSummary(ticketList) {

    document.getElementById(
        "totalTickets"
    ).textContent =
        ticketList.length;


    document.getElementById(
        "openTickets"
    ).textContent =
        ticketList.filter(
            ticket =>
                ticket.status
                    ?.toLowerCase() ===
                "open"
        ).length;


    document.getElementById(
        "pendingTickets"
    ).textContent =
        ticketList.filter(
            ticket =>
                ticket.status
                    ?.toLowerCase() ===
                "pending"
        ).length;


    document.getElementById(
        "resolvedTickets"
    ).textContent =
        ticketList.filter(
            ticket =>
                ticket.status
                    ?.toLowerCase() ===
                "resolved"
        ).length;

}


// =========================================================
// STATUS CLASS
// =========================================================

function getStatusClass(status) {

    const normalized =
        String(status || "")
            .toLowerCase()
            .trim();


    if (normalized === "open") {

        return "status-open";

    }


    if (
        normalized ===
        "in progress"
    ) {

        return "status-progress";

    }


    if (
        normalized ===
        "pending"
    ) {

        return "status-pending";

    }


    if (
        normalized ===
        "resolved"
    ) {

        return "status-resolved";

    }


    if (
        normalized ===
        "closed"
    ) {

        return "status-closed";

    }


    return "status-pending";

}


// =========================================================
// SEARCH + FILTER
// =========================================================

function filterTickets() {

    const search =
        document.getElementById(
            "searchTickets"
        )
        .value
        .trim()
        .toLowerCase();


    const status =
        document.getElementById(
            "statusFilter"
        ).value;


    const filtered =
        tickets.filter(
            ticket => {

                const matchesSearch =
                    String(
                        ticket.ticket_id
                    )
                    .toLowerCase()
                    .includes(search)

                    ||

                    String(
                        ticket.customer_id
                    )
                    .toLowerCase()
                    .includes(search)

                    ||

                    String(
                        ticket.subject
                    )
                    .toLowerCase()
                    .includes(search);


                const matchesStatus =
                    status === "all"

                    ||

                    String(
                        ticket.status
                    )
                    .toLowerCase()
                    ===
                    status.toLowerCase();


                return (
                    matchesSearch &&
                    matchesStatus
                );

            }
        );


    renderTickets(filtered);

}


// =========================================================
// EVENTS
// =========================================================

function setupEvents() {

    document
        .getElementById(
            "openTicketModal"
        )
        .addEventListener(
            "click",
            () => openTicketModal()
        );


    document
        .getElementById(
            "closeTicketModal"
        )
        .addEventListener(
            "click",
            closeTicketModal
        );


    document
        .getElementById(
            "cancelTicketModal"
        )
        .addEventListener(
            "click",
            closeTicketModal
        );


    document
        .getElementById(
            "ticketForm"
        )
        .addEventListener(
            "submit",
            saveTicket
        );


    document
        .getElementById(
            "searchTickets"
        )
        .addEventListener(
            "input",
            filterTickets
        );


    document
        .getElementById(
            "statusFilter"
        )
        .addEventListener(
            "change",
            filterTickets
        );


    document
        .getElementById(
            "closeDeleteModal"
        )
        .addEventListener(
            "click",
            closeDeleteModal
        );


    document
        .getElementById(
            "cancelDelete"
        )
        .addEventListener(
            "click",
            closeDeleteModal
        );


    document
        .getElementById(
            "confirmDelete"
        )
        .addEventListener(
            "click",
            deleteTicket
        );


    document
        .getElementById(
            "logoutButton"
        )
        .addEventListener(
            "click",
            logout
        );


    document
        .getElementById(
            "ticketModal"
        )
        .addEventListener(
            "click",
            event => {

                if (
                    event.target.id ===
                    "ticketModal"
                ) {

                    closeTicketModal();

                }

            }
        );


    document
        .getElementById(
            "deleteModal"
        )
        .addEventListener(
            "click",
            event => {

                if (
                    event.target.id ===
                    "deleteModal"
                ) {

                    closeDeleteModal();

                }

            }
        );

}


// =========================================================
// OPEN TICKET MODAL
// =========================================================

function openTicketModal(
    ticket = null
) {

    const modal =
        document.getElementById(
            "ticketModal"
        );


    const title =
        document.getElementById(
            "ticketModalTitle"
        );


    const ticketId =
        document.getElementById(
            "ticketId"
        );


    const customerId =
        document.getElementById(
            "customerId"
        );


    const subject =
        document.getElementById(
            "ticketSubject"
        );


    const description =
        document.getElementById(
            "ticketDescription"
        );


    const status =
        document.getElementById(
            "ticketStatus"
        );


    const message =
        document.getElementById(
            "ticketFormMessage"
        );


    message.textContent = "";

    message.className =
        "message";


    if (ticket) {

        editingTicketId =
            Number(
                ticket.ticket_id
            );


        title.textContent =
            "Edit Ticket";


        ticketId.value =
            ticket.ticket_id;


        customerId.value =
            ticket.customer_id;


        subject.value =
            ticket.subject;


        description.value =
            ticket.description;


        status.value =
            ticket.status;


        ticketId.disabled = true;

        customerId.disabled = true;

    } else {

        editingTicketId = null;


        title.textContent =
            "Create Ticket";


        ticketId.value = "";

        customerId.value = "";

        subject.value = "";

        description.value = "";

        status.value =
            "Open";


        ticketId.disabled = false;

        customerId.disabled = false;

    }


    modal.classList.add(
        "show"
    );

}


// =========================================================
// CLOSE TICKET MODAL
// =========================================================

function closeTicketModal() {

    document
        .getElementById(
            "ticketModal"
        )
        .classList.remove(
            "show"
        );


    document
        .getElementById(
            "ticketForm"
        )
        .reset();


    editingTicketId = null;


    document
        .getElementById(
            "ticketId"
        )
        .disabled = false;


    document
        .getElementById(
            "customerId"
        )
        .disabled = false;

}


// =========================================================
// EDIT
// =========================================================

function editTicket(
    ticketId
) {

    const ticket =
        tickets.find(
            item =>
                Number(
                    item.ticket_id
                ) ===
                Number(ticketId)
        );


    if (!ticket) {
        return;
    }


    openTicketModal(
        ticket
    );

}


// =========================================================
// SAVE
// =========================================================

async function saveTicket(
    event
) {

    event.preventDefault();


    const ticketId =
        Number(
            document.getElementById(
                "ticketId"
            ).value
        );


    const customerId =
        Number(
            document.getElementById(
                "customerId"
            ).value
        );


    const subject =
        document.getElementById(
            "ticketSubject"
        ).value.trim();


    const description =
        document.getElementById(
            "ticketDescription"
        ).value.trim();


    const status =
        document.getElementById(
            "ticketStatus"
        ).value;


    const button =
        document.getElementById(
            "saveTicketButton"
        );


    const message =
        document.getElementById(
            "ticketFormMessage"
        );


    const wasEditing =
        editingTicketId !== null;


    button.disabled = true;

    button.textContent =
        "Saving...";


    try {

        if (wasEditing) {

            await apiRequest(
                `/tickets/${editingTicketId}`,
                {
                    method: "PUT",

                    body:
                        JSON.stringify({
                            ticket_id:
                                editingTicketId,

                            customer_id:
                                customerId,

                            subject:
                                subject,

                            description:
                                description,

                            status:
                                status
                        })
                }
            );

        } else {

            await apiRequest(
                "/tickets",
                {
                    method: "POST",

                    body:
                        JSON.stringify({
                            ticket_id:
                                ticketId,

                            customer_id:
                                customerId,

                            subject:
                                subject,

                            description:
                                description,

                            status:
                                status
                        })
                }
            );

        }


        closeTicketModal();

        await loadTickets();


        showMessage(
            "ticketsMessage",

            wasEditing
                ? "Ticket updated successfully."
                : "Ticket created successfully.",

            "success"
        );


    } catch (error) {

        console.error(
            "Save ticket error:",
            error
        );


        message.textContent =
            error.message;


        message.className =
            "message error";


    } finally {

        button.disabled = false;

        button.textContent =
            "Save Ticket";

    }

}


// =========================================================
// DELETE MODAL
// =========================================================

function openDeleteModal(
    ticketId
) {

    deletingTicketId =
        Number(ticketId);


    document
        .getElementById(
            "deleteMessage"
        )
        .textContent = "";


    document
        .getElementById(
            "deleteModal"
        )
        .classList.add(
            "show"
        );

}


function closeDeleteModal() {

    deletingTicketId = null;


    document
        .getElementById(
            "deleteModal"
        )
        .classList.remove(
            "show"
        );

}


// =========================================================
// DELETE
// =========================================================

async function deleteTicket() {

    if (
        deletingTicketId ===
        null
    ) {

        return;

    }


    const button =
        document.getElementById(
            "confirmDelete"
        );


    const message =
        document.getElementById(
            "deleteMessage"
        );


    button.disabled = true;

    button.textContent =
        "Deleting...";


    try {

        await apiRequest(
            `/tickets/${deletingTicketId}`,
            {
                method: "DELETE"
            }
        );


        closeDeleteModal();


        await loadTickets();


        showMessage(
            "ticketsMessage",
            "Ticket deleted successfully.",
            "success"
        );


    } catch (error) {

        console.error(
            "Delete ticket error:",
            error
        );


        message.textContent =
            error.message;


    } finally {

        button.disabled = false;

        button.textContent =
            "Delete Ticket";

    }

}


// =========================================================
// MESSAGE
// =========================================================

function showMessage(
    elementId,
    text,
    type
) {

    const element =
        document.getElementById(
            elementId
        );


    element.textContent =
        text;


    element.className =
        type
            ? `message ${type}`
            : "message";

}


// =========================================================
// ESCAPE HTML
// =========================================================

function escapeHtml(
    value
) {

    return String(value)
        .replaceAll(
            "&",
            "&amp;"
        )
        .replaceAll(
            "<",
            "&lt;"
        )
        .replaceAll(
            ">",
            "&gt;"
        )
        .replaceAll(
            '"',
            "&quot;"
        )
        .replaceAll(
            "'",
            "&#039;"
        );

}


// =========================================================
// LOGOUT
// =========================================================

function logout() {

    localStorage.removeItem(
        "access_token"
    );

    localStorage.removeItem(
        "user"
    );


    window.location.href =
        "login.html";

}