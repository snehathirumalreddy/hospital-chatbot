// Send message from input box or quick buttons
function sendMessage(text = null) {
    let input = document.getElementById("userInput");
    let message = text ? text : input.value.trim();

    if (message === "") return;

    // Show user message
    addMessage(message, "user-message");

    // Clear input only if typed
    if (!text) input.value = "";

    // Send message to Flask backend
    fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        addMessage(data.reply, "bot-message");
    })
    .catch(() => {
        addMessage("⚠️ Server error. Please try again.", "bot-message");
    });
}

// Used by quick action buttons
function quickSend(text) {
    sendMessage(text);
}

// Add message to chat window
function addMessage(text, className) {
    let chatBox = document.getElementById("chatBox");
    let messageDiv = document.createElement("div");

    messageDiv.className = className;
    messageDiv.innerText = text;

    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Allow Enter key to send message
document.addEventListener("DOMContentLoaded", function () {
    let input = document.getElementById("userInput");

    input.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    });
});
