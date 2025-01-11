document.addEventListener('DOMContentLoaded', function() {
    // Chat widget-i dinamik olaraq əlavə et
    if (document.body) {
        const chatWidgetHTML = `
            <audio id="new-message-sound" preload="auto">
                <source src="/static/audio/notification.mp3" type="audio/mpeg">
            </audio>
            <audio id="chat-message-sound" preload="auto">
                <source src="/static/audio/chat-message.mp3" type="audio/mpeg">
            </audio>
            <div id="chat-widget" class="chat-widget">
                <div id="chat-icon" class="chat-icon">
                    <i class="fas fa-comments"></i>
                    <span id="total-unread" class="unread-count" style="display: none;">0</span>
                </div>
                <div id="chat-window" class="chat-window" style="display: none;">
                    <div class="chat-header">
                        <div class="chat-title">Mesajlar</div>
                        <div class="header-actions">
                            <button id="fullscreen-chat" class="header-button">
                                <i class="fas fa-expand"></i>
                            </button>
                            <button id="close-chat" class="header-button">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    </div>
                    <div class="chat-container">
                        <div class="chat-sidebar">
                            <div class="search-box">
                                <input type="text" id="user-search" placeholder="İstifadəçi axtar...">
                            </div>
                            <div id="users-list" class="users-list"></div>
                        </div>
                        <div class="chat-main" style="display: none;">
                            <div class="selected-user">
                                <i class="fas fa-arrow-left" id="back-to-users"></i>
                                <span id="selected-username"></span>
                            </div>
                            <div class="chat-messages" id="chat-messages"></div>
                            <div class="chat-input">
                                <button class="audio-btn" type="button">
                                    <i class="fas fa-microphone"></i>
                                    <div class="recording-wave" style="display: none;">
                                        <span></span><span></span><span></span><span></span><span></span>
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
        document.body.insertAdjacentHTML('beforeend', chatWidgetHTML);
    }

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
    let statusUpdateInterval;
    let totalUnreadMessages = 0;
    let lastUsersList = [];
    let isWindowFocused = true;

    // Focus izləmə
    window.addEventListener('focus', () => isWindowFocused = true);
    window.addEventListener('blur', () => isWindowFocused = false);

    // Real-time mesaj yeniləməsi
    function startRealtimeUpdates() {
        // Mesajları yoxlama - hər 2 saniyədə
        messageUpdateInterval = setInterval(() => {
            if (currentReceiverId) {
                fetch(`/istifadeciler/api/chat/messages/${currentReceiverId}/`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.messages) {
                            data.messages.forEach(message => {
                                const existingMessage = document.querySelector(`[data-message-id="${message.id}"]`);
                                if (!existingMessage) {
                                    appendMessage(message);
                                    if (!message.is_mine) {
                                        playChatMessageSound();
                                    }
                                }
                            });
                        }
                    });
            }
        }, 2000);

        // İstifadəçiləri yeniləmə - hər 5 saniyədə
        userUpdateInterval = setInterval(() => {
            fetch('/istifadeciler/api/chat/users/')
                .then(response => response.json())
                .then(data => {
                    updateUsersList(data);
                    updateTotalUnreadCount(data);
                });
        }, 5000);
    }

    function stopRealtimeUpdates() {
        clearInterval(messageUpdateInterval);
        clearInterval(userUpdateInterval);
    }

    // Mesaj səsini oxut
    function playMessageSound() {
        const audio = document.getElementById('chat-message-sound');
        if (audio) {
            audio.currentTime = 0;
            audio.play().catch(err => console.log('Səs oxutma xətası:', err));
        }
    }

    // Chat ikonuna klik
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

    // Tam ekran düyməsi
    fullscreenButton.addEventListener('click', () => {
        chatWindow.classList.toggle('fullscreen');
        fullscreenButton.innerHTML = chatWindow.classList.contains('fullscreen') ? 
            '<i class="fas fa-compress"></i>' : '<i class="fas fa-expand"></i>';
    });

    // Chat pəncərəsini bağla
    closeButton.addEventListener('click', () => {
        chatWindow.style.display = 'none';
        chatWindow.classList.remove('fullscreen');
        stopRealtimeUpdates();
    });

    // İstifadəçilər siyahısına qayıt
    backButton.addEventListener('click', () => {
        chatMain.style.display = 'none';
        chatSidebar.style.display = 'block';
        currentReceiverId = null;
        stopRealtimeUpdates();
        startRealtimeUpdates();
    });

    // Mesajları yenilə
    function updateMessages(messages) {
        const scrolledToBottom = chatMessages.scrollHeight - chatMessages.scrollTop === chatMessages.clientHeight;
        
        chatMessages.innerHTML = '';
        messages.forEach(appendMessage);
        
        if (scrolledToBottom) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        if (messages.length > 0) {
            lastMessageId = messages[messages.length - 1].id;
            
            // Oxunmamış mesajları oxundu olaraq işarələ
            const unreadMessages = messages.filter(m => !m.is_mine && !m.is_read);
            if (unreadMessages.length > 0) {
                markMessagesAsRead(unreadMessages.map(m => m.id));
            }
        }
    }

    // Mesajları oxundu olaraq işarələ
    function markMessagesAsRead(messageIds) {
        if (!messageIds.length) return;
        
        fetch('/istifadeciler/api/chat/mark-read/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ message_ids: messageIds })
        });
    }

    // Mesaj göndər
    sendButton.addEventListener('click', () => {
        const content = messageInput.value.trim();
        if (content) {
            sendMessage(content);
        }
    });

    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            const content = messageInput.value.trim();
            if (content) {
                sendMessage(content);
            }
        }
    });

    // Səs yazma - mobil üçün
    audioButton.addEventListener('touchstart', startRecording);
    audioButton.addEventListener('touchend', stopRecording);

    // Səs yazma - PC üçün
    audioButton.addEventListener('mousedown', startRecording);
    audioButton.addEventListener('mouseup', stopRecording);
    audioButton.addEventListener('mouseleave', stopRecording);

    // Səs yazmağı başlat
    async function startRecording(e) {
        e.preventDefault();
        if (isRecording) return;

        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            isRecording = true;

            audioButton.classList.add('recording');
            audioButton.querySelector('.recording-wave').style.display = 'flex';

            mediaRecorder.ondataavailable = (e) => {
                audioChunks.push(e.data);
            };

            mediaRecorder.start();
        } catch (err) {
            console.error('Səs yazma xətası:', err);
            showNotification('error', 'Səs yazmaq üçün icazə lazımdır');
        }
    }

    // Səs yazmağı bitir
    function stopRecording(e) {
        e.preventDefault();
        if (!isRecording) return;

        mediaRecorder.stop();
        isRecording = false;
        audioButton.classList.remove('recording');
        audioButton.querySelector('.recording-wave').style.display = 'none';

        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            sendAudioMessage(audioBlob);
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
        };
    }

    // Mesaj göndərmə funksiyası
    function sendMessage(content, type = 'text') {
        if (!currentReceiverId) return;

        const formData = new FormData();
        formData.append('receiver_id', currentReceiverId);
        formData.append('content', content);
        formData.append('type', type);

        fetch('/istifadeciler/api/chat/send/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                appendMessage(data.message);
                messageInput.value = '';
            }
        })
        .catch(error => console.error('Mesaj göndərmə xətası:', error));
    }

    // Mesaj silmə funksiyası
    function deleteMessage(messageId) {
        fetch(`/istifadeciler/api/chat/delete-message/${messageId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
                if (messageElement) {
                    messageElement.remove();
                }
            }
        })
        .catch(error => console.error('Mesaj silmə xətası:', error));
    }

    // Müvəqqəti mesajı yenilə
    function updateTempMessage(tempId, newMessage) {
        const messageEl = document.querySelector(`[data-message-id="${tempId}"]`);
        if (messageEl) {
            messageEl.dataset.messageId = newMessage.id;
            const statusSpan = messageEl.querySelector('.message-status');
            if (statusSpan) {
                statusSpan.innerHTML = '<i class="fas fa-check"></i>';
                statusSpan.classList.add('delivered');
            }
        }
    }

    // Xəta halında mesajı işarələ
    function markMessageError(messageId) {
        const messageEl = document.querySelector(`[data-message-id="${messageId}"]`);
        if (messageEl) {
            const statusSpan = messageEl.querySelector('.message-status');
            if (statusSpan) {
                statusSpan.innerHTML = '<i class="fas fa-exclamation-circle"></i>';
                statusSpan.classList.add('error');
            }
        }
    }

    // Səs mesajını göndər
    function sendAudioMessage(blob) {
        const formData = new FormData();
        formData.append('audio', blob, 'voice.webm');
        formData.append('receiver_id', currentReceiverId);
        
        fetch('/istifadeciler/api/chat/send-audio/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                appendMessage(data.message);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            } else {
                showNotification('error', data.message || 'Səs mesajı göndərilə bilmədi');
            }
        })
        .catch(error => {
            console.error('Səs mesajı göndərmə xətası:', error);
            showNotification('error', 'Səs mesajı göndərilə bilmədi');
        });
    }

    // İstifadəçi seçimi
    window.selectUser = function(userId, username) {
        currentReceiverId = userId;
        document.getElementById('selected-username').textContent = username;
        chatSidebar.style.display = 'none';
        chatMain.style.display = 'flex';
        loadMessages(userId);
    };

    // Mesajları yüklə
    function loadMessages(userId) {
        fetch(`/istifadeciler/api/chat/messages/${userId}/`)
            .then(response => response.json())
            .then(messages => {
                updateMessages(messages);
            });
    }

    // Link tanıma funksiyası
    function detectLinks(text) {
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        return text.replace(urlRegex, function(url) {
            return `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`;
        });
    }

    // Mesaj əlavə et
    function appendMessage(message) {
        const messageElement = createMessageElement(message);
        chatMessages.appendChild(messageElement);

        // Avtomatik scroll
        if (isScrolledToBottom()) {
            smoothScrollToBottom();
        }

        // Səs effektləri
        if (!message.is_mine) {
            if (!isWindowFocused || chatWindow.style.display !== 'flex') {
                playNewMessageSound();
            } else {
                playChatMessageSound();
            }
        }
    }

    // CSRF token funksiyası
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Bildiriş göstər
    function showNotification(type, message) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // İstifadəçiləri yüklə
    function loadChatUsers() {
        fetch('/istifadeciler/api/chat/users/')
            .then(response => response.json())
            .then(data => {
                const usersList = document.getElementById('users-list');
                usersList.innerHTML = '';
                
                // Admin və istifadəçi görünürlüyü
                if (data.is_admin) {
                    // Admin bütün istifadəçiləri görür
                    if (data.admins && data.admins.length > 0) {
                        usersList.innerHTML += '<div class="user-group-title">Adminlər</div>';
                        data.admins.forEach(user => {
                            if (user.id !== currentUserId) {
                                usersList.innerHTML += createUserItem(user);
                            }
                        });
                    }
                    
                    if (data.users && data.users.length > 0) {
                        usersList.innerHTML += '<div class="user-group-title">İstifadəçilər</div>';
                        data.users.forEach(user => {
                            usersList.innerHTML += createUserItem(user);
                        });
                    }
                } else {
                    // Normal istifadəçi yalnız adminləri görür
                    if (data.admins && data.admins.length > 0) {
                        usersList.innerHTML = '<div class="user-group-title">Adminlər</div>';
                        data.admins.forEach(user => {
                            usersList.innerHTML += createUserItem(user);
                        });
                    }
                }
            });
    }

    // İstifadəçi elementi yarat
    function createUserItem(user) {
        return `
            <div class="user-item ${user.unread_count > 0 ? 'has-unread' : ''}" 
                 onclick="selectUser(${user.id}, '${user.username}')">
                <div class="user-info">
                    <i class="fas ${user.is_admin ? 'fa-user-shield admin-icon' : 'fa-user'}"></i>
                    <span>${user.username}</span>
                </div>
                ${user.unread_count > 0 ? 
                    `<span class="unread-count">${user.unread_count}</span>` : 
                    ''}
            </div>
        `;
    }

    // İstifadəçi axtarışı
    const searchInput = document.getElementById('user-search');
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            const searchTerm = searchInput.value.toLowerCase();
            const userItems = document.querySelectorAll('.user-item');
            
            userItems.forEach(item => {
                const username = item.querySelector('.user-info span').textContent.toLowerCase();
                item.style.display = username.includes(searchTerm) ? 'flex' : 'none';
            });
        });
    }

    // İlkin yükləmə
    if (chatWindow.style.display === 'flex') {
        loadChatUsers();
        startRealtimeUpdates();
    }

    // Mesaj statuslarını yeniləyən funksiya
    function updateMessageStatuses(messages) {
        const messageElements = chatMessages.querySelectorAll('.message');
        
        messageElements.forEach(messageEl => {
            const messageId = messageEl.dataset.messageId;
            const message = messages.find(m => m.id.toString() === messageId);
            
            if (message && messageEl.classList.contains('mine')) {
                const statusSpan = messageEl.querySelector('.message-status');
                if (statusSpan) {
                    if (message.is_read) {
                        statusSpan.innerHTML = '<i class="fas fa-check-double"></i>';
                        statusSpan.classList.add('read');
                    } else if (message.is_delivered) {
                        statusSpan.innerHTML = '<i class="fas fa-check"></i>';
                        statusSpan.classList.add('delivered');
                    }
                }
            }
        });
    }

    // Səssiz mesaj yeniləməsi
    function updateMessagesQuietly(messages) {
        const scrolledToBottom = isScrolledToBottom();
        const fragment = document.createDocumentFragment();
        const existingIds = new Set(Array.from(chatMessages.children).map(el => el.dataset.messageId));

        messages.forEach(message => {
            if (!existingIds.has(message.id.toString())) {
                const messageEl = createMessageElement(message);
                fragment.appendChild(messageEl);
                
                if (!message.is_mine && !message.is_read) {
                    markMessagesAsRead([message.id]);
                }
            }
        });

        if (fragment.children.length > 0) {
            chatMessages.appendChild(fragment);
            
            if (scrolledToBottom) {
                smoothScrollToBottom();
            }
        }

        if (messages.length > 0) {
            lastMessageId = messages[messages.length - 1].id;
        }
    }

    // Yumşaq scroll funksiyası
    function smoothScrollToBottom() {
        chatMessages.scrollTo({
            top: chatMessages.scrollHeight,
            behavior: 'smooth'
        });
    }

    // Scroll pozisiyasını yoxla
    function isScrolledToBottom() {
        return chatMessages.scrollHeight - chatMessages.clientHeight <= chatMessages.scrollTop + 100;
    }

    // Yeni mesaj səsi
    function playNewMessageSound() {
        const audio = document.getElementById('new-message-sound');
        if (audio && (!isWindowFocused || !chatWindow.style.display === 'flex')) {
            audio.currentTime = 0;
            audio.play().catch(err => console.log('Səs oxutma xətası:', err));
        }
    }

    // Bildiriş göstər
    function showNotification(title, message) {
        if (!("Notification" in window)) return;

        if (Notification.permission === "granted") {
            new Notification(title, { body: message });
        } else if (Notification.permission !== "denied") {
            Notification.requestPermission().then(permission => {
                if (permission === "granted") {
                    new Notification(title, { body: message });
                }
            });
        }
    }

    // Mesaj elementi yaratma
    function createMessageElement(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${message.is_mine ? 'mine' : 'theirs'}`;
        messageDiv.dataset.messageId = message.id;

        let deleteButton = '';
        if (message.is_mine) {
            deleteButton = `
                <button class="delete-message" onclick="deleteMessage(${message.id})">
                    <i class="fas fa-trash"></i>
                </button>
            `;
        }

        const messageTime = new Date(message.created_at).toLocaleTimeString('az-AZ', {
            hour: '2-digit',
            minute: '2-digit'
        });

        let statusIcon = '';
        if (message.is_mine) {
            if (message.is_read) {
                statusIcon = '<i class="fas fa-check-double"></i>';
            } else if (message.is_delivered) {
                statusIcon = '<i class="fas fa-check"></i>';
            }
        }

        messageDiv.innerHTML = `
            <div class="message-content">
                ${message.type === 'audio' ? 
                    `<audio controls><source src="${message.content}" type="audio/webm"></audio>` :
                    detectLinks(message.content)
                }
                <div class="message-meta">
                    <span class="time">${messageTime}</span>
                    ${statusIcon}
                    ${deleteButton}
                </div>
            </div>
        `;

        return messageDiv;
    }

    // Yeni mesajları yoxla
    async function checkNewMessages() {
        try {
            const response = await fetch(`/istifadeciler/api/chat/messages/${currentReceiverId}/`);
            const messages = await response.json();
            const lastMessage = messages[messages.length - 1];

            if (lastMessage && lastMessage.id > lastMessageId) {
                updateMessagesQuietly(messages);
                if (!lastMessage.is_mine) {
                    if (!isWindowFocused) {
                        playNewMessageSound();
                        showNotification('Yeni mesaj', `${lastMessage.sender}: ${lastMessage.content}`);
                    }
                }
            } else {
                updateMessageStatuses(messages);
            }
        } catch (error) {
            console.error('Mesaj yoxlama xətası:', error);
        }
    }

    // Online istifadəçiləri yoxla
    async function checkOnlineUsers() {
        try {
            const response = await fetch('/istifadeciler/api/chat/users/');
            const data = await response.json();
            
            // İstifadəçi siyahısını müqayisə et və dəyişiklik varsa yenilə
            if (hasUserListChanged(data)) {
                updateUsersList(data);
                lastUsersList = data;
            }

            // Oxunmamış mesajları hesabla
            updateTotalUnreadCount(data);
        } catch (error) {
            console.error('İstifadəçi yoxlama xətası:', error);
        }
    }

    // İstifadəçi siyahısının dəyişib-dəyişmədiyini yoxla
    function hasUserListChanged(newData) {
        if (!lastUsersList.admins || !lastUsersList.users) return true;
        
        const oldUsers = [...(lastUsersList.admins || []), ...(lastUsersList.users || [])];
        const newUsers = [...(newData.admins || []), ...(newData.users || [])];
        
        if (oldUsers.length !== newUsers.length) return true;
        
        return JSON.stringify(oldUsers) !== JSON.stringify(newUsers);
    }

    // İstifadəçi siyahısını yenilə
    function updateUsersList(data) {
        const usersList = document.getElementById('users-list');
        const currentContent = usersList.innerHTML;
        let newContent = '';

        // Admin üçün bütün istifadəçiləri göstər
        if (data.is_admin) {
            if (data.users && data.users.length > 0) {
                newContent += '<div class="user-group-title">İstifadəçilər</div>';
                data.users.forEach(user => {
                    newContent += createUserItem(user);
                });
            }
        }
        
        // Adminləri göstər
        if (data.admins && data.admins.length > 0) {
            newContent += '<div class="user-group-title">Adminlər</div>';
            data.admins.forEach(user => {
                newContent += createUserItem(user);
            });
        }

        // Əgər məzmun dəyişibsə, yalnız onda DOM-u yenilə
        if (currentContent !== newContent) {
            usersList.innerHTML = newContent;
        }
    }

    // Ümumi oxunmamış mesaj sayını yenilə
    function updateTotalUnreadCount(data) {
        const allUsers = [...(data.admins || []), ...(data.users || [])];
        const totalUnread = allUsers.reduce((sum, user) => sum + (user.unread_count || 0), 0);
        
        const unreadBadge = document.getElementById('total-unread');
        const chatIcon = document.getElementById('chat-icon');
        
        if (unreadBadge) {
            if (totalUnread > 0) {
                unreadBadge.textContent = totalUnread;
                unreadBadge.style.display = 'flex';
                chatIcon.classList.add('has-unread');
                if (!isWindowFocused) {
                    playNewMessageSound();
                }
            } else {
                unreadBadge.style.display = 'none';
                chatIcon.classList.remove('has-unread');
            }
        }
    }

    // Mesaj silmə funksiyası
    window.deleteMessage = deleteMessage;
}); 