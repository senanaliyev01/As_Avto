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

    // Chat ikonuna klik
    document.getElementById('chat-icon').addEventListener('click', () => {
        chatWindow.style.display = chatWindow.style.display === 'none' ? 'flex' : 'none';
        if (chatWindow.style.display === 'flex') {
            loadChatUsers();
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
    });

    // İstifadəçilər siyahısına qayıt
    backButton.addEventListener('click', () => {
        chatMain.style.display = 'none';
        chatSidebar.style.display = 'block';
        currentReceiverId = null;
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

    // Səs yazmağı başlat
    async function startRecording(e) {
        e.preventDefault();
        if (isRecording) return;

        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            isRecording = true;

            // Vizual feedback
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
                chatMessages.innerHTML = '';
                messages.forEach(appendMessage);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            });
    }

    // Link tanıma funksiyası
    function detectLinks(text) {
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        return text.replace(urlRegex, function(url) {
            return `<a href="${url}" target="_blank">${url}</a>`;
        });
    }

    // Mesaj əlavə et
    function appendMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${message.is_mine ? 'mine' : 'theirs'}`;

        if (message.type === 'audio') {
            messageDiv.innerHTML = `
                <div class="message-content">
                    <audio controls>
                        <source src="${message.content}" type="audio/webm">
                    </audio>
                    <span class="time">${new Date(message.created_at).toLocaleTimeString()}</span>
                </div>
            `;
        } else {
            const messageContent = detectLinks(message.content);
            messageDiv.innerHTML = `
                <div class="message-content">
                    ${messageContent}
                    <span class="time">${new Date(message.created_at).toLocaleTimeString()}</span>
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

    // Avtomatik yeniləmə
    setInterval(() => {
        if (currentReceiverId) {
            loadMessages(currentReceiverId);
        }
    }, 3000);

    // İlkin yükləmə
    if (chatWindow.style.display === 'flex') {
        loadChatUsers();
    }
}); 