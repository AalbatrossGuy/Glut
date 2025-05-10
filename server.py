import secrets, time
import os.path
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, url_for,  send_from_directory, Blueprint
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
rootdir = os.path.abspath(os.path.dirname(__file__))
print(rootdir)
app.config["SECRET_KEY"] = str(secrets.SystemRandom().getrandbits(128))
app.config["MAX_CONTENT_LENGTH"] = 800 * 1000 * 1000 # 512 MB limit
# app.config.update(UPLOAD_PATH=os.path.join(rootdir, f'{os.getenv("ROOT_DIRECTORY")}/'))
app.config["UPLOAD_PATH"] = os.getenv("UPLOAD_PATH")
storage_directory = Blueprint('storage_directory', __name__, url_prefix="/gallery", static_folder="GlutRoot")
app.register_blueprint(storage_directory)

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
                start = time.time()
                with open(f"{os.getenv('ROOT_DIRECTORY')}/{get_file.filename}", 'wb') as file_binary:
                    for file_chunk in get_file.stream:
                        # print(f"CHUNK = {file_chunk}\n")
                        file_binary.write(file_chunk)
                end = time.time()
                print(f"TIME TAKEN = {end - start}s")
    return render_template("upload.html")


@app.route("/gallery", methods=["GET"])
def gallery():
    files = sorted(os.listdir(app.config['UPLOAD_PATH']))
    file_meta = []
    print(files)
    for file in files:
        file_meta.append({
            'name': file,
            'path': url_for("storage_directory.static", filename=file),
            'ext': file.rsplit('.', 1)[1].lower()
        })
        print(file_meta)
    return render_template("gallery.html", files=file_meta)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=4000)
