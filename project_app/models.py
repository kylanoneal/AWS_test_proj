from database import db
import datetime


class Summary(db.Model):
    id = db.Column("id", db.Integer, primary_key=True, autoincrement=True)
    title = db.Column("title", db.String(200))
    text = db.Column("text", db.String(500)) #currently limiting input text to 500 characters
    best_summary = db.Column("best_summary", db.String(500))
    #user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False) placeholder for when users are implemented

    def __init__(self, title, text, best_summary): #add user_id as a parameter when users are implemented
        self.title = title
        self.text = text
        self.best_summary = best_summary
        #self.user_id = user_id


'''class User(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    first_name = db.Column("first_name", db.String(100))
    last_name = db.Column("last_name", db.String(100))
    email = db.Column("email", db.String(100))
    password = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    sorting_order = db.Column("order", db.Boolean)
    #summaries = db.relationship("Summary", backref="user", lazy=True)

    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.registered_on = datetime.date.today()
        self.sorting_order = False'''