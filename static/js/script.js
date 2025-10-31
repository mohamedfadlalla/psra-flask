// Forum interactions
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
            likeBtn.innerHTML = `👍 ${data.likes}`;
        }
    })
    .catch(error => {
        console.error('Error toggling like:', error);
        alert('Error updating like. Please try again.');
    });
}

function filterPosts() {
    const category = document.getElementById('category-select').value;
    const search = document.getElementById('search-input').value;

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
            titleElement.textContent = `Forum > ${data.selected_category}`;
        }

        // Update the posts section
        const postsContainer = document.querySelector('.container > div:last-child');
        let postsHtml = '';

        if (data.posts.length > 0) {
            data.posts.forEach(post => {
                postsHtml += `
                <div class="card" style="margin-bottom: 20px;">
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                        <img src="/static/images/default-avatar.png" alt="Avatar" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;">
                        <div>
                            <strong>${post.author}</strong>
                            <br><small style="color: var(--text-muted);">${post.created_at}</small>
                        </div>
                    </div>
                    <h3><a href="/forum/post/${post.id}" style="text-decoration: none; color: var(--text-primary);">${post.title}</a></h3>
                    <p style="color: var(--text-secondary);">${post.content}</p>
                    <div style="display: flex; gap: 20px; margin-top: 10px;">
                        <span>👍 ${post.likes}</span>
                        <span>💬 ${post.comments}</span>
                    </div>
                </div>
                `;
            });
        } else {
            postsHtml = `
            <div class="card">
                <p>No discussions found. <a href="/forum/create">Start the first one!</a></p>
            </div>
            `;
        }

        // Replace the content after the title
        const titleDiv = postsContainer.querySelector('div');
        const titleHtml = titleDiv ? titleDiv.outerHTML : '';
        postsContainer.innerHTML = titleHtml + postsHtml;
    })
    .catch(error => {
        console.error('Error filtering posts:', error);
    });
}



// Upcoming event section functionality
function updateUpcomingEvent() {
    fetch('/api/next-event')
        .then(response => response.json())
        .then(data => {
            const upcomingSection = document.getElementById('upcoming-event');

            if (data.no_event) {
                upcomingSection.style.display = 'none';
                return;
            }

            // Show upcoming event section
            upcomingSection.style.display = 'block';

            // Update event info
            document.getElementById('upcoming-event-title').textContent = data.title;

            // Handle event image
            const imageContainer = document.getElementById('upcoming-event-image');
            const imageElement = document.getElementById('upcoming-event-img');
            if (data.image_url) {
                imageElement.src = '/static/images/' + data.image_url;
                imageContainer.style.display = 'block';
            } else {
                imageContainer.style.display = 'none';
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

            document.getElementById('upcoming-event-date').textContent = dateString;
            document.getElementById('upcoming-event-description').textContent = data.description || '';

            // Calculate time remaining for upcoming event countdown
            const now = new Date();
            const timeDiff = eventDate - now;

            if (timeDiff > 0) {
                const days = Math.floor(timeDiff / (1000 * 60 * 60 * 24));
                const hours = Math.floor((timeDiff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                const minutes = Math.floor((timeDiff % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((timeDiff % (1000 * 60)) / 1000);

                document.getElementById('upcoming-days').textContent = days.toString().padStart(2, '0');
                document.getElementById('upcoming-hours').textContent = hours.toString().padStart(2, '0');
                document.getElementById('upcoming-minutes').textContent = minutes.toString().padStart(2, '0');
                document.getElementById('upcoming-seconds').textContent = seconds.toString().padStart(2, '0');
            } else {
                // Event has passed, hide section
                upcomingSection.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error fetching next event:', error);
            document.getElementById('upcoming-event').style.display = 'none';
        });
}

// Add event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
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
        // Update upcoming event every second
        setInterval(updateUpcomingEvent, 1000);
    }
});

// Debounce function for search input
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

// Password toggle functionality
function togglePassword(fieldId) {
    const input = document.getElementById(fieldId);
    const button = input.nextElementSibling;

    if (input.type === 'password') {
        input.type = 'text';
        button.textContent = '🙈';
    } else {
        input.type = 'password';
        button.textContent = '👁️';
    }
}

// ===========================================
// SCROLL-TRIGGERED ANIMATIONS
// ===========================================

// Intersection Observer for scroll animations
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

// Observe all elements with animate-on-scroll class
function initScrollAnimations() {
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    animatedElements.forEach(element => {
        observer.observe(element);
    });
}

// ===========================================
// ENHANCED INTERACTIONS
// ===========================================

// Smooth scroll for anchor links
function initSmoothScrolling() {
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);

            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Card hover effects enhancement
function initCardInteractions() {
    const cards = document.querySelectorAll('.goal-card, .discussion-card, .partner-card');

    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

// Button ripple effect enhancement
function initButtonEffects() {
    const buttons = document.querySelectorAll('mui-button');

    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;

            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple-effect');

            this.appendChild(ripple);

            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
}

// ===========================================
// PERFORMANCE OPTIMIZATIONS
// ===========================================

// Lazy loading for images
function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');

    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        images.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback for browsers without IntersectionObserver
        images.forEach(img => {
            img.src = img.dataset.src;
        });
    }
}

// ===========================================
// INITIALIZATION
// ===========================================

// Wait for the DOM to be fully loaded before running the script
document.addEventListener('DOMContentLoaded', function () {
    // Initialize scroll animations
    initScrollAnimations();

    // Initialize smooth scrolling
    initSmoothScrolling();

    // Initialize card interactions
    initCardInteractions();

    // Initialize button effects
    initButtonEffects();

    // Initialize lazy loading
    initLazyLoading();

    // Mobile menu toggle
    const menuToggle = document.getElementById('menu-toggle');
    const mainNav = document.getElementById('main-nav');
    const icon = menuToggle.querySelector('i');

    if (menuToggle && mainNav) {
        menuToggle.addEventListener('click', function () {
            // Toggle the .is-active class on the nav menu
            mainNav.classList.toggle('is-active');

            // Toggle the hamburger/close icon
            if (mainNav.classList.contains('is-active')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times'); // The 'X' icon
                menuToggle.setAttribute('aria-expanded', 'true');
            } else {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
                menuToggle.setAttribute('aria-expanded', 'false');
            }
        });
    }
});
