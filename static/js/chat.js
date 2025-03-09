// Chat funksionallığı
let currentReceiverId = null;
let currentReceiverName = null;
let lastMessageCount = 0;
let lastMessageId = 0;
let chatSocket = null;

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

// Yeni mesaj bildirişi səsi
function playNewMessageSound() {
    const audio = document.getElementById('new-message-sound');
    if (audio) {
        audio.currentTime = 0;
        audio.play().catch(error => {
            console.log('Səs oxutma xətası:', error);
        });
    }
}

// Chat mesajı bildirişi səsi
function playChatMessageSound() {
    const audio = document.getElementById('chat-message-sound');
    if (audio) {
        audio.currentTime = 0;
        audio.play().catch(error => {
            console.log('Səs oxutma xətası:', error);
        });
    }
}

// Chat funksiyasını başlat
function initChat() {
    console.log('Chat funksiyası başladılır...'); // Debug üçün
    
    // İstifadəçi daxil olmayıbsa, funksiyadan çıx
    if (typeof currentUserId === 'undefined' || !currentUserId) {
        console.log('İstifadəçi daxil olmayıb, chat funksiyası başladılmır');
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
        console.log('Chat elementləri tapılmadı!'); // Debug üçün
        return;
    }

    // WebSocket bağlantısını yarat
    try {
        connectWebSocket();
    } catch (error) {
        console.error('WebSocket bağlantısı yaradılarkən xəta:', error);
        console.log('WebSocket bağlantısı yaradıla bilmədi, HTTP sorğularından istifadə ediləcək');
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
            console.error('İstifadəçilər yüklənərkən xəta:', error);
        }
    }, 5000);
    
    setInterval(() => {
        try {
            if (currentReceiverId) {
                loadMessages(currentReceiverId);
            }
        } catch (error) {
            console.error('Mesajlar yüklənərkən xəta:', error);
        }
    }, 2000);

    // Axtarış funksiyasını əlavə et
    const searchInput = document.getElementById('user-search');
    if (searchInput) {
        searchInput.addEventListener('input', filterUsers);
    }
}

