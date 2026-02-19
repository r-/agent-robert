// assistant.js - coordinates the chat UI and the API logic

import { sendMessageToAgent } from "./api.js";

export class Assistant {
    constructor(chat) {
        this.chat = chat;
        this.sessionKey = "web-demo-" + Math.floor(Math.random() * 1000);
    }

    async processText(message) {
        // Send to backend via router
        try {
            this.chat.addToolMessage("Talking to Agent Robert...");
            const response = await sendMessageToAgent(message, this.sessionKey);

            // Only show the FINAL answer. 
            // In future versions, we could stream tool outputs here.
            this.chat.addAIMessage(response.content);
            this.chat.addToolMessage(`Done in ${response.iterations} backend iterations.`);

        } catch (error) {
            this.chat.addAIMessage(`Error: ${error.message}`);
        }
    }

    async processAudio(blob, base64) {
        // Send audio as a data URI
        try {
            this.chat.addToolMessage("Transcribing audio (via Agent)...");
            const dataUri = `data:audio/wav;base64,${base64}`;

            const response = await sendMessageToAgent(dataUri, this.sessionKey);

            this.chat.addAIMessage(response.content);
            this.chat.addToolMessage(`Done in ${response.iterations} backend iterations.`);

        } catch (error) {
            this.chat.addAIMessage(`Error: ${error.message}`);
        }
    }
}
