from quart import request, session, redirect, url_for, jsonify
from requests_oauthlib import OAuth2Session
from rest.token_management import generate_random_token_for_user, save_google_auth_token, get_user_id
from rest.main_app import app

from oauthlib.oauth2.rfc6749.errors import TokenExpiredError
from dotenv import load_dotenv

import os
import logging
import sys

load_dotenv()
GCP_CLIENT_SECRET = os.getenv('GCP_CLIENT_SECRET')
GCP_CLIENT_ID = "390499960303-lv5cp1mheudrnrar6fsu06b727v1qbma.apps.googleusercontent.com"

GCP_REDIRECT_URI = "https://api.myjess.ai/oauth2callback"
GCP_TOKEN_URL = 'https://oauth2.googleapis.com/token'
GCP_SCOPE = ['https://www.googleapis.com/auth/userinfo.email', 
          'https://www.googleapis.com/auth/userinfo.profile']
GCP_AUTHORIZATION_BASE_URL = 'https://accounts.google.com/o/oauth2/v2/auth'


logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@app.post("/auth/oauth_exchange")
@app.post("/auth/auth_exchange")
async def oauth_exchange():
    data = None
    if request.content_type == 'application/json':
        try:
            data = await request.get_json(force=True)
        except Exception as e:
            return jsonify({"error": "Invalid JSON format"}), 400
    elif request.content_type == 'application/x-www-form-urlencoded':
        data = await request.form
    else:
        return jsonify({"error": "Unsupported Media Type"}), 415
    
    logger.debug(f"oauth_exchange {data}")
    logger.debug(f"Method: {request.method}")
    logger.debug(f"URL: {request.full_path}")
    logger.debug(f"Body: {await request.get_data()}")
    logger.debug(f"Headers: {request.headers}")

    response_data = {
        "access_token": data['code'],
        "token_type": "bearer"
    }
    return jsonify(response_data), 200, {'Content-Type': 'application/json'}


@app.get("/oauth")
async def oauth():
    # This is where everything starts, OpenAI will call this endpiont first
    logger.debug("oauth request received")
    # state is variable from OpanAI that you have to pass back
    # fucking security 
    state = request.args.get("state")
    logger.debug(f"auth state: {state}")
    openai_redirect_uri = None
    openai_redirect_uri = request.args.get("redirect_uri")

    logger.debug(f"openai_redirect_uri before: {openai_redirect_uri}")
    if not openai_redirect_uri:
        openai_redirect_uri = session['openai_redirect_uri']
    else:
        session['openai_redirect_uri'] = openai_redirect_uri

    if not state:
        state = session['state']
    else:
        session['state'] = state
    
    logger.debug(f"openai_redirect_uri after: {openai_redirect_uri}")

    # if this is the first time, our middle man have not yet
    # authentificated user at google
    if _is_google_auth_needed():
        return googleauth()

    # this should never happened but, who knows
    if 'oauth_token' not in session:
        raise RuntimeError("no oauth state")
    
    url = openai_redirect_uri + f"?code={session['openai_oauth_token']}&state={state}"
    logger.debug(f"Method: {request.method}")
    logger.debug(f"URL: {request.full_path}")
    logger.debug(f"Body: {await request.get_data()}")
    logger.debug(f"Headers: {request.headers}")
    logger.debug(f"URL: {url}")
    return redirect(url)


def googleauth():
    """Step 1: User Authorization.
    Redirect the user/resource owner to the OAuth provider (i.e. Google)
    using an URL with a few key OAuth parameters.
    """
    google = OAuth2Session(GCP_CLIENT_ID, scope=GCP_SCOPE, redirect_uri=GCP_REDIRECT_URI)
    authorization_url, state = google.authorization_url(GCP_AUTHORIZATION_BASE_URL)

    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
    return redirect(authorization_url)


@app.route("/oauth2callback", methods=["GET"])
async def callback():
    google = OAuth2Session(GCP_CLIENT_ID, 
                           state=session['oauth_state'], 
                           redirect_uri=GCP_REDIRECT_URI)
    token = google.fetch_token(GCP_TOKEN_URL, client_secret=GCP_CLIENT_SECRET,
                               authorization_response=request.url)

    session['oauth_token'] = token
    session['user_id'] = request_user_id(token)
    save_google_auth_token(session['user_id'], token)
    session['openai_oauth_token'] = generate_random_token_for_user(session['user_id'])
    return redirect(url_for('oauth'))


def request_user_id(access_token=None):
    logger.debug(f"auth token: {str(session['oauth_token'])}")
    google = OAuth2Session(GCP_CLIENT_ID, token=access_token)
    full_response = google.get('https://www.googleapis.com/oauth2/v1/userinfo')

    logger.debug(f"User ID Response: {str(full_response.json())}")
    # Parse the response to get user ID or email
    user_id = full_response.json()["id"]
    return user_id


def _is_google_auth_needed():
    if 'user_id' not in session or 'oauth_token' not in session:
        return True

    # check if the token in session can fetch profile info since
    # token can be stail
    google = OAuth2Session(GCP_CLIENT_ID, token=session['oauth_token'])
    full_response = None
    try:
        full_response = google.get('https://www.googleapis.com/oauth2/v1/userinfo')
    except TokenExpiredError as e:
        logger.debug(str(e))
        return True
    
    # if status code is not successful, go to google auth
    if full_response.status_code != 200:
        return True
    
    return False
