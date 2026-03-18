async function sendTransaction() {
  const sender = document.getElementById("sender").value;
  const receiver = document.getElementById("receiver").value;
  const amount = document.getElementById("amount").value;

  const response = await apiRequest("/transaction", "POST", {
    sender,
    receiver,
    amount
  });

  alert(response.message);
}