import secrets
import os.path
from werkzeug.utils import secure_filename
from flask_dropzone import Dropzone 
from flask import Flask, request, render_template
from dotenv import load_dotenv 

load_dotenv()

app = Flask(__name__)
dropzone = Dropzone(app)
rootdir = os.path.abspath(os.path.dirname(__file__))
print(rootdir)
app.config["SECRET_KEY"] = str(secrets.SystemRandom().getrandbits(128))

app.config.update(
        UPLOAD_PATH=os.path.join(rootdir, f'{os.getenv("ROOT_DIRECTORY")}/'),
        DROPZONE_ALLOWED_FILE_TYPE=f'{os.getenv("DROPZONE_ALLOWED_FILE_TYPE")}',
        DROPZONE_UPLOAD_ON_CLICK=os.getenv("DROPZONE_UPLOAD_ON_CLICK"),
        DROPZONE_INPUT_NAME=f"{os.getenv('DROPZONE_INPUT_NAME')}",
        DROPZONE_UPLOAD_MULTIPLE=os.getenv("DROPZONE_UPLOAD_MULTIPLE"),
        DROPZONE_MAX_FILE_SIZE=int(os.getenv("DROPZONE_MAX_FILE_SIZE")),
)

@app.get("/")
def index():
    return render_template("index.html")

#TODO: create redirect for successful upload

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        for item in request.files:
            if item.startswith('RAWFILE'):
                f = request.files.get(item)
                print(secure_filename(f.filename))
                print(os.path.join(app.config['UPLOAD_PATH'], secure_filename(f.filename)))
                f.save(os.path.join(app.config['UPLOAD_PATH'], secure_filename(f.filename)))
    return render_template("upload.html")


