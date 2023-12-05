from rest.main_app import app
from rest import auth_service, openai_service
from extensions import memory_extension
from extensions.alpaca import account, shares


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)