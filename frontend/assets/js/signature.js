async function signMessage(){
  const message = document.getElementById("message").value;

  const response = await apiRequest("/sign","POST",{message});

  document.getElementById("signature").value = response.signature;
}

async function verifySignature(){
  const message = document.getElementById("message").value;
  const signature = document.getElementById("signature").value;

  const response = await apiRequest("/verify","POST",{message,signature});

  document.getElementById("result").innerText =
    response.valid ? "Verified ✅" : "Invalid ❌";
}