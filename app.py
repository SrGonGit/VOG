import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Helpers

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def ensure_dirs():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def save_image(file_storage):
    """Salva a imagem e cria um thumbnail leve para a galeria."""
    ensure_dirs()
    filename = secure_filename(file_storage.filename)
    if not allowed_file(filename):
        raise ValueError("Extensão de arquivo não permitida.")

    # Evita overwrite adicionando timestamp
    name, ext = os.path.splitext(filename)
    ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
    filename = f"{name}_{ts}{ext.lower()}"

    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file_storage.save(path)

    # Gera thumbnail (largura máx 1280px, qualidade 85)
    try:
        with Image.open(path) as im:
            im = im.convert("RGB") if im.mode in ("RGBA", "P") else im
            im.thumbnail((1280, 1280))
            im.save(path, optimize=True, quality=85)
    except Exception as e:
        # Se der ruim no Pillow, mantemos o original
        app.logger.warning(f"Falha ao gerar thumbnail: {e}")

    return os.path.basename(path)


@app.template_filter('since')
def since(start_iso):
    """Converte diferença de tempo em anos/meses/dias (aprox) pro Jinja."""
    start = datetime.fromisoformat(start_iso) if isinstance(start_iso, str) else start_iso
    now = datetime.now()
    delta = now - start
    days = delta.days
    years = days // 365
    months = (days % 365) // 30
    rem_days = (days % 365) % 30
    return f"{years}a {months}m {rem_days}d"


@app.route('/')
def index():
    start_dt = app.config['parse_start_date']() if callable(app.config.get('parse_start_date')) else Config.parse_start_date()
    start_iso = start_dt.isoformat()
    return render_template('index.html', start_iso=start_iso)


@app.route('/galeria', methods=['GET', 'POST'])
def galeria():
    ensure_dirs()
    if request.method == 'POST':
        file = request.files.get('foto')
        if not file or file.filename == '':
            flash('Nenhum arquivo selecionado.', 'error')
            return redirect(url_for('galeria'))
        if not allowed_file(file.filename):
            flash('Tipo de arquivo não permitido.', 'error')
            return redirect(url_for('galeria'))
        try:
            filename = save_image(file)
            flash('Foto enviada com sucesso!', 'ok')
            return redirect(url_for('galeria'))
        except Exception as e:
            app.logger.exception(e)
            flash('Erro ao enviar a foto.', 'error')
            return redirect(url_for('galeria'))

    # Lista arquivos (ordem decrescente)
    files = []
    for f in os.listdir(app.config['UPLOAD_FOLDER']):
        if allowed_file(f):
            files.append(f)
    files.sort(reverse=True)
    return render_template('galeria.html', files=files)


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/timeline')
def timeline():
    items = app.config['TIMELINE']
    # Ordena por data desc
    items = sorted(items, key=lambda i: i['date'], reverse=True)
    return render_template('timeline.html', items=items)


if __name__ == '__main__':
    app.run(debug=True)
