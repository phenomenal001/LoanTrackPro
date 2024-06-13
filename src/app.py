from flask import Flask, request, render_template, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
import urllib
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import check_password_hash
import geopy.distance
import geocoder


app = Flask(__name__)

# set up the connection to the MSSQL database
server = 'localhost'  # replace <server_name> with the name of your server
database = 'MerchantFeildData'  # replace <database_name> with the name of your database
username = 'root'  # replace <username> with your username
# password = 'admin@123'  # replace <password> with your password

db_uri = f"mysql+pymysql://{username}@{server}/{database}"

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'some_secret_key'

db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'supervisor' or 'subordinate'

class LoanAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(20), unique=True, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Not completed')  
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)


login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check your username and password.')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'supervisor':
        assigned = LoanAccount.query.join(User).add_columns(LoanAccount.account_number, User.username, LoanAccount.status).filter(LoanAccount.assigned_to.isnot(None)).filter(LoanAccount.assigned_to ==  User.id).all()
        unassigned = LoanAccount.query.filter_by(assigned_to=None).all()
        return render_template('supervisor.html', assigned=assigned, unassigned=unassigned)
    elif current_user.role == 'subordinate':
        assigned = LoanAccount.query.filter_by(assigned_to=current_user.id).all()
        return render_template('subordinate.html', assigned=assigned)
    return "Unauthorized", 403

@app.route('/mark_complete/<int:loan_id>', methods=['POST'])
@login_required
def mark_complete(loan_id):
    if current_user.role != 'subordinate':
        return "Unauthorized", 403
    
    loan = LoanAccount.query.get(loan_id)
    if loan.assigned_to != current_user.id:
        return "Unauthorized", 403
    
    # Dummy coordinates for the subordinate. Replace with actual coordinates retrieval.
    # user_latitude = request.form.get('latitude')
    # user_longitude = request.form.get('longitude')
    
    coordinates = get_current_gps_coordinates()

    if coordinates is not None:
        user_latitude, user_longitude = coordinates

    subordinate_coords = (user_latitude, user_longitude)
    loan_coords = (loan.latitude, loan.longitude)
    
    distance = geopy.distance.distance(subordinate_coords, loan_coords).meters
   
    if distance <= 500:
        loan.status = 'Completed'
        db.session.commit()
        flash('Loan account marked as completed.')
    else:
        flash('You are not within the geo limits.', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

def get_current_gps_coordinates():
    g = geocoder.ip('me')#this function is used to find the current information using our IP Add
    if g.latlng is not None: #g.latlng tells if the coordiates are found or not
        return g.latlng
    else:
        return None

if __name__ == '__main__':
    # import ipdb;ipdb.set_trace()
    with app.app_context():
        db.create_all()
    
    app.run(host='0.0.0.0', port=5000)


