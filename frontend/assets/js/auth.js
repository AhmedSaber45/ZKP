function delay(milliseconds) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, milliseconds);
  });
}

async function login(event) {
  AuthUI.preventEvent(event);
  const logger = AuthUI.createMessageLogger("message");

  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  logger.reset();
  logger.append("Checking email and password.");

  if (!email || !password) {
    logger.append("Email and password are required.", true);
    return;
  }

  const response = await SRPAuth.login(email, password, {
    onStep: logger.append
  });

  if (response.status === "success") {
    logger.append("Redirecting to the dashboard.");
    localStorage.setItem("user", email.trim().toLowerCase());
    await delay(1200);
    window.location.href = "dashboard.html";
    return;
  }

  logger.append(response.message || "Login failed.", true);
}

async function register(event) {
  AuthUI.preventEvent(event);
  const logger = AuthUI.createMessageLogger("message");

  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  logger.reset();
  logger.append("Checking email and password.");

  if (!email || !password) {
    logger.append("Email and password are required.", true);
    return;
  }

  logger.append("Checking whether this email is already registered.");
  const checkResponse = await apiRequest("/auth/register/check", "POST", {
    email: email.trim().toLowerCase()
  });

  if (checkResponse.status !== "success") {
    logger.append(checkResponse.message || "Could not check email status.", true);
    return;
  }

  if (checkResponse.registered) {
    logger.append("Email already registered", true);
    return;
  }

  const payload = await SRPAuth.buildRegistrationPayload(email, password, {
    onStep: logger.append
  });

  logger.append("Sending email, salt, and verifier to the server.");
  const response = await apiRequest("/auth/register", "POST", payload);

  logger.append(
    response.message || "Registration failed.",
    response.status !== "success"
  );
}
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
