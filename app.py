from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)

# ---------------- MODELS ----------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Float)
    image = db.Column(db.String(200))

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    product_name = db.Column(db.String(100))
    price = db.Column(db.Float)

# ---------------- HOME ----------------

@app.route('/')
def home():
    products = Product.query.all()
    return render_template('index.html', products=products)

# ---------------- LOAD PRODUCTS ----------------

@app.route('/load-products')
def load_products():

    if Product.query.count() == 0:

        products = [
            Product(
                name="Laptop",
                price=50000,
                image="laptop.jpg"),
            Product(
                name="Phone",
                price=25000,
                image="phone.jpg"
                ),
            Product(
                name="Headphones",
                price=3000,
                image="headphones.jpg"
                ),
            Product(name="Keyboard",
                    price=1500,
                    image="keyboard.jpg"),
            Product(name="Mouse",
                    price=800,
                    image="mouse.jpg")]

        db.session.add_all(products)
        db.session.commit()

    return redirect('/')

# ---------------- REGISTER ----------------

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        existing = User.query.filter_by(username=username).first()

        if existing:
            return "User already exists"

        user = User(username=username, password=password)

        db.session.add(user)
        db.session.commit()

        return redirect('/login')

    return render_template('register.html')

# ---------------- LOGIN ----------------

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(
            username=username,
            password=password
        ).first()

        if user:
            session['username'] = username
            return redirect('/')

        return "Invalid Username or Password"

    return render_template('login.html')

# ---------------- LOGOUT ----------------

@app.route('/logout')
def logout():

    session.pop('username', None)

    return redirect('/')

# ---------------- ADD TO CART ----------------

@app.route('/add-to-cart/<int:id>')
def add_to_cart(id):

    if 'username' not in session:
        return redirect('/login')

    product = Product.query.get(id)

    item = Cart(
        username=session['username'],
        product_name=product.name,
        price=product.price
    )

    db.session.add(item)
    db.session.commit()

    return redirect('/cart')

# ---------------- CART ----------------

@app.route('/cart')
def cart():

    if 'username' not in session:
        return redirect('/login')

    items = Cart.query.filter_by(
        username=session['username']
    ).all()

    total = sum(item.price for item in items)

    return render_template(
        'cart.html',
        items=items,
        total=total
    )

# ---------------- CHECKOUT ----------------

@app.route('/checkout')
def checkout():

    if 'username' not in session:
        return redirect('/login')

    items = Cart.query.filter_by(
        username=session['username']
    ).all()

    total = sum(item.price for item in items)

    Cart.query.filter_by(
        username=session['username']
    ).delete()

    db.session.commit()

    return render_template(
        'checkout.html',
        total=total
    )

# ---------------- MAIN ----------------

if __name__ == '__main__':

    with app.app_context():
        db.create_all()

    app.run(debug=True)