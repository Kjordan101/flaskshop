from controller import app
from flask import Blueprint, render_template, flash, redirect, url_for, session, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base

mod = Blueprint('shop', __name__,template_folder="../../templates")

db = SQLAlchemy(app)
Base = automap_base()
Base.prepare(db.engine, reflect=True)
Product = Base.classes.products_table
Users = Base.classes.users

@mod.route('/')
def homepage():
    path = '/'

    results = db.session.query(Product).all()

    return render_template('index.html', results=results, path=path)

@mod.route('/products')
def productPage():
    path = '/products'

    results = db.session.query(Product).all()

    return render_template('product-list.html', results=results, path=path)

@mod.route('/products/<prodId>')
def productDetail(prodId):
    path = '/products/itm'

    cur_prod = db.session.query(Product).filter_by(id=prodId).all()

    return render_template('product-detail.html',cur_prod=cur_prod,path=path)

@mod.route('/cart', methods=['GET','POST'])
def cartPage():
    path = '/cart'
    if request.method == 'POST':
        product = request.form.getlist('productId')[0]

        return redirect(url_for('homepage'))

    return render_template('cart.html',path=path)
