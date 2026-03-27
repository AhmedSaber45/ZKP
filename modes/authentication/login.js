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

    const result = await SRPAuth.login(email, password, {
        onStep: logger.append
    });

    if (result.status !== "success") {
        logger.append(result.message || "Login failed.", true);
    }
}