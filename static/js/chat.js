class ChatApp {
    constructor() {
        this.initializeVariables();
        this.createChatWidget();
        this.attachEventListeners();
        this.startRealtimeUpdates();
    }

    initializeVariables() {
        this.currentReceiverId = null;
        this.lastMessageId = 0;
        this.isWindowFocused = true;
        this.config = window.CHAT_CONFIG || {};
        this.intervals = {
            messages: null,
            users: null
        };
    }

    createChatWidget() {
        const chatHTML = `
                            <div id="chat-messages" class="chat-messages"></div>
                            <div class="chat-input">
                                <button class="audio-btn" type="button">
                                    <i class="fas fa-microphone"></i>
                                    <div class="recording-wave" style="display: none;">
                                        <span></span><span></span><span></span>
                                        <span></span><span></span>
                                    </div>
                                </button>
                                <div class="message-input-container">
                                    <input type="text" id="message-input" placeholder="Mesajınızı yazın...">
                                </div>
                                <button id="send-message" type="button">
                                    <i class="fas fa-paper-plane"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', chatHTML);
        this.initializeElements();
    }

    initializeElements() {
        // Əsas elementləri əldə et
        this.elements = {
            chatWidget: document.getElementById('chat-widget'),
            chatWindow: document.getElementById('chat-window'),
            chatMessages: document.getElementById('chat-messages'),
            messageInput: document.getElementById('message-input'),
            sendButton: document.getElementById('send-message'),
            chatIcon: document.getElementById('chat-icon'),
            usersList: document.getElementById('users-list'),
            chatMain: document.querySelector('.chat-main'),
            chatSidebar: document.querySelector('.chat-sidebar'),
            backButton: document.getElementById('back-to-users'),
            closeButton: document.getElementById('close-chat'),
            fullscreenButton: document.getElementById('fullscreen-chat'),
            audioButton: document.querySelector('.audio-btn'),
            unreadBadge: document.getElementById('total-unread')
        };
    }

    attachEventListeners() {
        // Focus izləmə
        window.addEventListener('focus', () => this.isWindowFocused = true);
        window.addEventListener('blur', () => this.isWindowFocused = false);

        // Chat ikonuna klik
        this.elements.chatIcon.addEventListener('click', () => this.toggleChat());

        // Mesaj göndərmə
        this.elements.sendButton.addEventListener('click', () => this.sendMessage());
        this.elements.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Digər düymələr
        this.elements.backButton.addEventListener('click', () => this.showUsersList());
        this.elements.closeButton.addEventListener('click', () => this.closeChat());
        this.elements.fullscreenButton.addEventListener('click', () => this.toggleFullscreen());
    }

    async startRealtimeUpdates() {
        // Mesajları yoxla
        this.intervals.messages = setInterval(async () => {
            if (this.currentReceiverId) {
                await this.checkNewMessages();
            }
        }, 2000);

        // İstifadəçiləri yoxla
        this.intervals.users = setInterval(async () => {
            await this.updateUsers();
        }, 5000);
    }

    async checkNewMessages() {
        try {
            const response = await fetch(`/istifadeciler/api/chat/messages/${this.currentReceiverId}/`);
            const messages = await response.json();

            if (!Array.isArray(messages)) return;

            messages.forEach(message => {
                if (!document.querySelector(`[data-message-id="${message.id}"]`)) {
                    this.appendMessage(message);
                    if (!message.is_mine && !message.is_read) {
                        this.playMessageSound();
                    }
                }
            });

            // Oxunmamış mesajları yenilə
            const unreadMessages = messages.filter(m => !m.is_mine && !m.is_read);
            if (unreadMessages.length > 0) {
                this.markMessagesAsRead(unreadMessages.map(m => m.id));
            }
        } catch (error) {
            console.error('Mesaj yoxlama xətası:', error);
        }
    }

    async updateUsers() {
        try {
            const response = await fetch('/istifadeciler/api/chat/users/');
            const data = await response.json();
            
            this.updateUsersList(data);
            this.updateUnreadCount(data);
        } catch (error) {
            console.error('İstifadəçi yeniləmə xətası:', error);
        }
    }

    async sendMessage() {
        const content = this.elements.messageInput.value.trim();
        if (!content || !this.currentReceiverId) return;

        try {
            const formData = new FormData();
            formData.append('receiver_id', this.currentReceiverId);
            formData.append('content', content);

            const response = await fetch('/istifadeciler/api/chat/send/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.config.csrfToken
                },
                body: formData
            });

            const data = await response.json();
            if (data.status === 'success') {
                this.elements.messageInput.value = '';
                this.appendMessage(data.message);
            }
        } catch (error) {
            console.error('Mesaj göndərmə xətası:', error);
        }
    }

    appendMessage(message) {
        const messageElement = this.createMessageElement(message);
        this.elements.chatMessages.appendChild(messageElement);
        this.scrollToBottom();
    }

    createMessageElement(message) {
        const div = document.createElement('div');
        div.className = `message ${message.is_mine ? 'mine' : 'theirs'}`;
        div.dataset.messageId = message.id;

        const deleteButton = message.is_mine ? 
            `<button class="delete-message" onclick="chat.deleteMessage(${message.id})">
                <i class="fas fa-trash"></i>
            </button>` : '';

        const time = new Date(message.created_at).toLocaleTimeString('az-AZ', {
            hour: '2-digit',
            minute: '2-digit'
        });

        div.innerHTML = `
            <div class="message-content">
                ${message.type === 'audio' ? 
                    `<audio controls><source src="${message.content}" type="audio/webm"></audio>` :
                    this.detectLinks(message.content)
                }
                <div class="message-meta">
                    <span class="time">${time}</span>
                    ${message.is_mine ? `
                        ${message.is_read ? '<i class="fas fa-check-double"></i>' : 
                         message.is_delivered ? '<i class="fas fa-check"></i>' : ''}
                        ${deleteButton}
                    ` : ''}
                </div>
            </div>
        `;

        return div;
    }

    async deleteMessage(messageId) {
        try {
            const response = await fetch(`/istifadeciler/api/chat/delete-message/${messageId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.config.csrfToken
                }
            });

            if (response.ok) {
                const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
                if (messageElement) {
                    messageElement.remove();
                }
            }
        } catch (error) {
            console.error('Mesaj silmə xətası:', error);
        }
    }

    // Utility funksiyaları
    detectLinks(text) {
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        return text.replace(urlRegex, url => 
            `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`
        );
    }

    scrollToBottom() {
        this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
    }

    playMessageSound() {
        const audio = document.getElementById(
            this.isWindowFocused ? 'chat-message-sound' : 'new-message-sound'
        );
        if (audio) {
            audio.currentTime = 0;
            audio.play().catch(err => console.log('Səs oxutma xətası:', err));
        }
    }
}

// Chat tətbiqini başlat
const chat = new ChatApp(); 