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
let suppressWebSocketErrors = true; // WebSocket xətalarını gizlətmək üçün
let useOnlyHTTP = true; // Yalnız HTTP istifadə et, WebSocket-i tamamilə söndür

// Əlavə edildi - qruplar üçün dəyişənlər
let currentGroupId = null;
let currentGroupName = null;
let isCurrentChatGroup = false; // Chat-ın qrup və ya şəxsi olduğunu saxlayır

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

    // İstifadəçilər siyahısına qayıt
    backButton.addEventListener('click', () => {
        chatMain.style.display = 'none';
        chatSidebar.style.display = 'block';
        
        // Bütün dəyişənləri sıfırla
        currentReceiverId = null;
        currentReceiverName = null;
        currentGroupId = null;
        currentGroupName = null;
        isCurrentChatGroup = false;
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
            // Əgər cari çat qrupdursa, qrup mesajlarını yenilə
            if (isCurrentChatGroup && currentGroupId) {
                loadGroupMessages(currentGroupId);
            }
            // Əgər cari çat şəxsiidirsə, şəxsi mesajları yenilə
            else if (currentReceiverId) {
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
    
    let messageContent = '';
    if (message.message_type === 'image' && message.file_url) {
        messageContent = `<img src="${message.file_url}" alt="Şəkil" class="message-image">`;
    } else if (message.message_type === 'video' && message.file_url) {
        messageContent = `<video controls><source src="${message.file_url}" type="video/mp4">Video formatı dəstəklənmir</video>`;
    } else if (message.message_type === 'audio' && message.file_url) {
        messageContent = `<audio controls><source src="${message.file_url}" type="audio/mpeg">Səs formatı dəstəklənmir</audio>`;
    } else if (message.message_type === 'file' && message.file_url) {
        messageContent = `<div class="file-message">
            <i class="fas fa-file"></i>
            <span>${message.file_name}</span>
            <span class="file-size">(${message.file_size})</span>
            <a href="${message.file_url}" download class="download-btn">
                <i class="fas fa-download"></i>
            </a>
        </div>`;
    } else if (message.message_type === 'link' && message.file_url) {
        messageContent = `<a href="${message.file_url}" target="_blank" class="message-link">${message.content}</a>`;
    } else {
        messageContent = message.content;
    }
    
    messageDiv.innerHTML = `
        ${!message.is_mine ? `<div class="message-sender">${message.sender}</div>` : ''}
        <div class="message-content">${messageContent}</div>
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
            
            // Qrupları əlavə et
            if (data.groups && data.groups.length > 0) {
                usersList.innerHTML += '<div class="user-group-title">Qruplar</div>';
                data.groups.forEach(group => {
                    totalUnread += group.unread_count;
                    usersList.innerHTML += createGroupItem(group);
                });
            }
            
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

// Qrup elementi yaratmaq üçün yeni funksiya
function createGroupItem(group) {
    // Qrupa kilid qoymaq əgər giriş yoxdursa
    const isLocked = group.is_locked;
    const lockClass = isLocked ? 'locked' : '';
    const onClick = isLocked ? '' : `onclick="selectGroup(${group.id}, '${group.name}')"`;
    
    // Qrup avatarı və ya ikonu təyin et
    let avatarHtml = '';
    
    if (group.avatar) {
        // Qrupun avatarı varsa onu göstər
        avatarHtml = `<img src="${group.avatar}" alt="${group.name}" class="group-avatar">`;
    } else {
        // Qrupun avatarı yoxdursa, icon göstər (kilid və ya users)
        const icon = isLocked ? 'fa-lock' : 'fa-users';
        const adminClass = group.is_admin ? 'admin-icon' : '';
        avatarHtml = `<i class="fas ${icon} ${adminClass}"></i>`;
    }
    
    return `
        <div class="user-item group-item ${group.unread_count > 0 ? 'has-unread' : ''} ${lockClass}" 
             ${onClick}>
            <div class="user-info">
                <div class="avatar-container">
                    ${avatarHtml}
                    ${isLocked ? '<i class="fas fa-lock lock-overlay"></i>' : ''}
                </div>
                <span>${group.name}</span>
                <span class="group-members-count">(${group.members_count})</span>
            </div>
            ${isLocked ? 
                `<span class="lock-info" title="Bu qrupa daxil olmaq üçün icazəniz yoxdur">
                    <i class="fas fa-lock"></i>
                </span>` : 
                (group.unread_count > 0 ? 
                    `<span class="unread-count">${group.unread_count}</span>` : 
                    '')
            }
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
    
    // İstifadəçi seçildikdə qrup dəyişənlərini sıfırla
    currentGroupId = null;
    currentGroupName = null;
    isCurrentChatGroup = false;
    
    // Cari istifadəçi məlumatlarını təyin et
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

// Mesaj göndərmə funksiyası
function sendMessage() {
    const input = document.getElementById('message-input');
    const fileInput = document.getElementById('file-input');
    const messageType = document.getElementById('message-type').value;
    
    if (!input && !fileInput) return;
    
    const content = input ? input.value.trim() : '';
    const file = fileInput ? fileInput.files[0] : null;
    
    // Əgər qrup seçilibsə, qrup mesajı göndər
    if (isCurrentChatGroup && currentGroupId) {
        sendGroupMessage();
        return;
    }
    
    // Əgər istifadəçi seçilməyibsə, funksiyadan çıx
    if (!content && !file) return;

    // Mesajı əvvəlcədən göstər
    const tempMessageId = 'temp_' + Date.now();
    const chatMessages = document.getElementById('chat-messages');
    if (chatMessages) {
        const tempMessageDiv = document.createElement('div');
        tempMessageDiv.className = 'message mine';
        tempMessageDiv.id = tempMessageId;
        
        let messageContent = '';
        if (file) {
            if (messageType === 'image') {
                messageContent = `<img src="${URL.createObjectURL(file)}" alt="Şəkil" class="message-image">`;
            } else if (messageType === 'video') {
                messageContent = `<video controls><source src="${URL.createObjectURL(file)}" type="${file.type}">Video formatı dəstəklənmir</video>`;
            } else if (messageType === 'audio') {
                messageContent = `<audio controls><source src="${URL.createObjectURL(file)}" type="${file.type}">Səs formatı dəstəklənmir</audio>`;
            } else {
                messageContent = `<div class="file-message">
                    <i class="fas fa-file"></i>
                    <span>${file.name}</span>
                    <span class="file-size">(${formatFileSize(file.size)})</span>
                </div>`;
            }
        } else if (messageType === 'link') {
            messageContent = `<a href="${content}" target="_blank" class="message-link">${content}</a>`;
        } else {
            messageContent = content;
        }
        
        tempMessageDiv.innerHTML = `
            <div class="message-content">${messageContent}</div>
            <div class="message-status">
                <i class="fas fa-check"></i>
            </div>
        `;
        chatMessages.appendChild(tempMessageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // İnput sahəsini təmizlə
    if (input) input.value = '';
    if (fileInput) fileInput.value = '';
    
    // Mesaj sahəsini fokusla
    if (input) input.focus();

    // FormData yarat
    const formData = new FormData();
    formData.append('receiver_id', currentReceiverId);
    formData.append('content', content);
    formData.append('message_type', messageType);
    if (file) {
        formData.append('file', file);
    }

    // Mesajı göndər
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
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        // Müvəqqəti mesajı sil
        if (chatMessages && document.getElementById(tempMessageId)) {
            document.getElementById(tempMessageId).remove();
        }
        alert('Mesaj göndərilərkən xəta baş verdi');
    });
}

// Fayl ölçüsünü formatla
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
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
        if (!suppressWebSocketErrors) {
            console.log('DOM yükləndi, chat funksiyası başladılır...');
        }
        
        // Global funksiyaları window obyektinə əlavə et
        window.selectUser = selectUser;
        window.selectGroup = selectGroup;
        
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

function selectGroup(groupId, groupName) {
    if (!suppressWebSocketErrors) {
        console.log(`Qrup seçildi: ${groupName} (ID: ${groupId})`);
    }
    
    // Əvvəlki seçilmiş istifadəçi/qrupu sıfırlayaq
    currentReceiverId = null;
    currentReceiverName = null;
    
    // Qrup ID və adını saxlayaq
    currentGroupId = groupId;
    currentGroupName = groupName;
    isCurrentChatGroup = true;
    
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
    selectedUsername.textContent = `${groupName} (Qrup)`;
    
    loadGroupMessages(groupId);
}

// Qrup mesajlarını yükləmək üçün funksiya
function loadGroupMessages(groupId) {
    try {
        if (!suppressWebSocketErrors) {
            console.log(`Qrup mesajları yüklənir: Qrup ID ${groupId}`);
        }
        
        // Sorğu göndərmədən əvvəl yoxla ki, əvvəlki sorğu hələ davam edirmi
        if (window.loadingGroupMessages) {
            if (!suppressWebSocketErrors) {
                console.log('Qrup mesajları artıq yüklənir, gözlənilir...');
            }
            return;
        }
        
        window.loadingGroupMessages = true;
        
        fetch(`/istifadeciler/api/chat/group/messages/${groupId}/`, {
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
            window.loadingGroupMessages = false;
            
            if (!response.ok) {
                if (response.status === 403) {
                    if (!suppressWebSocketErrors) {
                        console.error('Bu qrupa daxil olmaq üçün icazəniz yoxdur');
                    }
                    
                    // İstifadəçilər siyahısına qayıt
                    const chatMain = document.querySelector('.chat-main');
                    const chatSidebar = document.querySelector('.chat-sidebar');
                    
                    if (chatMain && chatSidebar) {
                        chatMain.style.display = 'none';
                        chatSidebar.style.display = 'block';
                    }
                    
                    if (typeof showAnimatedMessage === 'function') {
                        showAnimatedMessage('Bu qrupa daxil olmaq üçün icazəniz yoxdur', true);
                    } else {
                        alert('Bu qrupa daxil olmaq üçün icazəniz yoxdur');
                    }
                    
                    // Qrup ID və adını sıfırla
                    currentGroupId = null;
                    currentGroupName = null;
                    isCurrentChatGroup = false;
                    
                    throw new Error('Bu qrupa daxil olmaq üçün icazəniz yoxdur');
                } else if (response.status === 404) {
                    if (!suppressWebSocketErrors) {
                        console.error('Qrup tapılmadı');
                    }
                    
                    // İstifadəçilər siyahısına qayıt
                    const chatMain = document.querySelector('.chat-main');
                    const chatSidebar = document.querySelector('.chat-sidebar');
                    
                    if (chatMain && chatSidebar) {
                        chatMain.style.display = 'none';
                        chatSidebar.style.display = 'block';
                    }
                    
                    if (typeof showAnimatedMessage === 'function') {
                        showAnimatedMessage('Qrup tapılmadı', true);
                    } else {
                        alert('Qrup tapılmadı');
                    }
                    
                    // Qrup ID və adını sıfırla
                    currentGroupId = null;
                    currentGroupName = null;
                    isCurrentChatGroup = false;
                    
                    throw new Error('Qrup tapılmadı');
                }
                
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(messages => {
            if (!suppressWebSocketErrors) {
                console.log(`${messages.length} qrup mesajı alındı`);
            }
            
            const chatMessages = document.getElementById('chat-messages');
            if (!chatMessages) {
                if (!suppressWebSocketErrors) {
                    console.error('chat-messages elementi tapılmadı!');
                }
                return;
            }
            
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
                </div>
            `).join('');
            
            // Mesajları aşağı sürüşdür
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
            // Uğurlu sorğudan sonra xəta sayğacını sıfırla
            window.groupMessageLoadErrors = 0;
        })
        .catch(error => {
            window.loadingGroupMessages = false;
            
            // Xəta sayğacını artır
            window.groupMessageLoadErrors = (window.groupMessageLoadErrors || 0) + 1;
            
            if (!suppressWebSocketErrors) {
                console.error('Qrup mesajları yüklənərkən xəta:', error);
            }
            
            // Əgər 3-dən az xəta varsa, yenidən cəhd et
            if (window.groupMessageLoadErrors < 3 && error.message !== 'Bu qrupa daxil olmaq üçün icazəniz yoxdur' && error.message !== 'Qrup tapılmadı') {
                if (!suppressWebSocketErrors) {
                    console.log(`Qrup mesajları yüklənərkən xəta baş verdi, ${window.groupMessageLoadErrors} cəhd. 5 saniyə sonra yenidən cəhd ediləcək...`);
                }
                setTimeout(() => loadGroupMessages(groupId), 5000);
            } else {
                if (!suppressWebSocketErrors) {
                    console.error('Qrup mesajları yüklənərkən çoxlu xəta baş verdi, yenidən cəhd edilmir.');
                }
                // 1 dəqiqə sonra xəta sayğacını sıfırla
                setTimeout(() => {
                    window.groupMessageLoadErrors = 0;
                }, 60000);
            }
        });
    } catch (error) {
        window.loadingGroupMessages = false;
        
        if (!suppressWebSocketErrors) {
            console.error('Qrup mesajları yüklənərkən ümumi xəta:', error);
        }
    }
}

// Qrupa mesaj göndərmək üçün funksiya
function sendGroupMessage() {
    // Əgər qrup seçilməyibsə, çıx
    if (!currentGroupId || !isCurrentChatGroup) {
        return;
    }
    
    const input = document.getElementById('message-input');
    if (!input) return;
    
    const content = input.value.trim();
    
    if (!content) return;

    if (!suppressWebSocketErrors) {
        console.log(`Qrupa mesaj göndərilir: ${content} (Qrup ID: ${currentGroupId})`);
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
        `;
        chatMessages.appendChild(tempMessageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // İnput sahəsini təmizlə
    input.value = '';
    
    // Mesaj sahəsini fokusla
    input.focus();

    // Əgər mesaj göndərilməkdədirsə, yeni sorğu göndərmə
    if (window.sendingGroupMessage) {
        if (!suppressWebSocketErrors) {
            console.log('Qrup mesajı artıq göndərilir, gözlənilir...');
        }
        return;
    }
    
    window.sendingGroupMessage = true;

    // HTTP sorğusu ilə mesaj göndər
    const formData = new FormData();
    formData.append('group_id', currentGroupId);
    formData.append('content', content);

    fetch('/istifadeciler/api/chat/group/send/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        },
        timeout: 10000 // 10 saniyə timeout
    })
    .then(response => {
        window.sendingGroupMessage = false;
        
        if (!response.ok) {
            if (response.status === 403) {
                // Müvəqqəti mesajı sil
                if (chatMessages && document.getElementById(tempMessageId)) {
                    document.getElementById(tempMessageId).remove();
                }
                
                if (typeof showAnimatedMessage === 'function') {
                    showAnimatedMessage('Bu qrupa mesaj göndərmək üçün icazəniz yoxdur', true);
                } else {
                    alert('Bu qrupa mesaj göndərmək üçün icazəniz yoxdur');
                }
                
                throw new Error('Bu qrupa mesaj göndərmək üçün icazəniz yoxdur');
            }
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (!suppressWebSocketErrors) {
            console.log('Qrup mesajı göndərildi:', data);
        }
        
        if (data.status === 'success') {
            // Müvəqqəti mesajı yenisi ilə əvəz et
            if (chatMessages && document.getElementById(tempMessageId)) {
                document.getElementById(tempMessageId).remove();
            }
            
            // Mesajları yenilə
            loadGroupMessages(currentGroupId);
            
            // Uğurlu sorğudan sonra xəta sayğacını sıfırla
            window.sendGroupMessageErrors = 0;
        } else {
            // Müvəqqəti mesajı sil
            if (chatMessages && document.getElementById(tempMessageId)) {
                document.getElementById(tempMessageId).remove();
            }
            
            if (!suppressWebSocketErrors) {
                console.error('Qrup mesajı göndərilə bilmədi:', data.message);
            }
            if (typeof showAnimatedMessage === 'function') {
                showAnimatedMessage('Qrup mesajı göndərilə bilmədi: ' + data.message, true);
            } else {
                alert('Qrup mesajı göndərilə bilmədi: ' + data.message);
            }
        }
    })
    .catch(error => {
        window.sendingGroupMessage = false;
        
        // Xəta sayğacını artır
        window.sendGroupMessageErrors = (window.sendGroupMessageErrors || 0) + 1;
        
        // Müvəqqəti mesajı sil
        if (chatMessages && document.getElementById(tempMessageId)) {
            document.getElementById(tempMessageId).remove();
        }
        
        if (!suppressWebSocketErrors) {
            console.error('Qrup mesajı göndərilərkən xəta:', error);
        }
        
        // Əgər 3-dən az xəta varsa, yenidən cəhd et
        if (window.sendGroupMessageErrors < 3 && error.message !== 'Bu qrupa mesaj göndərmək üçün icazəniz yoxdur') {
            if (!suppressWebSocketErrors) {
                console.log(`Qrup mesajı göndərilərkən xəta baş verdi, ${window.sendGroupMessageErrors} cəhd. 5 saniyə sonra yenidən cəhd ediləcək...`);
            }
            
            // Mesajı yenidən göndərmək üçün input-a qaytar
            input.value = content;
            
            // 5 saniyə sonra yenidən cəhd et
            setTimeout(() => {
                if (typeof showAnimatedMessage === 'function') {
                    showAnimatedMessage('Qrup mesajı göndərilməyə yenidən cəhd edilir...', false);
                }
                sendGroupMessage();
            }, 5000);
        } else {
            if (typeof showAnimatedMessage === 'function') {
                showAnimatedMessage('Qrup mesajı göndərilərkən xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.', true);
            } else {
                alert('Qrup mesajı göndərilərkən xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.');
            }
            
            // 1 dəqiqə sonra xəta sayğacını sıfırla
            setTimeout(() => {
                window.sendGroupMessageErrors = 0;
            }, 60000);
        }
    });
} 