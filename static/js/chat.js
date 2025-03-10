// WebSocket xətalarını gizlətmək üçün window.onerror hadisəsi
window.onerror = function(message, source, lineno, colno, error) {
    // WebSocket ilə bağlı xətaları gizlət
    if (source && source.includes('chat.js') && message && (
        message.includes('WebSocket') || 
        message.includes('ws://') || 
        message.includes('wss://')
    )) {
        // Xətanı gizlət
        return true;
    }
    
    // Digər xətaları normal emal et
    return false;
};

// Chat funksionallığı
let currentReceiverId = null;
let currentReceiverName = null;
let lastMessageCount = 0;
let lastMessageId = 0;
let chatSocket = null;
let usingWebSocket = false; // WebSocket istifadə edilib-edilmədiyini izləmək üçün
let suppressWebSocketErrors = true; // WebSocket xətalarını gizlətmək üçün
let useOnlyHTTP = true; // Yalnız HTTP istifadə et, WebSocket-i tamamilə söndür

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



// Chat funksiyasını başlat
function initChat() {
    if (!suppressWebSocketErrors) {
        console.log('Chat funksiyası başladılır...');
    }
    
    // İstifadəçi daxil olmayıbsa, funksiyadan çıx
    if (typeof currentUserId === 'undefined' || !currentUserId) {
        if (!suppressWebSocketErrors) {
            console.log('İstifadəçi daxil olmayıb, chat funksiyası başladılmır');
        }
        return;
    }
    
    const chatIcon = document.getElementById('chat-icon');
    const chatWindow = document.getElementById('chat-window');
    const closeChat = document.getElementById('close-chat');
    const backButton = document.getElementById('back-to-users');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-message');
    const chatMain = document.querySelector('.chat-main');
    const chatSidebar = document.querySelector('.chat-sidebar');

    if (!chatIcon || !chatWindow) {
        if (!suppressWebSocketErrors) {
            console.log('Chat elementləri tapılmadı!');
        }
        return;
    }

    // WebSocket bağlantısını yarat (yalnız HTTP istifadə edilmirsə)
    if (!useOnlyHTTP) {
        try {
            connectWebSocket();
        } catch (error) {
            if (!suppressWebSocketErrors) {
                console.error('WebSocket bağlantısı yaradılarkən xəta:', error);
                console.log('WebSocket bağlantısı yaradıla bilmədi, HTTP sorğularından istifadə ediləcək');
            }
        }
    }

    // Chat ikonuna klik
    chatIcon.addEventListener('click', () => {
        // Chat pəncərəsini aç/bağla
        chatWindow.style.display = chatWindow.style.display === 'none' ? 'flex' : 'none';
        
        if (chatWindow.style.display === 'flex') {
            // İstifadəçiləri yüklə
            loadChatUsers();
            
            // Chat əsas pəncərəsini gizlət, istifadəçilər siyahısını göstər
            chatMain.style.display = 'none';
            chatSidebar.style.display = 'block';
            
            // Bildiriş göstər
            if (typeof showAnimatedMessage === 'function') {
                // Oxunmamış mesaj sayını al
                const totalUnreadElement = document.getElementById('total-unread');
                const unreadCount = totalUnreadElement ? parseInt(totalUnreadElement.textContent) || 0 : 0;
                
                if (unreadCount > 0) {
                    showAnimatedMessage(`${unreadCount} oxunmamış mesajınız var!`, false);
                } else {
                    showAnimatedMessage('Mesajlarınız yoxdur', false);
                }
            }
            
            // Chat ikonundan bildiriş animasiyasını sil
            chatIcon.classList.remove('pulse-animation');
        }
    });

    // Chat pəncərəsini bağla
    closeChat.addEventListener('click', () => {
        chatWindow.style.display = 'none';
    });

    // İstifadəçilər siyahısına qayıt
    backButton.addEventListener('click', () => {
        chatMain.style.display = 'none';
        chatSidebar.style.display = 'block';
        currentReceiverId = null;
        currentReceiverName = null;
    });

    // Mesaj göndər
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // İstifadəçiləri və mesajları yenilə
    setInterval(() => {
        try {
            loadChatUsers();
        } catch (error) {
            if (!suppressWebSocketErrors) {
                console.error('İstifadəçilər yüklənərkən xəta:', error);
            }
        }
    }, 3000);
    
    setInterval(() => {
        try {
            if (currentReceiverId) {
                loadMessages(currentReceiverId);
            }
        } catch (error) {
            if (!suppressWebSocketErrors) {
                console.error('Mesajlar yüklənərkən xəta:', error);
            }
        }
    }, 1000);

    // Axtarış funksiyasını əlavə et
    const searchInput = document.getElementById('user-search');
    if (searchInput) {
        searchInput.addEventListener('input', filterUsers);
    }
}

