// Central Authentication Logic for ZKP Secure Vault

/**
 * Handles the login process by sending credentials to the ZKP API.
 * Redirects to the dashboard on success.
 */
async function login() {
    const email = document.getElementById("email").value;
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const secret = document.getElementById("secret").value;
    const message = document.getElementById("message");

    if (!username || !secret) {
        message.innerText = "Error: Username and Secret Key are required.";
        message.style.color = "#ef4444";
        return;
    }

    try {
        // We use the simplified login flow as per the current backend implementation
        const response = await fetch(`${API}/auth/login`, {
            method: "POST",
            credentials: "include",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, secret })
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem("user", username);
            message.innerText = "Access Granted. Redirecting to Vault...";
            message.style.color = "#22c55e";
            
            // Artificial delay for premium feel
            setTimeout(() => {
                window.location.href = "modes.html";
            }, 1000);
        } else {
            message.innerText = data.error || "Authentication Failed";
            message.style.color = "#ef4444";
        }
    } catch (err) {
        console.error("Login error:", err);
        message.innerText = "Connection Error: Backend unreachable.";
        message.style.color = "#ef4444";
    }
}

/**
 * Handles the registration process.
 */
async function register() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const message = document.getElementById("message");

    if (!email || !password) {
        message.innerText = "Error: Email and Password are required.";
        message.style.color = "#ef4444";
        return;
    }

    try {
        message.innerText = "Registering secure identity...";
        message.style.color = "var(--primary)";

        const response = await fetch(`${API}/auth/register`, {
            method: "POST",
            credentials: "include",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok) {
            message.innerText = "Registration Successful! You can now sign in.";
            message.style.color = "#22c55e";
            
            setTimeout(() => {
                window.location.href = "index.html";
            }, 2000);
        } else {
            message.innerText = data.error || "Registration Failed";
            message.style.color = "#ef4444";
        }
    } catch (err) {
        console.error("Registration error:", err);
        message.innerText = "Connection Error: Backend unreachable.";
        message.style.color = "#ef4444";
    }
}