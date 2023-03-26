from flask import Flask, redirect, request, render_template, session
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key_here')

# OAuth client credentials
client_id = 'your_client_id'
client_secret = 'your_client_secret'
authorization_url = 'https://my_server.com/authorize'
token_url = 'https://my_server.com/token'
scope = ''

@app.route('/')
def index():
    return 'Hello, world!'

@app.route('/authorize')
def authorize():
    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client, scope=scope)
    authorization_url, state = oauth.authorization_url(authorization_url)

    # save the state somewhere for later use
    session['oauth_state'] = state

    return redirect(authorization_url)

@app.route('/oauth_callback')
def oauth_callback():
    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client, state=session['oauth_state'])
    token = oauth.fetch_token(
        token_url=token_url,
        client_secret=client_secret,
        authorization_response=request.url,
    )

    # save the access token somewhere for later use
    session['oauth_token'] = token

    return redirect('/protected_resource')

@app.route('/protected_resource')
def protected_resource():
    token = session['oauth_token']

    headers = {
        'Authorization': f'Bearer {token["access_token"]}',
    }
    response = requests.get('https://my_server.com/protected_resource', headers=headers)

    return response.text

if __name__ == '__main__':
    app.run()

