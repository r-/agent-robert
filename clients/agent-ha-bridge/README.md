# Robert Bridge for Home Assistant

This is a **Custom Integration** for Home Assistant that bridges voice/text commands to an external [Agent R.O.B.E.R.T.](https://github.com/maker-norr/agent-robert) instance.

## Installation

1.  Copy the `custom_components/robert_bridge` folder into your Home Assistant's `config/custom_components/` directory.
2.  Restart Home Assistant.

## Configuration

Add the following to your `configuration.yaml` in Home Assistant:

```yaml
robert_bridge:
  url: "http://<YOUR_ROUTER_IP>:8787/agent"
  api_key: "ha-key-1"  (Must match a key in your api-router .env)
  session_key: "ha-room-1"
```

## Usage

1.  Go to **Settings -> Voice Assistants**.
2.  Create a new Assistant (or edit an existing one).
3.  Under **Conversation Agent**, select **Robert Bridge**.
4.  Now, any voice command given to this assistant will be sent to Robert!
