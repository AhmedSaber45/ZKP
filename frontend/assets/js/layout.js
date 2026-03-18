function getBasePath() {
  // صفحة موجودة في /frontend/ => ""
  // صفحة موجودة في /frontend/subfolder/ => "../"
  const pathParts = window.location.pathname.split("/");
  // افترض أن جميع الصفحات داخل frontend أو فولدرات فرعية مباشرة
  const depth = pathParts.length - pathParts.indexOf("frontend") - 2;
  return "../".repeat(depth);
  const pathParts = window.location.pathname.split("/");
  const depth = pathParts.length - pathParts.indexOf("frontend") - 2;
  return "../".repeat(depth >= 0 ? depth : 0);
}

function loadComponent(id, file) {
  const basePath = getBasePath();
  fetch(basePath + file)
    .then(res => res.text())
    .then(data => {
      document.getElementById(id).innerHTML = data;
      const container = document.getElementById(id);
      if (container) {
        container.innerHTML = data;
      }
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
    const welcomeUser = document.getElementById("welcomeUser");
    if (navUser && user) navUser.innerText = user;
    if (welcomeUser && user) welcomeUser.innerText = user;
  }, 300);
};

function logout() {
  localStorage.clear();
  window.location.href = "index.html";
}
  window.location.href = getBasePath() + "index.html";
}
