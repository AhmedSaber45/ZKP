async function castSecureVote() {
    const messageEl = document.getElementById("vote-message");

    function setMessage(text, isError = false) {
        if (!messageEl) return;
        messageEl.textContent = text;
        messageEl.style.color = isError ? "#ef4444" : "#22c55e";
    }

    const userIdEl = document.getElementById("voter-id-input");
    const secretXEl = document.getElementById("voter-secret-input");
    const selected = document.querySelector('input[name="choice"]:checked');

    if (!selected) {
        setMessage("Please select a proposal first.", true);
        return;
    }

    const user_id = userIdEl ? userIdEl.value.trim().toLowerCase() : localStorage.getItem("user") || "";
    if (!user_id) {
        setMessage("User ID is required for verification.", true);
        return;
    }

    const xVal = secretXEl ? secretXEl.value : prompt("Enter your secret (x) between 1-21:");
    const x = parseInt(xVal, 10);

    if (Number.isNaN(x) || x < 1 || x > 21) {
        setMessage("Invalid secret. Use a value between 1 and 21.", true);
        return;
    }

    const candidate = selected.value;
    const p = 23;
    const g = 5;

    setMessage("Initializing ZKP protocol...");

    try {
        const voter_hash = await sha256(user_id);
        const r = Math.floor(Math.random() * 10) + 1; // 1-10
        const t = Math.pow(g, r) % p;
        const y = Math.pow(g, x) % p;

        // Step 1: Start
        const step1Res = await fetch(`${API}/voting/start`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                voter_hash: voter_hash,
                commitment: t,
                public_key: y
            })
        });

        const step1 = await step1Res.json();

        if (step1.status === "error") {
            setMessage(step1.message || "Protocol start failed.", true);
            return;
        }

        const c = step1.challenge;

        // Step 2: Response
        const s = r + c * x;

        // Step 3: Submit proof and vote
        const step2Res = await fetch(`${API}/voting/submit`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                voter_hash: voter_hash,
                candidate: candidate,
                response: s
            })
        });

        const result = await step2Res.json();

        if (result.status === "error") {
            setMessage(result.message || "Verification failed.", true);
            return;
        }

        setMessage("Vote verified and recorded successfully!", false);
        
        // Refresh results if function exists
        if (typeof fetchResults === "function") {
            fetchResults();
        }

    } catch (err) {
        console.error(err);
        setMessage("Connection error. Is the backend running?", true);
    }
}

async function sha256(message) {
    const msgBuffer = new TextEncoder().encode(message);
    const hashBuffer = await crypto.subtle.digest("SHA-256", msgBuffer);
    return Array.from(new Uint8Array(hashBuffer))
        .map(b => b.toString(16).padStart(2, "0"))
        .join("");
}