// WebSocket bağlantısını yarat
function connectWebSocket() {
    // Əgər yalnız HTTP istifadə ediləcəksə, WebSocket bağlantısını yaratma
    if (useOnlyHTTP) {
        return;
    }
    
    if (suppressWebSocketErrors) {
        console.log('WebSocket bağlantısı yaradılır (səssiz rejim)...');
    } else {
        console.log('WebSocket bağlantısı yaradılır...');
    }
    
    try {
        // WebSocket bağlantısını yarat - HTTPS sayt üçün həmişə WSS istifadə et
        const wsUrl = 'wss://' + window.location.host + '/ws/chat/';
        
        if (!suppressWebSocketErrors) {
            console.log('WebSocket URL:', wsUrl);
            console.log('Cari host:', window.location.host);
            console.log('Cari protokol:', window.location.protocol);
        }
        
        // Əvvəlki bağlantını bağla
        if (chatSocket && chatSocket.readyState !== WebSocket.CLOSED) {
            chatSocket.close();
        }
        
        try {
            // WebSocket bağlantısını sınayırıq, lakin xəta baş verdikdə HTTP sorğularından istifadə edirik
            if (!suppressWebSocketErrors) {
                console.log('WebSocket obyekti yaradılır...');
            }
            
            chatSocket = new WebSocket(wsUrl);
            usingWebSocket = false; // Əvvəlcə false təyin edirik, bağlantı açıldıqda true olacaq
            
            // WebSocket bağlantısı üçün 5 saniyə gözləyirik
            let wsConnectTimeout = setTimeout(() => {
                if (!suppressWebSocketErrors) {
                    console.log('WebSocket bağlantısı vaxtı bitdi, HTTP sorğularından istifadə ediləcək');
                }
                
                if (chatSocket && chatSocket.readyState !== WebSocket.OPEN) {
                    chatSocket.close();
                    
                    // Alternativ WebSocket URL sınayaq
                    if (!suppressWebSocketErrors) {
                        tryAlternativeWebSocket();
                    }
                }
            }, 5000);
            
            chatSocket.onopen = function(e) {
                if (!suppressWebSocketErrors) {
                    console.log('WebSocket bağlantısı açıldı');
                }
                
                clearTimeout(wsConnectTimeout);
                usingWebSocket = true; // Bağlantı uğurlu olduqda true təyin edirik
                
                // İstifadəçiyə bildiriş göstər (yalnız debug rejimində)
                if (!suppressWebSocketErrors && typeof showAnimatedMessage === 'function') {
                    showAnimatedMessage('Chat serveri ilə bağlantı quruldu!', false);
                }
            };
            
            chatSocket.onmessage = function(e) {
                try {
                    const data = JSON.parse(e.data);
                    
                    if (!suppressWebSocketErrors) {
                        console.log('WebSocket mesajı alındı:', data);
                    }
                    
                    // Bağlantı statusu mesajı
                    if (data.status === 'connected') {
                        if (!suppressWebSocketErrors) {
                            console.log('WebSocket bağlantısı uğurla quruldu:', data.message);
                        }
                        return;
                    }
                    
                    if (data.message) {
                        // Əgər hazırda həmin istifadəçi ilə söhbət edirsinizsə, mesajı göstər
                        if (currentReceiverId && (data.message.sender === currentReceiverName || data.message.is_mine)) {
                            appendMessage(data.message);
                            
                            // Əgər mesaj bizim deyilsə, səs çal
                            if (!data.message.is_mine) {
                                playChatMessageSound();
                            }
                        } else {
                            // Əks halda bildiriş səsini çal
                            playNewMessageSound();
                            
                            // İstifadəçi siyahısını yenilə
                            loadChatUsers();
                        }
                    }
                } catch (error) {
                    if (!suppressWebSocketErrors) {
                        console.error('WebSocket mesajı işlənərkən xəta:', error);
                    }
                }
            };
            
            chatSocket.onclose = function(e) {
                if (!suppressWebSocketErrors) {
                    console.log('WebSocket bağlantısı bağlandı', e.code, e.reason);
                }
                
                clearTimeout(wsConnectTimeout);
                usingWebSocket = false;
                
                // WebSocket bağlantısı uğursuz olduqda HTTP sorğularından istifadə et
                if (e.code !== 1000 && !suppressWebSocketErrors) {
                    console.log('WebSocket bağlantısı qırıldı, HTTP sorğularından istifadə ediləcək');
                }
            };
            
            chatSocket.onerror = function(e) {
                if (!suppressWebSocketErrors) {
                    console.error('WebSocket xətası:', e);
                }
                
                clearTimeout(wsConnectTimeout);
                usingWebSocket = false;
                
                // Xəta baş verdikdə bağlantını bağla və HTTP sorğularından istifadə et
                if (chatSocket) {
                    chatSocket.close();
                }
                
                if (!suppressWebSocketErrors) {
                    console.log('WebSocket xətası baş verdi, HTTP sorğularından istifadə ediləcək');
                    
                    // İstifadəçiyə bildiriş göstər
                    if (typeof showAnimatedMessage === 'function') {
                        showAnimatedMessage('Chat serveri ilə bağlantı qurmaq mümkün olmadı. Mesajlar HTTP ilə göndəriləcək.', false);
                    }
                    
                    // Alternativ WebSocket URL sınayaq
                    tryAlternativeWebSocket();
                }
            };
        } catch (error) {
            if (!suppressWebSocketErrors) {
                console.error('WebSocket bağlantısı yaradılarkən xəta:', error);
                console.log('WebSocket bağlantısı yaradıla bilmədi, HTTP sorğularından istifadə ediləcək');
                
                // Alternativ WebSocket URL sınayaq
                tryAlternativeWebSocket();
            }
        }
    } catch (error) {
        if (!suppressWebSocketErrors) {
            console.error('WebSocket bağlantısı yaradılarkən xəta:', error);
        }
    }
}

