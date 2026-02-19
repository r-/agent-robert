# Agent Chat UI

A simple, local web interface for Agent R.O.B.E.R.T.

## Prerequisites
1.  **Backend Running**: You must have `api-router` running on port 8787.
    ```powershell
    cd ../api-router
    uv run fastapi dev api_router/main.py --port 8787
    ```

## How to Run
1.  **Start the Frontend**:
    Run the `start_chat.bat` script, or run:
    ```powershell
    python -m http.server 8000
    ```

2.  **Open in Browser**:
    Go to [http://localhost:8000](http://localhost:8000)

## Features
-   **Text Chat**: Talk to R.O.B.E.R.T. directly using the router bridge.
-   **Audio Recording**: Records audio (UI only for now, backend support coming soon).
-   **Tool Feedback**: Sees when the agent is "Thinking" or using tools.

## Audio Note
The microphone button records audio and converts it to Base64, but Agent R.O.B.E.R.T.'s current backend accepts text messages only. Audio messages will result in a polite "not implemented" response from the UI assistant logic.
