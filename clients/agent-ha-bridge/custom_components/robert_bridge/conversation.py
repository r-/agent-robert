"""Conversation support for Agent R.O.B.E.R.T."""
import logging
import httpx
from typing import Any, Literal
from homeassistant.core import HomeAssistant, Context
from homeassistant.components import conversation
from homeassistant.helpers import intent
from homeassistant.util import ulid

_LOGGER = logging.getLogger(__name__)

DOMAIN = "robert_bridge"

async def async_setup_agent(hass: HomeAssistant) -> bool:
    """Set up the conversation agent."""
    agent = RobertConversationAgent(hass)
    conversation.async_set_agent(hass, config_entry=None, agent=agent)
    return True


class RobertConversationAgent(conversation.AbstractConversationAgent):
    """Simple bridge to external Robert API."""

    def __init__(self, hass: HomeAssistant):
        """Initialize the agent."""
        self.hass = hass

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        """Return a list of supported languages."""
        return "*"  # Support all languages (Robert is multilingual)

    async def async_process(
        self, user_input: conversation.ConversationInput
    ) -> conversation.ConversationResult:
        """Process a sentence."""
        text = user_input.text
        language = user_input.language
        conversation_id = user_input.conversation_id or ulid.ulid()
        
        # Get config from HASS data
        conf = self.hass.data.get(DOMAIN, {})
        url = conf.get("url", "http://localhost:8787/agent")
        api_key = conf.get("api_key", "ha-bridge-1")
        session_key = conf.get("session_key", "ha-chat")

        _LOGGER.debug("Sending to Robert: %s (url=%s)", text, url)

        response_text = "I'm sorry, I couldn't reach Robert."
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(
                    url,
                    json={
                        "message": text,
                        "session_key": session_key
                    },
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    }
                )
                res.raise_for_status()
                data = res.json()
                
                # Extract the response content
                response_text = data.get("content", "Empty response from Robert.")
                _LOGGER.info("Robert replied: %s", response_text)

        except httpx.RequestError as err:
            _LOGGER.error("Connection error while talking to Robert: %s", err)
            response_text = f"Connection error: {err}"
        except httpx.HTTPStatusError as err:
            _LOGGER.error("Robert returned error %s: %s", err.response.status_code, err.response.text)
            response_text = f"Robert Error {err.response.status_code}"
        except Exception as err:
            _LOGGER.exception("Unexpected error talking to Robert")
            response_text = "An unexpected error occurred."

        # Return result to Home Assistant
        intent_response = intent.IntentResponse(language=language)
        intent_response.async_set_speech(response_text)
        
        return conversation.ConversationResult(
            response=intent_response,
            conversation_id=conversation_id,
        )