// Alternativ WebSocket URL sınayaq
function tryAlternativeWebSocket() {
    if (suppressWebSocketErrors) {
        return; // Xəta gizlədilmişsə, alternativ URL-ləri sınama
    }
    
    try {
        console.log('Alternativ WebSocket URL sınayırıq...');
        
        // Alternativ URL-lər
        const alternativeUrls = [
            'wss://' + window.location.host + '/ws/chat/default/',
            'wss://www.' + window.location.host + '/ws/chat/',
            'wss://www.' + window.location.host + '/ws/chat/default/'
        ];
        
        // Əvvəlki bağlantını bağla
        if (chatSocket && chatSocket.readyState !== WebSocket.CLOSED) {
            chatSocket.close();
        }
        
        // Alternativ URL-ləri sınayaq
        for (const url of alternativeUrls) {
            try {
                console.log('Alternativ WebSocket URL sınayırıq:', url);
                chatSocket = new WebSocket(url);
                usingWebSocket = false;
                
                chatSocket.onopen = function(e) {
                    console.log('Alternativ WebSocket bağlantısı açıldı:', url);
                    usingWebSocket = true;
                    
                    // İstifadəçiyə bildiriş göstər
                    if (typeof showAnimatedMessage === 'function') {
                        showAnimatedMessage('Chat serveri ilə bağlantı quruldu!', false);
                    }
                };
                
                // Digər event handler-ləri əlavə et
                chatSocket.onmessage = function(e) {
                    try {
                        const data = JSON.parse(e.data);
                        console.log('WebSocket mesajı alındı:', data);
                        
                        // Bağlantı statusu mesajı
                        if (data.status === 'connected') {
                            console.log('WebSocket bağlantısı uğurla quruldu:', data.message);
                            return;
                        }
                        
                        if (data.message) {
                            // Əgər hazırda həmin istifadəçi ilə söhbət edirsinizsə, mesajı göstər
                            if (currentReceiverId && (data.message.sender === currentReceiverName || data.message.is_mine)) {
                                appendMessage(data.message);
                                
                                // Əgər mesaj bizim deyilsə, səs çal
                                if (!data.message.is_mine) {
                                    playChatMessageSound();
                                }
                            } else {
                                // Əks halda bildiriş səsini çal
                                playNewMessageSound();
                                
                                // İstifadəçi siyahısını yenilə
                                loadChatUsers();
                            }
                        }
                    } catch (error) {
                        console.error('WebSocket mesajı işlənərkən xəta:', error);
                    }
                };
                
                // Əgər bağlantı uğurlu olsa, digər URL-ləri sınamağa ehtiyac yoxdur
                break;
            } catch (error) {
                console.error('Alternativ WebSocket bağlantısı yaradılarkən xəta:', error);
            }
        }
    } catch (error) {
        console.error('Alternativ WebSocket bağlantısı yaradılarkən xəta:', error);
    }
}

