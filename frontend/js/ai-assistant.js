const token =
    localStorage.getItem("access_token");


if (!token) {

    window.location.href =
        "login.html";

}


/* =========================
   DOM
========================= */

const customerSelect =
    document.getElementById(
        "customerSelect"
    );


const newChatButton =
    document.getElementById(
        "newChatButton"
    );


const clearChatButton =
    document.getElementById(
        "clearChatButton"
    );


const messageInput =
    document.getElementById(
        "messageInput"
    );


const sendButton =
    document.getElementById(
        "sendButton"
    );


const messagesContainer =
    document.getElementById(
        "messages"
    );


const welcomeMessage =
    document.getElementById(
        "welcomeMessage"
    );


const typingIndicator =
    document.getElementById(
        "typingIndicator"
    );


const errorMessage =
    document.getElementById(
        "errorMessage"
    );


const conversationStatus =
    document.getElementById(
        "conversationStatus"
    );


const conversationIdElement =
    document.getElementById(
        "conversationId"
    );


const logoutButton =
    document.getElementById(
        "logoutButton"
    );


/* =========================
   STATE
========================= */

let currentConversationId =
    null;


let currentCustomerId =
    null;


let customers = [];


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

        console.error(
            "User information error:",
            error
        );

    }

}


/* =========================
   LOAD CUSTOMERS
========================= */

async function loadCustomers() {

    try {

        const data =
            await apiRequest(
                "/customers"
            );


        if (Array.isArray(data)) {

            customers = data;

        } else if (
            Array.isArray(data.customers)
        ) {

            customers =
                data.customers;

        } else {

            customers = [];

        }


        renderCustomers();


    } catch (error) {

        console.error(
            "Failed to load customers:",
            error
        );


        showError(
            "Unable to load customers: " +
            error.message
        );

    }

}


/* =========================
   RENDER CUSTOMERS
========================= */

function renderCustomers() {

    customerSelect.innerHTML = `
        <option value="">
            Select customer
        </option>
    `;


    customers.forEach(customer => {

        const option =
            document.createElement(
                "option"
            );


        option.value =
            customer.id;


        option.textContent =
            `${customer.name} (#${customer.id})`;


        customerSelect.appendChild(
            option
        );

    });

}


/* =========================
   CUSTOMER CHANGE
========================= */

customerSelect.addEventListener(
    "change",
    async function () {

        const customerId =
            Number(
                customerSelect.value
            );


        if (!customerId) {

            currentCustomerId =
                null;

            currentConversationId =
                null;

            updateConversationInfo();

            return;

        }


        currentCustomerId =
            customerId;


        currentConversationId =
            null;


        clearMessages();

        updateConversationInfo();

        hideError();

    }
);


/* =========================
   CREATE CONVERSATION
========================= */

async function createConversation() {

    if (!currentCustomerId) {

        showError(
            "Please select a customer first."
        );

        return null;

    }


    try {

        const customer =
            customers.find(
                item =>
                    Number(item.id) ===
                    Number(currentCustomerId)
            );


        const customerName =
            customer?.name ||
            "Customer";


        const data =
            await apiRequest(
                "/conversations",
                {
                    method: "POST",

                    body: JSON.stringify({
                        customer_id:
                            Number(
                                currentCustomerId
                            ),

                        title:
                            `AI Support - ${customerName}`
                    })
                }
            );


        const conversation =
            data.conversation;


        currentConversationId =
            conversation.id;


        updateConversationInfo();


        return conversation.id;


    } catch (error) {

        console.error(
            "Conversation creation error:",
            error
        );


        showError(
            error.message
        );


        return null;

    }

}


/* =========================
   NEW CHAT
========================= */

newChatButton.addEventListener(
    "click",
    async function () {

        if (!currentCustomerId) {

            showError(
                "Select a customer before starting a conversation."
            );

            return;

        }


        clearMessages();

        currentConversationId =
            null;

        updateConversationInfo();

        hideError();

    }
);


/* =========================
   SEND MESSAGE
========================= */

