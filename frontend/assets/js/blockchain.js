function isValidWalletAddress(value) {
    return /^0x[a-fA-F0-9]{40}$/.test(String(value || "").trim());
}

function setStatus(message) {
    const statusEl = document.getElementById("status");
    if (statusEl) statusEl.textContent = message;
}

async function ensureAuthenticated() {
    try {
        const res = await apiRequest("/auth/me");
        return res.status === "success";
    } catch (e) {
        return false;
    }
}

function redirectToLogin(reason = "Please login first.") {
    showModal(
        "Session Required", 
        reason, 
        "info",
        {
            text: "Sign In",
            url: (typeof getRelativePrefix === 'function' ? getRelativePrefix() : "../../") + "modes/authentication/login.html"
        }
    );
}

async function loadMyWallet() {
    const authenticated = await ensureAuthenticated();
    if (!authenticated) {
        setStatus("Session expired.");
        redirectToLogin("You must be signed in to access blockchain features.");
        return null;
    }

    setStatus("Loading secure wallet...");
    const res = await apiRequest("/blockchain/wallet");

    if (res.needsSetup) {
        showModal(
            "Wallet Required", 
            "It looks like you haven't set up a blockchain wallet yet. Please use the 'Create Identity' feature in the Authentication section to link a wallet to your account.", 
            "info",
            {
                text: "Create Identity Now",
                url: typeof getRelativePrefix === 'function' ? getRelativePrefix() + "modes/authentication/register.html" : "../authentication/register.html"
            }
        );
        return null;
    }

    if (res.status !== "success" || !res.wallet) {
        setStatus(res.message || "Initialization failed.");
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

    setStatus("Wallet verified.");
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
    if (latestHashEl) latestHashEl.textContent = latestBlock?.hash ? `${latestBlock.hash.slice(0, 10)}...` : "-";
}

function renderNotifications(notifications) {
    const listEl = document.getElementById("notificationsList");
    if (!listEl) return;

    const safeItems = Array.isArray(notifications) ? notifications : [];
    listEl.innerHTML = safeItems.length
        ? safeItems
            .map((item) => `
                <div class="notification-item">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: var(--primary); margin-top: 2px;"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                    <div style="display: flex; flex-direction: column; gap: 4px;">
                        <span style="font-weight: 500;">${item.message}</span>
                        <span class="notification-time">${item.created_at}</span>
                    </div>
                </div>`)
            .join("")
        : '<p style="color: var(--text-muted); padding: 10px; font-size: 0.85rem;">No recent activity.</p>';
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
        container.innerHTML = '<p style="padding: 20px; color: var(--text-muted);">No records found in the ledger.</p>';
        return;
    }

    const tableRows = rows
        .map(
            (row) =>
                `<tr>
                    <td><span class="badge" style="background: rgba(59,130,246,0.1); color: var(--primary); font-family: monospace;">#${row.blockIndex}</span></td>
                    <td class="hash-cell">${row.txId.slice(0, 12)}...</td>
                    <td style="font-size: 0.75rem; opacity: 0.8;">${row.sender.slice(0, 8)}...</td>
                    <td style="font-size: 0.75rem; opacity: 0.8;">${row.receiver.slice(0, 8)}...</td>
                    <td class="amount-cell">${row.amount} <span style="font-size: 0.6rem; color: var(--text-muted);">ZKP</span></td>
                    <td style="font-size: 0.7rem; color: var(--text-muted);">${row.timestamp}</td>
                </tr>`
        )
        .join("");

    container.innerHTML = `
        <table>
            <thead>
                <tr>
                    <th>Block</th>
                    <th>TX Hash</th>
                    <th>Sender</th>
                    <th>Recipient</th>
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
        showModal("Invalid Input", "Please fill in all transaction details.", "error");
        return;
    }

    if (!isValidWalletAddress(sender) || !isValidWalletAddress(receiver)) {
        showModal("Address Error", "Wallet addresses must be in 0x format (40 hex characters).", "error");
        return;
    }

    if (Number.isNaN(amount) || amount <= 0) {
        showModal("Amount Error", "Please enter a valid amount greater than zero.", "error");
        return;
    }

    setStatus("Encrypting transaction...");
    try {
        const res = await apiRequest("/blockchain/transaction", "POST", {
            receiver,
            amount: amountText,
            data,
        });

        if (res.status !== "success" || !res.transaction) {
            showModal("Encryption Failed", res.message || "Could not process transaction.", "error");
            setStatus("Transaction failed.");
            return;
        }

        showModal("Success", `Transaction ${res.transaction.id.slice(0,10)}... broadcasted to pending pool.`, "success");
        if (receiverEl) receiverEl.value = "";
        if (amountEl) amountEl.value = "";
        if (dataEl) dataEl.value = "";
        await loadMyWallet();
    } catch (e) {
        showModal("Network Error", "Unable to reach blockchain API.", "error");
    }
}

async function mineBlock() {
    const minerEl = document.getElementById("miner");
    const miner = String(minerEl?.value || "").trim();

    if (miner && !isValidWalletAddress(miner)) {
        showModal("Invalid Miner", "Miner wallet address format is incorrect.", "error");
        return;
    }

    setStatus("Mining block...");
    try {
        const res = await apiRequest("/blockchain/mine", "POST", { miner });

        if (res.status !== "success" || !res.block) {
            showModal("Mining Error", res.message || "Failed to mine block.", "error");
            setStatus("Mining abandoned.");
            return;
        }

        showModal("Block Mined", `Block #${res.block.index} successfully integrated into chain.`, "success");
        await loadMyWallet();
    } catch (e) {
        showModal("Network Error", "Unable to reach blockchain API.", "error");
    }
}

async function getChain() {
    setStatus("Loading ledger...");
    try {
        const res = await apiRequest("/blockchain/chain");
        const tableContainer = document.getElementById("chainTableContainer");

        if (!res.chain || !tableContainer) {
            setStatus("Sync error.");
            return;
        }

        renderChainTable(res);
        updateSummary(res);
        setStatus("Ledger synced.");
    } catch (e) {
        setStatus("Network error.");
    }
}

async function validateChain() {
    setStatus("Auditing chain...");
    try {
        const res = await apiRequest("/blockchain/validate");

        if (typeof res.valid !== "boolean") {
            showModal("Audit Failed", res.message || "Validation technical error.", "error");
            return;
        }

        if (res.valid) {
            showModal("Integrity Verified", "The blockchain database is valid and untampered.", "success");
        } else {
            showModal("Security Alert", "Blockchain integrity compromised! Data tampered.", "error");
        }
    } catch (e) {
        showModal("Audit Error", "Unable to perform chain validation.", "error");
    }
}

async function loadNotifications() {
    try {
        const res = await apiRequest("/blockchain/notifications");
        if (res.status !== "success") return;
        renderNotifications(res.notifications || []);
    } catch (e) {}
}

window.addEventListener("load", async () => {
    const wallet = await loadMyWallet();
    if (!wallet) return;

    if (document.getElementById("chainTableContainer")) {
        await getChain();
    }

    if (document.getElementById("notificationsList")) {
        await loadNotifications();
    }
});