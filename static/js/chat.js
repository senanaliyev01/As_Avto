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
    
    // Cloudflare RUM2 xətasını gizlət
    if (message && message.includes('cdn-cgi/rum')) {
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
let suppressWebSocketErrors = false; // WebSocket xətalarını göstər
let useOnlyHTTP = true; // Yalnız HTTP istifadə et, WebSocket-i tamamilə söndür
let disableNotificationSounds = false; // Bildiriş səsləri deaktiv edilib/edilməyib

// Səs faylları üçün yollar
const SOUND_PATHS = {
    newMessage: '/as_avto/static/audio/notification.mp3',
    chatMessage: '/as_avto/static/audio/chat-message.mp3'
};

// Audio elementləri
let newMessageSound = null;
let chatMessageSound = null;

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
    const fullscreenChat = document.getElementById('fullscreen-chat');
    const testSound = document.getElementById('test-sound');
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
        chatWindow.style.display = chatWindow.style.display === 'none' ? 'flex' : 'none';
        if (chatWindow.style.display === 'flex') {
            loadChatUsers();
            chatMain.style.display = 'none';
            chatSidebar.style.display = 'block';
        }
    });

    // Chat pəncərəsini bağla
    closeChat.addEventListener('click', () => {
        chatWindow.style.display = 'none';
        // Tam ekrandan çıx
        if (chatWindow.classList.contains('fullscreen')) {
            toggleFullScreen();
        }
    });
    
    // Tam ekran düyməsinə klik
    if (fullscreenChat) {
        fullscreenChat.addEventListener('click', toggleFullScreen);
    }
    
    // Səs test düyməsinə klik
    if (testSound) {
        testSound.addEventListener('click', () => {
            // İlk öncə köhnə audio obyektlərini təmizlə və yenidən yarat
            if (newMessageSound) {
                newMessageSound.pause();
                newMessageSound.currentTime = 0;
            }
            
            if (chatMessageSound) {
                chatMessageSound.pause();
                chatMessageSound.currentTime = 0;
            }
            
            // Yeni audio obyektləri yarat
            newMessageSound = new Audio(SOUND_PATHS.newMessage);
            chatMessageSound = new Audio(SOUND_PATHS.chatMessage);
            
            console.log('Test üçün yeni audio obyektləri yaradıldı:');
            console.log('Bildiriş səsi yolu:', SOUND_PATHS.newMessage);
            console.log('Chat mesajı səsi yolu:', SOUND_PATHS.chatMessage);
            
            // Bildirişi göstər
            alert('Səs bildirişləri test edilir. İki səs ardıcıl çalınacaq.');
            
            // Birinci səsi çal
            console.log('Bildiriş səsini test edirəm...');
            newMessageSound.volume = 1.0;
            newMessageSound.play()
                .then(() => {
                    console.log('Bildiriş səsi uğurla çalındı');
                    
                    // 1.5 saniyə sonra ikinci səsi çal
                    setTimeout(() => {
                        console.log('Chat mesaj səsini test edirəm...');
                        chatMessageSound.volume = 1.0;
                        chatMessageSound.play()
                            .then(() => {
                                console.log('Chat mesaj səsi uğurla çalındı');
                                // Test uğurlu oldu
                                setTimeout(() => {
                                    alert('Səs testi uğurla tamamlandı. Əgər səsləri eşitdinizsə, sistem düzgün işləyir.');
                                }, 500);
                            })
                            .catch(error => {
                                console.error('Chat mesaj səsini test edərkən xəta:', error);
                                alert('Chat mesaj səsini test edərkən xəta baş verdi: ' + error.message);
                            });
                    }, 1500);
                })
                .catch(error => {
                    console.error('Bildiriş səsini test edərkən xəta:', error);
                    alert('Bildiriş səsini test edərkən xəta baş verdi: ' + error.message);
                    
                    if (error.name === 'NotSupportedError' || error.name === 'NotFoundError') {
                        alert('Bildiriş səs faylı tapılmadı və ya dəstəklənmir: ' + SOUND_PATHS.newMessage);
                    }
                });
        });
    }

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
    
    // ESC düyməsinə basıldıqda tam ekrandan çıx
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && chatWindow.classList.contains('fullscreen')) {
            toggleFullScreen();
        }
    });
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
                            if (!data.message.is_mine && !disableNotificationSounds) {
                                playChatMessageSound();
                            }
                        } else {
                            // Əks halda bildiriş səsini çal
                            if (!disableNotificationSounds) {
                                playNewMessageSound();
                            }
                            
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
                                if (!data.message.is_mine && !disableNotificationSounds) {
                                    playChatMessageSound();
                                }
                            } else {
                                // Əks halda bildiriş səsini çal
                                if (!disableNotificationSounds) {
                                    playNewMessageSound();
                                }
                                
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
        
        // Sorğu göndərmədən əvvəl yoxla ki, əvvəlki sorğu hələ davam edirmi
        if (window.loadingChatUsers) {
            if (!suppressWebSocketErrors) {
                console.log('İstifadəçilər artıq yüklənir, gözlənilir...');
            }
            return;
        }
        
        window.loadingChatUsers = true;
        
        fetch('/istifadeciler/api/chat/users/', {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken'),
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            },
            credentials: 'same-origin',
            timeout: 10000 // 10 saniyə timeout
        })
        .then(response => {
            window.loadingChatUsers = false;
            
            if (!response.ok) {
                if (response.status === 500) {
                    if (!suppressWebSocketErrors) {
                        console.error('Server xətası (500): İstifadəçilər yüklənə bilmədi');
                    }
                } else if (response.status === 502) {
                    if (!suppressWebSocketErrors) {
                        console.error('Bad Gateway xətası (502): Server cavab vermir');
                    }
                    // 502 xətası üçün 5 saniyə sonra yenidən cəhd et
                    setTimeout(loadChatUsers, 5000);
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
            
            // Adminləri əlavə et (bütün istifadəçilər adminləri görə bilər)
            if (data.admins && data.admins.length > 0) {
                usersList.innerHTML += '<div class="user-group-title">Adminlər</div>';
                data.admins.forEach(user => {
                    // Özünü göstərmə
                    if (user.id !== currentUserId) {
                        totalUnread += user.unread_count;
                        usersList.innerHTML += createUserItem(user);
                    }
                });
            }
            
            // İstifadəçiləri əlavə et (yalnız adminlər bütün istifadəçiləri görə bilər)
            if (isCurrentUserAdmin && data.users && data.users.length > 0) {
                usersList.innerHTML += '<div class="user-group-title">İstifadəçilər</div>';
                data.users.forEach(user => {
                    totalUnread += user.unread_count;
                    usersList.innerHTML += createUserItem(user);
                });
            }

            // Yeni mesaj varsa bildiriş səsini çal
            if (totalUnread > lastMessageCount && !disableNotificationSounds) {
                playNewMessageSound();
            }

            lastMessageCount = totalUnread;
            updateUnreadCount(totalUnread);
            
            // Uğurlu sorğudan sonra xəta sayğacını sıfırla
            window.chatUserLoadErrors = 0;
        })
        .catch(error => {
            window.loadingChatUsers = false;
            
            // Xəta sayğacını artır
            window.chatUserLoadErrors = (window.chatUserLoadErrors || 0) + 1;
            
            if (!suppressWebSocketErrors) {
                console.error('İstifadəçilər yüklənərkən xəta:', error);
            }
            
            // Əgər 3-dən az xəta varsa, yenidən cəhd et
            if (window.chatUserLoadErrors < 3) {
                if (!suppressWebSocketErrors) {
                    console.log(`İstifadəçilər yüklənərkən xəta baş verdi, ${window.chatUserLoadErrors} cəhd. 5 saniyə sonra yenidən cəhd ediləcək...`);
                }
                setTimeout(loadChatUsers, 5000);
            } else {
                if (!suppressWebSocketErrors) {
                    console.error('İstifadəçilər yüklənərkən çoxlu xəta baş verdi, yenidən cəhd edilmir.');
                }
                // 1 dəqiqə sonra xəta sayğacını sıfırla
                setTimeout(() => {
                    window.chatUserLoadErrors = 0;
                }, 60000);
            }
        });
    } catch (error) {
        window.loadingChatUsers = false;
        
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
        totalUnreadElement.textContent = totalUnread;
        totalUnreadElement.style.display = 'block';
        chatIcon.classList.add('has-notification');
    } else {
        totalUnreadElement.style.display = 'none';
        chatIcon.classList.remove('has-notification');
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
    
    chatSidebar.style.display = 'none';
    chatMain.style.display = 'flex';
    selectedUsername.textContent = username;
    
    loadMessages(userId);
}

// Mesaj yükləmə funksiyası
function loadMessages(receiverId) {
    try {
        if (!suppressWebSocketErrors) {
            console.log(`${receiverId} ID-li istifadəçi ilə mesajlar yüklənir...`);
        }
        
        // Sorğu göndərmədən əvvəl yoxla ki, əvvəlki sorğu hələ davam edirmi
        if (window.loadingMessages) {
            if (!suppressWebSocketErrors) {
                console.log('Mesajlar artıq yüklənir, gözlənilir...');
            }
            return;
        }
        
        window.loadingMessages = true;
        
        fetch(`/istifadeciler/api/chat/messages/${receiverId}/`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken'),
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            },
            credentials: 'same-origin',
            timeout: 10000 // 10 saniyə timeout
        })
            .then(response => {
                window.loadingMessages = false;
                
                if (!response.ok) {
                    if (response.status === 502) {
                        if (!suppressWebSocketErrors) {
                            console.error('Bad Gateway xətası (502): Server cavab vermir');
                        }
                        // 502 xətası üçün 5 saniyə sonra yenidən cəhd et
                        setTimeout(() => loadMessages(receiverId), 5000);
                    }
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
                if (lastMessage && lastMessage.id > lastMessageId && !lastMessage.is_mine && !disableNotificationSounds) {
                    playChatMessageSound();
                }

                // Son mesaj ID-sini yadda saxla
                if (lastMessage) {
                    lastMessageId = lastMessage.id;
                }
                
                // Mesajları aşağı sürüşdür
                chatMessages.scrollTop = chatMessages.scrollHeight;
                
                // Uğurlu sorğudan sonra xəta sayğacını sıfırla
                window.chatMessageLoadErrors = 0;
            })
            .catch(error => {
                window.loadingMessages = false;
                
                // Xəta sayğacını artır
                window.chatMessageLoadErrors = (window.chatMessageLoadErrors || 0) + 1;
                
                if (!suppressWebSocketErrors) {
                    console.error('Mesajlar yüklənərkən xəta:', error);
                }
                
                // Əgər 3-dən az xəta varsa, yenidən cəhd et
                if (window.chatMessageLoadErrors < 3) {
                    if (!suppressWebSocketErrors) {
                        console.log(`Mesajlar yüklənərkən xəta baş verdi, ${window.chatMessageLoadErrors} cəhd. 5 saniyə sonra yenidən cəhd ediləcək...`);
                    }
                    setTimeout(() => loadMessages(receiverId), 5000);
                } else {
                    if (!suppressWebSocketErrors) {
                        console.error('Mesajlar yüklənərkən çoxlu xəta baş verdi, yenidən cəhd edilmir.');
                    }
                    // 1 dəqiqə sonra xəta sayğacını sıfırla
                    setTimeout(() => {
                        window.chatMessageLoadErrors = 0;
                    }, 60000);
                }
            });
    } catch (error) {
        window.loadingMessages = false;
        
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

    // Əgər mesaj göndərilməkdədirsə, yeni sorğu göndərmə
    if (window.sendingMessage) {
        if (!suppressWebSocketErrors) {
            console.log('Mesaj artıq göndərilir, gözlənilir...');
        }
        return;
    }
    
    window.sendingMessage = true;

    // HTTP sorğusu ilə mesaj göndər
    const formData = new FormData();
    formData.append('receiver_id', currentReceiverId);
    formData.append('content', content);

    fetch('/istifadeciler/api/chat/send/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        },
        timeout: 10000 // 10 saniyə timeout
    })
    .then(response => {
        window.sendingMessage = false;
        
        if (!response.ok) {
            if (response.status === 502) {
                if (!suppressWebSocketErrors) {
                    console.error('Bad Gateway xətası (502): Server cavab vermir');
                }
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
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
            
            // Uğurlu sorğudan sonra xəta sayğacını sıfırla
            window.sendMessageErrors = 0;
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
        window.sendingMessage = false;
        
        // Xəta sayğacını artır
        window.sendMessageErrors = (window.sendMessageErrors || 0) + 1;
        
        // Müvəqqəti mesajı sil
        if (chatMessages && document.getElementById(tempMessageId)) {
            document.getElementById(tempMessageId).remove();
        }
        
        if (!suppressWebSocketErrors) {
            console.error('Mesaj göndərilərkən xəta:', error);
        }
        
        // Əgər 3-dən az xəta varsa və 502 xətasıdırsa, yenidən cəhd et
        if (window.sendMessageErrors < 3 && error.message && error.message.includes('502')) {
            if (!suppressWebSocketErrors) {
                console.log(`Mesaj göndərilərkən server xətası baş verdi, ${window.sendMessageErrors} cəhd. 5 saniyə sonra yenidən cəhd ediləcək...`);
            }
            
            // Mesajı yenidən göndərmək üçün input-a qaytar
            input.value = content;
            
            // 5 saniyə sonra yenidən cəhd et
            setTimeout(() => {
                if (typeof showAnimatedMessage === 'function') {
                    showAnimatedMessage('Mesaj göndərilməyə yenidən cəhd edilir...', false);
                }
                sendMessage();
            }, 5000);
        } else {
            if (typeof showAnimatedMessage === 'function') {
                showAnimatedMessage('Mesaj göndərilərkən xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.', true);
            } else {
                alert('Mesaj göndərilərkən xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.');
            }
            
            // 1 dəqiqə sonra xəta sayğacını sıfırla
            setTimeout(() => {
                window.sendMessageErrors = 0;
            }, 60000);
        }
    });
}

function filterUsers() {
    const searchTerm = document.getElementById('user-search').value.toLowerCase();
    const userItems = document.querySelectorAll('.user-item');
    const userGroupTitles = document.querySelectorAll('.user-group-title');
    
    // Əgər axtarış boşdursa hər şeyi göstər
    if (!searchTerm) {
        userGroupTitles.forEach(title => {
            title.style.display = 'block';
        });
        userItems.forEach(item => {
            item.style.display = 'flex';
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
        if (username.includes(searchTerm)) {
            item.style.display = 'flex';
            // İstifadəçinin admin olub-olmadığını yoxla
            const isAdmin = item.querySelector('.admin-icon') !== null;
            if (isAdmin) {
                adminFound = true;
                document.querySelector('.user-group-title:first-of-type').style.display = 'block';
            } else {
                userFound = true;
                document.querySelector('.user-group-title:last-of-type').style.display = 'block';
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
        // Yeni səs elementlərini yarat
        newMessageSound = new Audio(SOUND_PATHS.newMessage);
        chatMessageSound = new Audio(SOUND_PATHS.chatMessage);
        
        // Yeni mesaj bildiriş səsini konfiqurasiya et
        if (newMessageSound) {
            // Səsi yüklə
            newMessageSound.preload = 'auto';
            newMessageSound.volume = 1.0; // Tam səs səviyyəsi
                
                if (!suppressWebSocketErrors) {
                console.log('Yeni mesaj bildiriş səsi yaradıldı:', SOUND_PATHS.newMessage);
            }
            
            // Yükləmə xətasını izlə
            newMessageSound.addEventListener('error', (e) => {
                    if (!suppressWebSocketErrors) {
                    console.error('Bildiriş səsi yüklənərkən xəta:', e);
                    }
            });
        } else {
                    if (!suppressWebSocketErrors) {
                console.error('Yeni mesaj bildiriş səsi yaradıla bilmədi!');
            }
        }
        
        // Chat mesaj səsini konfiqurasiya et
        if (chatMessageSound) {
            // Səsi yüklə
            chatMessageSound.preload = 'auto';
            chatMessageSound.volume = 1.0; // Tam səs səviyyəsi
            
                    if (!suppressWebSocketErrors) {
                console.log('Chat mesaj səsi yaradıldı:', SOUND_PATHS.chatMessage);
                    }
            
            // Yükləmə xətasını izlə
            chatMessageSound.addEventListener('error', (e) => {
                    if (!suppressWebSocketErrors) {
                    console.error('Chat mesaj səsi yüklənərkən xəta:', e);
                    }
                });
        } else {
            if (!suppressWebSocketErrors) {
                console.error('Chat mesaj səsi yaradıla bilmədi!');
            }
        }
        
    } catch (error) {
        if (!suppressWebSocketErrors) {
            console.error('Audio inicializasiya edilərkən xəta:', error);
        }
    }
}

// Tam ekran rejimini açıb/bağlamaq
function toggleFullScreen() {
    const chatWindow = document.getElementById('chat-window');
    const fullscreenButton = document.getElementById('fullscreen-chat');
    
    if (!chatWindow || !fullscreenButton) return;
    
    chatWindow.classList.toggle('fullscreen');
    
    // Tam ekran ikonunu dəyiş
    if (chatWindow.classList.contains('fullscreen')) {
        fullscreenButton.innerHTML = '<i class="fas fa-compress"></i>';
        fullscreenButton.setAttribute('title', 'Tam ekrandan çıx');
    } else {
        fullscreenButton.innerHTML = '<i class="fas fa-expand"></i>';
        fullscreenButton.setAttribute('title', 'Tam ekran');
    }
    
    // İstifadəçilər siyahısını yenidən yüklə
    loadChatUsers();
}

// DOM yükləndikdə chat funksiyasını başlat
document.addEventListener('DOMContentLoaded', function() {
    try {
            console.log('DOM yükləndi, chat funksiyası başladılır...');
        
        // Səs fayllarının yollarını yoxla
        console.log('Səs fayllarının yolları:');
        console.log('Bildiriş səsi:', SOUND_PATHS.newMessage);
        console.log('Chat mesajı səsi:', SOUND_PATHS.chatMessage);
        
        // Səs fayllarının mövcudluğunu yoxla
        testAudioFileExistence(SOUND_PATHS.newMessage, 'Bildiriş səsi');
        testAudioFileExistence(SOUND_PATHS.chatMessage, 'Chat mesajı səsi');
        
        // Global funksiyaları window obyektinə əlavə et
        window.selectUser = selectUser;
        
        // Səs fayllarını yüklə
        initAudio();
        
        // Səs kilidlərini açmaq üçün istifadəçi qarşılıqlı əlaqəsini gözlə
        setupAudioUnlock();
        
        // Chat funksiyasını başlat
        const chatWidget = document.getElementById('chat-widget');
        if (chatWidget) {
                console.log('Chat widget tapıldı, inicializasiya edilir...');
            initChat();
        } else {
                console.log('Chat widget tapılmadı!');
            }
        
        // Bir neçə saniyə sonra audio elementlərini yenidən yükləməyə çalış (bəzi brauzerlər üçün)
        setTimeout(() => {
            console.log('Səs faylları yenidən yüklənir...');
            initAudio();
            setupAudioUnlock();
        }, 3000);
    } catch (error) {
        // Xətaları göstər
            console.error('Chat inicializasiya edilərkən xəta:', error);
        }
});

// Səs faylının mövcudluğunu yoxlamaq üçün test funksiyası
function testAudioFileExistence(url, name) {
    console.log(`${name} faylını yoxlayıram: ${url}`);
    
    fetch(url)
        .then(response => {
            if (response.ok) {
                console.log(`✅ ${name} faylı mövcuddur və əlçatandır.`);
            } else {
                console.error(`❌ ${name} faylına giriş mümkün deyil. Status: ${response.status}`);
                alert(`❌ ${name} faylına giriş mümkün deyil. Status: ${response.status}`);
            }
        })
        .catch(error => {
            console.error(`❌ ${name} faylına giriş xətası:`, error);
            alert(`❌ ${name} faylına giriş xətası: ${error.message}`);
        });
}

// Səs kilidlərini açmaq üçün funksiya
function setupAudioUnlock() {
    console.log('Səs kilidlərini açmağa çalışıram...');
    
    // Bütün səs elementləri üçün kilid açma funksiyası
    const unlockAudio = () => {
        console.log('İstifadəçi səs kilidi açma hadisəsini başlatdı (klik/toxunma)');
        
        // İlk öncə köhnə audio obyektlərini təmizlə və yenidən yarat
        if (newMessageSound) {
            newMessageSound.pause();
            newMessageSound.currentTime = 0;
        }
        
        if (chatMessageSound) {
            chatMessageSound.pause();
            chatMessageSound.currentTime = 0;
        }
        
        // Yeni audio obyektləri yarat
        newMessageSound = new Audio(SOUND_PATHS.newMessage);
        chatMessageSound = new Audio(SOUND_PATHS.chatMessage);
        
        console.log('Yeni audio obyektləri yaradıldı:');
        console.log('Bildiriş səsi yolu:', SOUND_PATHS.newMessage);
        console.log('Chat mesajı səsi yolu:', SOUND_PATHS.chatMessage);
        
        // Səsləri aşağı səviyyədə çalıb dayandır
        const playAndPause = (sound, name) => {
            sound.volume = 0.01; // Çox aşağı səs
            sound.muted = false;
            
            sound.play()
                .then(() => {
                    setTimeout(() => {
                        sound.pause();
                        sound.currentTime = 0;
                        sound.volume = 1.0;
                        console.log(`${name} səs kilidi açıldı`);
                    }, 10);
                })
                .catch(error => {
                    console.error(`${name} səs kilidi açılarkən xəta:`, error);
                    
                    if (error.name === 'NotSupportedError' || error.name === 'NotFoundError') {
                        console.error(`${name} səs faylı tapılmadı və ya dəstəklənmir:`, sound.src);
                    }
                });
        };
        
        // Səsləri ardıcıl çal və dayandır
        if (newMessageSound) {
            playAndPause(newMessageSound, 'Bildiriş səsi');
        }
        
        setTimeout(() => {
            if (chatMessageSound) {
                playAndPause(chatMessageSound, 'Chat mesajı səsi');
            }
        }, 100);
        
        // Hadisə dinləyicilərini sil
        document.body.removeEventListener('click', unlockAudio);
        document.body.removeEventListener('touchstart', unlockAudio);
    };
    
    // Həm klik, həm toxunma hadisələrini izlə
    document.body.addEventListener('click', unlockAudio, { once: true });
    document.body.addEventListener('touchstart', unlockAudio, { once: true });
}

// Yeni mesaj bildirişi üçün səs çal
function playNewMessageSound() {
    try {
        if (disableNotificationSounds) return;
        
        // Əgər səs obyekti yoxdursa, yenidən yarat
        if (!newMessageSound) {
            newMessageSound = new Audio(SOUND_PATHS.newMessage);
            newMessageSound.preload = 'auto';
        }
        
        // Səs səviyyəsini tam təyin et
        newMessageSound.volume = 1.0;
        
        // Mövcud səsi dayandır və başa qaytar
        newMessageSound.pause();
        newMessageSound.currentTime = 0;
        
        // Səs faylını yoxla
        console.log('Bildiriş səsi yüklənir:', SOUND_PATHS.newMessage);
        
        // Səsi çal
        newMessageSound.play()
            .then(() => {
                console.log('Bildiriş səsi uğurla çalındı');
            })
            .catch(error => {
                console.error('Bildiriş səsini çalarkən xəta:', error);
                
                if (error.name === 'NotSupportedError' || error.name === 'NotFoundError') {
                    console.error('Bildiriş səs faylı tapılmadı və ya dəstəklənmir:', SOUND_PATHS.newMessage);
                }
                
                // Avtomatik səs çalma məhdudiyyəti varsa (NotAllowedError)
                if (error.name === 'NotAllowedError') {
                    console.log('Bildiriş səsini çalmaq üçün istifadəçi qarşılıqlı əlaqəsi tələb olunur');
                    setupAudioUnlock();
                }
            });
    } catch (error) {
        console.error('Bildiriş səsi çalınarkən xəta:', error);
    }
}

// Chat mesajı üçün səs çal
function playChatMessageSound() {
    try {
        if (disableNotificationSounds) return;
        
        // Əgər səs obyekti yoxdursa, yenidən yarat
        if (!chatMessageSound) {
            chatMessageSound = new Audio(SOUND_PATHS.chatMessage);
            chatMessageSound.preload = 'auto';
        }
        
        // Səs səviyyəsini tam təyin et
        chatMessageSound.volume = 1.0;
        
        // Mövcud səsi dayandır və başa qaytar
        chatMessageSound.pause();
        chatMessageSound.currentTime = 0;
        
        // Səs faylını yoxla
        console.log('Chat mesajı səsi yüklənir:', SOUND_PATHS.chatMessage);
        
        // Səsi çal
        chatMessageSound.play()
            .then(() => {
                console.log('Chat mesajı səsi uğurla çalındı');
            })
            .catch(error => {
                console.error('Chat mesajı səsini çalarkən xəta:', error);
                
                if (error.name === 'NotSupportedError' || error.name === 'NotFoundError') {
                    console.error('Chat mesajı səs faylı tapılmadı və ya dəstəklənmir:', SOUND_PATHS.chatMessage);
                }
                
                // Avtomatik səs çalma məhdudiyyəti varsa (NotAllowedError)
                if (error.name === 'NotAllowedError') {
                    console.log('Chat mesajı səsini çalmaq üçün istifadəçi qarşılıqlı əlaqəsi tələb olunur');
                    setupAudioUnlock();
                }
            });
    } catch (error) {
        console.error('Chat mesajı səsi çalınarkən xəta:', error);
    }
} 