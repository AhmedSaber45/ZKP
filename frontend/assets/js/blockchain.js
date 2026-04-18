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
        const hasLocalUser = Boolean(localStorage.getItem("user"));
        if (res.status !== "success") {
            localStorage.removeItem("user");
            return false;
        }

        return hasLocalUser;
    } catch (e) {
        localStorage.removeItem("user");
        return false;
    }
}

function redirectToLogin(reason = "Please login first.") {
    const loginUrl = (typeof getRelativePrefix === 'function' ? getRelativePrefix() : "../../") + "modes/authentication/login.html";
    showModal(
        "Session Required", 
        reason, 
        "info",
        {
            text: "Sign In",
            url: loginUrl
        }
    );

    window.location.replace(loginUrl);
}

async function setupWalletPromptFlow() {
    return new Promise((resolve) => {
        const existingModal = document.getElementById("wallet-setup-modal");
        if (existingModal) existingModal.remove();

        const modalHtml = `
            <div id="wallet-setup-modal" class="modal-backdrop active">
                <div class="modal-card" style="max-width: 620px; width: calc(100% - 32px);">
                    <div class="modal-header" style="align-items: flex-start; gap: 14px;">
                        <div class="modal-icon info">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
                        </div>
                        <div style="flex: 1;">
                            <h3 class="modal-title" style="margin-bottom: 6px;">Wallet Setup Required</h3>
                            <p style="color: var(--text-muted); font-size: 0.92rem; line-height: 1.6; margin: 0;">This account is signed in, but no wallet is linked yet. Add your wallet details to continue.</p>
                        </div>
                    </div>

                    <div class="modal-body" style="display: flex; flex-direction: column; gap: 12px; padding-top: 18px;">
                        <div style="padding: 12px; border: 1px dashed var(--glass-border); border-radius: var(--radius-sm); background: rgba(59, 130, 246, 0.06);">
                            <div style="font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase; font-weight: 700; margin-bottom: 5px;">Example Wallet Address</div>
                            <code style="color: var(--primary); font-size: 0.84rem; word-break: break-all;">0xA1b2C3d4E5f60718293aBcD4eF56789012345678</code>
                        </div>

                        <div>
                            <label for="walletSetupAddress" style="display:block; font-size: 0.78rem; font-weight: 700; text-transform: uppercase; color: var(--text-muted); margin-bottom: 6px;">Wallet Address</label>
                            <input id="walletSetupAddress" placeholder="0x..." autocomplete="off">
                        </div>

                        <div>
                            <label for="walletSetupBalance" style="display:block; font-size: 0.78rem; font-weight: 700; text-transform: uppercase; color: var(--text-muted); margin-bottom: 6px;">Initial Balance (Optional)</label>
                            <input id="walletSetupBalance" type="number" min="0" step="0.0001" placeholder="1000" value="1000">
                        </div>

                        <div id="walletSetupError" style="display:none; color: #ef4444; font-size: 0.82rem;"></div>
                    </div>

                    <div class="modal-footer" style="justify-content: space-between; gap: 10px;">
                        <button id="walletSetupCancel" class="glass-btn" style="background: rgba(255,255,255,0.05); color: var(--text-muted); border: 1px solid var(--glass-border);">Cancel</button>
                        <button id="walletSetupSubmit" style="background: var(--primary);">Create Wallet</button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML("beforeend", modalHtml);

        const modalEl = document.getElementById("wallet-setup-modal");
        const addressInputEl = document.getElementById("walletSetupAddress");
        const balanceInputEl = document.getElementById("walletSetupBalance");
        const errorEl = document.getElementById("walletSetupError");
        const cancelBtnEl = document.getElementById("walletSetupCancel");
        const submitBtnEl = document.getElementById("walletSetupSubmit");

        function closeWith(result) {
            if (modalEl) modalEl.remove();
            resolve(result);
        }

        function showError(message) {
            if (!errorEl) return;
            errorEl.style.display = "block";
            errorEl.textContent = message;
        }

        cancelBtnEl?.addEventListener("click", () => {
            setStatus("Wallet setup cancelled.");
            closeWith(null);
        });

        submitBtnEl?.addEventListener("click", async () => {
            const walletAddress = String(addressInputEl?.value || "").trim();
            const initialBalanceText = String(balanceInputEl?.value || "").trim();

            if (!isValidWalletAddress(walletAddress)) {
                showError("Wallet address must use 0x and 40 hexadecimal characters.");
                return;
            }

            if (initialBalanceText && (Number.isNaN(Number(initialBalanceText)) || Number(initialBalanceText) < 0)) {
                showError("Initial balance must be a valid non-negative number.");
                return;
            }

            if (submitBtnEl) {
                submitBtnEl.disabled = true;
                submitBtnEl.textContent = "Creating...";
            }

            setStatus("Setting up secure wallet...");

            const payload = { wallet_address: walletAddress };
            if (initialBalanceText) {
                payload.initial_balance = initialBalanceText;
            }

            const setupRes = await apiRequest("/blockchain/wallet/setup", "POST", payload);
            if (setupRes.status !== "success" || !setupRes.wallet) {
                if (submitBtnEl) {
                    submitBtnEl.disabled = false;
                    submitBtnEl.textContent = "Create Wallet";
                }
                showError(setupRes.message || "Unable to create wallet.");
                setStatus("Wallet setup failed.");
                return;
            }

            closeWith(setupRes.wallet);
        });

        addressInputEl?.focus();
    });
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
            "Before using blockchain mode, enter your wallet address and opening balance.",
            "info"
        );

        const createdWallet = await setupWalletPromptFlow();
        if (!createdWallet) {
            return null;
        }

        showModal("Wallet Ready", "Wallet created successfully. Blockchain mode is now unlocked.", "success");

        return await loadMyWallet();
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

function compactText(value, start = 10, end = 6) {
    const text = String(value || "");
    if (!text) return "-";
    if (text.length <= start + end + 3) return text;
    return `${text.slice(0, start)}...${text.slice(-end)}`;
}

function parseIsoDate(value) {
    const date = new Date(String(value || ""));
    return Number.isNaN(date.getTime()) ? null : date;
}

function toRelativeTime(date) {
    const diffMs = Date.now() - date.getTime();
    const minute = 60 * 1000;
    const hour = 60 * minute;
    const day = 24 * hour;

    if (diffMs < minute) return "just now";
    if (diffMs < hour) {
        const mins = Math.round(diffMs / minute);
        return `${mins} min${mins === 1 ? "" : "s"} ago`;
    }
    if (diffMs < day) {
        const hours = Math.round(diffMs / hour);
        return `${hours} hour${hours === 1 ? "" : "s"} ago`;
    }
    const days = Math.round(diffMs / day);
    return `${days} day${days === 1 ? "" : "s"} ago`;
}

function formatReadableTime(value) {
    const date = parseIsoDate(value);
    if (!date) {
        return {
            label: String(value || "-"),
            relative: "",
            title: String(value || "-")
        };
    }

    return {
        label: date.toLocaleString([], {
            year: "numeric",
            month: "short",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit"
        }),
        relative: toRelativeTime(date),
        title: date.toISOString()
    };
}

function renderChainTable(chainData) {
    const container = document.getElementById("chainTableContainer");
    if (!container) return;

    const chain = Array.isArray(chainData?.chain) ? chainData.chain : [];
    const wallet = String(chainData?.wallet || "").trim().toLowerCase();
    const rows = [];

    for (const block of chain) {
        const blockIndex = block?.index ?? "-";
        const txs = Array.isArray(block?.transactions) ? block.transactions : [];

        for (const tx of txs) {
            const sender = String(tx?.sender || "-");
            const receiver = String(tx?.receiver || "-");
            const timestamp = tx?.timestamp || block?.timestamp || "-";
            const incoming = wallet && receiver.toLowerCase() === wallet;

            rows.push({
                blockIndex,
                txId: tx?.id || "-",
                sender,
                receiver,
                flow: incoming ? "Incoming" : "Outgoing",
                amount: tx?.amount_text || String(tx?.amount ?? "-"),
                timestamp,
                sortTime: parseIsoDate(timestamp)?.getTime() || 0
            });
        }
    }

    if (!rows.length) {
        container.innerHTML = '<p style="padding: 20px; color: var(--text-muted);">No records found in the ledger.</p>';
        return;
    }

    const cards = rows
        .sort((a, b) => b.sortTime - a.sortTime)
        .map((row) => {
            const time = formatReadableTime(row.timestamp);
            const isIncoming = row.flow === "Incoming";

            return `
                <article class="ledger-card">
                    <div class="ledger-card-header">
                        <span class="badge" style="background: rgba(59,130,246,0.12); color: var(--primary);">Block #${row.blockIndex}</span>
                        <span class="ledger-flow ${isIncoming ? "incoming" : "outgoing"}">${row.flow}</span>
                    </div>

                    <div class="ledger-hash" title="${row.txId}">TX ${compactText(row.txId, 14, 8)}</div>

                    <div class="ledger-grid">
                        <div class="ledger-item">
                            <span class="ledger-label">Sender</span>
                            <span class="ledger-value mono" title="${row.sender}">${compactText(row.sender, 12, 8)}</span>
                        </div>
                        <div class="ledger-item">
                            <span class="ledger-label">Recipient</span>
                            <span class="ledger-value mono" title="${row.receiver}">${compactText(row.receiver, 12, 8)}</span>
                        </div>
                        <div class="ledger-item">
                            <span class="ledger-label">Amount</span>
                            <span class="ledger-value amount ${isIncoming ? "incoming" : "outgoing"}">${row.amount} <small>ZKP</small></span>
                        </div>
                        <div class="ledger-item">
                            <span class="ledger-label">Time</span>
                            <span class="ledger-value" title="${time.title}">${time.label}</span>
                            <span class="ledger-subvalue">${time.relative}</span>
                        </div>
                    </div>
                </article>
            `;
        })
        .join("");

    container.innerHTML = `<div class="ledger-card-list">${cards}</div>`;
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
    const isAuthenticated = await ensureAuthenticated();
    if (!isAuthenticated) {
        setStatus("Session expired.");
        redirectToLogin("You must be signed in before entering blockchain mode.");
        return;
    }

    const wallet = await loadMyWallet();
    if (!wallet) return;

    if (document.getElementById("chainTableContainer")) {
        await getChain();
    }

    if (document.getElementById("notificationsList")) {
        await loadNotifications();
    }
});