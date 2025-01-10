document.addEventListener('DOMContentLoaded', function() {
    const chatWidget = document.getElementById('chat-widget');
    const chatWindow = document.getElementById('chat-window');
    const chatMessages = document.getElementById('chat-messages');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-message');
    const closeButton = document.getElementById('close-chat');
    const fullscreenButton = document.getElementById('fullscreen-chat');
    const audioButton = document.querySelector('.audio-btn');
    const backButton = document.getElementById('back-to-users');
    const chatMain = document.querySelector('.chat-main');
    const chatSidebar = document.querySelector('.chat-sidebar');
    
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    let currentReceiverId = null;
    let lastMessageId = 0;
    let messageUpdateInterval;
    let userUpdateInterval;
    let lastUserUpdateHash = '';

    // Realtime yeniləmələr üçün optimizasiya edilmiş funksiya
    function startRealtimeUpdates() {
        messageUpdateInterval = setInterval(() => {
            if (currentReceiverId) {
                fetch(`/istifadeciler/api/chat/messages/${currentReceiverId}/`)
                    .then(response => response.json())
                    .then(messages => {
                        if (messages.length > 0) {
                            const lastMessage = messages[messages.length - 1];
                            if (lastMessage && lastMessage.id > lastMessageId) {
                                const newMessages = messages.filter(msg => msg.id > lastMessageId);
                                appendNewMessages(newMessages);
                                if (!lastMessage.is_mine) {
                                    playMessageSound();
                                }
                            }
                        }
                    });
            }
        }, 1000);

        userUpdateInterval = setInterval(loadChatUsers, 2000);
    }

    // Yeni mesajları əlavə et
    function appendNewMessages(newMessages) {
        const wasAtBottom = isScrolledToBottom();
        
        newMessages.forEach(message => {
            appendMessage(message);
            lastMessageId = Math.max(lastMessageId, message.id);
        });

        if (wasAtBottom) {
            scrollToBottom();
        }

        // Oxunmamış mesajları işarələ
        const unreadMessages = newMessages.filter(m => !m.is_mine && !m.is_read);
        if (unreadMessages.length > 0) {
            markMessagesAsRead(unreadMessages.map(m => m.id));
        }
    }

    // Scroll vəziyyətini yoxla
    function isScrolledToBottom() {
        const threshold = 50; // 50px tolerans
        return (chatMessages.scrollHeight - chatMessages.scrollTop - chatMessages.clientHeight) < threshold;
    }

    // Aşağı scroll et
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // İstifadəçilər siyahısını yeniləmək üçün optimizasiya
    function loadChatUsers() {
        fetch('/istifadeciler/api/chat/users/')
            .then(response => response.json())
            .then(data => {
                const newHash = JSON.stringify(data);
                if (newHash !== lastUserUpdateHash) {
                    lastUserUpdateHash = newHash;
                    updateUsersList(data);
                }
            });
    }

    // İstifadəçilər siyahısını yenilə
    function updateUsersList(data) {
        const usersList = document.getElementById('users-list');
        const fragment = document.createDocumentFragment();
        
        if (data.admins && data.admins.length > 0) {
            const adminTitle = document.createElement('div');
            adminTitle.className = 'user-group-title';
            adminTitle.textContent = 'Adminlər';
            fragment.appendChild(adminTitle);
            
            data.admins.forEach(user => {
                fragment.appendChild(createUserElement(user));
            });
        }
        
        if (data.users && data.users.length > 0) {
            const userTitle = document.createElement('div');
            userTitle.className = 'user-group-title';
            userTitle.textContent = 'İstifadəçilər';
            fragment.appendChild(userTitle);
            
            data.users.forEach(user => {
                fragment.appendChild(createUserElement(user));
            });
        }

        // DOM-u bir dəfə yeniləyirik
        usersList.innerHTML = '';
        usersList.appendChild(fragment);
    }

    // İstifadəçi elementi yaratmaq
    function createUserElement(user) {
        const div = document.createElement('div');
        div.className = `user-item ${user.unread_count > 0 ? 'has-unread' : ''}`;
        div.onclick = () => selectUser(user.id, user.username);
        
        div.innerHTML = `
            <div class="user-info">
                <i class="fas ${user.is_admin ? 'fa-user-shield admin-icon' : 'fa-user'}"></i>
                <span>${user.username}</span>
            </div>
            ${user.unread_count > 0 ? 
                `<span class="unread-count">${user.unread_count}</span>` : 
                ''}
        `;
        
        return div;
    }

    // Mesaj elementi yaratmaq
    function createMessageElement(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${message.is_mine ? 'mine' : 'theirs'}`;
        
        const messageTime = new Date(message.created_at || new Date()).toLocaleTimeString('az-AZ', {
            hour: '2-digit',
            minute: '2-digit'
        });

        let statusIcon = '';
        if (message.is_mine) {
            statusIcon = message.is_read ? 
                '<span class="message-status read"><i class="fas fa-check-double"></i></span>' :
                message.is_delivered ?
                    '<span class="message-status delivered"><i class="fas fa-check"></i></span>' :
                    '<span class="message-status sent"><i class="fas fa-clock"></i></span>';
        }

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        if (message.type === 'audio') {
            contentDiv.innerHTML = `
                <audio controls>
                    <source src="${message.content}" type="audio/webm">
                </audio>
                <div class="message-meta">
                    <span class="time">${messageTime}</span>
                    ${statusIcon}
                </div>
            `;
        } else {
            contentDiv.innerHTML = `
                ${detectLinks(message.content)}
                <div class="message-meta">
                    <span class="time">${messageTime}</span>
                    ${statusIcon}
                </div>
            `;
        }

        messageDiv.appendChild(contentDiv);
        return messageDiv;
    }

    // Mesaj əlavə et
    function appendMessage(message) {
        const messageElement = createMessageElement(message);
        chatMessages.appendChild(messageElement);
    }

    // Qalan funksiyalar eyni qalır
    function stopRealtimeUpdates() {
        clearInterval(messageUpdateInterval);
        clearInterval(userUpdateInterval);
    }

    function playMessageSound() {
        const audio = document.getElementById('chat-message-sound');
        if (audio) {
            audio.currentTime = 0;
            audio.play().catch(err => console.log('Səs oxutma xətası:', err));
        }
    }

    // Event listener'lar
    document.getElementById('chat-icon').addEventListener('click', () => {
        const isVisible = chatWindow.style.display === 'flex';
        chatWindow.style.display = isVisible ? 'none' : 'flex';
        
        if (isVisible) {
            stopRealtimeUpdates();
        } else {
            loadChatUsers();
            startRealtimeUpdates();
            chatMain.style.display = 'none';
            chatSidebar.style.display = 'block';
        }
    });

    fullscreenButton.addEventListener('click', () => {
        chatWindow.classList.toggle('fullscreen');
        fullscreenButton.innerHTML = chatWindow.classList.contains('fullscreen') ? 
            '<i class="fas fa-compress"></i>' : '<i class="fas fa-expand"></i>';
    });

    closeButton.addEventListener('click', () => {
        chatWindow.style.display = 'none';
        chatWindow.classList.remove('fullscreen');
        stopRealtimeUpdates();
    });

    backButton.addEventListener('click', () => {
        chatMain.style.display = 'none';
        chatSidebar.style.display = 'block';
        currentReceiverId = null;
        stopRealtimeUpdates();
        startRealtimeUpdates();
    });

    // Səs yazma
    audioButton.addEventListener('touchstart', startRecording);
    audioButton.addEventListener('touchend', stopRecording);
    audioButton.addEventListener('mousedown', startRecording);
    audioButton.addEventListener('mouseup', stopRecording);
    audioButton.addEventListener('mouseleave', stopRecording);

    // Mesaj göndərmə
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Search funksionallığı
    const searchInput = document.getElementById('user-search');
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            const searchTerm = searchInput.value.toLowerCase();
            document.querySelectorAll('.user-item').forEach(item => {
                const username = item.querySelector('.user-info span').textContent.toLowerCase();
                item.style.display = username.includes(searchTerm) ? 'flex' : 'none';
            });
        });
    }

    // Köməkçi funksiyalar
    function detectLinks(text) {
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        return text.replace(urlRegex, url => 
            `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`
        );
    }

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }

    function showNotification(type, message) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 3000);
    }

    window.selectUser = function(userId, username) {
        currentReceiverId = userId;
        document.getElementById('selected-username').textContent = username;
        chatSidebar.style.display = 'none';
        chatMain.style.display = 'flex';
        loadMessages(userId);
    };

    // İlkin yükləmə
    if (chatWindow.style.display === 'flex') {
        loadChatUsers();
        startRealtimeUpdates();
    }
});