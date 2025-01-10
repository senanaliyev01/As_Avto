// Saat elementlərini əldə et
const currentTimeElement = document.getElementById('current-time');

// Təkmilləşdirilmiş saat funksiyası
function updateCurrentTime() {
    if (currentTimeElement) {
        const now = new Date();
        const hours = now.getHours().toString().padStart(2, '0');
        const minutes = now.getMinutes().toString().padStart(2, '0');
        const seconds = now.getSeconds().toString().padStart(2, '0');
        
        // Animasiyalı rəqəm dəyişməsi
        currentTimeElement.innerHTML = `
            <span class="time-unit">${hours}</span>:
            <span class="time-unit">${minutes}</span>:
            <span class="time-unit">${seconds}</span>
        `;
    }
}

// İş saatlarını yoxla və bildiriş göstər
function checkWorkingHours() {
    const now = new Date();
    const currentHour = now.getHours();
    const isWorkingHours = currentHour >= 9 && currentHour < 18;
    
    const workingHoursElement = document.querySelector('.working-hours p:first-child');
    if (workingHoursElement) {
        workingHoursElement.style.color = isWorkingHours ? '#4caf50' : '#ff5252';
        workingHoursElement.innerHTML = `İş vaxtımız: 09:00 - 18:00 
            <span class="status-badge" style="margin-left: 10px; font-size: 0.9em;">
                ${isWorkingHours ? '🟢 Açıqdır' : '🔴 Bağlıdır'}
            </span>`;
    }
}

// DOM yükləndikdə
document.addEventListener('DOMContentLoaded', () => {
    try {
        // Saatı başlat
        updateCurrentTime();
        setInterval(updateCurrentTime, 1000);

        // İş saatlarını yoxlaa
        checkWorkingHours();
        setInterval(checkWorkingHours, 60000); // Hər dəqiqə yoxla

    } catch (error) {
        console.error('Saat funksiyası xətası:', error);
    }
});

// Sadələşdirilmiş Swiperrr konfiqurasiyası
const swiperConfig = {
    slidesPerView: 'auto',
    spaceBetween: 30,
    centeredSlides: true,
    loop: true,
    autoplay: {
        delay: 3000,
        disableOnInteraction: false
    },
    pagination: {
        el: '.swiper-pagination',
        clickable: true
    },
    breakpoints: {
        320: {
            slidesPerView: 1,
            spaceBetween: 10
        },
        480: {
            slidesPerView: 2,
            spaceBetween: 20
        },
        768: {
            slidesPerView: 3,
            spaceBetween: 30
        },
        1024: {
            slidesPerView: 4,
            spaceBetween: 40
        }
    }
};

// İstifadəçi sayı animasiyası
function animateCount(element, target) {
    const start = parseInt(element.textContent) || 0;
    const duration = 1000; // 1 saniyə
    const steps = 20;
    const increment = (target - start) / steps;
    let current = start;
    let step = 0;

    const animate = () => {
        step++;
        current += increment;
        element.textContent = Math.round(current);

        if (step < steps) {
            requestAnimationFrame(animate);
        } else {
            element.textContent = target;
        }
    };

    animate();
}

// Səbət sayını yenilə
function updateCartCount() {
    fetch('/get_cart_count/')
        .then(response => response.json())
        .then(data => {
            const cartCount = document.getElementById('cart-count');
            if (cartCount) {
                cartCount.textContent = data.count;
            }
        })
        .catch(error => console.error('Error:', error));
}

// Statistika yeniləmə funksiyası
function updateStatistics() {
    fetch('/get_statistics/', {
        method: 'GET',
        headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
    })
    .then(response => response.json())
    .then(data => {
        // Hər bir statistika kartını yenilə
        Object.keys(data).forEach(key => {
            const element = document.querySelector(`.statistics-card .count[data-type="${key}"]`);
            if (element) {
                const currentValue = parseInt(element.textContent) || 0;
                const newValue = data[key];
                
                if (currentValue !== newValue) {
                    // Kartı vurğula
                    const card = element.closest('.statistics-card');
                    card.classList.add('updating');
                    
                    // Sayı animasiyası
                    animateCount(element, newValue);
                    
                    // Animasiyanı təmizlə
                    setTimeout(() => {
                        card.classList.remove('updating');
                    }, 1000);
                }
            }
        });
    })
    .catch(error => {
        console.error('Statistika yeniləmə xətası:', error);
        // Xəta halında yenidən cəhd et
        setTimeout(updateStatistics, 1000);
    });
}

// Chat funksionallığı
let currentReceiverId = null;
let currentReceiverName = null;
let lastMessageCount = 0;
let lastMessageId = 0;

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

