from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, MultipleFileField
from wtforms import StringField, PasswordField, SelectField, FloatField, DateField, TextAreaField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, ValidationError
from models import User, Policy
from datetime import date

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('user', 'User'), ('agent', 'Insurance Agent')], default='user')
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please choose a different one.')

class PolicyForm(FlaskForm):
    policy_number = StringField('Policy Number', validators=[DataRequired(), Length(min=5, max=50)])
    policy_type = SelectField('Policy Type', 
                             choices=[('health', 'Health Insurance'), 
                                    ('vehicle', 'Vehicle Insurance'), 
                                    ('life', 'Life Insurance'), 
                                    ('home', 'Home Insurance')],
                             validators=[DataRequired()])
    provider_name = StringField('Insurance Provider', validators=[DataRequired(), Length(min=2, max=100)])
    provider_contact = StringField('Provider Contact', validators=[Length(max=100)])
    premium_amount = FloatField('Premium Amount', validators=[DataRequired(), NumberRange(min=0)])
    coverage_amount = FloatField('Coverage Amount', validators=[DataRequired(), NumberRange(min=0)])
    issue_date = DateField('Issue Date', validators=[DataRequired()])
    expiry_date = DateField('Expiry Date', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Save Policy')

    def validate_policy_number(self, policy_number):
        policy = Policy.query.filter_by(policy_number=policy_number.data).first()
        if policy and (not hasattr(self, 'policy_id') or policy.id != self.policy_id):
            raise ValidationError('Policy number already exists. Please choose a different one.')

    def validate_expiry_date(self, expiry_date):
        if expiry_date.data <= self.issue_date.data:
            raise ValidationError('Expiry date must be after issue date.')

class ClaimForm(FlaskForm):
    claim_number = StringField('Claim Number', validators=[DataRequired(), Length(min=5, max=50)])
    policy_id = SelectField('Policy', validators=[DataRequired()], coerce=int)
    claim_amount = FloatField('Claim Amount', validators=[DataRequired(), NumberRange(min=0)])
    incident_date = DateField('Incident Date', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10)])
    documents = MultipleFileField('Upload Documents', 
                                 validators=[FileAllowed(['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'], 
                                           'Only PDF, image and document files allowed!')])
    submit = SubmitField('Submit Claim')

    def validate_incident_date(self, incident_date):
        if incident_date.data > date.today():
            raise ValidationError('Incident date cannot be in the future.')

class ClaimUpdateForm(FlaskForm):
    status = SelectField('Status', 
                        choices=[('pending', 'Pending'), 
                               ('processing', 'Processing'), 
                               ('approved', 'Approved'), 
                               ('rejected', 'Rejected')],
                        validators=[DataRequired()])
    remarks = TextAreaField('Remarks')
    submit = SubmitField('Update Claim')

class UserManagementForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    role = SelectField('Role', choices=[('user', 'User'), ('agent', 'Insurance Agent'), ('admin', 'Admin')])
    is_active = BooleanField('Active')
    submit = SubmitField('Update User')
