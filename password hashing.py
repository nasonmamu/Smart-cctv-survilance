from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

def create_user(username, password):
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

def check_password(user, password):
    return bcrypt.check_password_hash(user.password, password)
