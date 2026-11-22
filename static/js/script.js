/**
 * Once Upon a Page - Interactive Storybook Script
 * Handles password toggling, client-side validation, and magical UI interactions.
 */

document.addEventListener('DOMContentLoaded', function () {

    // =========================================================================
    // 1. Password Visibility Toggle Functionality
    // =========================================================================
    function setupPasswordToggle(toggleBtnId, inputId, iconId) {
        const toggleBtn = document.getElementById(toggleBtnId);
        const passwordInput = document.getElementById(inputId);
        const eyeIcon = document.getElementById(iconId);

        if (toggleBtn && passwordInput && eyeIcon) {
            toggleBtn.addEventListener('click', function (e) {
                e.preventDefault();
                const isPassword = passwordInput.getAttribute('type') === 'password';
                
                // Toggle input type
                passwordInput.setAttribute('type', isPassword ? 'text' : 'password');
                
                // Toggle eye icon class
                if (isPassword) {
                    eyeIcon.classList.remove('fa-eye');
                    eyeIcon.classList.add('fa-eye-slash');
                    toggleBtn.setAttribute('title', 'Hide passphrase');
                } else {
                    eyeIcon.classList.remove('fa-eye-slash');
                    eyeIcon.classList.add('fa-eye');
                    toggleBtn.setAttribute('title', 'Show passphrase');
                }
            });
        }
    }

    // Initialize toggle for Login Page
    setupPasswordToggle('toggleLoginPassword', 'loginPassword', 'loginEyeIcon');

    // Initialize toggles for Registration Page
    setupPasswordToggle('toggleRegisterPassword', 'registerPassword', 'registerEyeIcon');
    setupPasswordToggle('toggleConfirmPassword', 'registerConfirmPassword', 'confirmEyeIcon');


    // =========================================================================
    // 2. Real-Time Password Matching on Registration Form
    // =========================================================================
    const passwordInput = document.getElementById('registerPassword');
    const confirmInput = document.getElementById('registerConfirmPassword');
    const matchFeedback = document.getElementById('passwordMatchFeedback');

    function checkPasswordMatch() {
        if (!passwordInput || !confirmInput || !matchFeedback) return;

        const pwd = passwordInput.value;
        const confirmPwd = confirmInput.value;

        if (confirmPwd.length === 0) {
            matchFeedback.style.display = 'none';
            matchFeedback.textContent = '';
            confirmInput.style.borderColor = '';
            return;
        }

        matchFeedback.style.display = 'block';

        if (pwd === confirmPwd) {
            matchFeedback.textContent = '✨ Secret passphrases match perfectly!';
            matchFeedback.className = 'password-match-indicator mt-1 small match-success';
            confirmInput.style.borderColor = '#2E7D32';
        } else {
            matchFeedback.textContent = '✦ Passphrases do not match yet.';
            matchFeedback.className = 'password-match-indicator mt-1 small match-danger';
            confirmInput.style.borderColor = '#B85374';
        }
    }

    if (passwordInput && confirmInput) {
        passwordInput.addEventListener('input', checkPasswordMatch);
        confirmInput.addEventListener('input', checkPasswordMatch);
    }


    // =========================================================================
    // 3. Form Submission Handling & Visual Feedback
    // =========================================================================
    const forms = document.querySelectorAll('.storybook-form');
    forms.forEach(function (form) {
        form.addEventListener('submit', function (e) {
            const submitBtn = form.querySelector('.btn-storybook-primary');
            if (submitBtn) {
                // Add gentle loading indication
                const btnContent = submitBtn.querySelector('.btn-content');
                if (btnContent) {
                    btnContent.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-2"></i> Opening enchanted pages...';
                }
            }
        });
    });


    // =========================================================================
    // 4. Auto-dismiss Flash Alerts after 6 Seconds
    // =========================================================================
    const flashAlerts = document.querySelectorAll('.storybook-alert');
    if (flashAlerts.length > 0) {
        setTimeout(function () {
            flashAlerts.forEach(function (alertElement) {
                // Check if Bootstrap Alert instance is available
                if (window.bootstrap && bootstrap.Alert) {
                    const bsAlert = bootstrap.Alert.getOrCreateInstance(alertElement);
                    bsAlert.close();
                } else {
                    alertElement.style.transition = 'opacity 0.5s ease';
                    alertElement.style.opacity = '0';
                    setTimeout(() => alertElement.remove(), 500);
                }
            });
        }, 6000);
    }


    // =========================================================================
    // 5. Subtle Interactive Sparkle Particles on Click
    // =========================================================================
    document.addEventListener('click', function (e) {
        // Only trigger on card background or buttons for subtle magic
        const target = e.target;
        if (!target.closest('.storybook-card') && !target.closest('.storybook-wrapper')) return;

        createClickSparkle(e.clientX, e.clientY);
    });

    function createClickSparkle(x, y) {
        const sparkle = document.createElement('span');
        sparkle.textContent = ['✦', '✧', '✨'][Math.floor(Math.random() * 3)];
        sparkle.style.position = 'fixed';
        sparkle.style.left = `${x}px`;
        sparkle.style.top = `${y}px`;
        sparkle.style.pointerEvents = 'none';
        sparkle.style.color = '#D4A853';
        sparkle.style.fontSize = '1.1rem';
        sparkle.style.zIndex = '9999';
        sparkle.style.transform = 'translate(-50%, -50%) scale(0)';
        sparkle.style.transition = 'all 0.6s cubic-bezier(0.25, 1, 0.5, 1)';

        document.body.appendChild(sparkle);

        // Animate
        requestAnimationFrame(() => {
            const offsetX = (Math.random() - 0.5) * 40;
            const offsetY = (Math.random() - 0.5) * 40 - 20;
            sparkle.style.transform = `translate(calc(-50% + ${offsetX}px), calc(-50% + ${offsetY}px)) scale(1.3)`;
            sparkle.style.opacity = '0';
        });

        setTimeout(() => {
            if (sparkle.parentNode) {
                sparkle.parentNode.removeChild(sparkle);
            }
        }, 650);
    }


    // =========================================================================
    // 6. Dashboard Mobile Sidebar Toggle
    // =========================================================================
    const sidebarToggle = document.getElementById('sidebarToggle');
    const dashboardSidebar = document.getElementById('dashboardSidebar');

    if (sidebarToggle && dashboardSidebar) {
        sidebarToggle.addEventListener('click', function (e) {
            e.stopPropagation();
            dashboardSidebar.classList.toggle('sidebar-open');
        });

        // Close when clicking outside on mobile
        document.addEventListener('click', function (e) {
            if (dashboardSidebar.classList.contains('sidebar-open') && 
                !dashboardSidebar.contains(e.target) && 
                e.target !== sidebarToggle) {
                dashboardSidebar.classList.remove('sidebar-open');
            }
        });

        // Close sidebar on link click on mobile
        dashboardSidebar.querySelectorAll('.sidebar-link').forEach(function (link) {
            link.addEventListener('click', function () {
                if (window.innerWidth < 992) {
                    dashboardSidebar.classList.remove('sidebar-open');
                }
            });
        });
    }


    // =========================================================================
    // 7. Interactive 3D Book Hover Tilting
    // =========================================================================
    const bookContainers = document.querySelectorAll('.book-3d-container');
    bookContainers.forEach(container => {
        const bookObject = container.querySelector('.book-3d-object');
        if (!bookObject) return;

        container.addEventListener('mousemove', function (e) {
            const rect = container.getBoundingClientRect();
            const x = e.clientX - rect.left - (rect.width / 2);
            const y = e.clientY - rect.top - (rect.height / 2);
            
            // Calculate gentle subtle tilt
            const tiltY = (x / (rect.width / 2)) * 6 - 12; // base angle around -12deg
            const tiltX = -(y / (rect.height / 2)) * 4 + 2;

            bookObject.style.transform = `translateY(-14px) rotateY(${tiltY}deg) rotateX(${tiltX}deg) scale(1.04)`;
        });

        container.addEventListener('mouseleave', function () {
            // Reset to default standing angle
            bookObject.style.transform = '';
        });

        // Direct click handler to ensure book opens even on touch/mobile
        container.addEventListener('click', function (e) {
            if (e.target.closest('.btn-fav-toggle')) return;
            const link = container.querySelector('.book-3d-anchor-link') || 
                         container.querySelector('.book-card-title a') || 
                         container.querySelector('.btn-open-book-pill');
            if (link && !e.target.closest('a')) {
                window.location.href = link.href;
            }
        });
    });

});

