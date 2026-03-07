// const API = "http://192.168.1.100:5000";

// async function testBackend() {
//     const res = await fetch(`${API}/`);
//     const data = await res.json();
//     console.log(data);
// }
// testBackend();
const BASE_URL = "http://localhost:5000";

async function apiRequest(endpoint, method = "GET", data = null) {
  const options = {
    method: method,
    headers: {
      "Content-Type": "application/json"
    }
  };

  if (data) {
    options.body = JSON.stringify(data);
  }

  const response = await fetch(BASE_URL + endpoint, options);
  return response.json();
}