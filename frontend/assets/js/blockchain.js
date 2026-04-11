function isValidWalletAddress(value) {
    return /^0x[a-fA-F0-9]{40}$/.test(String(value || "").trim());
}

function setStatus(message) {
    const statusEl = document.getElementById("status");
    if (statusEl) statusEl.textContent = message;
}

async function ensureAuthenticated() {
    const res = await apiRequest("/auth/me");
    return res.status === "success";
}

function redirectToLogin(reason = "Please login first.") {
    alert(reason);
    window.location.href = "../authentication/login.html";
}

async function loadMyWallet() {
    const authenticated = await ensureAuthenticated();
    if (!authenticated) {
        setStatus("You are not logged in. Please login first.");
        redirectToLogin("You are signed out. Please login to access Blockchain.");
        return null;
    }

    setStatus("Loading your wallet from database...");
    const res = await apiRequest("/blockchain/wallet");

    if (res.needsSetup) {
        while (true) {
            const enteredWallet = prompt("First blockchain access: Enter your wallet address (0x + 40 hex characters)");
            if (enteredWallet === null) {
                setStatus("Wallet setup cancelled.");
                return null;
            }

            const walletAddress = String(enteredWallet || "").trim().toLowerCase();
            if (!isValidWalletAddress(walletAddress)) {
                setStatus("Wallet format invalid. Use 0x + 40 hex characters.");
                continue;
            }

            const enteredBalance = prompt("Enter your initial balance (example: 1000)");
            if (enteredBalance === null) {
                setStatus("Wallet setup cancelled.");
                return null;
            }

            const initialBalance = String(enteredBalance || "").trim();
            if (initialBalance === "" || Number.isNaN(Number(initialBalance)) || Number(initialBalance) < 0) {
                setStatus("Initial balance must be a non-negative number.");
                continue;
            }

            const setupRes = await apiRequest("/blockchain/wallet/setup", "POST", {
                wallet_address: walletAddress,
                initial_balance: initialBalance,
            });

            if (setupRes.status === "success") {
                setStatus("Wallet setup completed.");
                return await loadMyWallet();
            }

            setStatus(setupRes.message || "Wallet setup failed. Try again.");
        }
    }

    if (res.status !== "success" || !res.wallet) {
        setStatus(res.message || "Please login first.");
        if ((res.message || "").toLowerCase().includes("login") || (res.message || "").toLowerCase().includes("auth")) {
            redirectToLogin("Your session expired. Please login again.");
        }
        return null;
    }

    const senderEl = document.getElementById("sender");
    const minerEl = document.getElementById("miner");
    const currentWalletEl = document.getElementById("currentWallet");
    const walletAddressEl = document.getElementById("walletAddress");

    if (senderEl) senderEl.value = res.wallet.address;
    if (minerEl && !minerEl.value) minerEl.value = res.wallet.address;
    if (currentWalletEl) currentWalletEl.textContent = res.wallet.address;
    if (walletAddressEl) walletAddressEl.textContent = res.wallet.address;

    const balanceEl = document.getElementById("currentBalance");
    if (balanceEl) balanceEl.textContent = Number(res.wallet.balance || 0).toFixed(4);

    setStatus("Wallet loaded.");
    return res.wallet;
}

function updateSummary(chainData) {
    const chain = chainData.chain || [];
    const latestBlock = chain.length ? chain[chain.length - 1] : null;
    const totalTx = chain.reduce((acc, block) => acc + (block.transactions?.length || 0), 0);

    const chainLengthEl = document.getElementById("chainLength");
    const txCountEl = document.getElementById("txCount");
    const latestHashEl = document.getElementById("latestHash");

    if (chainLengthEl) chainLengthEl.textContent = String(chainData.length || 0);
    if (txCountEl) txCountEl.textContent = String(chainData.transactionCount ?? totalTx);
    if (latestHashEl) latestHashEl.textContent = latestBlock?.hash ? `${latestBlock.hash.slice(0, 18)}...` : "-";
}

function renderNotifications(notifications) {
    const listEl = document.getElementById("notificationsList");
    if (!listEl) return;

    const safeItems = Array.isArray(notifications) ? notifications : [];
    listEl.innerHTML = safeItems.length
        ? safeItems
            .map((item) => `<li>[${item.created_at}] ${item.message}</li>`)
            .join("")
        : "<li>No notifications yet.</li>";
}

