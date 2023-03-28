import logging
import os
import sys

from flask import Flask, request
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_bolt.adapter.socket_mode import SocketModeHandler

from znish.slack import app

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG if os.environ.get("APP_ENV") == "production" else logging.INFO)

handler = SlackRequestHandler(app)
flask_app = Flask(__name__)

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

@flask_app.route("/slack/install", methods=["GET"])
def install():
    return handler.handle(request)

@flask_app.route("/slack/oauth_redirect", methods=["GET"])
def oauth_redirect():
    assert os.environ.get('OAUTH_ENABLED') == 'true'
    return handler.handle(request)

if __name__ == "__main__":
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).connect()
    flask_app.run(debug=os.environ.get('FLASK_DEBUG') != 'false', host="0.0.0.0")