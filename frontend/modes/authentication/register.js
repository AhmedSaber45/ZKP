async function register(event) {
    if (event) {
        AuthUI.preventEvent(event);
    }
    
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const logArea = document.getElementById("logArea");
    const registerBtn = document.getElementById("registerBtn");
    
    if (!email || !password) {
        alert("Email and password are required.");
        return;
    }

    // Show log area and disable button
    logArea.style.display = "block";
    registerBtn.disabled = true;
    registerBtn.innerHTML = `<span>Generating Proofs...</span>`;

    const logger = AuthUI.createMessageLogger("message");
    logger.reset();
    logger.append("Validating secure identity request...");

    try {
        // Step 1: Check if email already exists
        logger.append("Checking email availability on the server...");
        const checkResult = await apiRequest("/auth/register/check", "POST", {
            email: email.trim().toLowerCase()
        });

        if (checkResult.status !== "success") {
            logger.append(checkResult.message || "Could not check email status.", true);
            registerBtn.disabled = false;
            registerBtn.innerHTML = `Create Secure Identity <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"></path><path d="M12 5l7 7-7 7"></path></svg>`;
            return;
        }

        if (checkResult.registered) {
            logger.append("Identity Error: This email is already protected by a vault.", true);
            registerBtn.disabled = false;
            registerBtn.innerHTML = `Create Secure Identity <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"></path><path d="M12 5l7 7-7 7"></path></svg>`;
            return;
        }

        // Step 2: Generate SRP registration payload (Client-side ZKP part)
        const payload = await SRPAuth.buildRegistrationPayload(email, password, {
            onStep: (msg) => {
                logger.append(msg);
                logArea.scrollTop = logArea.scrollHeight;
            }
        });

        // Step 3: Send to server
        logger.append("Dispatching verifier and salt for secure storage...");
        const result = await apiRequest("/auth/register", "POST", payload);

        if (result.status === "success") {
            logger.append("Identity Secured! Your vault is ready.");
            
            setTimeout(() => {
                window.location.href = "login.html";
            }, 2000);
        } else {
            logger.append(result.message || "Registration failed.", true);
            registerBtn.disabled = false;
            registerBtn.innerHTML = `Create Secure Identity <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"></path><path d="M12 5l7 7-7 7"></path></svg>`;
        }
    } catch (err) {
        console.error("Registration execution error:", err);
        logger.append("Unexpected error during identity initialization.", true);
        registerBtn.disabled = false;
        registerBtn.innerHTML = `Create Secure Identity <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"></path><path d="M12 5l7 7-7 7"></path></svg>`;
    }
}
