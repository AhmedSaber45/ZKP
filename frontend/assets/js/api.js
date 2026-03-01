const API = "http://192.168.1.100:5000";

async function testBackend() {
    const res = await fetch(`${API}/`);
    const data = await res.json();
    console.log(data);
}
testBackend();