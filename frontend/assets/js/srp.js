const SRPAuth = (() => {
  const N_HEX = [
    "EEAF0AB9ADB38DD69C33F80AFA8FC5E860726187752123DAAFCB",
    "B9E4D7EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C2",
    "45E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE",
    "386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007C",
    "B8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DC",
    "A3AD961C62F356208552BB9ED529077096966D670C354E4ABC98",
    "04F1746C08CA237327FFFFFFFFFFFFFFFF"
  ].join("").toLowerCase();
  const N = BigInt(`0x${N_HEX}`);
  const G = 2n;

  function toHex(value) {
    return value.toString(16);
  }

  function fromHex(value) {
    const normalized = String(value).trim().toLowerCase().replace(/^0x/, "");
    return BigInt(`0x${normalized}`);
  }

  function normalizeMod(value, modulus) {
    const result = value % modulus;
    return result >= 0n ? result : result + modulus;
  }

  function modPow(base, exponent, modulus) {
    let result = 1n;
    let currentBase = normalizeMod(base, modulus);
    let currentExponent = exponent;

    while (currentExponent > 0n) {
      if (currentExponent % 2n === 1n) {
        result = (result * currentBase) % modulus;
      }
      currentExponent /= 2n;
      currentBase = (currentBase * currentBase) % modulus;
    }

    return result;
  }

  function randomHex(byteLength = 16) {
    const bytes = new Uint8Array(byteLength);
    crypto.getRandomValues(bytes);
    return Array.from(bytes, (byte) => byte.toString(16).padStart(2, "0")).join("");
  }

  function randomBigInt(byteLength = 32) {
    return fromHex(randomHex(byteLength));
  }

  function reportStep(onStep, message, isError = false) {
    if (typeof onStep === "function") {
      onStep(message, isError);
    }
  }

  async function sha256Hex(...parts) {
    const encoded = new TextEncoder().encode(parts.map((part) => String(part)).join(":"));
    const digest = await crypto.subtle.digest("SHA-256", encoded);
    return Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, "0")).join("");
  }

  async function sha256Int(...parts) {
    return fromHex(await sha256Hex(...parts));
  }

  async function computeMultiplier() {
    return sha256Int(N_HEX, toHex(G));
  }

  async function computePrivateKey(password, salt) {
    return sha256Int(password, String(salt).toLowerCase());
  }

  async function buildRegistrationPayload(email, password, options = {}) {
    const { onStep } = options;

    reportStep(onStep, "Generating a random salt on the client.");
    const salt = randomHex(16);

    reportStep(onStep, "Deriving x from the password and salt.");
    const privateKey = await computePrivateKey(password, salt);

    reportStep(onStep, "Computing the verifier v = g^x mod N.");
    const verifier = modPow(G, privateKey, N);

    reportStep(onStep, "Registration payload is ready.");

    return {
      email: email.trim().toLowerCase(),
      salt,
      verifier: toHex(verifier)
    };
  }

  async function login(email, password, options = {}) {
    const { onStep } = options;
    const normalizedEmail = email.trim().toLowerCase();

    reportStep(onStep, "Generating client secret a and public value A.");
    const secretA = randomBigInt(32);
    const publicA = modPow(G, secretA, N);

    reportStep(onStep, "Sending email and A to the server.");
    const startResponse = await apiRequest("/auth/login/start", "POST", {
      email: normalizedEmail,
      A: toHex(publicA)
    });

    if (startResponse.status !== "success") {
      reportStep(onStep, startResponse.message || "Login start failed.", true);
      return startResponse;
    }

    reportStep(onStep, "Received salt and server public value B.");
    const publicB = fromHex(startResponse.B);
    const multiplier = await computeMultiplier();

    reportStep(onStep, "Deriving x from the password and salt.");
    const privateKey = await computePrivateKey(password, startResponse.salt);

    reportStep(onStep, "Computing scrambling parameter u and shared secret S.");
    const scrambling = await sha256Int(toHex(publicA), toHex(publicB));
    const verifierComponent = modPow(G, privateKey, N);
    const base = normalizeMod(publicB - (multiplier * verifierComponent), N);
    const exponent = secretA + (scrambling * privateKey);
    const sharedSecret = modPow(base, exponent, N);

    reportStep(onStep, "Deriving session key K and client proof M1.");
    const sessionKey = await sha256Hex(toHex(sharedSecret));
    const clientProof = await sha256Hex(toHex(publicA), toHex(publicB), sessionKey);

    reportStep(onStep, "Sending proof M1 to the server for verification.");
    const verifyResponse = await apiRequest("/auth/login/verify", "POST", {
      email: normalizedEmail,
      M1: clientProof
    });

    if (verifyResponse.status !== "success") {
      reportStep(onStep, verifyResponse.message || "Login verification failed.", true);
      return verifyResponse;
    }

    if (verifyResponse.M2) {
      reportStep(onStep, "Validating the server proof M2.");
      const expectedServerProof = await sha256Hex(toHex(publicA), clientProof, sessionKey);
      if (verifyResponse.M2 !== expectedServerProof) {
        reportStep(onStep, "Server proof mismatch.", true);
        return {
          status: "error",
          message: "Server proof mismatch"
        };
      }
    }

    reportStep(onStep, "Server verified the proof. Login successful.");

    return verifyResponse;
  }

  return {
    buildRegistrationPayload,
    login
  };
})();