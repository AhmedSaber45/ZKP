async function login() {
    const username = document.getElementById("username").value;
    const secret = document.getElementById("secret").value;
    const message = document.getElementById("message");

    if (!username || !secret) {
        message.innerText = "Please fill in all fields";
        message.style.color = "#ef4444";
        return;
    }

    try {
        const response = await fetch(`${API}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, secret })
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem("user", username);
            message.innerText = "Login Successful! Redirecting...";
            message.style.color = "#22c55e";
            setTimeout(() => {
                window.location.href = "dashboard.html";
            }, 1000);
        } else {
            message.innerText = data.error || "Login Failed";
            message.style.color = "#ef4444";
        }
    } catch (err) {
        console.error("Login error:", err);
        message.innerText = "Server unreachable. Check backend.";
        message.style.color = "#ef4444";
    }
}
