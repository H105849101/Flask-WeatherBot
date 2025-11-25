async function sendMessage() {
    const inputField = document.getElementById("user-input");
    const messagesDiv = document.getElementById("messages");

    const userMessage = inputField.value.trim();
    if (!userMessage) return;

    // User message
    const userContainer = document.createElement("div");
    userContainer.className = "user-message-container";

    const userBubble = document.createElement("div");
    userBubble.className = "user-message";
    userBubble.textContent = userMessage;

    userContainer.appendChild(userBubble);
    messagesDiv.appendChild(userContainer);

    inputField.value = "";

    // Sends data/ question to Flask
    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userMessage }),
        });

        const data = await response.json();

        //Bot response
        const botContainer = document.createElement("div");
        botContainer.className = "bot-message-container";

        const botBubble = document.createElement("div");
        botBubble.className = "bot-message";

        botBubble.innerHTML = data.response;

        botContainer.appendChild(botBubble);
        messagesDiv.appendChild(botContainer);

        // Automatically scrolls the conversation to the bottom
        messagesDiv.scrollTop = messagesDiv.scrollHeight;

    } catch (err) {
        console.error("Error:", err);
    }
}

// Allows user to press enter to send message
document.getElementById("user-input").addEventListener("keypress", function(e) {
    if (e.key === "Enter") {
        sendMessage();
    }
});