async function signMessage(){

const message =
document.getElementById("message").value;

if(!message){

alert("Enter message first");

return;

}

const private_key =
localStorage.getItem("private_key");

if(!private_key){

alert("Register identity first");

return;

}

const result =
await apiRequest(
"/sign",
"POST",
{
message,
private_key
}
);

document.getElementById(
"status"
).innerText =
"Signature generated successfully ✅";

alert(result.signature);

}


async function verifySignature(){

const message =
document.getElementById("message").value;

const signature =
document.getElementById("signature").value;

const public_key =
localStorage.getItem("public_key");

if(!public_key){

alert("Register identity first");

return;

}

const result =
await apiRequest(
"/verify",
"POST",
{
message,
signature,
public_key
}
);

document.getElementById(
"status"
).innerText =
result.valid
? "Signature Valid ✅"
: "Signature Invalid ❌";

}