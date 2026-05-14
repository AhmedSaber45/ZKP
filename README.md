# ZKP Secure Vault

A premium, cryptographic web application leveraging Zero-Knowledge Proofs (ZKP) for secure operations, including blockchain transactions, digital identities, and privacy-preserving governance.

## Key Features

- **Blockchain Transactions**: Secure, private ledger updates.
- **Digital Signatures**: Non-interactive ZK signatures.
- **Identity Management**: Privacy-preserving attribute verification.
- **Secure Voting**: Anonymous, verifiable governance.
- **Privacy Vault**: AES-256 encrypted secrets management.
- **System Audit**: Comprehensive cryptographic logging.


## 🐳 Quick Start with Docker (Recommended)

The easiest way to run the entire project (Frontend, Backend, and Database) is using Docker.

### Prerequisites:
- Install [Docker Desktop](https://www.docker.com/products/docker-desktop/).

### Steps:
1.  **Run with Docker Compose**:
    ```bash
##############################################   
#### docker-compose up --build  ##############
##############################################   

    ```
2.  **Access the application**:
    - **Frontend (UI)**: [http://localhost:8080](http://localhost:8080)
    - **Backend API**: [http://localhost:5000/api](http://localhost:5000/api)

---

## Blockchain Mode Encryption Notes

Blockchain mode encrypts transaction `data` using **AES-256-GCM** before it is signed and stored.

- Environment variable: `BLOCKCHAIN_DATA_AES_KEY`
- Value format: base64-encoded 32-byte key
- If not set, backend derives a fallback key from `SECRET_KEY` (acceptable for development, not recommended for production)

---

## Local Setup (Alternative)

To run the frontend of this project locally, you need a simple HTTP server. Follow one of the methods below:

### Method 1: Using Python
If you have Python installed, run the following command from the root directory of the project:

```bash
python -m http.server 8000
```
Then open your browser and navigate to: `http://localhost:8000/frontend/index.html`

### Method 2: Using Node.js (npx)
If you have Node.js installed, you can use `serve`:

```bash
npx serve .
```
Then open: `http://localhost:3000/frontend/index.html`

### Method 3: Visual Studio Code (Live Server)
If you use VS Code, you can install the **Live Server** extension and click the "Go Live" button in the bottom right corner while having `index.html` open.

---
*Note: Ensure the backend is running and properly configured in `assets/js/api.js` for full functionality.*

clear cash 
##############################
###### ctrl + f5 #############
##############################