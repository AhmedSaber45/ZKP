async function apiRequest(endpoint, method, data){

const response =
await fetch(
"http://127.0.0.1:5000" + endpoint,
{
method,

headers:{
"Content-Type":
"application/json"
},

body:
JSON.stringify(data)
}
);

return await response.json();

}