function initChat() {
    const chatIcon = document.getElementById('chat-icon');
    const chatWindow = document.getElementById('chat-window');
    const closeChat = document.getElementById('close-chat');
    const backButton = document.getElementById('back-to-users');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-message');
    const chatMain = document.querySelector('.chat-main');
    const chatSidebar = document.querySelector('.chat-sidebar');
    const fullscreenBtn = document.getElementById('fullscreen-chat');

    // Tam ekran funksionallığı
    fullscreenBtn.addEventListener('click', () => {
        chatWindow.classList.toggle('fullscreen');
        const icon = fullscreenBtn.querySelector('i');
        if (chatWindow.classList.contains('fullscreen')) {
            icon.classList.remove('fa-expand');
            icon.classList.add('fa-compress');
        } else {
            icon.classList.remove('fa-compress');
            icon.classList.add('fa-expand');
        }
    });

    // ESC düyməsi ilə tam ekrandan çıxış
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && chatWindow.classList.contains('fullscreen')) {
            chatWindow.classList.remove('fullscreen');
            const icon = fullscreenBtn.querySelector('i');
            icon.classList.remove('fa-compress');
            icon.classList.add('fa-expand');
        }
    });

    // Səs yazma dəyişənləri
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    let recordingTimeout;

    // Səs yazma funksiyaları
    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            isRecording = true;

            mediaRecorder.ondataavailable = (e) => {
                audioChunks.push(e.data);
            };

            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                sendAudioMessage(audioBlob);
                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorder.start();
            showRecordingIndicator();
        } catch (err) {
            console.error('Səs yazma xətası:', err);
            showNotification('error', 'Səs yazmaq üçün icazə lazımdır');
        }
    }

    function stopRecording() {
        if (isRecording && mediaRecorder) {
            mediaRecorder.stop();
            isRecording = false;
            hideRecordingIndicator();
        }
    }

    // Səs yazma indikatorunu göstər
    function showRecordingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'recording-indicator';
        indicator.innerHTML = `
            <i class="fas fa-microphone recording-icon"></i>
            <span>Səs yazılır...</span>
        `;
        document.body.appendChild(indicator);
    }

    // Səs yazma indikatorunu gizlət
    function hideRecordingIndicator() {
        const indicator = document.querySelector('.recording-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    // Səs göndərmə funksiyası
    function sendAudioMessage(blob) {
        const formData = new FormData();
        formData.append('audio', blob, 'voice.webm');
        formData.append('receiver_id', currentReceiverId);

        fetch('/chat/send-audio/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadMessages(currentReceiverId);
            } else {
                showNotification('error', 'Səs göndərilmədi');
            }
        })
        .catch(error => {
            console.error('Səs göndərmə xətası:', error);
            showNotification('error', 'Səs göndərilmədi');
        });
    }

    // Səs yazma düyməsi
    const audioButton = document.createElement('button');
    audioButton.className = 'audio-btn';
    audioButton.innerHTML = '<i class="fas fa-microphone"></i>';
    
    // Mobil cihazlar üçün
    audioButton.addEventListener('touchstart', (e) => {
        e.preventDefault();
        startRecording();
    });

    audioButton.addEventListener('touchend', (e) => {
        e.preventDefault();
        stopRecording();
    });

    // Desktop üçün
    audioButton.addEventListener('mousedown', (e) => {
        e.preventDefault();
        startRecording();
    });

    audioButton.addEventListener('mouseup', (e) => {
        e.preventDefault();
        stopRecording();
    });

    audioButton.addEventListener('mouseleave', (e) => {
        e.preventDefault();
        if (isRecording) {
            stopRecording();
        }
    });

    // Səs düyməsini chat input-a əlavə et
    const chatInput = document.querySelector('.chat-input');
    chatInput.insertBefore(audioButton, sendButton);

    if (!chatIcon || !chatWindow) return;

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
    setInterval(loadChatUsers, 3000);
    setInterval(() => {
        if (currentReceiverId) {
            loadMessages(currentReceiverId);
        }
    }, 1000);

    // Axtarış funksiyasını əlavə et
    const searchInput = document.getElementById('user-search');
    if (searchInput) {
        searchInput.addEventListener('input', filterUsers);
    }
}

