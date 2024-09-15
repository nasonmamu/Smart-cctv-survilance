import logging

logging.basicConfig(filename='admin_access.log', level=logging.INFO)

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    logging.info(f"User {current_user.username} accessed admin dashboard")
    return render_template('admin_dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            logging.info(f"User {username} logged in")
            return redirect(url_for('admin_dashboard'))
        else:
            logging.warning(f"Failed login attempt for user {username}")
    return render_template('login.html')
