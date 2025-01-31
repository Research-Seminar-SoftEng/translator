from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import DataRequired, Length
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO, emit
import cv2
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier
import numpy as np
import base64
import math

# for model
detector = HandDetector(maxHands=1)
classifier = Classifier("/Users/USER/desktop/researchSeminar/Models/keras_model.h5", "/Users/USER/desktop/researchSeminar/Models/labels.txt")
offset = 20
imgSize = 300
labels = ["Hello", "Thank You", "I Love You", "Yes", "Okay", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]



db = SQLAlchemy()
app = Flask(__name__)
socketio = SocketIO(app)

app.config['SECRET_KEY'] = "my-secrets"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///video-meeting.db"

# Initialize Bcrypt
bcrypt = Bcrypt(app)
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return Register.query.get(int(user_id))


class Register(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def is_active(self):
        return True

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return True


with app.app_context():
    db.create_all()


class RegistrationForm(FlaskForm):
    email = EmailField(label='Email', validators=[DataRequired()])
    first_name = StringField(label="First Name", validators=[DataRequired()])
    last_name = StringField(label="Last Name", validators=[DataRequired()])
    username = StringField(label="Username", validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField(label="Password", validators=[DataRequired(), Length(min=8, max=20)])


class LoginForm(FlaskForm):
    email = EmailField(label='Email', validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])


@app.route("/")
def home():
    return render_template('landingpage.html')




@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = Register.query.filter_by(email=email).first()

        if user:
            # Check if the hashed password matches the entered password
            if bcrypt.check_password_hash(user.password, password):  # Use Bcrypt's check
                login_user(user)
                return jsonify({"success": True})  # Redirect to dashboard
            else:
                # If password is incorrect
                return jsonify({
                    "success": False,
                    "errors": {
                        "password": "Invalid password"
                    }
                })
        else:
            # If user with the email doesn't exist
            return jsonify({
                "success": False,
                "errors": {
                    "email": "Invalid email"
                }
            })

    return render_template("login.html", form=form)





@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully!", "info")
    return redirect(url_for("login"))



@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegistrationForm()

    if request.method == "POST":
        if not form.validate_on_submit():
            errors = {field: ", ".join(messages) for field, messages in form.errors.items()}
            return jsonify({"success": False, "errors": errors})  # Return errors in JSON

        # Check if email or username already exists
        email_exists = Register.query.filter_by(email=form.email.data).first()
        username_exists = Register.query.filter_by(username=form.username.data).first()

        errors = {}
        if email_exists:
            errors["email"] = "Email already taken."
        if username_exists:
            errors["username"] = "Username already taken."

        if errors:
            return jsonify({"success": False, "errors": errors})  # Return errors in JSON

        # Hash password before storing in DB using Bcrypt's generate_password_hash
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        new_user = Register(
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            username=form.username.data,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully! You can now log in.", "success")

        return jsonify({"success": True, "redirect": url_for("login")})  # Return redirect URL

    return render_template("register.html", form=form)



@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", first_name=current_user.first_name, last_name=current_user.last_name)


@app.route("/meeting")
@login_required
def meeting():
    return render_template("meeting.html", username=current_user.username)


@app.route("/join", methods=["GET", "POST"])
@login_required
def join():
    if request.method == "POST":
        room_id = request.form.get("roomID")
        return redirect(f"/meeting?roomID={room_id}")

    return render_template("join.html")


@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    frame_data = data['frame']
    nparr = np.fromstring(base64.b64decode(frame_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    hands, img = detector.findHands(img)
    if hands:
        hand = hands[0]
        x, y, w, h = hand['bbox']
        imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255
        imgCrop = img[y - offset:y + h + offset, x - offset:x + w + offset]
        aspectRatio = h / w

        if aspectRatio > 1:
            k = imgSize / h
            wCal = math.ceil(k * w)
            imgResize = cv2.resize(imgCrop, (wCal, imgSize))
            wGap = math.ceil((imgSize - wCal) / 2)
            imgWhite[:, wGap: wCal + wGap] = imgResize
        else:
            k = imgSize / w
            hCal = math.ceil(k * h)
            imgResize = cv2.resize(imgCrop, (imgSize, hCal))
            hGap = math.ceil((imgSize - hCal) / 2)
            imgWhite[hGap: hCal + hGap, :] = imgResize

        prediction, index = classifier.getPrediction(imgWhite, draw=False)
        interpretation = labels[index]
        emit('interpretation', {'interpretation': interpretation}, broadcast=True, namespace='/')  # Broadcast interpretation to all clients
    else:
        interpretation = "No hands detected"

    return jsonify({'interpretation': interpretation})


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000)