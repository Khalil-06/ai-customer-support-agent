const token = localStorage.getItem("access_token");

if (!token) {
    window.location.href = "login.html";
}


// DOM ELEMENTS

const documentFile =
    document.getElementById("documentFile");

const uploadMessage =
    document.getElementById("uploadMessage");

const documentsTableBody =
    document.getElementById("documentsTableBody");

const documentCount =
    document.getElementById("documentCount");

const documentLimit =
    document.getElementById("documentLimit");

const documentsRemaining =
    document.getElementById("documentsRemaining");

const documentsHeaderCount =
    document.getElementById("documentsHeaderCount");

const refreshButton =
    document.getElementById("refreshButton");

const logoutButton =
    document.getElementById("logoutButton");

const deleteModal =
    document.getElementById("deleteModal");

const cancelDelete =
    document.getElementById("cancelDelete");

const confirmDelete =
    document.getElementById("confirmDelete");

let selectedDocument = null;


// USER INFORMATION

function loadUserInfo() {

    const userData =
        localStorage.getItem("user");

    if (!userData) {
        return;
    }

    try {

        const user = JSON.parse(userData);

        document.getElementById("userName")
            .textContent =
            user.email || "User";

        document.getElementById("userRole")
            .textContent =
            user.role || "User";

    } catch (error) {

        console.error(
            "Failed to read user data:",
            error
        );

    }
}


// LOAD DOCUMENTS

