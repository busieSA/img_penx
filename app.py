#image file handling 
from io import BytesIO
import base64
#normal code
from flask import Flask, render_template,request, redirect, url_for,send_file, flash
from datetime import datetime
#import sqlachemy
from flask_sqlalchemy import SQLAlchemy
import calendar
#wtforms here 
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField
from wtforms.validators import data_required

app = Flask(__name__)

# Set the database URI for SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///example.db'
app.config["SECRET_KEY"] = "verycrypticsecretcodeher"
db = SQLAlchemy(app)

# Define a custom Jinja2 filter to base64-encode binary data
def b64encode(data):
    return base64.b64encode(data).decode('utf-8')

# Register the custom filter with Jinja2
app.jinja_env.filters['b64encode'] = b64encode

#wtForm form classes 
class NamerForm(FlaskForm):
    name = StringField("what's your name", validators=[data_required()])
    submit = SubmitField("Submit")

#User form 
class UserForm(FlaskForm):
    name = StringField("name",validators=[data_required()])
    email = EmailField("email",validators=[data_required()])
    submit = SubmitField("Submit")

# All sqlalchemy classes here

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)


class Images(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.LargeBinary, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)


with app.app_context():
    db.create_all()


#get time (date, year, month)
d = datetime.now()
year = d.year
date = d.date
month = d.month
dt = d.strftime("%Y-%m-%d %H:%M:%S")
# Generate the calendar for the current month
cal = calendar.monthcalendar(year, month)

'''
will remove some of these routes when done
'''

@app.route('/name', methods=['POST', 'GET'])
def name():
    name = None
    form = NamerForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data=''
        flash("Form Submit successful")

    return render_template('name.html',
                           title='name',
                           form=form,
                           name=name)

@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    return render_template("add_user.html")


@app.route('/')
def home():
    return render_template("index.html", title="home Page")

@app.route("/user/<name>")
def user(name):
    return render_template("user.html", title="user profile", user_name=name)

#custom Error pages 
#invalid URl
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", title="page not found"), 404

#internal server error URl
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html", title="page not found"), 500

#yexy takes yes went wrong 


@app.route('/upload')
def upload_image():
    return render_template('upload.html', title='upload your image')

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == "POST":
        # Retrieve the uploaded file from the form data
        #file = request.files['file']
        img_get = request.files
        image = img_get['image']
        data = image.read()
        if not data:
            return redirect(url_for('loop',error="You have to select an image"))
        # Read the binary data of the file

        # Create a new Image object and store it in the database
        image = Images(data=data)
        db.session.add(image)
        db.session.commit()

        # Redirect the user to a page that displays the uploaded image (, id=image.id)
        return redirect(url_for('loop'))
        

'''

@app.route('/image/<int:id>')
def view_image(id):
    # Retrieve the Image object from the database
    image = Images.query.filter_by(id=id).first()

    # Send the binary data of the image to the user's browser
    return send_file(BytesIO(image.data), mimetype='image/jpeg')
'''

@app.route("/loop")
def loop():
    images = Images.query.all()
    return render_template('view.html', title="view images", imgs=images)

@app.route('/image/<int:image_id>')
def get_image(image_id):
    image = Images.query.filter_by(id=image_id).first()
    if image is not None:
        return render_template('viewer.html', img=image)
        #return send_file(BytesIO(image.data), mimetype='image/png')
    else:
        return "Image not found"   

@app.route('/<int:id>/delete-image', methods=["GET", "POST"])
def delete_image(id):
    image = Images.query.filter_by(id=id).first()
    if request.method == "GET":
        if image:
            db.session.delete(image)
            db.session.commit()
            flash("message delete successfully", "info")
        return redirect(url_for('loop'))
    return redirect(url_for('loop'))