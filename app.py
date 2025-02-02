from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

app = Flask(tuple)

# Configure upload folder and database
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///outfits.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

USER_NAME = "Alex"  # Replace with dynamic user login in the future

class Outfit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_filename = db.Column(db.String(100), nullable=False)
    matching_items = db.Column(db.String(200))

with app.app_context():
    db.create_all()

# Intro Page
@app.route("/")
def intro():
    return render_template("intro.html")

# Welcome Page
@app.route("/welcome")
def welcome():
    return render_template("welcome.html", name=USER_NAME)

# Main Home Page
@app.route("/home", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        if "file" not in request.files:
            return "No file part"

        file = request.files["file"]
        if file.filename == "":
            return "No selected file"

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            matching_items = "Red shoes, Gold earrings, Black hijab"  # Temporary placeholder

            new_outfit = Outfit(image_filename=filename, matching_items=matching_items)
            db.session.add(new_outfit)
            db.session.commit()

            return redirect(url_for("home"))

    outfits = Outfit.query.all()
    return render_template("home.html", name=USER_NAME, outfits=outfits)

if __name__ == "_main_":
    app.run(debug=True)