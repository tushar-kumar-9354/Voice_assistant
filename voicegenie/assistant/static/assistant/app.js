let recognition;
let isListening = false;


const outputDiv = document.getElementById('output');

// Restore old conversation
window.onload = () => {
  outputDiv.innerHTML = sessionStorage.getItem("chatHistory") || "";
};
async function askQuestion() {
  const question = document.getElementById("question").value;
  const audioPlayer = document.getElementById("responseAudio");

  const response = await fetch("/ask/", {
      method: "POST",
      headers: {
          "Content-Type": "application/json"
      },
      body: JSON.stringify({ prompt: question })
  });

  if (response.ok) {
      const blob = await response.blob();
      const audioUrl = URL.createObjectURL(blob);
      audioPlayer.src = audioUrl;
      audioPlayer.play();
  } else {
      alert("Failed to get audio response.");
  }
}


function startListening() {
  if (!('webkitSpeechRecognition' in window)) {
    alert("Your browser doesn't support speech recognition.");
    return;
  }

  recognition = new webkitSpeechRecognition();
  recognition.lang = 'en-US';
  recognition.continuous = false;
  recognition.interimResults = false;

  recognition.onresult = function (event) {
    const transcript = event.results[0][0].transcript;
    sendToBackend(transcript);
  };

  recognition.onerror = function (event) {
    console.error("Error:", event.error);
  };

  recognition.onend = function () {
    isListening = false;
  };

  recognition.start();
  isListening = true;
}

function stopListening() {
  if (recognition && isListening) {
    recognition.stop();
    isListening = false;
  }
}

function sendToBackend(text) {
  const csrftoken = getCookie("csrftoken");

  fetch("/ask/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify({ prompt: text })
  })
    .then(response => response.blob())
    .then(blob => {
      const audio = new Audio(URL.createObjectURL(blob));
      audio.play();
    })
    .catch(error => console.error("Error:", error));
}


function speak(text) {
  const audio = new Audio(`/ask/?text=${encodeURIComponent(text)}`);
  audio.play();
}


function getCookie(name) {
  let cookieValue = "";
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + "=")) {
        cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