// Mesajı əlavə et
function appendMessage(message) {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${message.is_mine ? 'mine' : 'theirs'}`;
    
    messageDiv.innerHTML = `
        ${!message.is_mine ? `<div class="message-sender">${message.sender}</div>` : ''}
        <div class="message-content">${message.content}</div>
        ${message.is_mine ? `
            <div class="message-status ${getMessageStatus(message)}">
                ${getStatusIcons(message)}
            </div>
        ` : ''}
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Chat istifadəçilərini yükləmə funksiyası
function loadChatUsers() {
    try {
        if (!suppressWebSocketErrors) {
            console.log('İstifadəçilər yüklənir...');
        }
        
        // Əgər istifadəçi daxil olmayıbsa, funksiyadan çıx
        if (!currentUserId) {
            if (!suppressWebSocketErrors) {
                console.log('İstifadəçi daxil olmayıb, istifadəçilər yüklənmir');
            }
            return;
        }
        
        fetch('/istifadeciler/api/chat/users/', {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken')
            },
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) {
                if (response.status === 500) {
                    if (!suppressWebSocketErrors) {
                        console.error('Server xətası (500): İstifadəçilər yüklənə bilmədi');
                    }
                } else if (response.status === 403) {
                    if (!suppressWebSocketErrors) {
                        console.error('Giriş icazəsi yoxdur (403): İstifadəçi daxil olmayıb və ya sessiyanın vaxtı bitib');
                    }
                } else {
                    if (!suppressWebSocketErrors) {
                        console.error(`HTTP xətası: ${response.status}`);
                    }
                }
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (!suppressWebSocketErrors) {
                console.log('İstifadəçi məlumatları alındı:', data);
            }
            
            const usersList = document.getElementById('users-list');
            if (!usersList) {
                if (!suppressWebSocketErrors) {
                    console.error('users-list elementi tapılmadı!');
                }
                return;
            }
            
            let totalUnread = 0;
            
            usersList.innerHTML = '';
            
            // Cari istifadəçinin admin olub-olmadığını yoxla
            const isCurrentUserAdmin = typeof isAdmin !== 'undefined' && isAdmin;
            
            // Adminləri əlavə et (yalnız istifadəçilər üçün və ya adminlər üçün bütün adminlər)
            if (data.admins && data.admins.length > 0) {
                usersList.innerHTML += '<div class="user-group-title">Adminlər</div>';
                data.admins.forEach(user => {
                    // Əgər cari istifadəçi admindisə və ya admin deyilsə, bütün adminləri göstər
                    if (isCurrentUserAdmin || !isCurrentUserAdmin) {
                        totalUnread += user.unread_count;
                        usersList.innerHTML += createUserItem(user);
                    }
                });
            }
            
            // İstifadəçiləri əlavə et (yalnız adminlər üçün)
            if (data.users && data.users.length > 0 && isCurrentUserAdmin) {
                usersList.innerHTML += '<div class="user-group-title">İstifadəçilər</div>';
                data.users.forEach(user => {
                    totalUnread += user.unread_count;
                    usersList.innerHTML += createUserItem(user);
                });
            }

            // Yeni mesaj varsa bildiriş səsini çal
            if (totalUnread > lastMessageCount) {
                playNewMessageSound();
            }

            lastMessageCount = totalUnread;
            updateUnreadCount(totalUnread);
        })
        .catch(error => {
            if (!suppressWebSocketErrors) {
                console.error('İstifadəçilər yüklənərkən xəta:', error);
            }
        });
    } catch (error) {
        if (!suppressWebSocketErrors) {
            console.error('İstifadəçilər yüklənərkən ümumi xəta:', error);
        }
    }
}

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

