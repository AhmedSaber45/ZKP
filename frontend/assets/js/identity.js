async function registerIdentity(){
  const identity = document.getElementById("identity").value;

  if(!identity){
    alert("Please enter identity");
    return;
  }

  const result = await apiRequest(
    "/identity/register",
    "POST",
    { identity }
  );

  localStorage.setItem("private_key", result.private_key);
  localStorage.setItem("public_key", result.public_key);

  const message = "Identity Registered Successfully ✅";
  const statusEl = document.getElementById("status");
  if(statusEl){
    statusEl.innerText = message;
  }

  localStorage.setItem("identityStatus", message);
}

function clearIdentityStatus(){
  localStorage.removeItem("identityStatus");
  const statusEl = document.getElementById("status");
  if(statusEl){
    statusEl.innerText = "";
  }
}

window.addEventListener("load", function(){
  const saved = localStorage.getItem("identityStatus");
  const statusEl = document.getElementById("status");
  if(saved && statusEl){
    statusEl.innerText = saved;
  }

  const clearButton = document.getElementById("clearStatusBtn");
  if(clearButton){
    clearButton.addEventListener("click", clearIdentityStatus);
  }
});