async function generateProof(){
  const username = localStorage.getItem("user");

  const response = await apiRequest("/identity-proof","POST",{username});

  document.getElementById("proof").value = response.proof;
}