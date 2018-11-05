try:
    import requests
    import pendulum
    import hashlib
    from config import public_key, private_key
    from flask import Flask, render_template, request
except ImportError as err:
    print(f"Failed to import required packages: {err}")

def get_character(public_key, private_key, name):
    # Generate timestamp required for Marvel API Authentication.
    now = pendulum.now('Europe/London')
    now = now.to_iso8601_string()

    # Generate hash required for Marvel API Authentication.
    m = hashlib.md5()
    m.update(now.encode('utf8'))
    m.update(private_key.encode('utf8'))
    m.update(public_key.encode('utf8'))

    endpoint = f"https://gateway.marvel.com:443/v1/public/characters?nameStartsWith={name}&limit=1"
    resp = requests.get(endpoint, params={"apikey": public_key, "ts": now, "hash": m.hexdigest()}).json()
    # Collect required data from resp.
    try:
        name = resp["data"]["results"][0]["name"]
        description = resp["data"]["results"][0]["description"]
        thumbnail = resp["data"]["results"][0]["thumbnail"]["path"]
        extension = resp["data"]["results"][0]["thumbnail"]["extension"]
        # Format URL for image from resp.
        thumbnail = f"{thumbnail}/landscape_incredible.{extension}"
        return {"name": name, "description": description, "thumbnail": thumbnail}
    except IndexError:
        return render_template("index.html")

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["search"]
        data = get_character(public_key, private_key, name)
        return render_template("index.html", data=data)
    
    return render_template("index.html")


if __name__ == '__main__':
   app.run()