async function loadDocuments() {

    try {

        const data =
            await apiRequest("/documents");

        let documents = [];

        if (Array.isArray(data)) {

            documents = data;

        } else if (Array.isArray(data.documents)) {

            documents = data.documents;

        }

        renderDocuments(documents);

        updateDocumentCount(documents.length);

        await loadUsage();

    } catch (error) {

        console.error(
            "Failed to load documents:",
            error
        );

        documentsTableBody.innerHTML = `
            <tr>
                <td colspan="3">
                    <div class="empty-state">
                        <div class="empty-state-icon">
                            ⚠️
                        </div>

                        <h4>
                            Unable to load documents
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


// LOAD USAGE
async function loadUsage() {
    try {
        const data = await apiRequest("/saas/usage");

        const usage = data.usage || {};
        const limits = data.limits || {};

        const used = Number(
            usage.documents ?? usage.documents_used ?? 0
        );

        const limit = Number(
            limits.documents ??
            limits.max_documents ??
            data.plan?.max_documents ??
            0
        );

        documentCount.textContent = used;
        documentLimit.textContent = limit;

        documentsRemaining.textContent = Math.max(
            limit - used,
            0
        );

    } catch (error) {
        console.error("Failed to load usage:", error);
    }
}

// RENDER DOCUMENTS

function renderDocuments(documents) {

    documentsTableBody.innerHTML = "";

    if (!documents.length) {

        documentsTableBody.innerHTML = `
            <tr>
                <td colspan="3">

                    <div class="empty-state">

                        <div class="empty-state-icon">
                            📚
                        </div>

                        <h4>
                            No documents yet
                        </h4>

                        <p>
                            Upload your first PDF to start
                            building your AI knowledge base.
                        </p>

                    </div>

                </td>
            </tr>
        `;

        documentsHeaderCount.textContent = "0 documents";

        return;
    }


    documents.forEach(doc => {

        const name =
            typeof doc === "string"
                ? doc
                : (
                    doc.document_name ||
                    doc.name ||
                    "Unknown document"
                );


        const row =
            document.createElement("tr");


        row.innerHTML = `

            <td>

                <div class="document-cell">

                    <div class="document-icon">
                        📄
                    </div>

                    <div class="document-name">
                        ${escapeHtml(name)}
                    </div>

                </div>

            </td>


            <td>

                <span class="status status-ready">
                    Ready
                </span>

            </td>


            <td>

                <button
                    class="delete-btn"
                >
                    Delete
                </button>

            </td>

        `;


        const deleteButton =
            row.querySelector(".delete-btn");


        deleteButton.addEventListener(
            "click",
            function () {

                openDeleteModal(name);

            }
        );


        documentsTableBody.appendChild(row);

    });


    documentsHeaderCount.textContent =
        `${documents.length} ${
            documents.length === 1
                ? "document"
                : "documents"
        }`;

}
// UPDATE COUNT

function updateDocumentCount(count) {

    documentCount.textContent =
        count;

    documentsHeaderCount.textContent =
        `${count} ${
            count === 1
                ? "document"
                : "documents"
        }`;

}


// UPLOAD DOCUMENT

documentFile.addEventListener(
    "change",
    async function () {

        const file =
            documentFile.files[0];

        if (!file) {
            return;
        }


        if (
            file.type !== "application/pdf" &&
            !file.name.toLowerCase().endsWith(".pdf")
        ) {

            showUploadMessage(
                "Please select a PDF file.",
                "error"
            );

            documentFile.value = "";

            return;
        }


        await uploadDocument(file);

    }
);


// UPLOAD FUNCTION

async function uploadDocument(file) {

    showUploadMessage(
        "Uploading and indexing document...",
        "success"
    );


    try {

        const formData =
            new FormData();

        formData.append(
            "file",
            file
        );


        const response =
            await fetch(
                `${API_BASE_URL}/documents/upload`,
                {
                    method: "POST",

                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    },

                    body: formData
                }
            );


        let data = {};

        try {

            data =
                await response.json();

        } catch (error) {

            data = {};

        }


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Document upload failed"
            );

        }


        showUploadMessage(
            "Document uploaded and indexed successfully.",
            "success"
        );


        documentFile.value = "";


        await loadDocuments();


    } catch (error) {

        console.error(
            "Upload error:",
            error
        );


        showUploadMessage(
            error.message,
            "error"
        );


        documentFile.value = "";

    }

}


// DELETE MODAL

function openDeleteModal(documentName) {

    selectedDocument =
        documentName;

    deleteModal.classList.add("show");

}


function closeDeleteModal() {

    selectedDocument = null;

    deleteModal.classList.remove("show");

}


cancelDelete.addEventListener(
    "click",
    closeDeleteModal
);


// CONFIRM DELETE

confirmDelete.addEventListener(
    "click",
    async function () {

        if (!selectedDocument) {
            return;
        }


        confirmDelete.disabled = true;

        confirmDelete.textContent =
            "Deleting...";


        try {

            const encodedName =
                encodeURIComponent(
                    selectedDocument
                );


            await apiRequest(
                `/documents/${encodedName}`,
                {
                    method: "DELETE"
                }
            );


            closeDeleteModal();

            await loadDocuments();


            showUploadMessage(
                "Document deleted successfully.",
                "success"
            );


        } catch (error) {

            console.error(
                "Delete error:",
                error
            );


            closeDeleteModal();


            showUploadMessage(
                error.message,
                "error"
            );

        } finally {

            confirmDelete.disabled =
                false;

            confirmDelete.textContent =
                "Delete";

        }

    }
);


// REFRESH

refreshButton.addEventListener(
    "click",
    async function () {

        refreshButton.disabled =
            true;

        refreshButton.textContent =
            "Refreshing...";

        try {

            await loadDocuments();

        } finally {

            refreshButton.disabled =
                false;

            refreshButton.textContent =
                "↻ Refresh";

        }

    }
);


// LOGOUT

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


// MESSAGE

function showUploadMessage(
    message,
    type
) {

    uploadMessage.textContent =
        message;

    uploadMessage.className =
        `message ${type}`;

}


// ESCAPE HTML

function escapeHtml(value) {

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");

}


function escapeAttribute(value) {

    return escapeHtml(value);

}


// INITIAL LOAD

loadUserInfo();

loadDocuments();