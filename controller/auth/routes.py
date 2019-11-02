from Flask import Blueprint
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

mod = Blueprint('auth', __name__)
s = URLSafeTimedSerializer(mod.config['SECRET_KEY'])
#get all the information we need from config
app.config.from_pyfile('config.cfg')
#initialize any other modules
mail = Mail(app)
fBcrypt = Bcrypt(app)


@mod.route('/sign-up', methods=['GET','POST'])
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
@mod.route('/confirm_email/<token>', methods=['GET','POST'])
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
