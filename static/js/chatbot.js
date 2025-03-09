// Chatbot funksiyaları
document.addEventListener('DOMContentLoaded', function() {
    // Chatbot elementlərini yaratma
    function createChatbotElements() {
        // Chatbot konteynerini yarat
        const chatbotContainer = document.createElement('div');
        chatbotContainer.id = 'chatbot-container';
        chatbotContainer.className = 'chatbot-container';
        
        // Chatbot ikonunu yarat
        const chatbotIcon = document.createElement('div');
        chatbotIcon.id = 'chatbot-icon';
        chatbotIcon.className = 'chatbot-icon';
        chatbotIcon.innerHTML = `
            <i class="fas fa-comments"></i>
            <span id="unread-count" class="unread-count d-none">0</span>
        `;
        
        // Chatbot pəncərəsini yarat
        const chatbotWindow = document.createElement('div');
        chatbotWindow.id = 'chatbot-window';
        chatbotWindow.className = 'chatbot-window d-none';
        chatbotWindow.innerHTML = `
            <div class="chatbot-header">
                <h5>Mesajlar</h5>
                <div class="chatbot-actions">
                    <button id="chatbot-minimize" class="btn btn-sm">
                        <i class="fas fa-minus"></i>
                    </button>
                    <a href="/chat/" class="btn btn-sm" title="Tam ekran">
                        <i class="fas fa-expand"></i>
                    </a>
                </div>
            </div>
            <div class="chatbot-body">
                <div id="chatbot-chat-list" class="chatbot-chat-list">
                    <div class="text-center py-3">
                        <div class="spinner-border spinner-border-sm text-primary" role="status">
                            <span class="visually-hidden">Yüklənir...</span>
                        </div>
                    </div>
                </div>
                <div id="chatbot-messages" class="chatbot-messages d-none">
                    <div class="chatbot-messages-header">
                        <button id="chatbot-back" class="btn btn-sm">
                            <i class="fas fa-arrow-left"></i>
                        </button>
                        <div id="chatbot-user-info" class="chatbot-user-info">
                            <img id="chatbot-user-avatar" src="" alt="" class="rounded-circle">
                            <span id="chatbot-user-name"></span>
                        </div>
                    </div>
                    <div id="chatbot-messages-container" class="chatbot-messages-container">
                        <div class="text-center py-3">
                            <div class="spinner-border spinner-border-sm text-primary" role="status">
                                <span class="visually-hidden">Yüklənir...</span>
                            </div>
                        </div>
                    </div>
                    <div class="chatbot-input">
                        <form id="chatbot-form">
                            <div class="input-group">
                                <input type="text" id="chatbot-input" class="form-control" placeholder="Mesajınızı yazın...">
                                <button type="submit" class="btn btn-primary">
                                    <i class="fas fa-paper-plane"></i>
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        `;
        
        // Elementləri əlavə et
        chatbotContainer.appendChild(chatbotIcon);
        chatbotContainer.appendChild(chatbotWindow);
        document.body.appendChild(chatbotContainer);
        
        // CSS stilləri əlavə et
        const style = document.createElement('style');
        style.textContent = `
            .chatbot-container {
                position: fixed;
                bottom: 20px;
                right: 20px;
                z-index: 1000;
                font-family: Arial, sans-serif;
            }
            
            .chatbot-icon {
                width: 60px;
                height: 60px;
                background-color: #003366;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                transition: all 0.3s ease;
                position: relative;
            }
            
            .chatbot-icon:hover {
                transform: scale(1.1);
            }
            
            .chatbot-icon i {
                color: white;
                font-size: 24px;
            }
            
            .unread-count {
                position: absolute;
                top: -5px;
                right: -5px;
                background-color: #dc3545;
                color: white;
                border-radius: 50%;
                width: 22px;
                height: 22px;
                font-size: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
            }
            
            .chatbot-window {
                position: absolute;
                bottom: 80px;
                right: 0;
                width: 350px;
                height: 500px;
                background-color: white;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
                display: flex;
                flex-direction: column;
                overflow: hidden;
                transition: all 0.3s ease;
            }
            
            .chatbot-header {
                background-color: #003366;
                color: white;
                padding: 15px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .chatbot-header h5 {
                margin: 0;
                font-size: 16px;
            }
            
            .chatbot-actions button, .chatbot-actions a {
                background: none;
                border: none;
                color: white;
                cursor: pointer;
                padding: 0 5px;
            }
            
            .chatbot-body {
                flex: 1;
                display: flex;
                flex-direction: column;
                overflow: hidden;
                position: relative;
            }
            
            .chatbot-chat-list {
                flex: 1;
                overflow-y: auto;
                padding: 10px;
            }
            
            .chatbot-chat-item {
                display: flex;
                align-items: center;
                padding: 10px;
                border-radius: 5px;
                cursor: pointer;
                transition: background-color 0.2s;
                margin-bottom: 5px;
            }
            
            .chatbot-chat-item:hover {
                background-color: #f8f9fa;
            }
            
            .chatbot-chat-avatar {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                margin-right: 10px;
                object-fit: cover;
            }
            
            .chatbot-chat-info {
                flex: 1;
                overflow: hidden;
            }
            
            .chatbot-chat-name {
                font-weight: bold;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            
            .chatbot-chat-preview {
                font-size: 12px;
                color: #6c757d;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            
            .chatbot-chat-meta {
                display: flex;
                flex-direction: column;
                align-items: flex-end;
            }
            
            .chatbot-chat-time {
                font-size: 11px;
                color: #6c757d;
            }
            
            .chatbot-chat-badge {
                background-color: #dc3545;
                color: white;
                border-radius: 50%;
                width: 18px;
                height: 18px;
                font-size: 11px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-top: 5px;
            }
            
            .chatbot-messages {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: white;
                display: flex;
                flex-direction: column;
            }
            
            .chatbot-messages-header {
                padding: 10px;
                display: flex;
                align-items: center;
                border-bottom: 1px solid #e9ecef;
            }
            
            .chatbot-messages-header button {
                background: none;
                border: none;
                cursor: pointer;
                padding: 0 10px 0 0;
                color: #6c757d;
            }
            
            .chatbot-user-info {
                display: flex;
                align-items: center;
            }
            
            .chatbot-user-info img {
                width: 30px;
                height: 30px;
                border-radius: 50%;
                margin-right: 10px;
                object-fit: cover;
            }
            
            .chatbot-messages-container {
                flex: 1;
                overflow-y: auto;
                padding: 15px;
            }
            
            .chatbot-message {
                margin-bottom: 15px;
                max-width: 80%;
            }
            
            .chatbot-message-sent {
                margin-left: auto;
                background-color: #007bff;
                color: white;
                border-radius: 15px 15px 0 15px;
                padding: 10px 15px;
            }
            
            .chatbot-message-received {
                margin-right: auto;
                background-color: #f1f1f1;
                border-radius: 15px 15px 15px 0;
                padding: 10px 15px;
            }
            
            .chatbot-message-time {
                font-size: 11px;
                margin-top: 5px;
                text-align: right;
            }
            
            .chatbot-message-sent .chatbot-message-time {
                color: rgba(255, 255, 255, 0.8);
            }
            
            .chatbot-message-received .chatbot-message-time {
                color: #6c757d;
            }
            
            .chatbot-input {
                padding: 10px;
                border-top: 1px solid #e9ecef;
            }
            
            .chatbot-input .form-control {
                border-radius: 20px 0 0 20px;
            }
            
            .chatbot-input .btn {
                border-radius: 0 20px 20px 0;
            }
            
            .d-none {
                display: none !important;
            }
            
            @media (max-width: 576px) {
                .chatbot-window {
                    width: 300px;
                    height: 450px;
                    bottom: 70px;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Chatbot elementlərini yarat
    createChatbotElements();
    
    // Elementləri seç
    const chatbotIcon = document.getElementById('chatbot-icon');
    const chatbotWindow = document.getElementById('chatbot-window');
    const chatbotMinimize = document.getElementById('chatbot-minimize');
    const chatbotBack = document.getElementById('chatbot-back');
    const chatbotChatList = document.getElementById('chatbot-chat-list');
    const chatbotMessages = document.getElementById('chatbot-messages');
    const chatbotMessagesContainer = document.getElementById('chatbot-messages-container');
    const chatbotForm = document.getElementById('chatbot-form');
    const chatbotInput = document.getElementById('chatbot-input');
    const unreadCount = document.getElementById('unread-count');
    
    let currentChatUserId = null;
    let chatUpdateInterval = null;
    
    // Chatbot ikonuna klik
    chatbotIcon.addEventListener('click', function() {
        chatbotWindow.classList.toggle('d-none');
        
        if (!chatbotWindow.classList.contains('d-none')) {
            loadChatList();
        }
    });
    
    // Chatbot-u minimalaşdır
    chatbotMinimize.addEventListener('click', function() {
        chatbotWindow.classList.add('d-none');
    });
    
    // Söhbət siyahısına qayıt
    chatbotBack.addEventListener('click', function() {
        chatbotMessages.classList.add('d-none');
        chatbotChatList.classList.remove('d-none');
        
        // Avtomatik yeniləmə intervalını təmizlə
        if (chatUpdateInterval) {
            clearInterval(chatUpdateInterval);
            chatUpdateInterval = null;
        }
        
        // Söhbət siyahısını yenilə
        loadChatList();
    });
    
    // Mesaj göndər
    chatbotForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!currentChatUserId) return;
        
        const content = chatbotInput.value.trim();
        
        if (!content) return;
        
        fetch('/api/messages/send/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                receiver_id: currentChatUserId,
                content: content
            })
        })
        .then(response => response.json())
        .then(data => {
            // Mesaj inputunu təmizlə
            chatbotInput.value = '';
            
            // Yeni mesajı göstər
            const messageElement = document.createElement('div');
            messageElement.className = 'chatbot-message chatbot-message-sent';
            messageElement.innerHTML = `
                <div class="chatbot-message-content">${data.content}</div>
                <div class="chatbot-message-time">
                    ${data.timestamp}
                    <i class="fas fa-check ms-1"></i>
                </div>
            `;
            chatbotMessagesContainer.appendChild(messageElement);
            
            // Söhbəti aşağı sürüşdür
            chatbotMessagesContainer.scrollTop = chatbotMessagesContainer.scrollHeight;
        })
        .catch(error => {
            console.error('Mesaj göndərilərkən xəta:', error);
        });
    });
    
    // Söhbət siyahısını yüklə
    function loadChatList() {
        fetch('/api/messages/chat-list/')
            .then(response => response.json())
            .then(data => {
                if (data.chat_list.length === 0) {
                    chatbotChatList.innerHTML = `
                        <div class="text-center py-3">
                            <p class="mb-0">Heç bir söhbət tapılmadı</p>
                        </div>
                    `;
                    return;
                }
                
                chatbotChatList.innerHTML = '';
                
                data.chat_list.forEach(chat => {
                    const chatItem = document.createElement('div');
                    chatItem.className = 'chatbot-chat-item';
                    chatItem.setAttribute('data-user-id', chat.id);
                    chatItem.innerHTML = `
                        <img src="${chat.avatar || '/static/img/default-avatar.png'}" alt="${chat.username}" class="chatbot-chat-avatar">
                        <div class="chatbot-chat-info">
                            <div class="chatbot-chat-name">${chat.full_name}</div>
                            <div class="chatbot-chat-preview">${chat.last_message}</div>
                        </div>
                        <div class="chatbot-chat-meta">
                            <div class="chatbot-chat-time">${chat.timestamp}</div>
                            ${chat.unread_count > 0 ? 
                                `<div class="chatbot-chat-badge">${chat.unread_count}</div>` : ''}
                        </div>
                    `;
                    
                    chatItem.addEventListener('click', function() {
                        const userId = this.getAttribute('data-user-id');
                        openChat(userId);
                    });
                    
                    chatbotChatList.appendChild(chatItem);
                });
            })
            .catch(error => {
                console.error('Söhbət siyahısı yüklənərkən xəta:', error);
                chatbotChatList.innerHTML = `
                    <div class="text-center py-3">
                        <p class="mb-0 text-danger">Xəta baş verdi. Yenidən cəhd edin.</p>
                    </div>
                `;
            });
    }
    
    // Söhbəti aç
    function openChat(userId) {
        currentChatUserId = userId;
        
        chatbotChatList.classList.add('d-none');
        chatbotMessages.classList.remove('d-none');
        
        loadMessages(userId);
        
        // Avtomatik yeniləmə intervalını təmizlə və yenidən başlat
        if (chatUpdateInterval) {
            clearInterval(chatUpdateInterval);
        }
        
        // Hər 10 saniyədə bir mesajları yenilə
        chatUpdateInterval = setInterval(() => {
            if (currentChatUserId) {
                loadMessages(currentChatUserId);
            }
        }, 10000);
    }
    
    // Mesajları yüklə
    function loadMessages(userId) {
        chatbotMessagesContainer.innerHTML = `
            <div class="text-center py-3">
                <div class="spinner-border spinner-border-sm text-primary" role="status">
                    <span class="visually-hidden">Yüklənir...</span>
                </div>
            </div>
        `;
        
        fetch(`/api/messages/${userId}/`)
            .then(response => response.json())
            .then(data => {
                // İstifadəçi məlumatlarını göstər
                document.getElementById('chatbot-user-name').textContent = data.user.full_name;
                document.getElementById('chatbot-user-avatar').src = data.user.avatar || '/static/img/default-avatar.png';
                
                // Mesajları göstər
                chatbotMessagesContainer.innerHTML = '';
                
                if (data.messages.length === 0) {
                    chatbotMessagesContainer.innerHTML = `
                        <div class="text-center py-3">
                            <p class="mb-0">Hələ heç bir mesaj yoxdur. Söhbətə başlayın!</p>
                        </div>
                    `;
                    return;
                }
                
                data.messages.forEach(message => {
                    const messageElement = document.createElement('div');
                    messageElement.className = `chatbot-message ${message.is_sender ? 'chatbot-message-sent' : 'chatbot-message-received'}`;
                    messageElement.innerHTML = `
                        <div class="chatbot-message-content">${message.content}</div>
                        <div class="chatbot-message-time">
                            ${message.timestamp}
                            ${message.is_sender ? 
                                `<i class="fas fa-${message.is_read ? 'check-double' : 'check'} ms-1"></i>` : ''}
                        </div>
                    `;
                    chatbotMessagesContainer.appendChild(messageElement);
                });
                
                // Söhbəti aşağı sürüşdür
                chatbotMessagesContainer.scrollTop = chatbotMessagesContainer.scrollHeight;
            })
            .catch(error => {
                console.error('Mesajlar yüklənərkən xəta:', error);
                chatbotMessagesContainer.innerHTML = `
                    <div class="text-center py-3">
                        <p class="mb-0 text-danger">Xəta baş verdi. Yenidən cəhd edin.</p>
                    </div>
                `;
            });
    }
    
    // Oxunmamış mesajların sayını yüklə
    function loadUnreadCount() {
        fetch('/api/messages/unread-count/')
            .then(response => response.json())
            .then(data => {
                if (data.count > 0) {
                    unreadCount.textContent = data.count > 99 ? '99+' : data.count;
                    unreadCount.classList.remove('d-none');
                } else {
                    unreadCount.classList.add('d-none');
                }
            })
            .catch(error => {
                console.error('Oxunmamış mesajlar yüklənərkən xəta:', error);
            });
    }
    
    // İlkin yükləmə
    loadUnreadCount();
    
    // Hər 30 saniyədə bir oxunmamış mesajların sayını yenilə
    setInterval(loadUnreadCount, 30000);
    
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
    
    // Chatbot-u global obyektə əlavə et
    window.chatbot = {
        open: function() {
            chatbotWindow.classList.remove('d-none');
            loadChatList();
        },
        close: function() {
            chatbotWindow.classList.add('d-none');
        },
        openChat: openChat
    };
}); 