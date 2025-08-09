import os
import subprocess
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Helpers

def is_image(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config['IMAGE_EXTENSIONS']

def is_video(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config['VIDEO_EXTENSIONS']

def allowed_file(filename):
    return is_image(filename) or is_video(filename)

def ensure_dirs():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def _unique_name(filename):
    name, ext = os.path.splitext(secure_filename(filename))
    ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
    return f"{name}_{ts}{ext.lower()}"


def _save_image(path):
    """Compress/resize imagem para ~1280px do maior lado"""
    try:
        with Image.open(path) as im:
            im = im.convert("RGB") if im.mode in ("RGBA", "P") else im
            im.thumbnail((1280, 1280))
            im.save(path, optimize=True, quality=85)
    except Exception as e:
        app.logger.warning(f"Falha ao processar imagem: {e}")


def _video_thumb(src_path, thumb_path):
    """Gera thumbnail JPG do vídeo usando ffmpeg (frame em 1s)."""
    try:
        # scale para largura máx 1280 mantendo proporção; -2 garante altura par
        cmd = [
            "ffmpeg", "-y", "-ss", "00:00:01", "-i", src_path,
            "-vframes", "1", "-vf", "scale=1280:-2", thumb_path
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        app.logger.warning(f"Falha ao gerar thumbnail de vídeo: {e}")
        return False


def save_upload(file_storage):
    """Salva arquivo (imagem ou vídeo). Retorna dict com metadados."""
    ensure_dirs()
    if not file_storage or file_storage.filename == '':
        raise ValueError("Nenhum arquivo selecionado.")

    if not allowed_file(file_storage.filename):
        raise ValueError("Extensão não permitida.")

    filename = _unique_name(file_storage.filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file_storage.save(path)

    meta = {"file": os.path.basename(path)}

    if is_image(filename):
        _save_image(path)
        meta.update({"kind": "image", "thumb": os.path.basename(path)})
    elif is_video(filename):
        # gera thumbnail JPG ao lado do arquivo de vídeo
        base, _ = os.path.splitext(path)
        thumb_path = base + ".jpg"
        if _video_thumb(path, thumb_path):
            meta.update({"kind": "video", "thumb": os.path.basename(thumb_path)})
        else:
            meta.update({"kind": "video", "thumb": None})

    return meta


@app.template_filter('since')
def since(start_iso):
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
    return render_template('index.html', start_iso=start_dt.isoformat())


@app.route('/galeria', methods=['GET', 'POST'])
def galeria():
    ensure_dirs()
    if request.method == 'POST':
        try:
            meta = save_upload(request.files.get('foto'))
            flash('Arquivo enviado com sucesso!', 'ok')
            return redirect(url_for('galeria'))
        except Exception as e:
            app.logger.exception(e)
            flash(str(e), 'error')
            return redirect(url_for('galeria'))

    # monta a lista de itens (imagens e vídeos)
    items = []
    for f in os.listdir(app.config['UPLOAD_FOLDER']):
        if allowed_file(f):
            item = {"file": f}
            if is_image(f):
                item.update({"kind": "image", "thumb": f})
            elif is_video(f):
                base, _ = os.path.splitext(f)
                thumb_candidate = base + ".jpg"
                item.update({"kind": "video", "thumb": thumb_candidate if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], thumb_candidate)) else None})
            items.append(item)
    # ordena por nome desc (timestamp embutido no nome)
    items.sort(key=lambda x: x['file'], reverse=True)
    return render_template('galeria.html', items=items)


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/timeline')
def timeline():
    items = app.config['TIMELINE']
    items = sorted(items, key=lambda i: i['date'], reverse=True)
    return render_template('timeline.html', items=items)


if __name__ == '__main__':
    app.run(debug=True)
