from flask import Flask, render_template, request, flash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import smtplib
import os

year = datetime.now().year
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "postgresql://postgres:tiger@localhost/detail")
#"postgresql://postgres:tiger@localhost/detail"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
db = SQLAlchemy(app)

# secret variables....
my_email = os.environ.get("MY_EMAIL")
password = os.environ.get("PASSWORD")


# send email using smtplib..
def send_email(msg, subject="Someone is in your website contact page."):
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=my_email, password=password)
        connection.sendmail(from_addr=my_email,
                            to_addrs=my_email,
                            msg=f"Subject:{subject}\n\n {msg}"
                            )


class Viewer(db.Model):
    __tablename__ = "viewer"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    message = db.Column(db.Text(), nullable=False)

    def __init__(self, name, email, message):
        self.name = name
        self.email = email
        self.message = message

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class Company(db.Model):
    __tablename__ = "company"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    ctc = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text(), nullable=False)

    def __init__(self, name, email, ctc, message):
        self.name = name
        self.email = email
        self.ctc = ctc
        self.message = message


# db.create_all()


@app.route("/")
def homepage():
    return render_template("index.html", year=year)


@app.route("/about")
def about():
    return render_template("about.html", year=year)


@app.route("/skills")
def skills():
    return render_template("skills.html", year=year)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    try:
        all_viewer = db.session.query(Viewer).all()
        emails = [i.to_dict()["email"] for i in all_viewer]
    except:
        emails = []

    try:
        if request.method == "POST":
            name = request.form["name"]
            email = request.form["email"]
            message = request.form["message"]

            if email in emails:
                flash("This email already exist.")

            elif name and email and message:
                flash("Your detail send successfully.")
                message_email = f"name: {name}\nemail: {email}\nmessage: {message}"
                send_email(message_email)
                new_viewer = Viewer(
                    name=name,
                    email=email,
                    message=message
                )
                db.session.add(new_viewer)
                db.session.commit()

            else:
                flash("Don't leave any boxes blank.")
    except:
        return render_template("contact.html", year=year)

    return render_template("contact.html", year=year)


@app.route("/hire_me", methods=["POST", "GET"])
def hire():
    try:
        if request.method == "POST":
            name = request.form["c-name"]
            email = request.form["c-email"]
            ctc = request.form["c-ctc"]
            message = request.form["c-message"]

            if name and email and message and ctc:
                flash("Your detail send successfully.")
                current_company = f"Company name: {name}\nCompany email: {email}\nCompany CTC: {ctc}\nCompany message: {message}"
                send_email(current_company, "Company want to hire you.")
                new_company = Company(
                    name=name,
                    email=email,
                    ctc=ctc,
                    message=message
                )
                db.session.add(new_company)
                db.session.commit()

            else:
                flash("Don't leave any boxes blank.")
    except:
        return render_template("hire.html", year=year)

    return render_template("hire.html", year=year)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)

