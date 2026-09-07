/* =========================================================
   TeleBot AI — Frontend Controller
   ========================================================= */

// Dynamically resolve to the same host/port serving this page
const API_BASE_URL = window.location.origin;

/* ── Onboarding State ────────────────────────────────────── */
let sessionPhone = null; // set after phone verification

/* ── Onboarding Elements ─────────────────────────────────── */
const onboardingOverlay  = document.getElementById('onboardingOverlay');
const phoneInput         = document.getElementById('phoneInput');
const verifyPhoneBtn     = document.getElementById('verifyPhoneBtn');
const phoneError         = document.getElementById('phoneError');
const onboardingForm     = document.getElementById('onboardingForm');
const onboardingSuccess  = document.getElementById('onboardingSuccess');
const successName        = document.getElementById('successName');
const successOperator    = document.getElementById('successOperator');
const startChatBtn       = document.getElementById('startChatBtn');

/* ── Onboarding Logic ────────────────────────────────────── */

// Only allow numeric digits in phone input
phoneInput.addEventListener('input', () => {
    phoneInput.value = phoneInput.value.replace(/\D/g, '');
    phoneError.textContent = '';
});

phoneInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') verifyPhone();
});

verifyPhoneBtn.addEventListener('click', verifyPhone);

async function verifyPhone() {
    const phone = phoneInput.value.trim();

    if (phone.length !== 10) {
        phoneError.textContent = '⚠️ Please enter a valid 10-digit mobile number.';
        return;
    }

    verifyPhoneBtn.disabled = true;
    verifyPhoneBtn.textContent = 'Verifying...';
    phoneError.textContent = '';

    try {
        const resp = await fetch(`${API_BASE_URL}/lookup/${phone}`);
        const data = await resp.json();

        if (data.found) {
            sessionPhone = phone;
            // Show success state
            successName.textContent = `Welcome, ${data.name}! 👋`;
            successOperator.textContent = `${data.operator} subscriber · ${phone}`;
            onboardingForm.style.display = 'none';
            onboardingSuccess.style.display = 'block';
        } else {
            phoneError.textContent = '❌ Number not found. Try: 6360341569, 9876543210, 8765432109…';
            verifyPhoneBtn.disabled = false;
            verifyPhoneBtn.textContent = 'Continue →';
        }
    } catch (err) {
        phoneError.textContent = '⚠️ Could not reach server. Is the bot running?';
        verifyPhoneBtn.disabled = false;
        verifyPhoneBtn.textContent = 'Continue →';
    }
}

startChatBtn.addEventListener('click', () => {
    onboardingOverlay.classList.add('hidden');
    // Remove from DOM after animation
    setTimeout(() => onboardingOverlay.remove(), 500);
    // Personalize the header with customer name from successName
    const name = successName.textContent.replace('Welcome, ', '').replace('! 👋', '');
    document.querySelector('.chat-header h2').textContent = `Hi, ${name}!`;
    addMessage(`👋 Hello ${name}! I'm your TeleBot AI assistant. How can I help you today?`, 'bot');
});

/* ── DOM References ──────────────────────────────────────── */
const messagesContainer = document.getElementById('messagesContainer');
const userInput         = document.getElementById('userInput');
const sendBtn           = document.getElementById('sendBtn');
const recordBtn         = document.getElementById('recordBtn');
const langBtns          = document.querySelectorAll('.lang-btn');
const audioPlayer       = document.getElementById('audioPlayer');
const clearChat         = document.getElementById('clearChat');
const avatarContainer   = document.querySelector('.avatar-container');
const callTimer         = document.getElementById('callTimer');
const callStatus        = document.getElementById('callStatus');
const startCallBtn      = document.getElementById('startCallBtn');
const endCallBtn        = document.getElementById('endCallBtn');
const callSimulator     = document.getElementById('callSimulator');

const recordLang        = document.getElementById('recordLang');

/* ── State ───────────────────────────────────────────────── */
let currentLanguage = 'en';
let mediaRecorder   = null;
let audioChunks     = [];
let isRecording     = false;
let inCall          = false;
let callInterval    = null;
let callStartTime   = null;
let isBotSpeaking   = false;

