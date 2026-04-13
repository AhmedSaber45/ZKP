const API_HOST = window.location.hostname === "127.0.0.1" ? "127.0.0.1" : "localhost";
const API_BASE_URL = `http://${API_HOST}:5000/api`;

async function apiRequest(endpoint, method = "GET", data = null) {
    const options = {
        method: method,
        credentials: "include",
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
        return await response.json();
    } catch (err) {
        console.error("API request failed:", err);
        return {status: "error", message: `Network error: ${err.message}`};
    }
}

const API = API_BASE_URL;

async function testBackend() {
    try {
        const res = await fetch(`${API_BASE_URL}/health`);
        const data = await res.json();
        console.log("[API] Connection Status:", data.status === "ok" ? "Connected ✅" : "Issue ❌");
    } catch (err) {
        console.warn("[API] Backend unreachable. Check if Docker containers are running.");
    }
}

testBackend();
