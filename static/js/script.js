/**
 * PSRA - Main JavaScript File
 * Pharmaceutical Studies and Research Association
 * 
 * Features:
 * - Forum interactions (likes, filtering)
 * - Dark mode toggle
 * - Toast notifications
 * - Scroll animations
 * - Mobile navigation
 * - Event countdown
 */

// ===========================================
// FORUM INTERACTIONS
// ===========================================

/**
 * Toggle like on a post
 * @param {number} postId - The ID of the post to like/unlike
 */
function toggleLike(postId) {
    fetch(`/forum/post/${postId}/like`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        const likeBtn = document.getElementById('like-btn');
        if (likeBtn) {
            likeBtn.innerHTML = `<i class="fas fa-thumbs-up"></i> ${data.likes}`;
            likeBtn.classList.toggle('liked', data.liked);
        }
    })
    .catch(error => {
        console.error('Error toggling like:', error);
        showToast('Error updating like. Please try again.', 'error');
    });
}

/**
 * Filter posts by category and search term
 */
function filterPosts() {
    const category = document.getElementById('category-select')?.value || '';
    const search = document.getElementById('search-input')?.value || '';

    fetch(`/forum/?category=${encodeURIComponent(category)}&search=${encodeURIComponent(search)}`, {
        headers: {
            'Accept': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        // Update the title
        const titleElement = document.querySelector('h2');
        if (titleElement) {
            titleElement.innerHTML = `Forum <span class="text-secondary">› ${data.selected_category || 'All Discussions'}</span>`;
        }

        // Update the posts section
        const postsContainer = document.querySelector('.forum-container > div:last-child');
        if (!postsContainer) return;

        let postsHtml = '';

        if (data.posts && data.posts.length > 0) {
            data.posts.forEach(post => {
                postsHtml += `
                <div class="card post-card">
                    <div class="card-body">
                        <div class="post-header">
                            <div class="avatar avatar-md">
                                <img src="/static/images/${post.author_avatar || 'default-avatar.png'}" alt="${post.author}">
                            </div>
                            <div class="post-author-info">
                                <span class="post-author-name">${post.author}</span>
                                <br><span class="post-date">${post.created_at}</span>
                            </div>
                        </div>
                        <h3 class="post-title">
                            <a href="/forum/post/${post.id}">${post.title}</a>
                        </h3>
                        <p class="post-content">${post.content}</p>
                        <div class="post-footer">
                            <span><i class="fas fa-thumbs-up"></i> ${post.likes}</span>
                            <span><i class="fas fa-comments"></i> ${post.comments}</span>
                        </div>
                    </div>
                </div>
                `;
            });
        } else {
            postsHtml = `
            <div class="card">
                <div class="card-body text-center" style="padding: 40px;">
                    <i class="fas fa-comments" style="font-size: 3rem; color: var(--text-muted); margin-bottom: 16px;"></i>
                    <h3>No discussions found</h3>
                    <p class="text-muted">Try different keywords or <a href="/forum/create">start a new discussion</a></p>
                </div>
            </div>
            `;
        }

        // Find the posts container and update
        const postsList = postsContainer.querySelector('.posts-list') || postsContainer;
        postsList.innerHTML = postsHtml;
    })
    .catch(error => {
        console.error('Error filtering posts:', error);
        showToast('Error loading posts. Please try again.', 'error');
    });
}

// ===========================================
// TOAST NOTIFICATIONS
// ===========================================

/**
 * Show a toast notification
 * @param {string} message - The message to display
 * @param {string} type - The type of toast (success, error, warning, info)
 * @param {number} duration - Duration in milliseconds
 */
function showToast(message, type = 'info', duration = 5000) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const iconMap = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };

    toast.innerHTML = `
        <i class="fas ${iconMap[type] || iconMap.info}"></i>
        <span>${message}</span>
        <button class="toast-close" aria-label="Close notification">
            <i class="fas fa-times"></i>
        </button>
    `;

    container.appendChild(toast);

    // Close button functionality
    toast.querySelector('.toast-close').addEventListener('click', () => {
        removeToast(toast);
    });

    // Auto remove after duration
    setTimeout(() => {
        removeToast(toast);
    }, duration);
}

/**
 * Remove a toast with animation
 * @param {HTMLElement} toast - The toast element to remove
 */
function removeToast(toast) {
    toast.style.animation = 'slideOut 0.3s ease forwards';
    setTimeout(() => toast.remove(), 300);
}

// ===========================================
// DARK MODE
// ===========================================

/**
 * Initialize dark mode based on saved preference or system preference
 */
function initDarkMode() {
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
        document.documentElement.setAttribute('data-theme', 'dark');
        updateThemeIcon(true);
    }
}

/**
 * Toggle dark mode
 */
function toggleDarkMode() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme');
    
    if (currentTheme === 'dark') {
        html.removeAttribute('data-theme');
        localStorage.setItem('theme', 'light');
        updateThemeIcon(false);
    } else {
        html.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
        updateThemeIcon(true);
    }
}

