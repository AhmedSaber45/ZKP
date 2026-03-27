async function generateProof(){

let username = localStorage.getItem("user");

let response = await fetch("/identity/generate_proof", {

method:"POST",

headers:{
"Content-Type":"application/json"
},

body: JSON.stringify({
username: username
})

})

let data = await response.json();

document.getElementById("proof").value = data.proof;

}