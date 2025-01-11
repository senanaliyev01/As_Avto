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
    let statusUpdateInterval;
    let totalUnreadMessages = 0;
    let lastUsersList = [];
    let isWindowFocused = true;

    // Focus izləmə
    window.addEventListener('focus', () => isWindowFocused = true);
    window.addEventListener('blur', () => isWindowFocused = false);

    // Real-time mesaj yeniləməsi
    function startRealtimeUpdates() {
        // Mesajları yoxlama - hər 1 saniyədə
        messageUpdateInterval = setInterval(() => {
            if (currentReceiverId) {
                checkNewMessages();
            }
        }, 1000);

        // İstifadəçiləri yeniləmə - hər 3 saniyədə
        userUpdateInterval = setInterval(() => {
            checkOnlineUsers();
        }, 3000);
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

        const tempId = Date.now();
        
        try {
            // Müvəqqəti mesajı göstər
            appendMessage({
                id: tempId,
                content: content,
                is_mine: true,
                is_delivered: false,
                is_read: false,
                created_at: new Date()
            });

            messageInput.value = '';
            
            if (isScrolledToBottom()) {
                smoothScrollToBottom();
            }

            // Mesajı göndər
            const formData = new FormData();
            formData.append('receiver_id', currentReceiverId);
            formData.append('content', content);

            const response = await fetch('/istifadeciler/api/chat/send/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });

            const data = await response.json();

            if (data.status === 'success') {
                updateTempMessage(tempId, data.message);
                playSound('chat');
            } else {
                throw new Error(data.message || 'Mesaj göndərmə xətası');
            }
        } catch (error) {
            console.error('Mesaj göndərmə xətası:', error);
            markMessageError(tempId);
        }
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
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${message.is_mine ? 'mine' : 'theirs'}`;
        messageDiv.dataset.messageId = message.id; // Message ID əlavə edirik
        
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

        // Yeni mesajı əlavə edərkən səlis animasiya
        messageDiv.style.opacity = '0';
        chatMessages.appendChild(messageDiv);
        
        // Səlis görünmə effekti
        requestAnimationFrame(() => {
            messageDiv.style.transition = 'opacity 0.3s ease';
            messageDiv.style.opacity = '1';
        });

        // Avtomatik scroll
        if (chatMessages.scrollTop + chatMessages.clientHeight >= chatMessages.scrollHeight - 100) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
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

    // İstifadəçi rolunu təyin et
    const isAdmin = window.isAdmin || false;

    // Səs effektləri
    const newMessageSound = document.getElementById('new-message-sound');
    const chatMessageSound = document.getElementById('chat-message-sound');

    function playSound(type) {
        const audio = type === 'new' ? newMessageSound : chatMessageSound;
        if (audio) {
            audio.currentTime = 0;
            audio.volume = 0.5; // Səs səviyyəsini azalt
            audio.play().catch(err => console.warn('Səs oxuma xətası:', err));
        }
    }

    // İstifadəçiləri yükləmə funksiyasını təkmilləşdirək
    async function loadChatUsers() {
        try {
            const response = await fetch('/istifadeciler/api/chat/users/');
            const data = await response.json();
            
            const usersList = document.getElementById('users-list');
            let newContent = '';

            // Admin bütün istifadəçiləri görür
            if (isAdmin) {
                if (data.users?.length > 0) {
                    newContent += '<div class="user-group-title">İstifadəçilər</div>';
                    data.users.forEach(user => {
                        newContent += createUserItem(user);
                    });
                }
            }

            // Adminləri göstər (həm admin həm də normal istifadəçilər üçün)
            if (data.admins?.length > 0) {
                newContent += '<div class="user-group-title">Adminlər</div>';
                data.admins.forEach(user => {
                    newContent += createUserItem(user);
                });
            }

            // DOM-u yalnız dəyişiklik varsa yenilə
            if (usersList.innerHTML !== newContent) {
                usersList.innerHTML = newContent;
            }

            updateTotalUnreadCount(data);
        } catch (error) {
            console.error('İstifadəçi yükləmə xətası:', error);
        }
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
    function initialize() {
        requestNotificationPermission();
        
        if (chatWindow.style.display === 'flex') {
            loadChatUsers();
            startRealtimeUpdates();
        }

        // Enter ilə mesaj göndərmə
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    // Funksiyaları çağır
    initialize();

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
        const target = chatMessages.scrollHeight;
        const duration = 300;
        const start = chatMessages.scrollTop;
        const distance = target - start;
        let startTime = null;

        function animation(currentTime) {
            if (startTime === null) startTime = currentTime;
            const timeElapsed = currentTime - startTime;
            const progress = Math.min(timeElapsed / duration, 1);
            
            chatMessages.scrollTop = start + distance * easeInOutQuad(progress);
            
            if (progress < 1) {
                requestAnimationFrame(animation);
            }
        }
        
        requestAnimationFrame(animation);
    }

    // Scroll pozisiyasını yoxla
    function isScrolledToBottom() {
        const tolerance = 50; // 50px tolerans
        return chatMessages.scrollHeight - chatMessages.scrollTop - chatMessages.clientHeight < tolerance;
    }

    // Easing funksiyası
    function easeInOutQuad(t) {
        return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
    }

    // Yeni mesaj səsi
    function playNewMessageSound() {
        const audio = document.getElementById('new-message-sound');
        if (audio) {
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

        const messageTime = new Date(message.created_at).toLocaleTimeString('az-AZ', {
            hour: '2-digit',
            minute: '2-digit'
        });

        messageDiv.innerHTML = `
            <div class="message-content">
                ${message.type === 'audio' ? 
                    `<audio controls><source src="${message.content}" type="audio/webm"></audio>` :
                    detectLinks(message.content)
                }
                <div class="message-meta">
                    <span class="time">${messageTime}</span>
                    ${statusIcon}
                </div>
            </div>
        `;

        return messageDiv;
    }

    // Yeni mesajları yoxla
    async function checkNewMessages() {
        if (!currentReceiverId) return;

        try {
            const response = await fetch(`/istifadeciler/api/chat/messages/${currentReceiverId}/`);
            const messages = await response.json();
            
            if (!messages.length) return;

            const lastMessage = messages[messages.length - 1];
            
            if (lastMessage.id > lastMessageId) {
                updateMessagesQuietly(messages);
                
                if (!lastMessage.is_mine) {
                    // Səhifə fokusda deyilsə bildiriş göstər
                    if (!isWindowFocused) {
                        playSound('new');
                        showNotification('Yeni mesaj', `${lastMessage.sender}: ${lastMessage.content}`);
                    } else {
                        playSound('chat');
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
        if (unreadBadge) {
            if (totalUnread > 0) {
                unreadBadge.textContent = totalUnread;
                unreadBadge.style.display = 'flex';
            } else {
                unreadBadge.style.display = 'none';
            }
        }
    }

    // Bildiriş icazəsini yoxla və istə
    function requestNotificationPermission() {
        if ("Notification" in window && Notification.permission === "default") {
            Notification.requestPermission();
        }
    }
}); 
