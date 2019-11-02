from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from wtforms import *
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
class signUp(Form):
    email = StringField('E-mail',
       [
        Length(min=6, message=(u'Little short for an email address?')),
        Email(message=('That\'s not a valid email address.')),
        DataRequired(message=('That\'s not a valid email address.'))
        ])
    name = StringField('Name',[DataRequired(message='Don\'t be shy!')])
    pword = PasswordField('Password',validators=
    [
    DataRequired(message=('This Field can not be left empty')),
    Length(min=8, message=('Your Password must have a minimum of 8 characters'))
    ])
    confirm_pword = PasswordField('Confirm Password',validators=
    [
    DataRequired(),
    EqualTo('pword', message=('Passwords must match'))
    ])
    def validate_email(self,email):
        user = db.session.query(Users).filter_by(email=email).first()
        if user != None:
            raise ValidationError('Email Address Is Already In Use.')
class Login(Form):
    email = StringField('E-mail',
        [
        Length(min=6, message=(u'Little short for an email address?')),
        Email(message=('That\'s not a valid email address.')),
        DataRequired(message=('That\'s not a valid email address.'))
        ])

    pword = PasswordField('Password',validators=
        [
        DataRequired(message=('This Field can not be left empty')),
        Length(min=1, message=('Your Password must have a minimum of 8 characters'))
        ])
def validate_number(min=-1,max=-1):
    message = 'Price may not be negative'
    def _validate_number(form,field):
        if field.data < 0:
            raise ValidationError(message)
    return _validate_number
    #create the form that we need too create products
class productForm(Form):
    title = StringField('Title',[validators.InputRequired(),validators.length(min=4,max=25)])
    imageurl = StringField('Image',[validators.InputRequired(),validators.length(min=4,max=250)])
    price = FloatField('Price',[validators.InputRequired(), validate_number(min=0) ])
    description = TextAreaField('Description')
