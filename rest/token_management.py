import secrets

from google.cloud import firestore
from google.oauth2 import service_account

json_path = "./auth-service-account.json"
credentials = service_account.Credentials.from_service_account_file(json_path)

db = firestore.Client(credentials=credentials, project='auth-404816')

def save_google_auth_token(user_id, token):
    doc_ref = db.collection(u'google_auth_tokens').document(user_id)
    doc_ref.set({
        u'google_auth_token': token
    })

def get_google_auth_token(user_id):
    doc_ref = db.collection(u'google_auth_tokens').document(user_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()["google_auth_token"]
    else:
        return None

def get_user_token(user_id):
    doc_ref = db.collection(u'tokens').document(user_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()["token"]
    else:
        return None
    
def generate_random_token_for_user(user_id):
    token = secrets.token_hex(8)
    doc_ref = db.collection(u'tokens').document(user_id)
    doc_ref.set({
        u'token': token
    })
    return token

def invalidate_token_for_user(user_id):
    doc_ref = db.collection(u'tokens').document(user_id)
    doc_ref.delete()

def verify_token(user_id, token):
    doc_ref = db.collection(u'tokens').document(user_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()["token"] == token
    else:
        return False

def get_user_id(token):
    doc_ref = db.collection(u'tokens').where(u'token', u'==', token)
    docs = doc_ref.stream()
    for doc in docs:
        return doc.id
    return None
