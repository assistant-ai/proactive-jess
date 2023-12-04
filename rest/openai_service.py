from rest.main_app import app

from quart import request, send_file, Response


@app.get("/legal")
async def legal():
    with open("legal") as f:
        text = f.read()
        return Response(text, mimetype="text/yaml")
    

@app.get("/.well-known/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        # This is a trick we do to populate the PLUGIN_HOSTNAME constant in the OpenAPI spec
        text = text.replace("PLUGIN_HOSTNAME", f"https://{host}")
        return Response(text, mimetype="text/yaml")