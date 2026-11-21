// Production Backend URL
const API_BASE_URL = "https://ai-customer-support-agent-030v.onrender.com";

async function apiRequest(endpoint, options = {}) {

    const token = localStorage.getItem("access_token");

    const headers = new Headers(options.headers || {});

    // Authentication
    if (token) {
        headers.set("Authorization", `Bearer ${token}`);
    }

    // Support JSON and PDF/FormData uploads
    if (!(options.body instanceof FormData) && !headers.has("Content-Type")) {
        headers.set("Content-Type", "application/json");
    }

    const response = await fetch(
        `${API_BASE_URL}${endpoint}`,
        {
            ...options,
            headers
        }
    );

    // Handle response
    const responseText = await response.text();

    let data = {};

    try {
        data = responseText ? JSON.parse(responseText) : {};
    } catch {
        data = { detail: responseText };
    }

    if (!response.ok) {
        throw new Error(
            data.detail || "Something went wrong"
        );
    }

    return data;
}