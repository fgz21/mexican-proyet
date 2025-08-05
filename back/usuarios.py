from flask import Blueprint, render_template, request, session, redirect, url_for

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

# ... (mantén tus datos y otras configuraciones igual)

@usuarios_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in usuarios and usuarios[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('usuarios.mostrar_usuarios'))
        return render_template('login.html', error='Credenciales incorrectas')
    return render_template('login.html')

@usuarios_bp.route('/')
def mostrar_usuarios():
    if 'username' not in session:
        return redirect(url_for('usuarios.login'))
    return render_template('usuarios.html', registros=registros)

@usuarios_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('usuarios.login'))