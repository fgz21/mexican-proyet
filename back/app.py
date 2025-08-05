from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__,
            template_folder='../front/templates',
            static_folder='../front/static')
app.secret_key = 'tu_clave_secreta_aqui'

# Datos de usuarios
user_db = {
    'admin': {'password': 'admin123', 'nombre': 'Administrador', 'rol': 'admin'}
}

# Datos de registros (vacíos)
registros = [
    {'nombre': '', 'creditos': 0, 'contador': 0, 'ajuste': '-', 'estado': 'Inactivo'},
    {'nombre': '', 'creditos': 0, 'contador': 0, 'ajuste': '+', 'estado': 'Inactivo'}
]

@app.route('/')
def home():
    """Redirige automáticamente al login"""
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in user_db and user_db[username]['password'] == password:
            session['username'] = username
            session['nombre'] = user_db[username]['nombre']
            return redirect(url_for('dashboard'))  # Redirige al dashboard después del login
        
        return render_template('login.html', error='Credenciales incorrectas')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('usuarios.html', registros=registros, usuario=session.get('nombre'))


@app.route('/gestion_usuarios')
def gestion_usuarios():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('gestion_usuarios.html')

@app.route('/cambiar_password')
def cambiar_password():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('cambiar_password.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)