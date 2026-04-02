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
            
            // Close sidebar when a link is clicked (mobile)
            link.addEventListener('click', () => {
              if (window.innerWidth <= 768) {
                closeSidebar();
              }
            });
        });

        // Current page highlighting and sub-menu expansion
        const currentPath = window.location.pathname;
        const cleanPath = currentPath.split('/').pop().replace('.html', '');

        links.forEach(link => {
            const linkHref = link.getAttribute('href');
            if (!linkHref) return;
            
            const cleanLink = linkHref.split('/').pop().replace('.html', '');
            
            // Exact match for active state
            if (cleanPath === cleanLink && cleanPath !== "" && cleanPath !== "index") {
                link.classList.add('active');
                
                // If this is a sub-menu item, expand the parent
                const subMenu = link.closest('.sub-menu');
                if (subMenu) {
                    subMenu.parentElement.classList.add('expanded');
                }
            } else {
                link.classList.remove('active');
            }

            // Handle Sub-menu Toggle
            if (link.classList.contains('has-submenu')) {
                link.addEventListener('click', (e) => {
                    e.preventDefault(); // Prevent jump for parent items
                    const wrapper = link.closest('.menu-item-wrapper');
                    if (wrapper) {
                        wrapper.classList.toggle('expanded');
                    }
                });
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
  
  // Create backdrop if it doesn't exist
  if (!document.querySelector('.sidebar-backdrop')) {
    const backdrop = document.createElement('div');
    backdrop.className = 'sidebar-backdrop';
    backdrop.onclick = toggleSidebar;
    document.body.appendChild(backdrop);
  }
});

function toggleSidebar() {
  const sidebar = document.querySelector('.sidebar');
  const backdrop = document.querySelector('.sidebar-backdrop');
  if (sidebar) {
    sidebar.classList.toggle('open');
    if (backdrop) {
      backdrop.classList.toggle('active');
    }
    // Toggle body scroll
    document.body.style.overflow = sidebar.classList.contains('open') ? 'hidden' : '';
  }
}

function closeSidebar() {
  const sidebar = document.querySelector('.sidebar');
  const backdrop = document.querySelector('.sidebar-backdrop');
  if (sidebar && sidebar.classList.contains('open')) {
    sidebar.classList.remove('open');
    if (backdrop) {
      backdrop.classList.remove('active');
    }
    document.body.style.overflow = '';
  }
}

function logout() {
  localStorage.clear();
  window.location.href = getRelativePrefix() + "index.html";
}

// --- Navbar Hide on Scroll ---
(function() {
    let lastScrollTop = 0;
    const threshold = 5;
    
    function handleScroll() {
        const navbar = document.querySelector('.navbar');
        if (!navbar) return;

        // Current scroll position
        const currentScroll = window.pageYOffset || document.documentElement.scrollTop;
        const st = Math.max(currentScroll, 0);

        // Check if we've scrolled enough to matter
        if (Math.abs(lastScrollTop - st) <= threshold) return;

        // Hide if scrolling down and past navbar height
        if (st > lastScrollTop && st > 80) {
            navbar.classList.add('nav-hidden');
        } else {
            // Show if scrolling up
            navbar.classList.remove('nav-hidden');
        }

        lastScrollTop = st;
    }

    window.addEventListener('scroll', handleScroll, { passive: true });
})();