function renderChainTable(chainData) {
    const container = document.getElementById("chainTableContainer");
    if (!container) return;

    const chain = Array.isArray(chainData?.chain) ? chainData.chain : [];
    const rows = [];

    for (const block of chain) {
        const blockIndex = block?.index ?? "-";
        const txs = Array.isArray(block?.transactions) ? block.transactions : [];

        for (const tx of txs) {
            rows.push({
                blockIndex,
                txId: tx?.id || "-",
                sender: tx?.sender || "-",
                receiver: tx?.receiver || "-",
                amount: tx?.amount_text || String(tx?.amount ?? "-"),
                timestamp: tx?.timestamp || block?.timestamp || "-",
            });
        }
    }

    if (!rows.length) {
        container.innerHTML = "<p>No records found for your wallet.</p>";
        return;
    }

    const tableRows = rows
        .map(
            (row) =>
                `<tr>
                    <td>${row.blockIndex}</td>
                    <td>${row.txId}</td>
                    <td>${row.sender}</td>
                    <td>${row.receiver}</td>
                    <td>${row.amount}</td>
                    <td>${row.timestamp}</td>
                </tr>`
        )
        .join("");

    container.innerHTML = `
        <table border="1" cellspacing="0" cellpadding="8">
            <thead>
                <tr>
                    <th>Block</th>
                    <th>Transaction ID</th>
                    <th>Sender</th>
                    <th>Receiver</th>
                    <th>Amount</th>
                    <th>Timestamp</th>
                </tr>
            </thead>
            <tbody>
                ${tableRows}
            </tbody>
        </table>
    `;
}

async function sendTransaction() {
    const senderEl = document.getElementById("sender");
    const receiverEl = document.getElementById("receiver");
    const amountEl = document.getElementById("amount");
    const dataEl = document.getElementById("txData");

    const sender = String(senderEl?.value || "").trim();
    const receiver = String(receiverEl?.value || "").trim();
    const amountText = String(amountEl?.value || "").trim();
    const data = String(dataEl?.value || "").trim();
    const amount = Number(amountText);

    if (!sender || !receiver || !amountText) {
        setStatus("Please complete sender, receiver, and amount.");
        return;
    }

    if (!isValidWalletAddress(sender) || !isValidWalletAddress(receiver)) {
        setStatus("Wallet addresses must match 0x + 40 hex format.");
        return;
    }

    if (Number.isNaN(amount) || amount <= 0) {
        setStatus("Amount must be a valid number greater than zero.");
        return;
    }

    setStatus("Creating secure transaction...");
    const res = await apiRequest("/blockchain/transaction", "POST", {
        receiver,
        amount: amountText,
        data,
    });

    if (res.status !== "success" || !res.transaction) {
        setStatus(res.message || "Transaction creation failed.");
        return;
    }

    setStatus(`Transaction ${res.transaction.id} created and added to pending pool.`);
    if (receiverEl) receiverEl.value = "";
    if (amountEl) amountEl.value = "";
    if (dataEl) dataEl.value = "";
    await loadMyWallet();
}

async function mineBlock() {
    const minerEl = document.getElementById("miner");
    const miner = String(minerEl?.value || "").trim();

    if (miner && !isValidWalletAddress(miner)) {
        setStatus("Miner wallet address is invalid.");
        return;
    }

    setStatus("Mining block and confirming pending transactions...");
    const res = await apiRequest("/blockchain/mine", "POST", { miner });

    if (res.status !== "success" || !res.block) {
        setStatus(res.message || "Mining failed.");
        return;
    }

    setStatus(`Block #${res.block.index} mined successfully.`);
    await loadMyWallet();
}

async function getChain() {
    setStatus("Loading your blockchain records...");
    const res = await apiRequest("/blockchain/chain");
    const tableContainer = document.getElementById("chainTableContainer");

    if (!res.chain || !tableContainer) {
        setStatus(res.message || "Failed to load chain.");
        return;
    }

    renderChainTable(res);
    updateSummary(res);
    setStatus("Your records loaded.");
}

async function validateChain() {
    setStatus("Validating blockchain integrity...");
    const res = await apiRequest("/blockchain/validate");

    if (typeof res.valid !== "boolean") {
        setStatus(res.message || "Validation failed.");
        return;
    }

    setStatus(res.valid ? "Chain is valid." : "Chain is invalid.");
}

async function loadNotifications() {
    const listEl = document.getElementById("notificationsList");
    if (!listEl) return;

    const res = await apiRequest("/blockchain/notifications");
    if (res.status !== "success") {
        setStatus(res.message || "Failed to load notifications.");
        return;
    }

    renderNotifications(res.notifications || []);
}

window.addEventListener("load", async () => {
    const wallet = await loadMyWallet();
    if (!wallet) {
        return;
    }

    if (document.getElementById("chainTableContainer")) {
        await getChain();
    }

    if (document.getElementById("notificationsList")) {
        await loadNotifications();
    }
});