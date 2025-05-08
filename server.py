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
app.config["MAX_CONTENT_LENGTH"] = 512 * 1000 * 1000 # 512 MB limit
# app.config.update(UPLOAD_PATH=os.path.join(rootdir, f'{os.getenv("ROOT_DIRECTORY")}/'))


@app.get("/")
def index():
    print("upload.html loaded")
    return render_template("index.html")

#TODO: create redirect for successful upload

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method =="POST":
        for file in request.files:
            print(f"request.files = {request.files}")
            if file.startswith('myfile'):
                get_file = request.files.get(file)
                print(f"file = {get_file}")
                print(get_file.filename)
                print(f"STREAM = {get_file.stream}")
                with open(f"{os.getenv('ROOT_DIRECTORY')}/{get_file.filename}", 'wb') as file_binary:
                    for file_chunk in get_file.stream:
                        print(f"CHUNK = {file_chunk}\n")
                        file_binary.write(file_chunk)
    return render_template("upload.html")


@app.route("/gallery", methods=["GET"])
def gallery():
    files = sorted(os.listdir(app.config['UPLOAD_PATH']))
    print(files)
    return render_template("gallery.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=4000)
