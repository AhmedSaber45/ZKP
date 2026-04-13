function getRelativePrefix() {
    const loc = window.location.pathname;
    if (loc.includes('/modes/digital_trust/') || loc.includes('/modes/governance/secure_voting/') || loc.includes('/modes/security/')) return "../../../";
    if (loc.includes('/modes/')) return "../../";
    return "";
}

function loadComponent(id, file) {
  const prefix = getRelativePrefix();
  console.log(`[Layout] Loading ${file} with prefix: ${prefix}`);
  
  fetch(prefix + file + '?cb=' + new Date().getTime(), { cache: 'no-store' })
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

        // Special handling for navbar user display and auth button
        if (id === "navbar-container") {
          const user = localStorage.getItem("user");
          const navUser = document.getElementById("navUser");
          const userInfo = document.getElementById("userInfo");
          const authBtn = document.getElementById("authBtn");
          const authBtnText = document.getElementById("authBtnText");
          const authBtnIcon = document.getElementById("authBtnIcon");

          if (user) {
            if (navUser) navUser.innerText = user;
            if (userInfo) userInfo.style.display = 'flex';
            if (authBtnText) authBtnText.innerText = "Sign Out";
            if (authBtn) {
              authBtn.onclick = logout;
              authBtn.classList.remove('login-btn');
              authBtn.classList.add('logout-btn');
            }
            if (authBtnIcon) {
              authBtnIcon.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                  <polyline points="16 17 21 12 16 7"></polyline>
                  <line x1="21" y1="12" x2="9" y2="12"></line>
                </svg>`;
            }
          } else {
            if (userInfo) userInfo.style.display = 'none';
            if (authBtnText) authBtnText.innerText = "Sign In";
            if (authBtn) {
              authBtn.onclick = () => {
                window.location.href = getRelativePrefix() + "modes/authentication/login.html";
              };
              authBtn.classList.remove('logout-btn');
              authBtn.classList.add('login-btn');
            }
            if (authBtnIcon) {
              authBtnIcon.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path>
                  <polyline points="10 17 15 12 10 7"></polyline>
                  <line x1="15" y1="12" x2="3" y2="12"></line>
                </svg>`;
            }
          }
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
  console.log("[Auth] Logging out and clearing all state...");
  localStorage.clear(); // Clear all user data
  sessionStorage.clear(); // Optional: clear session data too
  
  // Navigate to home page with a timestamp to force a fresh refresh and bypass cache
  window.location.href = getRelativePrefix() + "index.html?v=" + new Date().getTime();
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

// --- Global Modal Utility ---
function showModal(title, message, type = 'info', action = null) {
    // Remove existing modal if any
    let existingModal = document.getElementById('global-modal');
    if (existingModal) existingModal.remove();

    const icons = {
        success: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`,
        error: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>`,
        info: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`
    };

    let actionBtnHTML = '';
    if (action && action.text) {
        const onclickAttr = action.url 
            ? `onclick="window.location.href='${action.url}'"` 
            : (action.callback ? `onclick="${action.callback}"` : '');
        actionBtnHTML = `<button ${onclickAttr} style="background: var(--primary);">${action.text}</button>`;
    }

    const modalHTML = `
    <div id="global-modal" class="modal-backdrop">
        <div class="modal-card">
            <div class="modal-header">
                <div class="modal-icon ${type}">${icons[type] || icons.info}</div>
                <h3 class="modal-title">${title}</h3>
            </div>
            <div class="modal-body">${message}</div>
            <div class="modal-footer">
                <button onclick="closeModal()" class="glass-btn" style="background: rgba(255,255,255,0.05); color: var(--text-muted); border: 1px solid var(--glass-border);">Dismiss</button>
                ${actionBtnHTML}
            </div>
        </div>
    </div>`;

    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Small delay to trigger animation
    setTimeout(() => {
        const modal = document.getElementById('global-modal');
        if (modal) modal.classList.add('active');
    }, 10);

    // Close on ESC
    const escHandler = (e) => {
        if (e.key === 'Escape') {
            closeModal();
            document.removeEventListener('keydown', escHandler);
        }
    };
    document.addEventListener('keydown', escHandler);
}

function closeModal() {
    const modal = document.getElementById('global-modal');
    if (modal) {
        modal.classList.remove('active');
        setTimeout(() => modal.remove(), 300);
    }
}


