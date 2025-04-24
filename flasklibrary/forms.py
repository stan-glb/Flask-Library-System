from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SelectField,SubmitField,BooleanField,IntegerField,FileField,TextAreaField
from wtforms.validators import DataRequired,Length,Email,EqualTo,ValidationError,NumberRange,Optional
from flask_wtf.file import FileRequired,FileAllowed
from flasklibrary.models import User
from flasklibrary.models import AdminCode
from flask_login import current_user
from flask import current_app

class RegistrationForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(),Length(min=2,max=20)])
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',[DataRequired(),EqualTo('password')])
    role = SelectField('Role', choices=[('user', 'User'), ('admin', 'Admin')], validators=[DataRequired()])
    admin_code = StringField('Admin Code') 
    submit = SubmitField('Sign Up')

    def validate_username(self,username):
        user = User.query.filter_by(username= username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one')
    
    def validate_email(self,email):
        user = User.query.filter_by(email= email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one')
    

    # def validate_admin_code(self, admin_code):
    #     """
    #     Only validate the admin_code if the role selected is 'admin'.
    #     """
    #     try:
    #         if self.role.data == 'admin':
    #             if not admin_code.data:
    #                 raise ValidationError('Admin code is required to register as admin.')

    #             code_entry = AdminCode.query.filter_by(code=str(admin_code.data)).first()
    #             if not code_entry:
    #                 raise ValidationError('Invalid or expired admin code.')
    #         else:
    #             # Make sure to clear admin_code if not registering as admin
    #             self.admin_code.data = None
    #     except Exception as e:
    #         raise ValidationError('Error validating admin code. Please try again.')

    def validate_admin_code(self, admin_code):
        # Only run this validation if admin is selected
        if self.role.data == 'admin':
            if admin_code.data == "":
                raise ValidationError('Admin code is required to register as admin.')

            code_entry = AdminCode.query.filter_by(code=str(admin_code.data)).first()

            if not code_entry:
                raise ValidationError('Invalid or expired admin code.')
        else:
            # Wipe admin_code to avoid "user" accidentally submitting it
            self.admin_code.data = None
        

    # def validate(self, **kwargs):
    #     is_valid = super().validate(**kwargs)
    #     if not is_valid:
    #         return False

    #     # Restrict admin sign-up
    #     allowed_admins = current_app.config.get('ALLOWED_ADMIN_EMAILS', [])
    #     if self.role.data == 'admin' and self.email.data not in allowed_admins:
    #         self.role.errors.append('You are not authorized to register as an admin.')
    #         return False

    #     return True





class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    role = SelectField('Role', choices=[('user', 'User'), ('admin', 'Admin')], validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(),Length(min=2,max=20)])
    email = StringField('Email',validators=[DataRequired(),Email()])
    submit = SubmitField('Update')

    def validate_username(self,username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one')
    
    def validate_email(self,email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one')



class BookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=4)])
    pages = IntegerField('Pages', validators=[DataRequired(), NumberRange(min=1, message="Pages must be at least 1")])
    image = FileField('Upload Image')
    description = StringField('Description', validators=[DataRequired(), Length(min=10)])
    content = TextAreaField('Content', validators=[DataRequired(), Length(min=10)])
    submit = SubmitField('Create Book')

    def __init__(self, *args, **kwargs):
        self.is_update = kwargs.pop('is_update', False)
        super(BookForm, self).__init__(*args, **kwargs)

        if self.is_update:
            self.image.validators = [FileAllowed(['jpg', 'jpeg', 'png'], 'Image must be in jpg, jpeg or png format!')]
        else:
            self.image.validators = [
                FileRequired(message="Image is required!"),
                FileAllowed(['jpg', 'jpeg', 'png'], 'Image must be in jpg, jpeg or png format!')
            ]


