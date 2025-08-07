from flask import Flask, render_template, request, redirect, url_for, session, make_response
from fpdf import FPDF
from datetime import datetime
import os
import barcode
from barcode.writer import ImageWriter
import qrcode
import uuid


app = Flask(__name__,
            template_folder='../front/templates',
            static_folder='../front/static')
app.secret_key = 'tu_clave_secreta_aqui'

user_db = {
    'admin': {'password': 'admin123', 'nombre': 'Administrador', 'rol': 'admin'}
}

registros = [
    {'nombre': '', 'creditos': 0, 'contador': 0, 'ajuste': '-', 'estado': 'Inactivo'},
    {'nombre': '', 'creditos': 0, 'contador': 0, 'ajuste': '+', 'estado': 'Inactivo'}
]


class ConstanciaPDF(FPDF):
    def header(self):
        pass  # Sin encabezado como solicitaste

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}/{{nb}}', 0, 0, 'C')

    def add_barcode(self, rfc):
        if not os.path.exists('tmp/barcodes'):
            os.makedirs('tmp/barcodes')
        
        code = barcode.get('code128', rfc, writer=ImageWriter())
        filename = code.save(f'tmp/barcodes/{rfc}')
        # Posición del código de barras ajustada
        self.image(filename, x=150, y=25, w=45, h=15)
        self.ln(5)

    def add_qrcode(self, data):
        if not os.path.exists('tmp/qrcodes'):
            os.makedirs('tmp/qrcodes')
        
        unique_id = str(uuid.uuid4())
        qr_data = f"{data['rfc']}|{data['idcif']}|{unique_id}|{datetime.now().timestamp()}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=4,
            border=2,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        filename = f"tmp/qrcodes/{unique_id}.png"
        img.save(filename)
        
        # Posición del QR ajustada
        self.image(filename, x=15, y=25, w=20, h=20)
        
        return filename

    def add_constancia_content(self, datos):
        # Marco principal con medidas exactas
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.5)
        self.rect(10, 10, 110, 70)  # Cuadro del mismo tamaño
        
        # Título arriba de la línea
        self.set_font('Arial', 'B', 16)
        self.set_xy(12, 15)
        self.cell(0, 6, 'CÉDULA DE IDENTIFICACIÓN FISCAL', 0, 1, 'L')
        
        # Línea divisoria bajo el título
        self.line(10, 22, 120, 22)
        
        # Imagen HACIENDA-SAT y QR en la izquierda
        self.image('../front/img/HACIENDA-SAT.jpg', x=15, y=25, w=25, h=15)
        self.add_qrcode(datos)
        
        # Código de barras en derecha
        self.add_barcode(datos['rfc'])
        
        # Información al lado derecho (alineada con imagen/QR)
        
        self.set_font('Arial', 'B', 12)
        self.set_xy(45, 28)  # Posición ajustada
        self.cell(60, 6, datos['rfc'], 0, 1, 'C')  # Centrado con ancho de 60
        
        self.set_font('Arial', '', 10)
        self.set_xy(45, 34)  # Posición ajustada con espacio
        self.cell(60, 5, 'Registro Federal de Contribuyentes', 0, 1, 'C')  # Centrado
        
        self.set_font('Arial', 'B', 12)
        self.set_xy(45, 40)  # Posición ajustada
        self.cell(60, 6, datos.get('nombre_comercial', ''), 0, 1, 'C')  # Centrado
        
        self.set_font('Arial', '', 10)
        self.set_xy(45, 44)  # Posición ajustada
        self.cell(60, 5, 'Nombre, denominación o razón social', 0, 1, 'C')  # Centrado
        
        self.set_font('Arial', '', 10)
        self.set_xy(45, 52)  # Posición ajustada
        self.cell(60, 5, f"IdCIF: {datos['idcif']}", 0, 1, 'C')  # Centrado
        
        self.set_font('Arial', 'B', 10)
        self.set_xy(45, 58)  # Posición ajustada
        self.cell(60, 5, "VALIDA TU INFORMACIÓN FISCAL", 0, 1, 'C')  # Centrado

        # Resto del documento (se mantiene igual)
        self.ln(10)
        
        # Fecha de emisión
        fecha_emision = datetime.strptime(datos['fecha_inicio'], '%Y-%m-%d').strftime("%d DE %B DE %Y").upper()
        self.set_font('Arial', 'B', 10)
        self.cell(0, 6, f"{datos['lugar_emision']} A {fecha_emision}", 0, 1, 'R')
        
        # RFC al final
        self.set_font('Arial', 'B', 12)
        self.set_xy(10, 65)
        self.cell(0, 8, datos['rfc'], 0, 1, 'L')

        # Resto del contenido original (sin cambios)
        self.ln(15)
        
        # Tabla de datos de identificación
        self.set_fill_color(220, 220, 220)
        self.set_font('Arial', 'B', 10)
        self.cell(0, 6, 'Datos de Identificación del Contribuyente:', 'LTR', 1, 'L', 1)


        datos_tabla = [
            ("RFC:", datos['rfc']),
            ("CURP:", datos.get('curp', '')),
            ("Nombre(s):", datos.get('nombre', '')),
            ("Primer Apellido:", datos.get('primer_apellido', '')),
            ("Segundo Apellido:", datos.get('segundo_apellido', '')),
            ("Fecha inicio de operaciones:", fecha_emision),
            ("Estatus en el padrón:", "ACTIVO"),
            ("Fecha de último cambio de estado:", fecha_emision),
            ("Nombre Comercial:", datos.get('nombre_comercial', ''))
        ]
        
        self.set_font('Arial', '', 10)
        for etiqueta, valor in datos_tabla:
            self.cell(60, 6, etiqueta, 'L', 0, 'L')
            self.cell(0, 6, valor, 'R', 1, 'L')
            self.set_x(10)
        
        self.cell(0, 1, '', 'LBR', 1)
        self.ln(10)
        
        # Tabla de domicilio (todos los campos vacíos)
        self.set_fill_color(220, 220, 220)
        self.set_font('Arial', 'B', 10)
        self.cell(0, 6, 'Datos del domicilio registrado', 'LTR', 1, 'L', 1)
        
        domicilio_data = [
            ("Código Postal:", datos.get('codigo_postal', ''), "Tipo de Vialidad:", datos.get('tipo_vialidad', '')),
            ("Nombre de Vialidad:", datos.get('nombre_vialidad', ''), "Número Exterior:", datos.get('numero_exterior', '')),
            ("Número Interior:", datos.get('numero_interior', ''), "Nombre de Colonia:", datos.get('colonia', '')),
            ("Nombre de la Localidad:", datos.get('localidad', ''), "Nombre de Municipio o Demarcación Territorial:", datos.get('municipio', '')),
            ("Nombre de la Entidad Federativa:", datos.get('entidad_federativa', ''), "Entre Calle:", datos.get('entre_calle', ''))
        ]
        
        self.set_font('Arial', '', 10)
        for row in domicilio_data:
            self.cell(50, 6, row[0], 'L', 0, 'L')
            self.cell(40, 6, row[1], 0, 0, 'L')
            self.cell(50, 6, row[2], 0, 0, 'L')
            self.cell(0, 6, row[3], 'R', 1, 'L')
            self.set_x(10)
        
        self.cell(0, 1, '', 'LBR', 1)
        
        # Nueva página para actividades económicas y regímenes
        self.add_page()
        
        # Actividades económicas
        self.set_fill_color(220, 220, 220)
        self.set_font('Arial', 'B', 10)
        self.cell(0, 6, 'Actividades Económicas:', 'LTR', 1, 'L', 1)
        self.ln(2)
        
        headers = ["Orden", "Actividad Económica", "Porcentaje", "Fecha Inicio", "Fecha Fin"]
        widths = [15, 80, 25, 35, 35]
        
        self.set_font('Arial', 'B', 9)
        for i, header in enumerate(headers):
            self.cell(widths[i], 6, header, 1, 0, 'C')
        self.ln()
        
        self.set_font('Arial', '', 9)
        self.cell(widths[0], 6, "1", 1, 0, 'C')
        self.cell(widths[1], 6, datos['actividad'], 1, 0, 'L')
        self.cell(widths[2], 6, f"{datos['porcentaje']}%", 1, 0, 'C')
        self.cell(widths[3], 6, datos['fecha_inicio'], 1, 0, 'C')
        self.cell(widths[4], 6, "", 1, 1, 'C')
        
        self.ln(10)
        
        # Regímenes
        self.set_fill_color(220, 220, 220)
        self.set_font('Arial', 'B', 10)
        self.cell(0, 6, 'Regímenes:', 'LTR', 1, 'L', 1)
        self.ln(2)
        
        reg_headers = ["Regimen", "Fecha Inicio", "Fecha Fin"]
        reg_widths = [100, 40, 40]
        
        self.set_font('Arial', 'B', 9)
        for i, header in enumerate(reg_headers):
            self.cell(reg_widths[i], 6, header, 1, 0, 'C')
        self.ln()
        
        self.set_font('Arial', '', 9)
        self.cell(reg_widths[0], 6, datos.get('regimen', ''), 1, 0, 'L')
        self.cell(reg_widths[1], 6, datos['fecha_inicio'], 1, 0, 'C')
        self.cell(reg_widths[2], 6, "", 1, 1, 'C')
        
        self.ln(15)
        
        # Texto final (fijo)
        self.set_font('Arial', '', 8)
        texto_final = [
            "Sus datos personales son incorporados y protegidos en los sistemas del SAT, de conformidad con los Lineamientos de Protección de Datos",
            "Personales y con diversas disposiciones fiscales y legales sobre confidencialidad y protección de datos, a fin de ejercer las facultades",
            "conferidas a la autoridad fiscal.",
            "",
            "Si desea modificar o corregir sus datos personales, puede acudir a cualquier Módulo de Servicios Tributarios y/o a través de la dirección",
            "http://sat.gob.mx",
            "",
            '"La corrupción tiene consecuencias ¡denúnciala! Si conoces algún posible acto de corrupción o delito presenta una queja o denuncia a través',
            'de: www.sat.gob.mx, denuncias@sat.gob.mx, desde México: (55) 8852 2222, desde el extranjero: + 55 8852 2222, SAT móvil o www.gob.mx/sfp".'
        ]
        
        for texto in texto_final:
            self.cell(0, 4, texto, 0, 1)
        
        self.ln(10)
        self.set_font('Courier', '', 8)
        self.cell(0, 4, "Cadena Original Sello: lj2025/08/05[D]MMT20702IW4JCONSTANCIA DE SITUACIÓN FISCAL[200001088888800791414]]", 0, 1)
        self.cell(0, 4, "Sello Digital: q9VzGqb+ro/KIFdVucsFAYChroirOVwfqvBznLgtUpsWTeq0lgRzuKHsyLJvqw3uo+xAICHoOGgzwDCBB0EPaSo", 0, 1)
        self.cell(0, 4, "3DGZtafattUZpnzJsJlR3nSg0mZDz2R+SDD2zDySmruJ9Jl+uDQx34MyQUG1HAPw+pr+O8j60hAucIOpYz6q8AHe", 0, 1)



@app.route('/generar-constancia', methods=['POST'])
def generar_constancia():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    datos = {
        'rfc': request.form['rfc'],
        'idcif': request.form['id_cif'],
        'lugar_emision': request.form['lugar_emision'],
        'actividad': request.form['actividad'],
        'porcentaje': request.form['porcentaje'],
        'fecha_inicio': request.form['fecha_inicio'],
        'nombre': '',
        'curp': ''
    }

    pdf = ConstanciaPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.add_constancia_content(datos)
    
    if not os.path.exists('tmp'):
        os.makedirs('tmp')
    pdf_path = f"tmp/constancia_{datos['rfc']}.pdf"
    pdf.output(pdf_path)
    
    with open(pdf_path, 'rb') as f:
        response = make_response(f.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=constancia_{datos["rfc"]}.pdf'
    
    return response

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in user_db and user_db[username]['password'] == password:
            session['username'] = username
            session['nombre'] = user_db[username]['nombre']
            return redirect(url_for('dashboard'))
        
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