async function vote() {
    const messageEl = document.getElementById("vote-message");

    function setMessage(text, isError = false) {
        if (!messageEl) return;
        messageEl.textContent = text;
        messageEl.style.color = isError ? "#b91c1c" : "#166534";
    }

    const user_id = document.getElementById("user_id").value.trim().toLowerCase();
    const candidate = document.getElementById("candidate").value;

    const p = 23;
    const g = 5;

    const x = parseInt(prompt("Enter your secret (x):"), 10);
    if (Number.isNaN(x)) {
        setMessage("Invalid secret. Please enter a numeric value for x.", true);
        return;
    }
    if (x < 1 || x > 21) {
        setMessage("Invalid secret. Use a value between 1 and 21.", true);
        return;
    }

    const voter_hash = await sha256(user_id);

    const r = Math.floor(Math.random() * 10);

    const t = Math.pow(g, r) % p;
    const y = Math.pow(g, x) % p;

    // Step 1
    const step1 = await apiRequest("/voting/start", "POST", {
        voter_hash: voter_hash,
        commitment: t,
        public_key: y
    });

    if (step1.status === "error") {
        setMessage(step1.message || "Failed to start voting proof.", true);
        return;
    }

    const c = step1.challenge;

    // Step 2
    const s = r + c * x;

    // Step 3
    const result = await apiRequest("/voting/submit", "POST", {
        voter_hash: voter_hash,
        candidate: candidate,
        response: s
    });

    if (result.status === "error") {
        const isInvalidProof = (result.message || "").toLowerCase().includes("invalid proof");
        if (isInvalidProof) {
            setMessage("Invalid secret (x). Please try the correct secret for this voter.", true);
            return;
        }
        setMessage(result.message || "Vote failed.", true);
        return;
    }

    setMessage(result.message || "Vote recorded successfully.");
}


// simple SHA-256
async function sha256(message) {
    const msgBuffer = new TextEncoder().encode(message);
    const hashBuffer = await crypto.subtle.digest("SHA-256", msgBuffer);
    return Array.from(new Uint8Array(hashBuffer))
        .map(b => b.toString(16).padStart(2, "0"))
        .join("");
}