// =============================================================================
// 8. Global AJAX Favorites Manager & Toast Notifications
// =============================================================================

function showToast(message, icon = '✨') {
    const toastEl = document.getElementById('magicalToast');
    const toastMsg = document.getElementById('toastMsg');
    const toastIcon = document.getElementById('toastIcon');

    if (toastEl && toastMsg) {
        toastMsg.textContent = message;
        if (toastIcon) toastIcon.textContent = icon;

        if (window.bootstrap && bootstrap.Toast) {
            const toast = bootstrap.Toast.getOrCreateInstance(toastEl, { delay: 3500 });
            toast.show();
        } else {
            toastEl.style.display = 'block';
            setTimeout(() => { toastEl.style.display = 'none'; }, 3500);
        }
    }
}

window.toggleFavorite = function (event, bookId) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }

    if (!bookId) return;

    fetch('/api/favorites/toggle', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ book_id: bookId })
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            showToast(data.message || 'Unable to update favorites.', '⚠️');
            return;
        }

        const isFav = data.is_favorite;
        showToast(data.message, isFav ? '💜' : '✦');

        // Update all favorite toggle buttons for this book on the page
        const toggleButtons = document.querySelectorAll(`.btn-fav-toggle[data-book-id="${bookId}"]`);
        toggleButtons.forEach(btn => {
            const icon = btn.querySelector('i');
            if (isFav) {
                btn.classList.add('is-favorited');
                btn.setAttribute('title', 'Remove from favorites');
                if (icon) {
                    icon.className = 'fa-solid fa-heart text-danger';
                }
            } else {
                btn.classList.remove('is-favorited');
                btn.setAttribute('title', 'Add to favorites');
                if (icon) {
                    icon.className = 'fa-regular fa-heart';
                }
            }
        });

        // Update nav badge count if present
        const favBadges = document.querySelectorAll('.fav-count-badge');
        favBadges.forEach(badge => {
            let count = parseInt(badge.textContent.trim() || '0', 10);
            count = isFav ? count + 1 : Math.max(0, count - 1);
            badge.textContent = count;
            badge.style.display = count > 0 ? 'inline-block' : 'none';
        });

        // If currently in the Favorites Shelf View and un-favoriting, remove card instantly
        const favoritesGrid = document.getElementById('favoritesGrid');
        if (favoritesGrid && !isFav) {
            const cardCol = document.getElementById(`favCol-${bookId}`);
            if (cardCol) {
                cardCol.style.transition = 'all 0.4s cubic-bezier(0.25, 1, 0.5, 1)';
                cardCol.style.opacity = '0';
                cardCol.style.transform = 'scale(0.85) translateY(20px)';

                setTimeout(() => {
                    if (cardCol.parentNode) cardCol.parentNode.removeChild(cardCol);

                    // Update shelf count badge
                    const favShelfCount = document.getElementById('favShelfCount');
                    const remainingCards = favoritesGrid.querySelectorAll('.book-shelf-column');
                    if (favShelfCount) {
                        favShelfCount.textContent = `${remainingCards.length} saved`;
                    }

                    // If no favorites remain, display exact required empty state
                    if (remainingCards.length === 0) {
                        favoritesGrid.outerHTML = `
                            <div class="empty-state-card text-center p-5 rounded-4 shadow-sm my-4" id="emptyFavCard">
                                <div class="empty-emoji mb-3">💜 📚</div>
                                <h4 class="fw-bold mb-2">No favourite stories yet!</h4>
                                <p class="text-muted mb-4">Start exploring and save the stories you love. 💜</p>
                                <a href="/dashboard" class="btn btn-storybook-primary px-4 py-2">
                                    <span class="btn-content">Discover Storybooks</span>
                                </a>
                            </div>
                        `;
                    }
                }, 400);
            }
        }
    })
    .catch(err => {
        console.error('Error toggling favorite:', err);
        showToast('Something went wrong. Please try again.', '⚠️');
    });
};

