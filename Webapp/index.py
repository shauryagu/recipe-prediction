import os
from flask import Flask, flash, request, redirect, url_for, render_template
import subprocess
import io
import cv2
import requests
from PIL import Image
import json
from requests_toolbelt.multipart.encoder import MultipartEncoder
# from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './static'
ALLOWED_EXTENSIONS = set(['jpg'])

app = Flask(__name__)


# @app.route('/')
# def main():
#     return 'Image to Recipe classifier'


app.config['IMAGE_UPLOADS'] = UPLOAD_FOLDER


# @app.route('/', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         if 'file1' not in request.files:
#             return 'there is no file1 in form!'
#         file1 = request.files['file1']
#         path = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
#         file1.save(path)
#         return path

#         return 'ok'
#     return '''
#     <h1>Upload new File</h1>
#     <form method="post" enctype="multipart/form-data">
#       <input type="file" name="file1">
#       <input type="submit">
#     </form>
# '''

uploaded_list = []


@app.route("/")
def home():
    return render_template("index.html", imgs=uploaded_list)


@app.route('/upload-image', methods=['GET', 'POST'])
def upload_image():
    if request.method == "POST":
        if request.files:
            image = request.files["image"]
            image.save(os.path.join(
                app.config["IMAGE_UPLOADS"], image.filename))
            # return render_template("upload_image.html", uploaded_image=image.filename)
            uploaded_list.append(image.filename)
            return redirect(url_for('home'))
    return redirect(url_for('home'))


@app.route("/classify-images", methods=["GET", "POST"])
def classify():
    preds = []
    if (request.method == "POST"):
        for img_name in uploaded_list:
            img = cv2.imread(f"./static/{img_name}")
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            pil = Image.fromarray(img)
            buffer = io.BytesIO()
            pil.save(buffer, quality=100, format="JPEG")

            m = MultipartEncoder(
                fields={'file': ("imageToUpload", buffer.getvalue(), "image/jpeg")})

            response = requests.post("https://classify.roboflow.com/442-final-project-ynitf/1?api_key=AGC9DRPf7W0CEHss8hsi",
                                     data=m, headers={'Content-Type': m.content_type})

            out = response.json()

            if ("predicted_classes" in out and len(out["predicted_classes"]) > 0):
                pred = out["predicted_classes"][0]
                preds.append(pred)

    if (len(preds) > 0):
        ingredients = ""
        ingredients += preds[0]

        for i in range(1, len(preds)):
            ingredients += ",+" + preds[i]

        url = f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={ingredients}&rank=1&number=20&apiKey=60fd27b254064992854b2563fca05d52"

        r = requests.get(url)

        data = json.loads(r.text)

        recipes = []

        for i in data[:5]:
            recipes.append(i)

        # output = subprocess.check_output(
        #     f'base64 static/{img_name} | curl - d @- "https://classify.roboflow.com/442-final-project-ynitf/1?api_key=AGC9DRPf7W0CEHss8hsi"')
        # print(output)
    return render_template("index.html", predictions=preds, recipes=recipes)


# @app.route('/uploads/<filename>')
# def send_uploaded_file(filename=''):
#     from flask import send_from_directory
#     return send_from_directory(app.config["IMAGE_UPLOADS"], filename)


# if __name__ == "__main__":
#     app.run()
