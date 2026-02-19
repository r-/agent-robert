// api.js - talks to our local python-api-router

const ROUTER_URL = "http://127.0.0.1:8787/agent";
// In a real app, this key would be managed securely, or the router itself handles auth
// For this local demo, we use the client key defined in api-router's config.
const CLIENT_KEY = "rk-robot-1";

export async function sendMessageToAgent(message, sessionKey = "web-chat-01") {
    // We only send the *new* message. 
    // Agent R.O.B.E.R.T. manages history on the server side via sessionKey.

    // Note: We now support text AND audio messages via this endpoint.

    const payload = {
        message: message, // Can be text OR "data:audio/wav;base64,..."
        session_key: sessionKey
    };

    try {
        const response = await fetch(ROUTER_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${CLIENT_KEY}`
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Router Error ${response.status}: ${errorText}`);
        }

        const data = await response.json();
        return data; // { content: "...", iterations: N }

    } catch (error) {
        console.error("API Error:", error);
        throw error;
    }
}
