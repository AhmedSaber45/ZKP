function getRelativePrefix() {
    const loc = window.location.pathname;
    if (loc.includes('/modes/digital_trust/') || loc.includes('/modes/governance/secure_voting/') || loc.includes('/modes/security/')) return "../../../";
    if (loc.includes('/modes/')) return "../../";
    return "";
}

function loadComponent(id, file) {
  const prefix = getRelativePrefix();
  console.log(`[Layout] Loading ${file} with prefix: ${prefix}`);
  
  fetch(prefix + file)
    .then(res => {
      if (!res.ok) throw new Error(`Could not load ${file}`);
      return res.text();
    })
    .then(data => {
      const container = document.getElementById(id);
      if (container) {
        container.innerHTML = data;
        
        // Fix relative links in the component
        const links = container.querySelectorAll('a');
        links.forEach(link => {
            const originalHref = link.getAttribute('href');
            if (originalHref && !originalHref.startsWith('http') && !originalHref.startsWith('#')) {
                const newHref = prefix + originalHref;
                link.setAttribute('href', newHref);
            }
        });

        // Current page highlighting
        const currentPath = window.location.pathname;
        links.forEach(link => {
            const linkHref = link.getAttribute('href');
            // Clean paths for comparison
            const cleanPath = currentPath.split('/').pop();
            const cleanLink = linkHref.split('/').pop();
            
            if (cleanPath === cleanLink && cleanPath !== "" && cleanPath !== "index.html") {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });

        // Special handling for navbar user display
        if (id === "navbar-container") {
          const user = localStorage.getItem("user");
          const navUser = document.getElementById("navUser");
          if (navUser && user) navUser.innerText = user;
        }
      }
    })
    .catch(err => console.error("Component load error:", err));
}

window.addEventListener('load', () => {
  loadComponent("navbar-container", "components/navbar.html");
  loadComponent("sidebar-container", "components/sidebar.html");
  loadComponent("footer-container", "components/footer.html");

  const user = localStorage.getItem("user");
  const welcomeUser = document.getElementById("welcomeUser");
  if (welcomeUser && user) {
    welcomeUser.innerText = user;
  }
});

function logout() {
  localStorage.clear();
  window.location.href = getRelativePrefix() + "index.html";
}
