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

    // Polling interval for checking new messages and users
    let messagePollingInterval;
    let userPollingInterval;

    // Mesajları yenilə (Polling)
    function pollMessages() {
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
    }

    // İstifadəçiləri yenilə (Polling)
    function pollUsers() {
        fetch('/istifadeciler/api/chat/users/')
            .then(response => response.json())
            .then(data => {
                const usersList = document.getElementById('users-list');
                usersList.innerHTML = '';
                
                if (data.admins && data.admins.length > 0) {
                    usersList.innerHTML += '<div class="user-group-title">Adminlər</div>';
                    data.admins.forEach(user => {
                        usersList.innerHTML += createUserItem(user);
                    });
                }
                
                if (data.users && data.users.length > 0) {
                    usersList.innerHTML += '<div class="user-group-title">İstifadəçilər</div>';
                    data.users.forEach(user => {
                        usersList.innerHTML += createUserItem(user);
                    });
                }
            });
    }

    // Polling başlat
    function startPolling() {
        messagePollingInterval = setInterval(pollMessages, 5000); // Mesajlar hər 5 saniyədə bir yeniləyir
        userPollingInterval = setInterval(pollUsers, 10000); // İstifadəçilər hər 10 saniyədə bir yeniləyir
    }

    // Polling durdur
    function stopPolling() {
        clearInterval(messagePollingInterval);
        clearInterval(userPollingInterval);
    }

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

    // Chat ikonuna klik
    document.getElementById('chat-icon').addEventListener('click', () => {
        const isVisible = chatWindow.style.display === 'flex';
        chatWindow.style.display = isVisible ? 'none' : 'flex';
        
        if (isVisible) {
            stopPolling();
        } else {
            loadChatUsers();
            startPolling();
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
        stopPolling();
    });

    // İstifadəçilər siyahısına qayıt
    backButton.addEventListener('click', () => {
        chatMain.style.display = 'none';
        chatSidebar.style.display = 'block';
        currentReceiverId = null;
        stopPolling();
        startPolling();
    });

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

    // İstifadəçiləri yüklə
    function loadChatUsers() {
        fetch('/istifadeciler/api/chat/users/')
            .then(response => response.json())
            .then(data => {
                const usersList = document.getElementById('users-list');
                usersList.innerHTML = '';
                
                if (data.admins && data.admins.length > 0) {
                    usersList.innerHTML += '<div class="user-group-title">Adminlər</div>';
                    data.admins.forEach(user => {
                        usersList.innerHTML += createUserItem(user);
                    });
                }
                
                if (data.users && data.users.length > 0) {
                    usersList.innerHTML += '<div class="user-group-title">İstifadəçilər</div>';
                    data.users.forEach(user => {
                        usersList.innerHTML += createUserItem(user);
                    });
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
                    <span class="username">${user.username}</span>
                </div>
                ${user.unread_count > 0 ? `<span class="unread-count">${user.unread_count}</span>` : ''}
            </div>
        `;
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

    // Səsli xəbərdarlıq
    function playMessageSound() {
        const audio = new Audio('/static/audio/new-message.mp3');
        audio.play();
    }

    // Mesajı əlavə et
    function appendMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.textContent = message.content;
        chatMessages.appendChild(messageDiv);
    }

    // Polling başlat
    startPolling();
});
