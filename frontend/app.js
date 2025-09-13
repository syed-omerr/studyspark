// Global variables
let recognition = null;
let utterance = null;

// Theme handling
function initializeTheme() {
    const themeSwitch = document.getElementById('theme-switch');
    const savedTheme = localStorage.getItem('theme') || 'light';
    
    // Set initial theme
    document.documentElement.setAttribute('data-theme', savedTheme);
    themeSwitch.checked = savedTheme === 'dark';
    
    // Handle theme changes
    themeSwitch.addEventListener('change', function() {
        const theme = this.checked ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    });
}

// Initialize theme when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeTheme);

// Check for browser support
const hasSpeechRecognition = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
const hasSpeechSynthesis = 'speechSynthesis' in window;

// DOM Elements
const voiceBtn = document.getElementById('voice-btn');
const voiceStatus = document.getElementById('voice-status');
const questionInput = document.getElementById('question');
const submitBtn = document.getElementById('submit-btn');
const lessonOutput = document.getElementById('lesson-output');
const lessonContent = document.getElementById('lesson-content');
const memeImg = document.getElementById('meme-img');
const voiceItBtn = document.getElementById('voice-it-btn');
const pauseBtn = document.getElementById('pause-btn');

// API Configuration
const API_URL = 'http://localhost:5001/api';

// Form Submission Handler
async function handleSubmit(event) {
    event.preventDefault();
    const question = questionInput.value.trim();
    const subject = document.getElementById('subject').value;

    if (!question) {
        alert('Please enter a question!');
        return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = 'Generating...';
    lessonOutput.style.display = 'none';

    try {
        const response = await fetch(`${API_URL}/lesson`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: question,
                subject: subject,
                language: 'slang'  // This will be converted to a more formal explanation
            })
        });

        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }

        // Format the lesson content with proper HTML structure
        lessonContent.innerHTML = data.lesson.split('\n').map(line => 
            line.trim() ? `<p>${line}</p>` : ''
        ).join('');

        // Handle meme display
        if (data.meme_url) {
            memeImg.src = data.meme_url;
            memeImg.style.display = 'block';
            memeImg.alt = 'Educational Meme';
        } else {
            memeImg.style.display = 'none';
        }

        lessonOutput.style.display = 'block';
        
        // Scroll to the output section
        lessonOutput.scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to generate lesson. Please try again.');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Generate Lesson';
    }
}

// Event Listeners
submitBtn.addEventListener('click', handleSubmit);

// Speech Recognition Setup
function setupSpeechRecognition() {
    if (!hasSpeechRecognition) {
        voiceBtn.style.display = 'none';
        return;
    }

    recognition = new (window.webkitSpeechRecognition || window.SpeechRecognition)();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
        voiceStatus.textContent = '🎤 Listening... Speak now!';
        voiceStatus.style.color = '#ffb347';
        voiceBtn.disabled = true;
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        questionInput.value = transcript;
        voiceStatus.textContent = `Recognized: ${transcript}`;
        voiceBtn.disabled = false;
    };

    recognition.onerror = (event) => {
        voiceStatus.textContent = `Error: ${event.error}`;
        voiceStatus.style.color = '#ff4b4b';
        voiceBtn.disabled = false;
    };

    recognition.onend = () => {
        voiceBtn.disabled = false;
    };

    voiceBtn.addEventListener('click', () => {
        try {
            recognition.start();
        } catch (error) {
            console.error('Recognition error:', error);
        }
    });
}

// Speech Synthesis Setup
function setupSpeechSynthesis() {
    if (!hasSpeechSynthesis) {
        voiceItBtn.style.display = 'none';
        pauseBtn.style.display = 'none';
        return;
    }

    voiceItBtn.addEventListener('click', () => {
        if (window.speechSynthesis.speaking) {
            window.speechSynthesis.cancel();
        }
        const text = lessonContent.textContent;
        utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1;
        utterance.pitch = 1;
        window.speechSynthesis.speak(utterance);
    });

    pauseBtn.addEventListener('click', () => {
        if (!window.speechSynthesis.speaking) return;
        if (window.speechSynthesis.paused) {
            window.speechSynthesis.resume();
        } else {
            window.speechSynthesis.pause();
        }
    });
}

// API Functions
async function generateLesson() {
    const subject = document.getElementById('subject').value;
    const language = document.querySelector('input[name="language"]:checked').value;
    const query = questionInput.value.trim();

    if (!query) {
        alert('Please enter a question!');
        return;
    }

    try {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Processing...';

        const response = await fetch(`${API_URL}/lesson`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query,
                subject,
                language
            })
        });

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to generate lesson');
        }

        // Display lesson
        lessonContent.innerHTML = data.lesson;
        
        // Handle meme image
        if (data.meme_url) {
            memeImg.src = data.meme_url;
            memeImg.style.display = 'block';
        } else {
            memeImg.style.display = 'none';
        }

        lessonOutput.style.display = 'block';
        
    } catch (error) {
        alert(`Error: ${error.message}`);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Get Lesson';
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    setupSpeechRecognition();
    setupSpeechSynthesis();
    
    submitBtn.addEventListener('click', generateLesson);
    
    // Also submit on Enter key in textarea (Ctrl/Cmd + Enter)
    questionInput.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            generateLesson();
        }
    });
});