// Chat istifadəçilərini yükləmə funksiyası
function loadChatUsers() {
    fetch('/istifadeciler/api/chat/users/')
        .then(response => response.json())
        .then(data => {
            const usersList = document.getElementById('users-list');
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
    currentReceiverId = userId;
    currentReceiverName = username;
    
    const chatMain = document.querySelector('.chat-main');
    const chatSidebar = document.querySelector('.chat-sidebar');
    const selectedUsername = document.getElementById('selected-username');
    
    chatSidebar.style.display = 'none';
    chatMain.style.display = 'flex';
    selectedUsername.textContent = username;
    
    loadMessages(userId);
}

// Mesaj yükləmə funksiyası
function loadMessages(receiverId) {
    fetch(`/istifadeciler/api/chat/messages/${receiverId}/`)
        .then(response => response.json())
        .then(messages => {
            const chatMessages = document.getElementById('chat-messages');
            
            const lastMessage = messages[messages.length - 1];
            
            chatMessages.innerHTML = messages.map(msg => `
                <div class="message ${msg.is_mine ? 'mine' : 'theirs'}">
                    ${!msg.is_mine ? `<div class="message-sender">${msg.sender}</div>` : ''}
                    <div class="message-content">
                        ${msg.type === 'audio' ? 
                            `<audio controls src="${msg.content}"></audio>` : 
                            formatMessageContent(msg.content)}
                    </div>
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

            if (lastMessage) {
                lastMessageId = lastMessage.id;
            }

            // Avtomatik aşağı sürüşdür
            chatMessages.scrollTop = chatMessages.scrollHeight;
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
    const content = input.value.trim();
    
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
            input.value = '';
            loadMessages(currentReceiverId);
        }
    })
    .catch(error => console.error('Error sending message:', error));
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

// Chat-i inizializasiya et
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing chat...'); // Debug üçün
    initChat();
});

// DOM yükləndikdə
document.addEventListener('DOMContentLoaded', function() {
    // Saat funksiyalarını ləğv edirik
    // updateCurrentTime();
    // setInterval(updateCurrentTime, 1000);
    // checkWorkingHours();
    // setInterval(checkWorkingHours, 60000);

    // Swiper-ləri inicializasiya et
    new Swiper('.brandsSwiper', swiperConfig);
    new Swiper('.carBrandsSwiper', {
        ...swiperConfig,
        autoplay: {
            ...swiperConfig.autoplay,
            delay: 3500
        }
    });

    // İlkin statistikaları yüklə
    updateStatistics();

    // Hər 1 saniyədə bir yenilə
    setInterval(updateStatistics, 1000);

    // Səbət sayını yenilə
    updateCartCount();

    // Rəy formu üçün
    const reviewForm = document.querySelector('.review-form form');
    if (reviewForm) {
        reviewForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Ulduz seçilməyibsə xəbərdarlıq et
            const rating = reviewForm.querySelector('input[name="qiymetlendirme"]:checked');
            if (!rating) {
                showReviewNotification('error', 'Zəhmət olmasa, qiymətləndirmə üçün ulduz seçin');
                return;
            }

            // Rəy yazılmayıbsa xəbərdarlıq et
            const review = reviewForm.querySelector('textarea[name="rey"]').value.trim();
            if (!review) {
                showReviewNotification('error', 'Zəhmət olmasa, rəyinizi yazın');
                return;
            }

            // Formu göndər
            fetch(reviewForm.action, {
                method: 'POST',
                body: new FormData(reviewForm),
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showReviewNotification('success', 'Rəyiniz uğurla göndərildi. Təsdiqlənməsi gözlənilir');
                    reviewForm.reset();
                } else {
                    showReviewNotification('error', data.message || 'Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin');
                }
            })
            .catch(error => {
                showReviewNotification('error', 'Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin');
            });
        });
    }
});

// CSS-də əlavə et
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.2); }
        100% { transform: scale(1); }
    }
    
    .message-count.pulse {
        animation: pulse 0.5s ease-in-out;
    }
    
    .has-new-message {
        background-color: rgba(59, 130, 246, 0.1);
    }
`;
document.head.appendChild(style);

function showReviewNotification(type, message) {
    // Əvvəlki bildirişi sil
    const existingNotification = document.querySelector('.review-notification');
    if (existingNotification) {
        existingNotification.remove();
    }

    // Yeni bildiriş yarat
    const notification = document.createElement('div');
    notification.className = `review-notification ${type}`;
    notification.innerHTML = `
        <div class="icon">
            <i class="fas fa-${type === 'success' ? 'check' : 'exclamation-circle'}"></i>
        </div>
        <div class="content">
            <h4>${type === 'success' ? 'Uğurlu!' : 'Xəta!'}</h4>
            <p>${message}</p>
        </div>
        <div class="progress">
            <div class="progress-bar"></div>
        </div>
    `;

    document.body.appendChild(notification);

    // Animasiyanı başlat
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);

    // Bildirişi gizlət
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 500);
    }, 3000);
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

// Link tanıma funksiyası
function formatMessageContent(content) {
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    return content.replace(urlRegex, url => `<a href="${url}" class="message-link" target="_blank">${url}</a>`);
}


