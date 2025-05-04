import secrets
import os.path
from werkzeug.utils import secure_filename
# from flask import Flask, flash, render_template, request, redirect, url_for
# from flask_uploads import DOCUMENTS, IMAGES, UploadSet, configure_uploads
#
# app = Flask(__name__)
# apple = UploadSet("baloo", DOCUMENTS + IMAGES)
# app.config["UPLOADED_BALOO_DEST"] = "static/images/"

# configure_uploads(app, apple)
#
#
# @app.post("/upload")
# def upload():
#     if "filesave" in request.files:
#         print('true')
#         print(request.files["filesave"])
#         apple.save(request.files["filesave"], name="foo.png")
#         print('done')
#         return redirect(url_for("index"))
#
# @app.get("/")
# def index():
#     return render_template("index.html")

from flask_dropzone import Dropzone 
from flask import Flask, request, render_template
app = Flask(__name__)
dropzone = Dropzone(app)
rootdir = os.path.abspath(os.path.dirname(__file__))
print(rootdir)
app.config["SECRET_KEY"] = str(secrets.SystemRandom().getrandbits(128))

app.config.update(
        UPLOAD_PATH=os.path.join(rootdir, 'uploade/'),
        DROPZONE_ALLOWED_FILE_TYPE='image',
        # DROPZONE_UPLOAD_ON_CLICK=True,
        DROPZONE_INPUT_NAME="testfile"
        )

@app.get("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        for key, f in request.files.items():
            if key.startswith('testfile'):
                f = request.files.get('testfile')
                f.save(os.path.join(app.config['UPLOAD_PATH'], secure_filename(f.filename)))
    return render_template("upload.html")

