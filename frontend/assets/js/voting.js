async function vote() {
  const candidate = document.querySelector('input[name="candidate"]:checked');

  if (!candidate) {
    alert("Select candidate");
    return;
  }

  const response = await apiRequest("/vote", "POST", {
    candidate: candidate.value
  });

  alert(response.message);
}
async function loadResults(){
  const response = await apiRequest("/results");

  const container = document.getElementById("results");
  container.innerHTML = "";

  response.results.forEach(r => {
    container.innerHTML += `
      <p>${r.candidate}: ${r.votes} votes</p>
    `;
  });
}