/**
 * Update the theme toggle icon
 * @param {boolean} isDark - Whether dark mode is enabled
 */
function updateThemeIcon(isDark) {
    const themeIcon = document.getElementById('theme-icon');
    if (themeIcon) {
        if (isDark) {
            themeIcon.classList.remove('fa-moon');
            themeIcon.classList.add('fa-sun');
        } else {
            themeIcon.classList.remove('fa-sun');
            themeIcon.classList.add('fa-moon');
        }
    }
}

// ===========================================
// MOBILE NAVIGATION
// ===========================================

/**
 * Initialize mobile navigation toggle
 */
function initMobileNav() {
    const menuToggle = document.getElementById('menu-toggle');
    const mainNav = document.getElementById('main-nav');
    const menuIcon = document.getElementById('menu-icon');

    if (menuToggle && mainNav) {
        menuToggle.addEventListener('click', () => {
            const isExpanded = menuToggle.getAttribute('aria-expanded') === 'true';
            menuToggle.setAttribute('aria-expanded', !isExpanded);
            mainNav.classList.toggle('active');
            
            if (menuIcon) {
                if (mainNav.classList.contains('active')) {
                    menuIcon.classList.remove('fa-bars');
                    menuIcon.classList.add('fa-times');
                } else {
                    menuIcon.classList.remove('fa-times');
                    menuIcon.classList.add('fa-bars');
                }
            }
        });
    }
}

/**
 * Initialize user dropdown menus
 */
function initDropdowns() {
    const dropdownToggles = document.querySelectorAll('.user-dropdown-toggle');
    
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', (e) => {
            e.preventDefault();
            const dropdown = toggle.nextElementSibling;
            const isExpanded = toggle.getAttribute('aria-expanded') === 'true';
            
            // Close other dropdowns
            document.querySelectorAll('.nav-dropdown-menu').forEach(menu => {
                if (menu !== dropdown) {
                    menu.style.opacity = '0';
                    menu.style.visibility = 'hidden';
                    menu.style.transform = 'translateY(-10px)';
                }
            });
            
            toggle.setAttribute('aria-expanded', !isExpanded);
            
            if (!isExpanded) {
                dropdown.style.opacity = '1';
                dropdown.style.visibility = 'visible';
                dropdown.style.transform = 'translateY(0)';
            } else {
                dropdown.style.opacity = '0';
                dropdown.style.visibility = 'hidden';
                dropdown.style.transform = 'translateY(-10px)';
            }
        });
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.nav-dropdown')) {
            document.querySelectorAll('.nav-dropdown-menu').forEach(menu => {
                menu.style.opacity = '0';
                menu.style.visibility = 'hidden';
                menu.style.transform = 'translateY(-10px)';
            });
            document.querySelectorAll('.user-dropdown-toggle').forEach(toggle => {
                toggle.setAttribute('aria-expanded', 'false');
            });
        }
    });
}

// ===========================================
// HEADER SCROLL EFFECT
// ===========================================

/**
 * Add shadow to header on scroll
 */
function initHeaderScroll() {
    const header = document.getElementById('header');
    if (!header) return;

    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });
}

// ===========================================
// SCROLL ANIMATIONS
// ===========================================

/**
 * Initialize scroll-triggered animations
 */
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);

    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    animatedElements.forEach(element => {
        observer.observe(element);
    });
}

// ===========================================
// EVENT COUNTDOWN
// ===========================================

/**
 * Update upcoming event section
 */
