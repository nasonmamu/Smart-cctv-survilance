from flask_login import current_user

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('login'))
    return render_template('admin_dashboard.html')
