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
