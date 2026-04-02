async function registerIdentity(){

const identity =
document.getElementById("identity").value;

if(!identity){

alert("Please enter identity");

return;

}

const result =
await apiRequest(
"/register_identity",
"POST",
{identity}
);

localStorage.setItem(
"private_key",
result.private_key
);

localStorage.setItem(
"public_key",
result.public_key
);

document.getElementById(
"status"
).innerText =
"Identity Registered Successfully ✅";

}