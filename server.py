import secrets
import os.path
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
rootdir = os.path.abspath(os.path.dirname(__file__))
print(rootdir)
app.config["SECRET_KEY"] = str(secrets.SystemRandom().getrandbits(128))

app.config.update(UPLOAD_PATH=os.path.join(rootdir, f'{os.getenv("ROOT_DIRECTORY")}/'))


@app.get("/")
def index():
    print("upload.html loaded")
    return render_template("index.html")

#TODO: create redirect for successful upload

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        for item in request.files:
            print(request.files)
            if item.startswith('myfiles'):
                f = request.files.get(item)
                print(secure_filename(f.filename))
                print(os.path.join(app.config['UPLOAD_PATH'], secure_filename(f.filename)))
                f.save(os.path.join(app.config['UPLOAD_PATH'], secure_filename(f.filename)))
    return render_template("upload.html")