// WebSocket bağlantısını yarat
function connectWebSocket() {
    console.log('WebSocket bağlantısı yaradılır...'); // Debug üçün
    
    try {
        // WebSocket bağlantısını yarat
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${wsProtocol}//${window.location.host}/ws/chat/`;
        
        console.log('WebSocket URL:', wsUrl); // Debug üçün
        
        // Əvvəlki bağlantını bağla
        if (chatSocket && chatSocket.readyState !== WebSocket.CLOSED) {
            chatSocket.close();
        }
        
        try {
            // WebSocket bağlantısını sınayırıq, lakin xəta baş verdikdə HTTP sorğularından istifadə edirik
            chatSocket = new WebSocket(wsUrl);
            
            // WebSocket bağlantısı üçün 3 saniyə gözləyirik
            let wsConnectTimeout = setTimeout(() => {
                console.log('WebSocket bağlantısı vaxtı bitdi, HTTP sorğularından istifadə ediləcək');
                if (chatSocket && chatSocket.readyState !== WebSocket.OPEN) {
                    chatSocket.close();
                }
            }, 3000);
            
            chatSocket.onopen = function(e) {
                console.log('WebSocket bağlantısı açıldı');
                clearTimeout(wsConnectTimeout);
            };
            
            chatSocket.onmessage = function(e) {
                try {
                    const data = JSON.parse(e.data);
                    console.log('WebSocket mesajı alındı:', data);
                    
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
            
            chatSocket.onclose = function(e) {
                console.log('WebSocket bağlantısı bağlandı', e.code, e.reason);
                clearTimeout(wsConnectTimeout);
                
                // WebSocket bağlantısı uğursuz olduqda HTTP sorğularından istifadə et
                if (e.code !== 1000) {
                    console.log('WebSocket bağlantısı qırıldı, HTTP sorğularından istifadə ediləcək');
                }
            };
            
            chatSocket.onerror = function(e) {
                console.error('WebSocket xətası:', e);
                clearTimeout(wsConnectTimeout);
                
                // Xəta baş verdikdə bağlantını bağla və HTTP sorğularından istifadə et
                if (chatSocket) {
                    chatSocket.close();
                }
                console.log('WebSocket xətası baş verdi, HTTP sorğularından istifadə ediləcək');
            };
        } catch (error) {
            console.error('WebSocket bağlantısı yaradılarkən xəta:', error);
            console.log('WebSocket bağlantısı yaradıla bilmədi, HTTP sorğularından istifadə ediləcək');
        }
    } catch (error) {
        console.error('WebSocket bağlantısı yaradılarkən xəta:', error);
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
    console.log('İstifadəçilər yüklənir...'); // Debug üçün
    
    // Əgər istifadəçi daxil olmayıbsa, funksiyadan çıx
    if (!currentUserId) {
        console.log('İstifadəçi daxil olmayıb, istifadəçilər yüklənmir');
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
                console.error('Server xətası (500): İstifadəçilər yüklənə bilmədi');
            } else if (response.status === 403) {
                console.error('Giriş icazəsi yoxdur (403): İstifadəçi daxil olmayıb və ya sessiyanın vaxtı bitib');
            } else {
                console.error(`HTTP xətası: ${response.status}`);
            }
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('İstifadəçi məlumatları alındı:', data); // Debug üçün
        
        const usersList = document.getElementById('users-list');
        if (!usersList) {
            console.error('users-list elementi tapılmadı!');
            return;
        }
        
        let totalUnread = 0;
        
        usersList.innerHTML = '';
        
        // Adminləri və istifadəçiləri əlavə et
        if (data.admins && data.admins.length > 0) {
            usersList.innerHTML += '<div class="user-group-title">Adminlər</div>';
            data.admins.forEach(user => {
                totalUnread += user.unread_count;
                usersList.innerHTML += createUserItem(user);
            });
        }
        
        if (data.users && data.users.length > 0) {
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
        console.error('İstifadəçilər yüklənərkən xəta:', error);
    });
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
    console.log(`İstifadəçi seçildi: ${username} (ID: ${userId})`); // Debug üçün
    
    currentReceiverId = userId;
    currentReceiverName = username;
    
    const chatMain = document.querySelector('.chat-main');
    const chatSidebar = document.querySelector('.chat-sidebar');
    const selectedUsername = document.getElementById('selected-username');
    
    if (!chatMain || !chatSidebar || !selectedUsername) {
        console.error('Chat elementləri tapılmadı!');
        return;
    }
    
    chatSidebar.style.display = 'none';
    chatMain.style.display = 'flex';
    selectedUsername.textContent = username;
    
    loadMessages(userId);
}

// Mesaj yükləmə funksiyası
function loadMessages(receiverId) {
    console.log(`${receiverId} ID-li istifadəçi ilə mesajlar yüklənir...`); // Debug üçün
    
    fetch(`/istifadeciler/api/chat/messages/${receiverId}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(messages => {
            console.log(`${messages.length} mesaj alındı`); // Debug üçün
            
            const chatMessages = document.getElementById('chat-messages');
            if (!chatMessages) {
                console.error('chat-messages elementi tapılmadı!');
                return;
            }
            
            // Son mesajın ID-sini al
            const lastMessage = messages.length > 0 ? messages[messages.length - 1] : null;
            
            // HTML-i yenilə
            chatMessages.innerHTML = messages.map(msg => `
                <div class="message ${msg.is_mine ? 'mine' : 'theirs'}">
                    ${!msg.is_mine ? `<div class="message-sender">${msg.sender}</div>` : ''}
                    <div class="message-content">${msg.content}</div>
                    ${msg.is_mine ? `
                        <div class="message-status ${getMessageStatus(msg)}">
                            ${getStatusIcons(msg)}
                        </div>
                    ` : ''}
                </div>
            `).join('');

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
            console.error('Mesajlar yüklənərkən xəta:', error);
        });
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

    console.log(`Mesaj göndərilir: ${content} (Alıcı ID: ${currentReceiverId})`); // Debug üçün

    // WebSocket ilə mesaj göndərməyə çalış
    let websocketSent = false;
    if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
        try {
            chatSocket.send(JSON.stringify({
                'message': content,
                'sender': currentUserId,
                'receiver': currentReceiverId
            }));
            websocketSent = true;
            console.log('Mesaj WebSocket ilə göndərildi');
        } catch (error) {
            console.error('WebSocket ilə mesaj göndərilərkən xəta:', error);
        }
    } else {
        console.log('WebSocket bağlantısı açıq deyil, HTTP sorğusu ilə mesaj göndərilir');
    }

    // HTTP sorğusu ilə mesaj göndər (WebSocket uğursuz olduqda və ya hər halda)
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
        console.log('Mesaj göndərildi:', data); // Debug üçün
        
        if (data.status === 'success') {
            input.value = '';
            
            // Mesajları yenilə
            loadMessages(currentReceiverId);
            
            // Mesaj göndərildikdən sonra mesaj sahəsini fokusla
            input.focus();
        } else {
            console.error('Mesaj göndərilə bilmədi:', data.message);
            alert('Mesaj göndərilə bilmədi: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Mesaj göndərilərkən xəta:', error);
        alert('Mesaj göndərilərkən xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.');
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
    const newMessageSound = document.getElementById('new-message-sound');
    const chatMessageSound = document.getElementById('chat-message-sound');
    
    if (newMessageSound) {
        newMessageSound.load();
    }
    
    if (chatMessageSound) {
        chatMessageSound.load();
    }
}

// DOM yükləndikdə chat funksiyasını başlat
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM yükləndi, chat funksiyası başladılır...');
    
    // Global funksiyaları window obyektinə əlavə et
    window.selectUser = selectUser;
    
    // Chat widget-i inicializasiya et
    const chatWidget = document.getElementById('chat-widget');
    if (chatWidget) {
        console.log('Chat widget tapıldı, inicializasiya edilir...');
        initChat();
    } else {
        console.log('Chat widget tapılmadı!');
    }
}); 