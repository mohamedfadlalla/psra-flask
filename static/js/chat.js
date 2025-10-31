// Chat functionality using Socket.IO
class ChatManager {
    constructor() {
        this.socket = null;
        this.currentUserId = null;
        this.otherUserId = null;
        this.typingTimeout = null;
        this.isTyping = false;
        this.init();
    }

    init() {
        // Get user IDs from the page
        this.currentUserId = document.body.getAttribute('data-current-user-id');
        this.otherUserId = document.body.getAttribute('data-other-user-id');

        if (this.currentUserId && this.otherUserId) {
            this.connectSocket();
            this.setupEventListeners();
        }
    }

    connectSocket() {
        this.socket = io();

        // Join user's personal room
        this.socket.emit('join', { user_id: this.currentUserId });

        // Set up socket event listeners
        this.socket.on('joined', (data) => {
            console.log('Joined room:', data.room);
        });

        this.socket.on('new_message', (data) => {
            this.handleNewMessage(data);
        });

        this.socket.on('message_sent', (data) => {
            this.handleMessageSent(data);
        });

        this.socket.on('typing_started', (data) => {
            this.showTypingIndicator(data.user_name);
        });

        this.socket.on('typing_stopped', (data) => {
            this.hideTypingIndicator();
        });

        this.socket.on('messages_read', (data) => {
            this.handleMessagesRead(data);
        });

        this.socket.on('error', (data) => {
            console.error('Socket error:', data.message);
        });
    }

    setupEventListeners() {
        const messageForm = document.querySelector('.reply-form form');
        const messageInput = document.querySelector('#content');

        if (messageForm && messageInput) {
            // Handle form submission
            messageForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.sendMessage();
            });

            // Handle typing events
            messageInput.addEventListener('input', () => {
                this.handleTyping();
            });

            messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }

        // Mark messages as read when conversation is viewed
        this.markMessagesAsRead();
    }

    sendMessage() {
        const messageInput = document.querySelector('#content');
        const content = messageInput.value.trim();

        if (!content) return;

        // Stop typing indicator
        this.stopTyping();

        // Send via Socket.IO
        this.socket.emit('send_message', {
            sender_id: parseInt(this.currentUserId),
            receiver_id: parseInt(this.otherUserId),
            content: content
        });

        // Clear input
        messageInput.value = '';
    }

    handleNewMessage(data) {
        // Only add if it's not from current user (to avoid duplication)
        if (data.sender_id != this.currentUserId) {
            this.addMessageToUI(data, false);
            // Auto-scroll to bottom
            this.scrollToBottom();
        }
    }

    handleMessageSent(data) {
        // Add sent message to UI
        this.addMessageToUI(data, true);
        // Auto-scroll to bottom
        this.scrollToBottom();
    }

    addMessageToUI(messageData, isSent) {
        const container = document.getElementById('messages-container');

        // Create message element
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isSent ? 'sent' : 'received'}`;
        messageDiv.setAttribute('data-message-id', messageData.id);

        messageDiv.innerHTML = `
            <div class="message-content">
                <p>${this.escapeHtml(messageData.content)}</p>
                <small class="message-time">${this.formatTime(messageData.created_at)}</small>
                ${isSent && messageData.is_read ? '<small class="read-receipt">✓✓</small>' : ''}
            </div>
        `;

        // Insert before typing indicator
        const typingIndicator = document.getElementById('typing-indicator');
        container.insertBefore(messageDiv, typingIndicator);
    }

    handleTyping() {
        if (!this.isTyping) {
            this.isTyping = true;
            this.socket.emit('typing_start', {
                sender_id: parseInt(this.currentUserId),
                receiver_id: parseInt(this.otherUserId)
            });
        }

        // Clear existing timeout
        clearTimeout(this.typingTimeout);

        // Set new timeout to stop typing
        this.typingTimeout = setTimeout(() => {
            this.stopTyping();
        }, 1000);
    }

    stopTyping() {
        if (this.isTyping) {
            this.isTyping = false;
            this.socket.emit('typing_stop', {
                sender_id: parseInt(this.currentUserId),
                receiver_id: parseInt(this.otherUserId)
            });
        }
        clearTimeout(this.typingTimeout);
    }

    showTypingIndicator(userName) {
        const indicator = document.getElementById('typing-indicator');
        const userNameSpan = document.getElementById('typing-user-name');

        userNameSpan.textContent = userName;
        indicator.style.display = 'block';
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        indicator.style.display = 'none';
    }

    markMessagesAsRead() {
        // Mark messages as read when viewing conversation
        this.socket.emit('mark_read', {
            user_id: parseInt(this.currentUserId),
            other_user_id: parseInt(this.otherUserId)
        });
    }

    handleMessagesRead(data) {
        // Update read receipts for sent messages
        data.message_ids.forEach(messageId => {
            const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
            if (messageElement && messageElement.classList.contains('sent')) {
                const existingReceipt = messageElement.querySelector('.read-receipt');
                if (!existingReceipt) {
                    const receipt = document.createElement('small');
                    receipt.className = 'read-receipt';
                    receipt.textContent = '✓✓';
                    messageElement.querySelector('.message-content').appendChild(receipt);
                }
            }
        });

        // Update navigation badge count
        this.updateNavBadge();
    }

    updateNavBadge() {
        // Update the unread message count in navigation
        const badge = document.querySelector('.notification-badge');
        if (badge) {
            // Get current count from server or decrement by read messages
            // For now, we'll hide the badge if it exists (simplified approach)
            // In a production app, you'd want to fetch the actual count
            fetch('/api/unread-count')
                .then(response => response.json())
                .then(data => {
                    if (data.count > 0) {
                        badge.textContent = data.count;
                        badge.style.display = 'inline-flex';
                    } else {
                        badge.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Error updating badge:', error);
                });
        }
    }

    scrollToBottom() {
        const container = document.getElementById('messages-container');
        container.scrollTop = container.scrollHeight;
    }

    formatTime(isoString) {
        const date = new Date(isoString);
        return date.toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    deleteMessage(messageId) {
        if (confirm('Are you sure you want to delete this message? This action cannot be undone.')) {
            fetch(`/forum/messages/delete/${messageId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Remove the message from UI
                    const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
                    if (messageElement) {
                        messageElement.remove();
                    }
                    // Update nav badge
                    this.updateNavBadge();
                } else {
                    alert('Error deleting message: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Error deleting message:', error);
                alert('Error deleting message. Please try again.');
            });
        }
    }
}

// Global functions for delete operations
function deleteMessage(messageId) {
    if (window.chatManager) {
        window.chatManager.deleteMessage(messageId);
    }
}

function deleteConversation(button) {
    const userId = button.getAttribute('data-user-id');
    const userName = button.getAttribute('data-user-name');

    if (confirm(`Are you sure you want to delete the entire conversation with ${userName}? This will delete all messages and cannot be undone.`)) {
        fetch(`/forum/messages/delete_conversation/${userId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Redirect to messages page
                window.location.href = '/forum/messages';
            } else {
                alert('Error deleting conversation: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error deleting conversation:', error);
            alert('Error deleting conversation. Please try again.');
        });
    }
}

// Initialize chat when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize on conversation pages
    if (document.getElementById('messages-container')) {
        window.chatManager = new ChatManager();
    }
});