function updateUnreadCount(totalUnread) {
    const totalUnreadElement = document.getElementById('total-unread');
    const chatIcon = document.getElementById('chat-icon');
    
    if (!totalUnreadElement || !chatIcon) return;
    
    if (totalUnread > 0) {
        // Bildiriş sayını göstər
        totalUnreadElement.textContent = totalUnread;
        totalUnreadElement.style.display = 'block';
        
        // Chat ikonuna bildiriş sinfi əlavə et
        chatIcon.classList.add('has-notification');
        
        // Chat ikonunu animasiya et
        chatIcon.classList.add('pulse-animation');
        
        // Bildiriş səsini çal (əgər söndürülməyibsə)
        if (!disableNotificationSounds) {
            playNewMessageSound();
        }
    } else {
        // Bildiriş sayını gizlət
        totalUnreadElement.style.display = 'none';
        
        // Chat ikonundan bildiriş sinfini sil
        chatIcon.classList.remove('has-notification');
        
        // Chat ikonundan animasiyanı sil
        chatIcon.classList.remove('pulse-animation');
    }
}

function selectUser(userId, username) {
    if (!suppressWebSocketErrors) {
        console.log(`İstifadəçi seçildi: ${username} (ID: ${userId})`);
    }
    
    currentReceiverId = userId;
    currentReceiverName = username;
    
    const chatMain = document.querySelector('.chat-main');
    const chatSidebar = document.querySelector('.chat-sidebar');
    const selectedUsername = document.getElementById('selected-username');
    
    if (!chatMain || !chatSidebar || !selectedUsername) {
        if (!suppressWebSocketErrors) {
            console.error('Chat elementləri tapılmadı!');
        }
        return;
    }
    
    // İstifadəçilər siyahısını gizlət, mesajlaşma pəncərəsini göstər
    chatSidebar.style.display = 'none';
    chatMain.style.display = 'flex';
    
    // Seçilmiş istifadəçinin adını göstər
    selectedUsername.textContent = username;
    
    // Bildiriş göstər
    if (typeof showAnimatedMessage === 'function') {
        showAnimatedMessage(`${username} ilə söhbət başladıldı`, false);
    }
    
    // Mesajları yüklə
    loadMessages(userId);
    
    // Mesaj sahəsini fokusla
    const messageInput = document.getElementById('message-input');
    if (messageInput) {
        messageInput.focus();
    }
}