// Detect the best supported MIME type once
const MIME_TYPE = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
    ? 'audio/webm;codecs=opus'
    : MediaRecorder.isTypeSupported('audio/webm')
    ? 'audio/webm'
    : 'audio/ogg';

// Language name mappings for helper placeholder text
const LANG_PLACEHOLDERS = {
    'en': 'Type or speak in English...',
    'hi': 'Type or speak in Hindi (हिंदी)...',
    'te': 'Type or speak in Telugu (తెలుగు)...',
    'kn': 'Type or speak in Kannada (ಕನ್ನಡ)...'
};

/* ── Language Selection ──────────────────────────────────── */
langBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        langBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentLanguage = btn.dataset.lang;
        
        // Update input placeholder and mic badge
        userInput.placeholder = LANG_PLACEHOLDERS[currentLanguage] || 'Type your message here...';
        if (recordLang) recordLang.textContent = currentLanguage.toUpperCase();
        
        addMessage(`🌐 Language switched to ${btn.innerText.trim()}`, 'bot');
    });
});

/* =========================================================
   SHARED VOICE RECORDING ENGINE
   One function used by both manual mic button AND call mode.
   ========================================================= */
function startRecording(onComplete) {
    return new Promise(async (resolve, reject) => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream, { mimeType: MIME_TYPE });
            audioChunks = [];

            mediaRecorder.ondataavailable = (e) => {
                if (e.data && e.data.size > 0) audioChunks.push(e.data);
            };

            mediaRecorder.onstop = () => {
                // Release microphone immediately
                stream.getTracks().forEach(t => t.stop());
                isRecording = false;

                const blob = new Blob(audioChunks, { type: MIME_TYPE });
                if (blob.size < 1000) {
                    // Too small — likely no audio captured
                    onComplete(null, 'Audio too short. Please speak clearly and try again.');
                } else {
                    onComplete(blob, null);
                }
            };

            mediaRecorder.onerror = (e) => {
                stream.getTracks().forEach(t => t.stop());
                isRecording = false;
                onComplete(null, `Recording error: ${e.error}`);
            };

            mediaRecorder.start(100); // collect chunks every 100ms
            isRecording = true;
            resolve();
        } catch (err) {
            isRecording = false;
            reject(err);
        }
    });
}

function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
    }
}

/* =========================================================
   SPEECH-TO-TEXT PIPELINE
   Takes a blob → sends to backend → returns transcript string
   ========================================================= */
async function transcribeBlob(blob) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(blob);
        reader.onloadend = async () => {
            try {
                const base64Audio = reader.result.split(',')[1];
                if (!base64Audio) {
                    reject(new Error('Failed to encode audio as base64'));
                    return;
                }

                console.log(`[STT] Sending ${blob.size} bytes | type=${MIME_TYPE}`);

                // 30-second timeout for Whisper transcription
                const controller = new AbortController();
                const timeout = setTimeout(() => controller.abort(), 30000);

                const resp = await fetch(`${API_BASE_URL}/speech-to-text`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        audio_content: base64Audio,
                        mime_type: MIME_TYPE,
                        language: currentLanguage
                    }),
                    signal: controller.signal
                });

                clearTimeout(timeout);

                if (!resp.ok) {
                    reject(new Error(`Server returned ${resp.status}`));
                    return;
                }

                const data = await resp.json();
                console.log(`[STT] Transcript: "${data.transcript}"`);
                resolve(data.transcript || '');
            } catch (err) {
                console.error('[STT] Fetch error:', err);
                reject(err);
            }
        };
        reader.onerror = () => reject(new Error('FileReader failed to read audio blob'));
    });
}

/* =========================================================
   MANUAL MICROPHONE BUTTON (Using Web Speech API)
   ========================================================= */
let recognition = null;