// =============================================================================
// 9. Reading Preferences & Theme Quick Toggle Manager
// =============================================================================
const StorybookPreferences = {
    init: function () {
        this.applyTheme();
        this.applyNightSky();
        this.setupThemeToggle();
        this.setupSettingsToggles();
    },

    getTheme: function () {
        const stored = localStorage.getItem('storybook_theme');
        if (stored) return stored;
        if (window.USER_PREFS && window.USER_PREFS.theme) return window.USER_PREFS.theme;
        return 'light';
    },

    setTheme: function (theme) {
        localStorage.setItem('storybook_theme', theme);
        this.applyTheme(theme);
        this.syncToServer({ theme: theme });
    },

    applyTheme: function (theme) {
        const activeTheme = theme || this.getTheme();
        if (activeTheme === 'dark') {
            document.documentElement.setAttribute('data-theme', 'dark');
            document.body.classList.add('dark-theme');
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
            document.body.classList.remove('dark-theme');
        }
        this.updateThemeButtonUI(activeTheme);
    },

    updateThemeButtonUI: function (theme) {
        const toggleBtn = document.getElementById('themeToggleBtn');
        const icon = document.getElementById('themeToggleIcon');
        if (!toggleBtn || !icon) return;

        if (theme === 'dark') {
            icon.className = 'fa-solid fa-sun';
            toggleBtn.title = 'Switch to Light Mode';
            toggleBtn.setAttribute('aria-label', 'Switch to Light Mode');
        } else {
            icon.className = 'fa-solid fa-moon';
            toggleBtn.title = 'Switch to Dark Mode';
            toggleBtn.setAttribute('aria-label', 'Switch to Dark Mode');
        }
    },

    setupThemeToggle: function () {
        const toggleBtn = document.getElementById('themeToggleBtn');
        if (!toggleBtn) return;

        this.updateThemeButtonUI(this.getTheme());

        toggleBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const current = this.getTheme();
            const next = current === 'dark' ? 'light' : 'dark';
            this.setTheme(next);
        });
    },

    isNightSkyEnabled: function () {
        const stored = localStorage.getItem('storybook_night_sky');
        if (stored !== null) return stored === 'true';
        if (window.USER_PREFS && window.USER_PREFS.night_sky !== undefined) {
            return Boolean(window.USER_PREFS.night_sky);
        }
        return true;
    },

    setNightSky: function (enabled) {
        localStorage.setItem('storybook_night_sky', enabled ? 'true' : 'false');
        this.applyNightSky(enabled);
        this.syncToServer({ night_sky: enabled });
    },

    applyNightSky: function (enabled) {
        const isEnabled = (enabled !== undefined) ? enabled : this.isNightSkyEnabled();
        document.documentElement.setAttribute('data-night-sky', isEnabled ? 'true' : 'false');
        if (isEnabled) {
            document.body.classList.remove('night-sky-disabled');
        } else {
            document.body.classList.add('night-sky-disabled');
        }
    },

    isWhispersEnabled: function () {
        const stored = localStorage.getItem('storybook_page_turn_whispers');
        if (stored !== null) return stored === 'true';
        if (window.USER_PREFS && window.USER_PREFS.page_turn_whispers !== undefined) {
            return Boolean(window.USER_PREFS.page_turn_whispers);
        }
        return true;
    },

    setWhispers: function (enabled) {
        localStorage.setItem('storybook_page_turn_whispers', enabled ? 'true' : 'false');
        this.syncToServer({ page_turn_whispers: enabled });
    },

    setupSettingsToggles: function () {
        const ambientToggle = document.getElementById('ambientToggle');
        const soundToggle = document.getElementById('soundToggle');

        if (ambientToggle) {
            ambientToggle.checked = this.isNightSkyEnabled();
            ambientToggle.addEventListener('change', () => {
                this.setNightSky(ambientToggle.checked);
            });
        }

        if (soundToggle) {
            soundToggle.checked = this.isWhispersEnabled();
            soundToggle.addEventListener('change', () => {
                this.setWhispers(soundToggle.checked);
            });
        }
    },

    syncToServer: function (payload) {
        try {
            fetch('/api/user/preferences', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            }).catch(() => {});
        } catch (e) {}
    }
};

// Initialize Preferences on Page Load
StorybookPreferences.init();