// Mesaj yükləmə funksiyası
function loadMessages(receiverId) {
    try {
        if (!suppressWebSocketErrors) {
            console.log(`${receiverId} ID-li istifadəçi ilə mesajlar yüklənir...`);
        }
        
        fetch(`/istifadeciler/api/chat/messages/${receiverId}/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(messages => {
                if (!suppressWebSocketErrors) {
                    console.log(`${messages.length} mesaj alındı`);
                }
                
                const chatMessages = document.getElementById('chat-messages');
                if (!chatMessages) {
                    if (!suppressWebSocketErrors) {
                        console.error('chat-messages elementi tapılmadı!');
                    }
                    return;
                }
                
                // Son mesajın ID-sini al
                const lastMessage = messages.length > 0 ? messages[messages.length - 1] : null;
                
                // Müvəqqəti mesajları saxla
                const tempMessages = Array.from(chatMessages.querySelectorAll('.message[id^="temp_"]'));
                
                // Mesajları tarixə görə sırala (köhnədən yeniyə)
                messages.sort((a, b) => {
                    const dateA = new Date(a.created_at || 0);
                    const dateB = new Date(b.created_at || 0);
                    return dateA - dateB;
                });
                
                // HTML-i yenilə
                chatMessages.innerHTML = messages.map(msg => `
                    <div class="message ${msg.is_mine ? 'mine' : 'theirs'}" data-id="${msg.id}">
                        ${!msg.is_mine ? `<div class="message-sender">${msg.sender}</div>` : ''}
                        <div class="message-content">${msg.content}</div>
                        ${msg.is_mine ? `
                            <div class="message-status ${getMessageStatus(msg)}">
                                ${getStatusIcons(msg)}
                            </div>
                        ` : ''}
                    </div>
                `).join('');
                
                // Müvəqqəti mesajları əlavə et (əgər serverdən gələn mesajlarda yoxdursa)
                tempMessages.forEach(tempMsg => {
                    const tempId = tempMsg.id;
                    const tempContent = tempMsg.querySelector('.message-content').textContent;
                    
                    // Eyni məzmunlu mesaj serverdən gəlibsə, müvəqqəti mesajı əlavə etmə
                    const isDuplicate = messages.some(msg => 
                        msg.content === tempContent && msg.is_mine
                    );
                    
                    if (!isDuplicate) {
                        chatMessages.appendChild(tempMsg);
                    }
                });

                // Yeni mesaj gəlibsə və bu mesaj bizim deyilsə səs çal
                if (lastMessage && lastMessage.id > lastMessageId && !lastMessage.is_mine) {
                    playChatMessageSound();
                }

                // Son mesaj ID-sini yadda saxla
                if (lastMessage) {
                    lastMessageId = lastMessage.id;
                }
                
                // Mesajları aşağı sürüşdür
                chatMessages.scrollTop = chatMessages.scrollHeight;
            })
            .catch(error => {
                if (!suppressWebSocketErrors) {
                    console.error('Mesajlar yüklənərkən xəta:', error);
                }
            });
    } catch (error) {
        if (!suppressWebSocketErrors) {
            console.error('Mesajlar yüklənərkən ümumi xəta:', error);
        }
    }
}

// Mesaj statusunu müəyyən et
function getMessageStatus(msg) {
    if (msg.is_read) return 'read';
    if (msg.is_delivered) return 'delivered';
    return 'sent';
}

// Status ikonlarını qaytarır
function getStatusIcons(msg) {
    if (msg.is_read) {
        return '<i class="fas fa-check"></i><i class="fas fa-check"></i>';
    } else if (msg.is_delivered) {
        return '<i class="fas fa-check"></i><i class="fas fa-check"></i>';
    } else {
        return '<i class="fas fa-check"></i>';
    }
}

function sendMessage() {
    const input = document.getElementById('message-input');
    if (!input) return;
    
    const content = input.value.trim();
    
    if (!content || !currentReceiverId) return;

    if (!suppressWebSocketErrors) {
        console.log(`Mesaj göndərilir: ${content} (Alıcı ID: ${currentReceiverId})`);
    }

    // Mesajı əvvəlcədən göstər (daha yaxşı istifadəçi təcrübəsi üçün)
    const tempMessageId = 'temp_' + Date.now();
    const chatMessages = document.getElementById('chat-messages');
    if (chatMessages) {
        const tempMessageDiv = document.createElement('div');
        tempMessageDiv.className = 'message mine';
        tempMessageDiv.id = tempMessageId;
        tempMessageDiv.innerHTML = `
            <div class="message-content">${content}</div>
            <div class="message-status">
                <i class="fas fa-check"></i>
            </div>
        `;
        chatMessages.appendChild(tempMessageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // İnput sahəsini təmizlə
    input.value = '';
    
    // Mesaj sahəsini fokusla
    input.focus();

    // WebSocket ilə mesaj göndərməyə çalış (yalnız HTTP istifadə edilmirsə)
    let websocketSent = false;
    if (!useOnlyHTTP && usingWebSocket && chatSocket && chatSocket.readyState === WebSocket.OPEN) {
        try {
            chatSocket.send(JSON.stringify({
                'message': content,
                'sender': currentUserId,
                'receiver': currentReceiverId
            }));
            websocketSent = true;
            if (!suppressWebSocketErrors) {
                console.log('Mesaj WebSocket ilə göndərildi');
            }
        } catch (error) {
            if (!suppressWebSocketErrors) {
                console.error('WebSocket ilə mesaj göndərilərkən xəta:', error);
            }
        }
    } else {
        if (!suppressWebSocketErrors) {
            console.log('WebSocket bağlantısı açıq deyil, HTTP sorğusu ilə mesaj göndərilir');
        }
    }

    // HTTP sorğusu ilə mesaj göndər
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
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (!suppressWebSocketErrors) {
            console.log('Mesaj göndərildi:', data);
        }
        
        if (data.status === 'success') {
            // Müvəqqəti mesajı yenisi ilə əvəz et
            if (chatMessages && document.getElementById(tempMessageId)) {
                const tempMessage = document.getElementById(tempMessageId);
                tempMessage.querySelector('.message-status').className = 'message-status read';
                tempMessage.querySelector('.message-status').innerHTML = '<i class="fas fa-check"></i><i class="fas fa-check"></i>';
            }
            
            // Mesajları yenilə
            loadMessages(currentReceiverId);
        } else {
            // Müvəqqəti mesajı sil
            if (chatMessages && document.getElementById(tempMessageId)) {
                document.getElementById(tempMessageId).remove();
            }
            
            if (!suppressWebSocketErrors) {
                console.error('Mesaj göndərilə bilmədi:', data.message);
            }
            if (typeof showAnimatedMessage === 'function') {
                showAnimatedMessage('Mesaj göndərilə bilmədi: ' + data.message, true);
            } else {
                alert('Mesaj göndərilə bilmədi: ' + data.message);
            }
        }
    })
    .catch(error => {
        // Müvəqqəti mesajı sil
        if (chatMessages && document.getElementById(tempMessageId)) {
            document.getElementById(tempMessageId).remove();
        }
        
        if (!suppressWebSocketErrors) {
            console.error('Mesaj göndərilərkən xəta:', error);
        }
        if (typeof showAnimatedMessage === 'function') {
            showAnimatedMessage('Mesaj göndərilərkən xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.', true);
        } else {
            alert('Mesaj göndərilərkən xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.');
        }
    });
}

function filterUsers() {
    const searchTerm = document.getElementById('user-search').value.toLowerCase();
    const userItems = document.querySelectorAll('.user-item');
    const userGroupTitles = document.querySelectorAll('.user-group-title');
    
    // Cari istifadəçinin admin olub-olmadığını yoxla
    const isCurrentUserAdmin = typeof isAdmin !== 'undefined' && isAdmin;
    
    // Əgər axtarış boşdursa hər şeyi göstər
    if (!searchTerm) {
        userGroupTitles.forEach(title => {
            title.style.display = 'block';
        });
        userItems.forEach(item => {
            // Admin olmayan istifadəçilər üçün yalnız adminləri göstər
            const isAdmin = item.querySelector('.admin-icon') !== null;
            if (isCurrentUserAdmin || (!isCurrentUserAdmin && isAdmin)) {
                item.style.display = 'flex';
            } else {
                item.style.display = 'none';
            }
        });
        return;
    }

    // Əvvəlcə bütün başlıqları və istifadəçiləri gizlət
    userGroupTitles.forEach(title => {
        title.style.display = 'none';
    });
    userItems.forEach(item => {
        item.style.display = 'none';
    });

    // Axtarış sözünə uyğun istifadəçiləri göstər
    let adminFound = false;
    let userFound = false;

    userItems.forEach(item => {
        const username = item.querySelector('.user-info span').textContent.toLowerCase();
        const isItemAdmin = item.querySelector('.admin-icon') !== null;
        
        if (username.includes(searchTerm)) {
            // Admin olmayan istifadəçilər üçün yalnız adminləri göstər
            if (isCurrentUserAdmin || (!isCurrentUserAdmin && isItemAdmin)) {
                item.style.display = 'flex';
                
                // İstifadəçinin admin olub-olmadığını yoxla
                if (isItemAdmin) {
                    adminFound = true;
                    const adminTitle = document.querySelector('.user-group-title:first-of-type');
                    if (adminTitle) adminTitle.style.display = 'block';
                } else {
                    userFound = true;
                    const userTitle = document.querySelector('.user-group-title:last-of-type');
                    if (userTitle) userTitle.style.display = 'block';
                }
            }
        }
    });
}

// Səhifə yükləndikdə istifadəçi qarşılıqlı əlaqəsini gözlə
document.addEventListener('click', function initAudioOnUserInteraction() {
    initAudio();
    document.removeEventListener('click', initAudioOnUserInteraction);
}, { once: true });

// Audio elementlərini inicializasiya et
function initAudio() {
    try {
        const newMessageSound = document.getElementById('new-message-sound');
        const chatMessageSound = document.getElementById('chat-message-sound');
        
        if (newMessageSound) {
            // Səsi yüklə
            newMessageSound.load();
            
            // Səsi unmute et (istifadəçi qarşılıqlı əlaqəsindən sonra)
            document.addEventListener('click', function unmuteSounds() {
                newMessageSound.muted = false;
                if (chatMessageSound) {
                    chatMessageSound.muted = false;
                }
                document.removeEventListener('click', unmuteSounds);
                
                if (!suppressWebSocketErrors) {
                    console.log('Səslər unmute edildi');
                }
            }, { once: true });
            
            // Səsi səssiz çal və dayandır (istifadəçi qarşılıqlı əlaqəsini təmin etmək üçün)
            newMessageSound.volume = 0;
            const playPromise = newMessageSound.play();
            
            if (playPromise !== undefined) {
                playPromise.then(_ => {
                    // Səs uğurla çalındı, dayandır və səsi normal səviyyəyə qaytar
                    newMessageSound.pause();
                    newMessageSound.currentTime = 0;
                    newMessageSound.volume = 1;
                    if (!suppressWebSocketErrors) {
                        console.log('Bildiriş səsi inicializasiya edildi');
                    }
                }).catch(error => {
                    if (!suppressWebSocketErrors) {
                        console.error('Bildiriş səsi inicializasiya edilərkən xəta:', error);
                    }
                });
            }
        }
        
        if (chatMessageSound) {
            // Səsi yüklə
            chatMessageSound.load();
            
            // Səsi səssiz çal və dayandır (istifadəçi qarşılıqlı əlaqəsini təmin etmək üçün)
            chatMessageSound.volume = 0;
            const playPromise = chatMessageSound.play();
            
            if (playPromise !== undefined) {
                playPromise.then(_ => {
                    // Səs uğurla çalındı, dayandır və səsi normal səviyyəyə qaytar
                    chatMessageSound.pause();
                    chatMessageSound.currentTime = 0;
                    chatMessageSound.volume = 1;
                    if (!suppressWebSocketErrors) {
                        console.log('Chat mesajı səsi inicializasiya edildi');
                    }
                }).catch(error => {
                    if (!suppressWebSocketErrors) {
                        console.error('Chat mesajı səsi inicializasiya edilərkən xəta:', error);
                    }
                });
            }
        }
    } catch (error) {
        if (!suppressWebSocketErrors) {
            console.error('Audio inicializasiya edilərkən xəta:', error);
        }
    }
}

// DOM yükləndikdə chat funksiyasını başlat
document.addEventListener('DOMContentLoaded', function() {
    try {
        if (!suppressWebSocketErrors) {
            console.log('DOM yükləndi, chat funksiyası başladılır...');
        }
        
        // Chat üçün əlavə CSS stilləri əlavə et
        addChatStyles();
        
        // Global funksiyaları window obyektinə əlavə et
        window.selectUser = selectUser;
        
        // Audio elementlərini inicializasiya et
        initAudio();
        
        // Chat widget-i inicializasiya et
        const chatWidget = document.getElementById('chat-widget');
        if (chatWidget) {
            if (!suppressWebSocketErrors) {
                console.log('Chat widget tapıldı, inicializasiya edilir...');
            }
            initChat();
        } else {
            if (!suppressWebSocketErrors) {
                console.log('Chat widget tapılmadı!');
            }
        }
    } catch (error) {
        // Xətaları gizlət
        if (!suppressWebSocketErrors) {
            console.error('Chat inicializasiya edilərkən xəta:', error);
        }
    }
});

// Chat üçün əlavə CSS stilləri əlavə et
function addChatStyles() {
    const style = document.createElement('style');
    style.textContent = `
        /* Chat ikonuna animasiya */
        @keyframes pulse {
            0% {
                transform: scale(1);
                box-shadow: 0 0 0 0 rgba(0, 51, 102, 0.7);
            }
            70% {
                transform: scale(1.1);
                box-shadow: 0 0 0 10px rgba(0, 51, 102, 0);
            }
            100% {
                transform: scale(1);
                box-shadow: 0 0 0 0 rgba(0, 51, 102, 0);
            }
        }
        
        .pulse-animation {
            animation: pulse 1.5s infinite;
        }
        
        /* Bildiriş sayı üçün stil */
        .unread-count {
            position: absolute;
            top: -5px;
            right: -5px;
            background-color: #ff5252;
            color: white;
            border-radius: 50%;
            width: 22px;
            height: 22px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        }
        
        /* Chat ikonuna hover effekti */
        .chat-icon:hover {
            transform: scale(1.1);
            transition: transform 0.3s ease;
        }
    `;
    document.head.appendChild(style);
} 