recordBtn.addEventListener('click', async () => {
    if (isRecording) {
        // Stop recognition
        if (recognition) recognition.stop();
        isRecording = false;
        recordBtn.classList.remove('recording');
        return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        addMessage('🚫 Speech Recognition is not supported in this browser.', 'user');
        return;
    }

    recognition = new SpeechRecognition();
    
    // Map our language codes to standard BCP 47 tags for SpeechRecognition
    const langMap = {
        'en': 'en-IN',
        'hi': 'hi-IN',
        'kn': 'kn-IN',
        'te': 'te-IN'
    };
    recognition.lang = langMap[currentLanguage] || 'en-IN';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recordBtn.classList.add('recording');
    isRecording = true;
    const processingMsgEl = addMessage('🎙 Listening... (click mic to stop)', 'user');

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        if (transcript && transcript.trim()) {
            updateMessage(processingMsgEl, transcript);
            sendMessage(transcript, processingMsgEl);
        } else {
            updateMessage(processingMsgEl, "🎤 Couldn't hear clearly. Please try again.");
        }
    };

    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        if (event.error !== 'aborted') {
            updateMessage(processingMsgEl, `⚠️ Voice processing failed: ${event.error}`);
        }
    };

    recognition.onend = () => {
        isRecording = false;
        recordBtn.classList.remove('recording');
    };

    recognition.start();
});

/* =========================================================
   CALL MODE
   ========================================================= */
async function startCall() {
    inCall = true;
    callStartTime = new Date();
    callInterval = setInterval(updateCallTimer, 1000);
    if (startCallBtn) startCallBtn.style.display = 'none';
    if (endCallBtn) endCallBtn.style.display = 'flex';
    if (callSimulator) callSimulator.classList.add('call-active');
    setCallStatus('📡 Connecting...');
    addMessage('<i>📞 Call started. Speak now!</i>', 'bot');
    setTimeout(() => listenForCallInput(), 800);
}

function endCall() {
    inCall = false;
    clearInterval(callInterval);
    stopRecording();
    if (startCallBtn) startCallBtn.style.display = 'flex';
    if (endCallBtn) endCallBtn.style.display = 'none';
    if (callSimulator) callSimulator.classList.remove('call-active');
    if (callTimer) callTimer.innerText = '00:00';
    setCallStatus('Ready to talk');
    addMessage('<i>📵 Call ended.</i>', 'bot');
}

let callRecognition = null;

async function listenForCallInput() {
    if (!inCall || isBotSpeaking) return;
    setCallStatus('🎙 Listening...');

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        setCallStatus('🚫 Speech Recognition not supported.');
        setTimeout(() => endCall(), 2000);
        return;
    }

    if (callRecognition) {
        callRecognition.stop();
    }

    callRecognition = new SpeechRecognition();
    const langMap = {
        'en': 'en-IN',
        'hi': 'hi-IN',
        'kn': 'kn-IN',
        'te': 'te-IN'
    };
    callRecognition.lang = langMap[currentLanguage] || 'en-IN';
    callRecognition.interimResults = false;
    callRecognition.maxAlternatives = 1;

    let recognized = false;

    callRecognition.onresult = async (event) => {
        recognized = true;
        const transcript = event.results[0][0].transcript;
        if (transcript && transcript.trim()) {
            setCallStatus('⏳ Processing...');
            addMessage(transcript, 'user');
            await sendChatAndSpeak(transcript);
        } else {
            setCallStatus('🔇 No speech detected. Listening again...');
            if (inCall) setTimeout(() => listenForCallInput(), 1000);
        }
    };

    callRecognition.onerror = (event) => {
        console.error('Call Speech recognition error:', event.error);
        if (event.error !== 'aborted') {
            setCallStatus('⚠️ Error. Listening again...');
            if (inCall) setTimeout(() => listenForCallInput(), 1500);
        }
    };

    callRecognition.onend = () => {
        // If we didn't get any result and the call is still active, restart listening
        if (!recognized && inCall && !isBotSpeaking) {
            listenForCallInput();
        }
    };

    try {
        callRecognition.start();
    } catch (e) {
        console.error("Failed to start call recognition:", e);
    }
}

async function sendChatAndSpeak(text) {
    if (!inCall) return;
    setCallStatus('🤔 AI thinking...');

    try {
        const resp = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text, user_id: 'call_user', language: currentLanguage
            })
        });
        const data = await resp.json();
        addMessage(data.bot_response, 'bot');
        setCallStatus('🔊 AI speaking...');
        await playTTSAndWait(data.bot_response, data.language || currentLanguage);
        // After bot finishes speaking, listen again
        if (inCall) setTimeout(() => listenForCallInput(), 500);
    } catch (err) {
        console.error('Chat error in call:', err);
        setCallStatus('⚠️ Error. Listening again...');
        if (inCall) setTimeout(() => listenForCallInput(), 1500);
    }
}

