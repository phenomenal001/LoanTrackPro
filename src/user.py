from app import db, User, app
from werkzeug.security import generate_password_hash

def create_user(username, password, role):
    hashed_password = generate_password_hash(password, method='sha256')
    new_user = User(username=username, password=hashed_password, role=role)
    db.session.add(new_user)
    db.session.commit()
    print(f'User {username} created with role {role}.')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure the tables are created

        # Create a supervisor
        create_user('supervisor1', 'password', 'supervisor')

        # Create subordinates
        create_user('subordinate1', 'password', 'subordinate')
        create_user('subordinate2', 'password', 'subordinate')