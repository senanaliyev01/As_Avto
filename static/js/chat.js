document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chatMessages');
    const messageForm = document.getElementById('messageForm');
    const messageInput = document.getElementById('messageInput');
    const audioButton = document.querySelector('.audio-btn');
    const fullscreenButton = document.getElementById('fullscreen-chat');
    const chatWindow = document.getElementById('chat-window');
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;

    // WebSocket bağlantısı
    const chatSocket = new WebSocket(
        'ws://' + window.location.host + '/ws/chat/'
    );

    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        if (data.message) {
            appendMessage(data.message);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    };

    // Mesaj göndərmə
    messageForm.onsubmit = function(e) {
        e.preventDefault();
        const message = messageInput.value.trim();
        if (message) {
            fetch('/chat/send-message/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    message: message
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    messageInput.value = '';
                    appendMessage(data.message);
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                }
            });
        }
    };

    // Link tanıma funksiyası
    function detectLinks(text) {
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        return text.replace(urlRegex, function(url) {
            return `<a href="${url}" target="_blank">${url}</a>`;
        });
    }

    // Mesajı əlavə et
    function appendMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${message.sender === currentUserId ? 'sent' : 'received'}`;

        if (message.type === 'audio') {
            messageDiv.innerHTML = `
                <div class="message-content">
                    <audio controls>
                        <source src="${message.content}" type="audio/webm">
                    </audio>
                    <span class="time">${new Date().toLocaleTimeString()}</span>
                </div>
            `;
        } else {
            const messageContent = detectLinks(message.content);
            messageDiv.innerHTML = `
                <div class="message-content">
                    <p>${messageContent}</p>
                    <span class="time">${new Date().toLocaleTimeString()}</span>
                </div>
            `;
        }

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Link kliklərini dinlə
        const links = messageDiv.querySelectorAll('a');
        links.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                window.open(this.href, '_blank');
            });
        });
    }

    // Tam ekran funksiyası
    fullscreenButton.addEventListener('click', () => {
        chatWindow.classList.toggle('fullscreen');
        const icon = fullscreenButton.querySelector('i');
        if (chatWindow.classList.contains('fullscreen')) {
            icon.classList.replace('fa-expand', 'fa-compress');
        } else {
            icon.classList.replace('fa-compress', 'fa-expand');
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
            showRecordingIndicator();

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
        hideRecordingIndicator();

        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            sendAudioMessage(audioBlob);
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
        };
    }

    // Səs yazma indikatorunu göstər
    function showRecordingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'recording-indicator';
        indicator.innerHTML = `
            <div class="recording-wave">
                <span></span><span></span><span></span><span></span><span></span>
            </div>
            <span>Səs yazılır...</span>
        `;
        document.querySelector('.chat-input').appendChild(indicator);
    }

    // Səs yazma indikatorunu gizlət
    function hideRecordingIndicator() {
        const indicator = document.querySelector('.recording-indicator');
        if (indicator) indicator.remove();
    }

    // CSRF token al
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
}); 