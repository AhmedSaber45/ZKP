const API = "http://localhost:5000/api";

async function testBackend() {
    try {
        const res = await fetch("http://localhost:5000/");
        const data = await res.json();
        console.log("Backend Connection Success:", data);
    } catch (err) {
        console.warn("Backend might be offline or URL prefix is wrong.");
    }
}
testBackend();