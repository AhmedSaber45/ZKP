async function signMessage(){

let message = document.getElementById("message").value;

let response = await fetch("/signature/sign", {

method:"POST",

headers:{
"Content-Type":"application/json"
},

body: JSON.stringify({
message: message
})

})

let data = await response.json();

document.getElementById("signature").value = data.signature;

}



async function verifySignature(){

let message = document.getElementById("message").value;

let signature = document.getElementById("signature").value;

let response = await fetch("/signature/verify", {

method:"POST",

headers:{
"Content-Type":"application/json"
},

body: JSON.stringify({
message: message,
signature: signature
})

})

let data = await response.json();

document.getElementById("result").innerText =
data.valid ? "Valid Signature ✅" : "Invalid Signature ❌";

}