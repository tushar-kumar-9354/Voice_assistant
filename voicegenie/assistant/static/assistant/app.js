const startBtn       = document.getElementById('startBtn');
const statusDiv      = document.getElementById('status');
const conversation   = document.getElementById('conversation');
const responseAudio  = document.getElementById('responseAudio');

window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if (!window.SpeechRecognition) {
  statusDiv.textContent = "🚫 Speech recognition not supported";
  startBtn.disabled = true;
} else {
  const recog = new SpeechRecognition();
  recog.lang            = 'en-US';
  recog.interimResults  = false;
  recog.continuous       = false;

  recog.onstart = () => statusDiv.textContent = "Listening…";
  recog.onend   = () => statusDiv.textContent = "Processing…";
  recog.onerror = e => statusDiv.textContent = `Error: ${e.error}`;

  recog.onresult = async e => {
    const text = e.results[0][0].transcript.trim();
    conversation.innerHTML += `<p><strong>You:</strong> ${text}</p>`;
    await askGPT(text);
    statusDiv.textContent = "Ready";
  };

  startBtn.onclick = () => recog.start();
}
const chatHistory = []; // 💾 Tracks full conversation

async function askGPT(prompt) {
  try {
    // Save user input
    chatHistory.push({ role: "user", text: prompt });

    const res = await fetch('/ask/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify({ prompt, history: chatHistory })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.error || res.statusText);
    }

    const data = await res.json();

    // Save bot reply
    chatHistory.push({ role: "bot", text: data.reply });

    // Display response
    conversation.innerHTML += `<p><strong>Bot:</strong> ${data.reply}</p>`;
    responseAudio.src = data.audio_url;
    responseAudio.hidden = false;
    await responseAudio.play();

  } catch (e) {
    statusDiv.textContent = `❌ ${e.message}`;
  }
}

  

function getCookie(name) {
  return document.cookie.match(new RegExp('(^|;)\\s*' + name + '=([^;]+)'))?.pop() || '';
}

