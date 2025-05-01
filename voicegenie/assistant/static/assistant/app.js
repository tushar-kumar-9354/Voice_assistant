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

async function askGPT(prompt) {
  try {
    const res = await fetch('/ask/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify({ prompt })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.error || res.statusText);
    }
    const blob = await res.blob();
    const url  = URL.createObjectURL(blob);
    responseAudio.src    = url;
    responseAudio.hidden = false;
    await responseAudio.play();
    conversation.innerHTML += `<p><strong>Bot:</strong> (spoken)</p>`;
  } catch (e) {
    statusDiv.textContent = `❌ ${e.message}`;
  }
}

function getCookie(name) {
  return document.cookie.match(new RegExp('(^|;)\\s*' + name + '=([^;]+)'))?.pop() || '';
}
