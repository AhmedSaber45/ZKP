const API_BASE_URL = "http://127.0.0.1:5000/api";

async function apiRequest(endpoint, method = "GET", data = null) {
    const options = {
        method: method,
        headers: {
            "Content-Type": "application/json"
        }
    };
    if (data) options.body = JSON.stringify(data);
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        if (!response.ok) {
            console.error(`HTTP ${response.status}: ${response.statusText}`);
        }
        const jsonData = await response.json();
        return jsonData;
    } catch (err) {
        console.error("API request failed:", err);
        return {status: "error", message: `Network error: ${err.message}`};
    }
}