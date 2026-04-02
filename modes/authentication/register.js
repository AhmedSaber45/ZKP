async function register() {

    const username = document.getElementById("username").value;
    const secret = document.getElementById("secret").value;

    const result = await apiRequest("/auth/register", "POST", {
        username: username,
        secret: secret
    });

    alert(result.message);
}