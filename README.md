# Jessica GPT Based Personal Assistent

Jessica (Jess) is a GPT based personal assitent that have access to:

* your Google Calendar
* long term memory
* current day/time

# Usage Prep

To use it you have to provide following things in the ```.env``` file:
```
TELEGRAM_TOKEN=...
TELEGRAM_CHAT_ID=...
OPENAI_API_KEY=...
USER_ID=...
PINECONE_KEY=...
```
USER_ID used for pinecone DB and can be random string.

and file creds.json which should be your personal credentials for access Google, can be obtained by:
```
 GCP_PROJECT_WITH_API_ENABLED=...
 gcloud auth application-default login --scopes="https://www.googleapis.com/auth/calendar,https://www.googleapis.com/auth/cloud-platform"
 gcloud auth application-default set-quota-project $GCP_PROJECT_WITH_API_ENABLED
```

test:
```
pip3 install -r ./requirements.txt 
python3 ./telegram_bot.py 
```

Deploy as docker:
```
./deploy.sh 
```