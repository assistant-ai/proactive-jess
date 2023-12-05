from google.cloud import firestore


def get_user_data(user_id):
    print("Getting user data for user ID: " + user_id)
    # Initialize Firestore client
    db = firestore.Client(project='jess-backend')

    # Fetch user credentials from Firestore
    # Assuming the collection name is 'default'
    user_ref = db.collection('default').document(user_id)
    user_doc = user_ref.get()
    if user_doc.exists:
        return user_doc.to_dict()
    else:
        raise ValueError("User ID not found in Firestore")