function updateUpcomingEvent() {
    fetch('/api/next-event')
        .then(response => response.json())
        .then(data => {
            const upcomingSection = document.getElementById('upcoming-event');
            if (!upcomingSection) return;

            if (data.no_event) {
                upcomingSection.style.display = 'none';
                return;
            }

            upcomingSection.style.display = 'block';

            // Update event info
            const titleEl = document.getElementById('upcoming-event-title');
            if (titleEl) titleEl.textContent = data.title;

            // Handle event image
            const imageContainer = document.getElementById('upcoming-event-image');
            const imageElement = document.getElementById('upcoming-event-img');
            if (imageContainer && imageElement) {
                if (data.image_url) {
                    imageElement.src = '/static/images/' + data.image_url;
                    imageContainer.style.display = 'block';
                } else {
                    imageContainer.style.display = 'none';
                }
            }

            // Format date
            const eventDate = new Date(data.event_datetime);
            const dateOptions = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
            let dateString = eventDate.toLocaleDateString('en-US', dateOptions);

            if (data.has_time) {
                const timeOptions = { hour: 'numeric', minute: '2-digit', hour12: true };
                dateString += ' at ' + eventDate.toLocaleTimeString('en-US', timeOptions);
            } else {
                dateString += ' (All Day)';
            }

            const dateEl = document.getElementById('upcoming-event-date');
            if (dateEl) dateEl.textContent = dateString;

            const descEl = document.getElementById('upcoming-event-description');
            if (descEl) descEl.textContent = data.description || '';

            // Calculate time remaining
            const now = new Date();
            const timeDiff = eventDate - now;

            if (timeDiff > 0) {
                const days = Math.floor(timeDiff / (1000 * 60 * 60 * 24));
                const hours = Math.floor((timeDiff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                const minutes = Math.floor((timeDiff % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((timeDiff % (1000 * 60)) / 1000);

                const daysEl = document.getElementById('upcoming-days');
                const hoursEl = document.getElementById('upcoming-hours');
                const minutesEl = document.getElementById('upcoming-minutes');
                const secondsEl = document.getElementById('upcoming-seconds');

                if (daysEl) daysEl.textContent = days.toString().padStart(2, '0');
                if (hoursEl) hoursEl.textContent = hours.toString().padStart(2, '0');
                if (minutesEl) minutesEl.textContent = minutes.toString().padStart(2, '0');
                if (secondsEl) secondsEl.textContent = seconds.toString().padStart(2, '0');
            } else {
                upcomingSection.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error fetching next event:', error);
            const upcomingSection = document.getElementById('upcoming-event');
            if (upcomingSection) upcomingSection.style.display = 'none';
        });
}

// ===========================================
// PASSWORD TOGGLE
// ===========================================

/**
 * Toggle password visibility
 * @param {string} fieldId - The ID of the password field
 */
function togglePassword(fieldId) {
    const input = document.getElementById(fieldId);
    const icon = document.getElementById(fieldId + '-toggle-icon');
    
    if (!input) return;

    if (input.type === 'password') {
        input.type = 'text';
        if (icon) {
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
        }
    } else {
        input.type = 'password';
        if (icon) {
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
        }
    }
}

// ===========================================
// UTILITY FUNCTIONS
// ===========================================

/**
 * Debounce function for performance optimization
 * @param {Function} func - The function to debounce
 * @param {number} wait - The wait time in milliseconds
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Smooth scroll to element
 * @param {string} targetId - The ID of the target element
 */
function smoothScrollTo(targetId) {
    const targetElement = document.querySelector(targetId);
    if (targetElement) {
        targetElement.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// ===========================================
// LAZY LOADING
// ===========================================

/**
 * Initialize lazy loading for images
 */
function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');

    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    imageObserver.unobserve(img);
                }
            });
        });

        images.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback for browsers without IntersectionObserver
        images.forEach(img => {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
        });
    }
}

// ===========================================
// FORM VALIDATION HELPERS
// ===========================================

/**
 * Show form error
 * @param {string} fieldId - The ID of the field
 * @param {string} message - The error message
 */
function showFormError(fieldId, message) {
    const field = document.getElementById(fieldId);
    if (!field) return;

    field.classList.add('error');
    
    // Remove existing error message
    const existingError = field.parentElement.querySelector('.form-error');
    if (existingError) existingError.remove();

    // Add new error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'form-error';
    errorDiv.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${message}`;
    field.parentElement.appendChild(errorDiv);
}

/**
 * Clear form error
 * @param {string} fieldId - The ID of the field
 */
function clearFormError(fieldId) {
    const field = document.getElementById(fieldId);
    if (!field) return;

    field.classList.remove('error');
    const existingError = field.parentElement.querySelector('.form-error');
    if (existingError) existingError.remove();
}

// ===========================================
// INITIALIZATION
// ===========================================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize dark mode
    initDarkMode();
    
    // Initialize theme toggle
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleDarkMode);
    }

    // Initialize mobile navigation
    initMobileNav();
    
    // Initialize dropdowns
    initDropdowns();
    
    // Initialize header scroll effect
    initHeaderScroll();
    
    // Initialize scroll animations
    initScrollAnimations();
    
    // Initialize lazy loading
    initLazyLoading();

    // Forum search and filter
    const searchInput = document.getElementById('search-input');
    const categorySelect = document.getElementById('category-select');

    if (searchInput) {
        searchInput.addEventListener('input', debounce(filterPosts, 300));
    }

    if (categorySelect) {
        categorySelect.addEventListener('change', filterPosts);
    }

    // Initialize upcoming event section if on home page
    if (document.getElementById('upcoming-event')) {
        updateUpcomingEvent();
        setInterval(updateUpcomingEvent, 1000);
    }

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(link => {
        link.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId !== '#') {
                e.preventDefault();
                smoothScrollTo(targetId);
            }
        });
    });
});

// Export functions for global use
window.toggleLike = toggleLike;
window.filterPosts = filterPosts;
window.showToast = showToast;
window.toggleDarkMode = toggleDarkMode;
window.togglePassword = togglePassword;
window.smoothScrollTo = smoothScrollTo;
window.showFormError = showFormError;
window.clearFormError = clearFormError;
