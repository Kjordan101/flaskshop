from flask import Flask, render_template,flash, redirect, url_for, session, request
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from wtforms import *
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base

app = Flask(__name__)
#initialize serializer
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
#get all the information we need from config
app.config.from_pyfile('config.cfg')
#initialize any other modules
mail = Mail(app)
db = SQLAlchemy(app)
fBcrypt = Bcrypt(app)

#Copy the data from existing database
Base = automap_base()
Base.prepare(db.engine, reflect=True)
Product = Base.classes.products_table
Users = Base.classes.users


'''
The point of this app is to emulate the functionality
of my nodejs ecommerce app
Here is my list of Todos:
-Add mysql (done)
-ADD PROPER DATABASE (done)
-Add all templates (done)
-Add sign up ability (done)
-Add users(done)
-Add login flow(done)
-Add Error Handling
-Add carts
-Add Orders
-Add all tables
-Add form validation
-Add security
'''

@app.route('/')
def homepage():
    path = '/'
    #Grabs everything from db schema
    results = db.session.query(Product).all()
    #send results through to the page to be used on it
    return render_template('index.html', results=results, path=path)

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
@app.route('/sign-up', methods=['GET','POST'])
def signUpPage():
    path='/sign-up'
    form = signUp(request.form)
    if request.method == 'POST' and form.validate():
        #Get information from form and save it in database
        email = form.email.data
        name = form.name.data
        pword = form.pword.data
        pw_hash = fBcrypt.generate_password_hash(pword,rounds=15).decode('utf-8')
        confirm_pword = form.confirm_pword.data
        new_user = Users(email=email, username=name, password=pw_hash, verified=0)
        #Send confirmation email to users
        token = s.dumps(email, salt='email-confirm')
        msg = Message('Confirm Email for Flask-Shop', sender='flaskshop5@gmail.com',recipients=[email])
        link = url_for('confirm_email',token=token, _external=True)
        msg.body = '<h1>Confirm your email address for flask shop</h1> <br> <p>Your link is {}</p>'.format(link)
        mail.send(msg)
        #Save changes to database
        db.session.add(new_user)
        db.session.commit()
        print(email,name)
        return redirect(url_for('homepage'))

    return render_template('sign-up.html',path=path,form=form)

@app.route('/confirm_email/<token>', methods=['GET','POST'])
def confirm_email(token):
    try:
        email = s.loads(token,salt='email-confirm', max_age=3600)

        cur_user = db.session.query(Users).filter_by(email=email).first()
        cur_user.verified = 1

        db.session.commit()
    except SignatureExpired:
        #add flash message here
        return render_template(url_for('homepage'))

    return render_template('auth/email_confirmed.html')
@app.route('/login', methods=['GET','POST'])
def loginPage():
    #Add error Handling for this form
    path='/login'
    form =Login(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        pword = form.pword.data
        cur_user = db.session.query(Users).filter_by(email=email).first() if db.session.query(Users).filter_by(email=email).first() != None else False
        if cur_user:
            #create session for the user
            session['loggedin'] = True
            session['id'] = cur_user.id
            session['username'] = email
            return redirect(url_for('homepage'))
        else:
            return redirect(url_for('productPage'))
    return render_template('login.html',path=path,form=form)

@app.route('/logout')
def logout():
    session.pop('loggedin',False)
    session.pop('id',None)
    session.pop('username',None)
    return redirect(url_for('homepage'))

@app.route('/products')
def productPage():
    path = '/products'

    results = db.session.query(Product).all()

    return render_template('product-list.html', results=results, path=path)

@app.route('/products/<prodId>')
def productDetail(prodId):
    path = '/products/itm'

    cur_prod = db.session.query(Product).filter_by(id=prodId).all()

    return render_template('product-detail.html',cur_prod=cur_prod,path=path)

@app.route('/cart', methods=['GET','POST'])
def cartPage():
    path = '/cart'
    if request.method == 'POST':
        product = request.form.getlist('productId')[0]

        return redirect(url_for('homepage'))

    return render_template('cart.html',path=path)

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

@app.route('/admin/add-product', methods=['GET','POST'])
def addProducts():
    path = '/admin/add-product'
    form = productForm(request.form)
    #add error handling
    if len(session) != 0:
        return render_template('edit-product.html',path=path,form=form)
    if len(session) != 0 and request.method == 'POST' and form.validate():
        # update = db.session.query(Product).filter()
        product = Product(title=form.title.data,imageurl=form.imageurl.data,price=form.price.data,description=form.description.data,userId=session['id'])
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('productPage'))
    return redirect(url_for('homepage'))

@app.route('/admin/edit-product/<productId>',methods=['GET','POST'])
def editProduct(productId):
    #Work on the security for this page
    path = '/admin/edit-product'
    form = productForm(request.form)
    if len(session) != 0 and request.method == 'POST':
        product = db.session.query(Product).filter_by(id=productId).filter_by(userId=session['id']).first()
        product.title = form.title.data
        product.imageurl = form.imageurl.data
        product.price = form.price.data
        product.description = form.description.data
        db.session.commit()
        return redirect(url_for('adminProducts'))
    return render_template('edit-product.html',path=path,form=form,productId=productId)
@app.route('/admin/products')
def adminProducts():
    path = '/admin/products'
    if len(session) != 0:
        results = db.session.query(Product).filter_by(userId=session['id']).all()

        return render_template('/admin/products.html',results=results,path=path)
    return redirect(url_for('homepage'))

if __name__ == '__main__':
    app.run(debug=True)
