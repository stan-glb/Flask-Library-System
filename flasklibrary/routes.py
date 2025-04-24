from flask import render_template,url_for,flash,redirect,request,current_app,abort
from flasklibrary import app,db,bcrypt
from werkzeug.utils import secure_filename
from functools import wraps
import os
from datetime import datetime,timedelta
import secrets
from sqlalchemy import text
import random
from sqlalchemy import or_
from PIL import Image
import uuid
from flasklibrary.models import User,Book,AdminCode
from flasklibrary.forms import RegistrationForm,LoginForm,BookForm,UpdateAccountForm
from flask_login import login_user,current_user,logout_user,login_required


# -------------------- Task: Generate Code & Cleanup -------------------- #
def generate_and_cleanup_code():
    with app.app_context():
        try:
            code = f"{random.randint(100000, 999999)}"
            new_code = AdminCode(code=code)
            db.session.add(new_code)

            expiration_cutoff = datetime.utcnow() - timedelta(seconds=60)
            expired_codes = AdminCode.query.filter(AdminCode.created_at < expiration_cutoff).all()
            for c in expired_codes:
                db.session.delete(c)

            db.session.commit()
        except Exception as e:
           print(f"[Scheduler ERROR] {e}")





# Function To restrict access to certain pages based on a user's role

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != required_role:
                flash("You don't have access to this page as a User!","warning")
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route("/")
@app.route("/home")
def home():
    search_query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)

    if search_query:
        books_query = Book.query.filter(
            or_(
                Book.title.ilike(f'%{search_query}%'),
                Book.description.ilike(f'%{search_query}%'),
                Book.isbn.ilike(f'%{search_query}%'),
                Book.content.ilike(f'%{search_query}%')
            )
        ).order_by(Book.published_date.desc())

        books = books_query.paginate(page=page, per_page=10)

        if not books.items:
            flash(f"No results found for '{search_query}'.", 'warning')
    else:
        books = Book.query.order_by(Book.published_date.desc()).paginate(page=page, per_page=10)

    return render_template('home.html', books=books)

# Function to create admin if User table is Empty


def create_default_admin():
    if User.query.count() == 0:
        pwd = "admin123"
        hashed_password = bcrypt.generate_password_hash(pwd).decode('utf-8')
        default_admin = User(
            username="admin",
            email="admin@demo.com",
            password=hashed_password,
            role="admin"
        )
        db.session.add(default_admin)
        db.session.commit()

    



@app.route("/register", methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,email= form.email.data,password=hashed_password,role=form.role.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been create! You are now able to log in','success')
        return redirect(url_for('login'))
    return render_template('register.html',title='Register',form=form)

# @app.route("/register", methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for('home'))

#     form = RegistrationForm()

#     if form.validate_on_submit():
#         # ✅ Do admin code check here
#         if form.role.data == 'admin':
#             if not form.admin_code.data:
#                 flash('Admin code is required to register as admin.', 'danger')
#                 return render_template('register.html', title='Register', form=form)

#             code_entry = AdminCode.query.filter_by(code=str(form.admin_code.data)).first()
#             if not code_entry:
#                 flash('Invalid or expired admin code.', 'danger')
#                 return render_template('register.html', title='Register', form=form)

#         hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
#         user = User(username=form.username.data,
#                     email=form.email.data,
#                     password=hashed_password,
#                     role=form.role.data)
#         db.session.add(user)
#         db.session.commit()
#         flash('Your account has been created! You are now able to log in', 'success')
#         return redirect(url_for('login'))

#     return render_template('register.html', title='Register', form=form)


@app.route("/login",methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data,role=form.role.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user,remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful.email,role or password is incorrect/invalid!', 'danger')
    return render_template('login.html',title='Login',form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account",methods=['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()
    
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        
    return render_template('account.html',title='Account',form=form)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    f_ext = os.path.splitext(secure_filename(form_picture.filename))[1]
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path,'static/profile_pics',picture_fn)
    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/create-book", methods=['GET', 'POST'])
@login_required
@role_required('admin')
def create_book():
    form = BookForm(is_update=False)  # creation mode

    if form.validate_on_submit():
        picture_file = save_picture(form.image.data)

        isbn = str(uuid.uuid4()).replace('-', '')[:13]  # generate unique ISBN

        new_book = Book(
            title=form.title.data,
            pages=form.pages.data,
            image_file=picture_file,
            description=form.description.data,
            content=form.content.data,
            isbn=isbn
        )

        db.session.add(new_book)
        db.session.commit()
        flash('Book added successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('create_book.html', title='Create Book', form=form, legend='Create Book', is_editing=True)




@app.route("/book/<int:book_id>")
@login_required
def read_book(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('read_book.html',book=book)


@app.route("/book/<int:book_id>/update", methods=['GET', 'POST'])
@login_required
@role_required('admin')
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    form = BookForm(is_update=True)  # update mode

    if form.validate_on_submit():
        book.title = form.title.data
        book.pages = form.pages.data
        book.description = form.description.data
        book.content = form.content.data

        # Save new image only if uploaded
        if form.image.data and form.image.data.filename != '':
            picture_file = save_picture(form.image.data)
            book.image_file = picture_file

        db.session.commit()
        flash('Book has been updated successfully!', 'success')
        return redirect(url_for('home'))

    elif request.method == 'GET':
        # Populate form with current book data
        form.title.data = book.title
        form.pages.data = book.pages
        form.description.data = book.description
        form.content.data = book.content

    return render_template('update_book.html', title='Update Book', form=form, legend='Update Book', book=book)

    
@app.route("/book/<int:book_id>/delete",methods=['POST'])
@login_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('Book has been deleted successfully!', 'success')
    return redirect(url_for('home'))



@app.route("/getcode")
@login_required
@role_required('admin')
def get_code():
    code = AdminCode.query.first()
    flash('Code successfully generated!', 'success')
    return render_template('gen_code.html',code=code)


