import secrets
from flask import Flask, flash, render_template, request, redirect, url_for
from flask_uploads import DOCUMENTS, IMAGES, UploadSet, configure_uploads

app = Flask(__name__)
apple = UploadSet("baloo", DOCUMENTS + IMAGES)
app.config["UPLOADED_BALOO_DEST"] = "static/"
app.config["SECRET_KEY"] = str(secrets.SystemRandom().getrandbits(128))
configure_uploads(app, apple)


@app.post("/upload")
def upload():
    if "filesave" in request.files:
        print('true')
        print(request.files["filesave"])
        apple.save(request.files["filesave"], name="foo.png")
        print('done')
        return redirect(url_for("index"))

@app.get("/")
def index():
    return render_template("upload.html")
