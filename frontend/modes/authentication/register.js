function isValidEmail(email) {
    return /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/.test(String(email || "").trim());
}

function evaluatePasswordStrength(password) {
    const value = String(password || "");
    return {
        minLength: value.length >= 8,
        hasLower: /[a-z]/.test(value),
        hasUpper: /[A-Z]/.test(value),
        hasDigit: /\d/.test(value),
        hasSpecial: /[^A-Za-z0-9]/.test(value),
    };
}

function isStrongPassword(password) {
    const checks = evaluatePasswordStrength(password);
    return checks.minLength && checks.hasLower && checks.hasUpper && checks.hasDigit && checks.hasSpecial;
}

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

    const normalizedEmail = email.trim().toLowerCase();
    if (!isValidEmail(normalizedEmail)) {
        alert("Please enter a valid email address.");
        return;
    }

    if (!isStrongPassword(password)) {
        alert("Password must be at least 8 characters and include uppercase, lowercase, number, and special character.");
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
            email: normalizedEmail
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
        const payload = await SRPAuth.buildRegistrationPayload(normalizedEmail, password, {
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
