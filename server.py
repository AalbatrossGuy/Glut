import secrets, time, os, math
import os.path
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, url_for,  send_from_directory, Blueprint
from dotenv import load_dotenv
from moviepy import VideoFileClip
import cv2
load_dotenv()

app = Flask(__name__)
rootdir = os.path.abspath(os.path.dirname(__file__))
print(rootdir)
app.config["SECRET_KEY"] = str(secrets.SystemRandom().getrandbits(128))
app.config["MAX_CONTENT_LENGTH"] = 800 * 1000 * 1000 # 800 MB limit
app.config["UPLOAD_PATH"] = os.getenv("UPLOAD_PATH")
storage_directory = Blueprint('storage_directory', __name__, url_prefix="/gallery", static_folder="GlutRoot")
app.register_blueprint(storage_directory)

def format_size(file_size):
    UNIT = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB") # Following the decimal system
    get_unit = int(math.floor(math.log(file_size, 1000)))
    p = math.pow(1000, get_unit)
    final_size = round(file_size / p, 2)
    return f"{final_size} {UNIT[get_unit]}"

def create_thumbnail(file) -> None:
    video = VideoFileClip(f"GlutRoot/{file}")
    filenoext = file.rsplit('.', 1)[0]
    get_frame = video.get_frame(3)
    cv2.imwrite(f"GlutRoot/thumbnails/{filenoext}.jpg", get_frame)

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
                file_extension = get_file.filename.rsplit('.', 1)[1].lower()
                print(f"STREAM = {get_file.stream}")
                start = time.time()
                with open(f"{os.getenv('ROOT_DIRECTORY')}/{get_file.filename}", 'wb') as file_binary:
                    for file_chunk in get_file.stream:
                        file_binary.write(file_chunk)
                end = time.time()
                if file_extension in ['mp4', 'mov']:
                    create_thumbnail(get_file.filename)
                print(f"TIME TAKEN = {end - start}s")
    return render_template("upload.html")


@app.route("/gallery", methods=["GET"])
def gallery():
    files = sorted(os.listdir(app.config['UPLOAD_PATH']))
    file_meta = []
    # print(files)
    for file in files:
        if file == "thumbnails":
            continue
        if file.rsplit('.', 1)[1].lower() in ['mp4', 'mov']:
            file_meta.append({
                'name': file,
                'path': url_for("storage_directory.static", filename=file),
                'ext': file.rsplit('.', 1)[1].lower(),
                'size': format_size(os.stat(f"GlutRoot/{file}").st_size),
                'thumbnail': url_for("storage_directory.static", filename=f"thumbnails/{file.rsplit('.', 1)[0]}.jpg"), 
            })
        else:
        # if not file.rsplit('.', 1)[1].lower() in ['mp4', 'mov']:
            file_meta.append({
                'name': file,
                'path': url_for("storage_directory.static", filename=file),
                'ext': file.rsplit('.', 1)[1].lower(),
                'size': format_size(os.stat(f"GlutRoot/{file}").st_size),
            })
    return render_template("gallery.html", files=file_meta)

def test():
    return 'SENDING FROM FUNC'

app.jinja_env.globals.update(test=test)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=4000)
