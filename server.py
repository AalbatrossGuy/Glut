import secrets, time, os, math, json
import os.path
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, url_for,  send_from_directory, Blueprint, session, redirect
import flask_login as user_handler
from flask_login import LoginManager, UserMixin, current_user
from dotenv import load_dotenv
from moviepy import VideoFileClip
import cv2
load_dotenv()

app = Flask(__name__)
login_handler = LoginManager()
rootdir = os.path.abspath(os.path.dirname(__file__))
print(rootdir)
app.config["SECRET_KEY"] = str(secrets.SystemRandom().getrandbits(128))
app.config["MAX_CONTENT_LENGTH"] = 800 * 1000 * 1000 # 800 MB limit
app.config["UPLOAD_PATH"] = os.getenv("ROOT_DIRECTORY")
app.config["SESSION_PERMANENT"] = False
storage_directory = Blueprint('storage_directory', __name__, url_prefix="/gallery", static_folder=f"{os.getenv('ROOT_DIRECTORY')}")
app.register_blueprint(storage_directory)
login_handler.init_app(app)

user_list = {}
with open('users.json') as get_users:
    user_list = json.load(get_users)

class User(UserMixin):
    pass 

@login_handler.user_loader 
def user_loader(user_name):
    if user_name not in user_list:
        return

    user = User()
    user.id = user_name
    return user

@login_handler.request_loader
def request_loader(http_request):
    user_name = http_request.form.get('username')
    if user_name not in user_list:
        return

    user = User()
    user.id = user_name
    user.is_authenticated = http_request.form['password'] == user_list[user_name]
    return user

def format_size(file_size):
    UNIT = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB") # Following the decimal system
    get_unit = int(math.floor(math.log(file_size, 1000)))
    p = math.pow(1000, get_unit)
    final_size = round(file_size / p, 2)
    return f"{final_size} {UNIT[get_unit]}"

def create_thumbnail(file) -> None:
    video = VideoFileClip(f"{os.getenv('ROOT_DIRECTORY')}/{current_user.id}/{file}")
    filenoext = file.rsplit('.', 1)[0]
    get_frame = video.get_frame(3)
    cv2.imwrite(f"{os.getenv('ROOT_DIRECTORY')}/{os.getenv('THUMBNAILS')}/{filenoext}.jpg", get_frame)

@app.get("/")
def index():
    print("upload.html loaded")
    return render_template("index.html")

#TODO: create redirect for successful upload
@app.route("/upload", methods=["GET", "POST"])
@user_handler.login_required
def upload():
    user = current_user.id
    if request.method =="POST":
        for file in request.files:
            print(f"request.files = {request.files}")
            if file.startswith('myfile'):
                get_file = request.files.get(file)
                file_extension = get_file.filename.rsplit('.', 1)[1].lower()
                print(f"STREAM = {get_file.stream}")
                start = time.time()
                with open(f"{os.getenv('ROOT_DIRECTORY')}/{user}/{get_file.filename}", 'wb') as file_binary:
                    for file_chunk in get_file.stream:
                        file_binary.write(file_chunk)
                end = time.time()
                if file_extension in ['mp4', 'mov']:
                    create_thumbnail(get_file.filename)
                print(f"TIME TAKEN = {end - start}s")
    return render_template("upload.html")



@app.route("/gallery", methods=["GET"])
@user_handler.login_required
def gallery():
    user = current_user.id
    files = sorted(os.listdir(f"{app.config['UPLOAD_PATH']}/{user}"))
    file_meta = []
    # print(files)
    for file in files:
        if file == "thumbnails":
            continue
        if file.rsplit('.', 1)[1].lower() in ['mp4', 'mov']:
            file_meta.append({
                'name': file,
                'path': url_for("storage_directory.static", filename=f"{user}/{file}"),
                'ext': file.rsplit('.', 1)[1].lower(),
                'size': format_size(os.stat(f"{os.getenv('ROOT_DIRECTORY')}/{user}/{file}").st_size),
                'thumbnail': url_for("storage_directory.static", filename=f"{os.getenv('THUMBNAILS')}/{file.rsplit('.', 1)[0]}.jpg"), 
            })
        else:
        # if not file.rsplit('.', 1)[1].lower() in ['mp4', 'mov']:
            file_meta.append({
                'name': file,
                'path': url_for("storage_directory.static", filename=f"{user}/{file}"),
                'ext': file.rsplit('.', 1)[1].lower(),
                'size': format_size(os.stat(f"{os.getenv('ROOT_DIRECTORY')}/{user}/{file}").st_size),
            })
    return render_template("gallery.html", files=file_meta)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        user_name = request.form.get('username')
        if request.form.get('password') == user_list[user_name]:
            user = User()
            user.id = user_name
            user_handler.login_user(user)
            return redirect(url_for('index'))
        return render_template("login.html")


@app.route("/logout")
def logout():
    user_handler.logout_user()
    return redirect(url_for('index'))

# def test():
#     return 'SENDING FROM FUNC'
#
# app.jinja_env.globals.update(test=test)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=4000)
