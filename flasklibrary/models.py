from flasklibrary import db,login_manager
from datetime import datetime,timedelta
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key= True)
    username = db.Column(db.String(20), unique= True,nullable=False)
    email = db.Column(db.String(120), unique= True,nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"User('{self.username}','{self.email}',{self.role})"
    

class Book(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    title =  db.Column(db.String(100), nullable=False)
    published_date = db.Column(db.DateTime, nullable = False, default = datetime.utcnow )
    pages = db.Column(db.Integer, nullable=False)
    isbn = db.Column(db.String(50), unique= True,nullable=False)
    description = db.Column(db.String(100),nullable=False)
    image_file = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable = False)

    def __repr__(self):
        return f"Book('{self.title}','{self.published_date}','{self.image_file}')"
    


class AdminCode(db.Model):
    code = db.Column(db.String(6),primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # def is_expired(self):
    #     return datetime.utcnow() > self.created_at + timedelta(minutes=5)