async function sendMessage() {

    const message =
        messageInput.value.trim();


    if (!message) {
        return;
    }


    if (!currentCustomerId) {

        showError(
            "Please select a customer first."
        );

        return;

    }


    sendButton.disabled =
        true;

    messageInput.disabled =
        true;


    hideError();


    try {

        /*
         * Create a conversation automatically
         * if this is the first message.
         */

        if (!currentConversationId) {

            const conversationId =
                await createConversation();


            if (!conversationId) {

                return;

            }

        }


        addMessage(
            "user",
            message
        );


        messageInput.value = "";

        resizeTextarea();


        showTyping();


        const data =
            await apiRequest(
                "/ai/chat",
                {
                    method: "POST",

                    body: JSON.stringify({

                        conversation_id:
                            Number(
                                currentConversationId
                            ),

                        message:
                            message

                    })
                }
            );


        hideTyping();


        /*
         * Backend returns reply + history.
         */

        if (data.reply) {

            addMessage(
                "ai",
                data.reply
            );

        }


    } catch (error) {

        hideTyping();


        console.error(
            "AI chat error:",
            error
        );


        showError(
            error.message
        );


    } finally {

        sendButton.disabled =
            false;

        messageInput.disabled =
            false;

        messageInput.focus();

    }

}


/* =========================
   SEND BUTTON
========================= */

sendButton.addEventListener(
    "click",
    sendMessage
);


/* =========================
   ENTER TO SEND
========================= */

messageInput.addEventListener(
    "keydown",
    function (event) {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            sendMessage();

        }

    }
);


/* =========================
   AUTO RESIZE
========================= */

messageInput.addEventListener(
    "input",
    resizeTextarea
);


function resizeTextarea() {

    messageInput.style.height =
        "auto";


    messageInput.style.height =
        Math.min(
            messageInput.scrollHeight,
            130
        ) + "px";

}


/* =========================
   ADD MESSAGE
========================= */

function addMessage(
    sender,
    message
) {

    if (welcomeMessage) {

        welcomeMessage.style.display =
            "none";

    }


    const row =
        document.createElement(
            "div"
        );


    row.className =
        `message-row ${sender}`;


    const bubble =
        document.createElement(
            "div"
        );


    bubble.className =
        "message-bubble";


    const meta =
        document.createElement(
            "div"
        );


    meta.className =
        "message-meta";


    meta.textContent =
        sender === "user"
            ? "You"
            : "AI Support Agent";


    const content =
        document.createElement(
            "div"
        );


    content.textContent =
        message;


    bubble.appendChild(meta);

    bubble.appendChild(content);

    row.appendChild(bubble);


    messagesContainer.insertBefore(
        row,
        typingIndicator
    );


    scrollToBottom();

}


/* =========================
   CLEAR CHAT
========================= */

clearChatButton.addEventListener(
    "click",
    function () {

        clearMessages();

    }
);


function clearMessages() {

    const messageRows =
        messagesContainer.querySelectorAll(
            ".message-row"
        );


    messageRows.forEach(
        row => row.remove()
    );


    if (welcomeMessage) {

        welcomeMessage.style.display =
            "block";

    }


    hideError();


    scrollToBottom();

}


/* =========================
   TYPING
========================= */

function showTyping() {

    typingIndicator.classList.add(
        "show"
    );


    scrollToBottom();

}


function hideTyping() {

    typingIndicator.classList.remove(
        "show"
    );

}


/* =========================
   CONVERSATION INFO
========================= */

function updateConversationInfo() {

    if (!currentConversationId) {

        conversationStatus.textContent =
            "No conversation selected.";

        conversationIdElement.textContent =
            "—";

        return;

    }


    conversationStatus.textContent =
        "Conversation active.";


    conversationIdElement.textContent =
        `#${currentConversationId}`;

}


/* =========================
   ERROR
========================= */

function showError(message) {

    errorMessage.textContent =
        message;

    errorMessage.classList.add(
        "show"
    );

}


function hideError() {

    errorMessage.textContent =
        "";

    errorMessage.classList.remove(
        "show"
    );

}


/* =========================
   SUGGESTIONS
========================= */

document
    .querySelectorAll(".suggestion")
    .forEach(button => {

        button.addEventListener(
            "click",
            function () {

                messageInput.value =
                    button.dataset.message;

                resizeTextarea();

                messageInput.focus();

            }
        );

    });


/* =========================
   SCROLL
========================= */

function scrollToBottom() {

    setTimeout(
        () => {

            messagesContainer.scrollTop =
                messagesContainer.scrollHeight;

        },
        50
    );

}


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
   INITIALIZE
========================= */

loadUserInfo();

loadCustomers();