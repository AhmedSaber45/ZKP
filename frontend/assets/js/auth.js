async function login() {
  const username = document.getElementById("username").value;
  const secret = document.getElementById("secret").value;

  const response = await apiRequest("/login", "POST", {
    username: username,
    secret: secret
  });

  if (response.success) {
    localStorage.setItem("user", username);
    window.location.href = "dashboard.html";
  } else {
    document.getElementById("message").innerText = "Login Failed";
  }
}
function generateKey(){
  const randomKey = Math.random().toString(36).substring(2);
  document.getElementById("publicKey").value = randomKey;
}

async function register(){
  const username = document.getElementById("username").value;
  const secret = document.getElementById("secret").value;
  const publicKey = document.getElementById("publicKey").value;

  const response = await apiRequest("/register","POST",{
    username,
    secret,
    publicKey
  });

  document.getElementById("message").innerText = response.message;
}