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
    const checkResult = await apiRequest("/auth/register/check", "POST", {
        email: email.trim().toLowerCase()
    });

    if (checkResult.status !== "success") {
        logger.append(checkResult.message || "Could not check email status.", true);
        return;
    }

    if (checkResult.registered) {
        logger.append("Email already registered", true);
        return;
    }

    const payload = await SRPAuth.buildRegistrationPayload(email, password, {
        onStep: logger.append
    });

    logger.append("Sending email, salt, and verifier to the server.");

    const result = await apiRequest("/auth/register", "POST", payload);

    logger.append(result.message || "Registration failed.", result.status !== "success");
}