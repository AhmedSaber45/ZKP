async function login(event) {
    if (event) {
        AuthUI.preventEvent(event);
    }
    
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const logArea = document.getElementById("logArea");
    const loginBtn = document.getElementById("loginBtn");
    
    if (!email || !password) {
        alert("Please enter both email and password.");
        return;
    }

    // Show log area and disable button
    logArea.style.display = "block";
    loginBtn.disabled = true;
    loginBtn.innerHTML = `<span>Processing...</span>`;

    const logger = AuthUI.createMessageLogger("message");
    logger.reset();
    logger.append("Initiating SRP Secure Handshake...");

    try {
        const result = await SRPAuth.login(email, password, {
            onStep: (msg, isError) => {
                logger.append(msg, isError);
                // Auto-scroll log area
                logArea.scrollTop = logArea.scrollHeight;
            }
        });

        if (result.status === "success") {
            logger.append("Authentication Verified. Secure session established!");
            localStorage.setItem("user", email.split('@')[0]); // Use part of email as username

            const sessionCheck = await apiRequest("/auth/me");
            if (sessionCheck.status !== "success") {
                logger.append("Session cookie was not established. Please refresh and login again.", true);
                loginBtn.disabled = false;
                loginBtn.innerHTML = `Authenticate <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path><polyline points="10 17 15 12 10 7"></polyline><line x1="15" y1="12" x2="3" y2="12"></line></svg>`;
                return;
            }
            
            // Premium feel delay before redirect
            setTimeout(() => {
                window.location.href = "../../modes.html";
            }, 1500);
        } else {
            logger.append(result.message || "Authentication Failed.", true);
            loginBtn.disabled = false;
            loginBtn.innerHTML = `Authenticate <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path><polyline points="10 17 15 12 10 7"></polyline><line x1="15" y1="12" x2="3" y2="12"></line></svg>`;
        }
    } catch (err) {
        console.error("Login execution error:", err);
        logger.append("Critical Error during handshake.", true);
        loginBtn.disabled = false;
        loginBtn.innerHTML = `Authenticate <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path><polyline points="10 17 15 12 10 7"></polyline><line x1="15" y1="12" x2="3" y2="12"></line></svg>`;
    }
}