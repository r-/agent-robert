// main.js - entry point for the chat UI

import { Chat } from "./chat.js";
import { Assistant } from "./assistant.js";
import { recordOnce, blobToBase64 } from "./recorder.js";

document.addEventListener("DOMContentLoaded", () => {

    const chatWindow = document.getElementById("chat-window");
    const chatInput = document.getElementById("chat-input");
    const micButton = document.getElementById("mic-button");
    const statusIndicator = document.getElementById("status-indicator");

    const chat = new Chat(chatWindow);
    const assistant = new Assistant(chat);

    // Initial greeting
    chat.addAIMessage("Hello! I am Agent R.O.B.E.R.T. How can I help you?");

    // ----- TEXT INPUT -----
    chatInput.addEventListener("keydown", async (e) => {
        if (e.key === "Enter") {
            await sendText();
        }
    });

    async function sendText() {
        const text = chatInput.value.trim();
        if (!text) return;

        chatInput.value = "";
        chat.addUserMessage(text);

        statusIndicator.textContent = "● Thinking...";
        statusIndicator.style.color = "#ffc107";

        try {
            await assistant.processText(text);
        } finally {
            statusIndicator.textContent = "● Online";
            statusIndicator.style.color = "#28a745";
        }
    }

    // ----- AUDIO INPUT -----
    micButton.addEventListener("click", async () => {
        if (micButton.classList.contains("recording")) return; // debounce

        micButton.classList.add("recording");
        micButton.textContent = "🎙️";
        statusIndicator.textContent = "● Listening...";
        statusIndicator.style.color = "#dc3545";

        try {
            // Record 3 seconds
            const blob = await recordOnce(3000);
            const base64 = await blobToBase64(blob);

            chat.addUserMessage("(Sending audio...)");

            // Send to assistant
            await assistant.processAudio(blob, base64);

        } catch (error) {
            console.error(error);
            chat.addAIMessage("Microphone error: " + error.message);
        } finally {
            micButton.classList.remove("recording");
            micButton.textContent = "🎤";
            statusIndicator.textContent = "● Online";
            statusIndicator.style.color = "#28a745";
        }
    });

});
