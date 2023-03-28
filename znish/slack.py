import logging
import os
import sys

from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_bolt.app.app import App
from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_sdk.oauth.installation_store import FileInstallationStore
from slack_sdk.oauth.state_store import FileOAuthStateStore

from znish.bot import send_message

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG if os.environ.get("APP_ENV") == "production" else logging.INFO)

oauth_settings = OAuthSettings(
    client_id=os.environ["SLACK_CLIENT_ID"],
    client_secret=os.environ["SLACK_CLIENT_SECRET"],
    scopes=["app_mentions:read", "chat:write", "channels:read"],
    installation_store=FileInstallationStore(base_dir="./data/installations"),
    state_store=FileOAuthStateStore(expiration_seconds=600, base_dir="./data/states"),
    redirect_uri=os.environ["SLACK_REDIRECT_URI"],
)

app = App(
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"), oauth_settings=oauth_settings,
)

@app.event("app_mention")
def handle_mentions(event, client, say):
    input = event['text']
    reply = send_message(input)
    logging.info(f"send reply={reply}")
    say(reply)

@app.event("message")
def handle_message(event, client, say):
    logging.debug(event)

if __name__ == "__main__":
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()