function updateCallTimer() {
    const diff = new Date(new Date() - callStartTime);
    const m = String(diff.getUTCMinutes()).padStart(2, '0');
    const s = String(diff.getUTCSeconds()).padStart(2, '0');
    if (callTimer) callTimer.innerText = `${m}:${s}`;
}

function setCallStatus(msg) {
    if (callStatus) callStatus.innerText = msg;
}

if (startCallBtn) startCallBtn.addEventListener('click', startCall);
if (endCallBtn)   endCallBtn.addEventListener('click', endCall);

/* =========================================================
   TTS — returns a Promise that resolves when audio finishes
   ========================================================= */
function playTTSAndWait(text, lang) {
    return new Promise((resolve) => {
        if (!('speechSynthesis' in window)) {
            console.warn('SpeechSynthesis not supported.');
            resolve();
            return;
        }

        isBotSpeaking = true;
        avatarContainer.classList.add('talking');

        const utterance = new SpeechSynthesisUtterance(text);
        
        // Map our language codes to standard BCP 47 tags for SpeechSynthesis
        const langMap = {
            'en': 'en-IN',
            'hi': 'hi-IN',
            'kn': 'kn-IN',
            'te': 'te-IN'
        };
        utterance.lang = langMap[lang] || 'en-IN';
        
        utterance.onend = () => {
            isBotSpeaking = false;
            avatarContainer.classList.remove('talking');
            resolve();
        };
        utterance.onerror = (e) => {
            console.error('SpeechSynthesis error:', e);
            isBotSpeaking = false;
            avatarContainer.classList.remove('talking');
            resolve();
        };

        window.speechSynthesis.speak(utterance);
    });
}

// Also handle non-call TTS
async function playTTS(text, lang) {
    await playTTSAndWait(text, lang);
}

/* =========================================================
   TEXT CHAT
   ========================================================= */
async function sendMessage(customText = null, existingMsgEl = null) {
    const text = customText !== null ? customText : userInput.value.trim();
    if (!text) return;

    if (!existingMsgEl) {
        addMessage(text, 'user');
    }
    if (customText === null) {
        userInput.value = '';
    }

    const loadingEl = addMessage('<i>Thinking...</i>', 'bot');
    loadingEl.classList.add('loading');

    try {
        const resp = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text, user_id: 'user_123', session_id: 'session_456',
                phone: sessionPhone || '6360341569',
                language: currentLanguage
            })
        });
        const data = await resp.json();
        loadingEl.remove();
        addMessage(data.bot_response, 'bot');
        playTTS(data.bot_response, data.language || currentLanguage);
    } catch (err) {
        console.error('Chat error:', err);
        loadingEl.remove();
        addMessage('⚠️ Could not connect to the server. Is the bot running?', 'bot');
    }
}

/* =========================================================
   MESSAGE HELPERS
   ========================================================= */
function addMessage(text, sender) {
    const div = document.createElement('div');
    div.className = `message ${sender}`;
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const avatar = sender === 'bot' ? '🤖' : '👤';
    div.innerHTML = `
        <div class="msg-avatar">${avatar}</div>
        <div class="msg-body">
            <div class="message-content">${text}</div>
            <div class="message-time">${time}</div>
        </div>`;
    messagesContainer.appendChild(div);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    return div;
}

function updateMessage(el, newText) {
    const content = el.querySelector('.message-content');
    if (content) content.innerHTML = newText;
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

/* ── Quick Actions ───────────────────────────────────────── */
document.getElementById('quickActions').addEventListener('click', (e) => {
    const btn = e.target.closest('.quick-action-btn');
    if (btn) {
        userInput.value = btn.dataset.query;
        sendMessage();
    }
});

/* ── Send Button / Enter Key ─────────────────────────────── */
sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

/* ── Clear Chat ──────────────────────────────────────────── */
clearChat.addEventListener('click', () => {
    messagesContainer.innerHTML = '';
    addMessage('Chat cleared. How can I help you today?', 'bot');
});
