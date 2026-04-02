function getBasePath() {
  // صفحة موجودة في /frontend/ => ""
  // صفحة موجودة في /frontend/subfolder/ => "../"
  const pathParts = window.location.pathname.split("/");
  // افترض أن جميع الصفحات داخل frontend أو فولدرات فرعية مباشرة
  const depth = pathParts.length - pathParts.indexOf("frontend") - 2;
  return "../".repeat(depth);
}

function loadComponent(id, file) {
  const basePath = getBasePath();
  fetch(basePath + file)
    .then(res => res.text())
    .then(data => {
      document.getElementById(id).innerHTML = data;
    });
}

window.onload = function () {
  loadComponent("navbar-container", "components/navbar.html");
  loadComponent("sidebar-container", "components/sidebar.html");
  loadComponent("footer-container", "components/footer.html");

  const user = localStorage.getItem("user");
  setTimeout(() => {
    const navUser = document.getElementById("navUser");
    if (navUser && user) {
      navUser.innerText = user;
    }
  }, 200);
};

function logout() {
  localStorage.clear();
  window.location.href = "index.html";
}