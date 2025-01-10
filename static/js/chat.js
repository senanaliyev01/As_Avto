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

    // Real-time mesaj yeniləməsi
    function startRealtimeUpdates() {
        // Mesajları hər 2 saniyədə bir yenilə
        messageUpdateInterval = setInterval(() => {
            if (currentReceiverId) {
                fetch(`/istifadeciler/api/chat/messages/${currentReceiverId}/`)
                    .then(response => response.json())
                    .then(messages => {
                        const lastMessage = messages[messages.length - 1];
                        if (lastMessage && lastMessage.id > lastMessageId) {
                            // Yeni mesajlar var
                            updateMessages(messages);
                            if (!lastMessage.is_mine) {
                                playMessageSound();
                            }
                        }
                    });
            }
        }, 2000);

        // İstifadəçiləri hər 5 saniyədə bir yenilə
        userUpdateInterval = setInterval(loadChatUsers, 5000);
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
        if (messages.length === 0) return;
        
        const lastMsg = messages[messages.length - 1];
        
        // Əgər yeni mesaj yoxdursa, heç nə etmirik
        if (lastMsg.id <= lastMessageId) return;
        
        // Scroll pozisiyasını yoxlayırıq
        const scrolledToBottom = Math.abs(
            chatMessages.scrollHeight - chatMessages.scrollTop - chatMessages.clientHeight
        ) < 10;
        
        // Mövcud mesajları saxlayırıq
        const existingMessages = {};
        chatMessages.querySelectorAll('.message').forEach(el => {
            const msgId = el.getAttribute('data-message-id');
            if (msgId) existingMessages[msgId] = el;
        });
        
        // Yeni mesajları əlavə edirik
        messages.forEach(message => {
            if (!existingMessages[message.id]) {
                const messageDiv = createMessageElement(message);
                chatMessages.appendChild(messageDiv);
                delete existingMessages[message.id];
            }
        });
        
        // Scroll pozisiyasını qoruyuruq
        if (scrolledToBottom) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        lastMessageId = lastMsg.id;
        
        // Oxunmamış mesajları işarələyirik
        const unreadMessages = messages.filter(m => !m.is_mine && !m.is_read);
        if (unreadMessages.length > 0) {
            markMessagesAsRead(unreadMessages.map(m => m.id));
        }
    }

    // Yeni funksiya: Mesaj elementi yaratmaq üçün
    function createMessageElement(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${message.is_mine ? 'mine' : 'theirs'}`;
        messageDiv.setAttribute('data-message-id', message.id);
        
        let statusIcon = '';
        if (message.is_mine) {
            if (message.is_read) {
                statusIcon = '<span class="message-status read"><i class="fas fa-check-double"></i></span>';
            } else if (message.is_delivered) {
                statusIcon = '<span class="message-status delivered"><i class="fas fa-check"></i></span>';
            } else {
                statusIcon = '<span class="message-status sent"><i class="fas fa-clock"></i></span>';
            }
        }

        const messageTime = new Date(message.created_at || new Date()).toLocaleTimeString('az-AZ', {
            hour: '2-digit',
            minute: '2-digit'
        });

        if (message.type === 'audio') {
            messageDiv.innerHTML = `
                <div class="message-content">
                    <audio controls>
                        <source src="${message.content}" type="audio/webm">
                    </audio>
                    <div class="message-meta">
                        <span class="time">${messageTime}</span>
                        ${statusIcon}
                    </div>
                </div>
            `;
        } else {
            const messageContent = detectLinks(message.content);
            messageDiv.innerHTML = `
                <div class="message-content">
                    ${messageContent}
                    <div class="message-meta">
                        <span class="time">${messageTime}</span>
                        ${statusIcon}
                    </div>
                </div>
            `;
        }

        return messageDiv;
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
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
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
    function sendMessage() {
        const content = messageInput.value.trim();
        if (!content || !currentReceiverId) return;

        const formData = new FormData();
        formData.append('receiver_id', currentReceiverId);
        formData.append('content', content);

        fetch('/istifadeciler/api/chat/send/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                messageInput.value = '';
                appendMessage(data.message);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        })
        .catch(error => console.error('Error:', error));
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
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${message.is_mine ? 'mine' : 'theirs'}`;
        
        let statusIcon = '';
        if (message.is_mine) {
            if (message.is_read) {
                statusIcon = '<span class="message-status read"><i class="fas fa-check-double"></i></span>';
            } else if (message.is_delivered) {
                statusIcon = '<span class="message-status delivered"><i class="fas fa-check"></i></span>';
            } else {
                statusIcon = '<span class="message-status sent"><i class="fas fa-clock"></i></span>';
            }
        }

        const messageTime = new Date(message.created_at || new Date()).toLocaleTimeString('az-AZ', {
            hour: '2-digit',
            minute: '2-digit'
        });

        if (message.type === 'audio') {
            messageDiv.innerHTML = `
                <div class="message-content">
                    <audio controls>
                        <source src="${message.content}" type="audio/webm">
                    </audio>
                    <div class="message-meta">
                        <span class="time">${messageTime}</span>
                        ${statusIcon}
                    </div>
                </div>
            `;
        } else {
            const messageContent = detectLinks(message.content);
            messageDiv.innerHTML = `
                <div class="message-content">
                    ${messageContent}
                    <div class="message-meta">
                        <span class="time">${messageTime}</span>
                        ${statusIcon}
                    </div>
                </div>
            `;
        }

        chatMessages.appendChild(messageDiv);
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
                const currentUsers = new Set();
                
                // Mövcud istifadəçiləri saxlayırıq
                const existingUsers = {};
                usersList.querySelectorAll('.user-item').forEach(el => {
                    const userId = el.getAttribute('data-user-id');
                    if (userId) existingUsers[userId] = el;
                });
                
                // Adminləri əlavə edirik
                if (data.admins && data.admins.length > 0) {
                    if (!usersList.querySelector('.admin-group')) {
                        usersList.insertAdjacentHTML('beforeend', '<div class="user-group-title admin-group">Adminlər</div>');
                    }
                    data.admins.forEach(user => {
                        updateOrCreateUserElement(user, existingUsers, usersList);
                        currentUsers.add(user.id.toString());
                    });
                }
                
                // İstifadəçiləri əlavə edirik
                if (data.users && data.users.length > 0) {
                    if (!usersList.querySelector('.users-group')) {
                        usersList.insertAdjacentHTML('beforeend', '<div class="user-group-title users-group">İstifadəçilər</div>');
                    }
                    data.users.forEach(user => {
                        updateOrCreateUserElement(user, existingUsers, usersList);
                        currentUsers.add(user.id.toString());
                    });
                }
                
                // Artıq mövcud olmayan istifadəçiləri silirik
                Object.keys(existingUsers).forEach(userId => {
                    if (!currentUsers.has(userId)) {
                        existingUsers[userId].remove();
                    }
                });
            });
    }

    // Yeni funksiya: İstifadəçi elementini yeniləmək və ya yaratmaq üçün
    function updateOrCreateUserElement(user, existingUsers, usersList) {
        const userElement = existingUsers[user.id];
        const newUserHtml = createUserItem(user);
        
        if (userElement) {
            // Əgər məzmun dəyişibsə, yeniləyirik
            if (userElement.outerHTML !== newUserHtml) {
                userElement.outerHTML = newUserHtml;
            }
            delete existingUsers[user.id];
        } else {
            // Yeni element əlavə edirik
            usersList.insertAdjacentHTML('beforeend', newUserHtml);
        }
    }

    // createUserItem funksiyasını yeniləyirik
    function createUserItem(user) {
        return `
            <div class="user-item ${user.unread_count > 0 ? 'has-unread' : ''}" 
                 onclick="selectUser(${user.id}, '${user.username}')"
                 data-user-id="${user.id}">
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
}); 