document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chatMessages');
    const messageForm = document.getElementById('messageForm');
    const messageInput = document.getElementById('messageInput');
    const audioButton = document.querySelector('.audio-btn');
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

    // Auto-resize input
    messageInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
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
            showNotification('Səs yazmaq üçün icazə lazımdır');
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

    // Səs mesajını göndər
    function sendAudioMessage(blob) {
        const formData = new FormData();
        formData.append('audio', blob, 'voice.webm');
        
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
                appendMessage({
                    type: 'audio',
                    content: data.url,
                    sender: currentUserId
                });
            }
        });
    }

    // Mesaj göndər
    function sendMessage(content) {
        chatSocket.send(JSON.stringify({
            'message': content,
            'sender': currentUserId
        }));
    }

    // Mesajı əlavə et
    function appendMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${message.sender === currentUserId ? 'sent' : 'received'}`;

        if (message.type === 'audio') {
            messageDiv.innerHTML = `
                <audio controls>
                    <source src="${message.content}" type="audio/webm">
                </audio>
                <span class="time">${new Date().toLocaleTimeString()}</span>
            `;
        } else {
            messageDiv.innerHTML = `
                <div class="message-content">
                    <p>${message.content}</p>
                    <span class="time">${new Date().toLocaleTimeString()}</span>
                </div>
            `;
        }

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Səs yazma indikatorunu göstər
    function showRecordingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'recording-indicator';
        indicator.innerHTML = `
            <div class="recording-wave"></div>
            <span>Səs yazılır...</span>
        `;
        audioButton.appendChild(indicator);
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
}); 