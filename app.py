import os
from datetime import datetime
from flask import Flask, render_template, url_for
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Helpers

def is_image(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config['IMAGE_EXTENSIONS']

def is_video(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config['VIDEO_EXTENSIONS']


def build_gallery_items():
    """Lê static/uploads e cria lista de mídias (imagens/vídeos) para a galeria.
    Regra opcional: se existir par `video.ext` e `video.jpg`, usamos `video.jpg` como poster e **não** listamos o JPG sozinho.
    """
    upload_dir = app.config['UPLOAD_FOLDER']
    if not os.path.isdir(upload_dir):
        return []

    files = os.listdir(upload_dir)

    # mapear possíveis posters
    posters_for_videos = set()
    for f in files:
        if is_video(f):
            base, _ = os.path.splitext(f)
            cand = base + ".jpg"
            if cand in files:
                posters_for_videos.add(cand)

    items = []
    for f in files:
        if is_image(f):
            # se for poster de um vídeo, não listar como imagem independente
            if f in posters_for_videos:
                continue
            items.append({
                "kind": "image",
                "src": url_for('static', filename=f"uploads/{f}")
            })
        elif is_video(f):
            base, _ = os.path.splitext(f)
            poster = base + ".jpg" if base + ".jpg" in files else None
            items.append({
                "kind": "video",
                "src": url_for('static', filename=f"uploads/{f}"),
                "poster": url_for('static', filename=f"uploads/{poster}") if poster else None
            })

    # ordena desc por nome (assumindo timestamp no nome, se você usar esse padrão)
    items.sort(key=lambda x: x['src'], reverse=True)
    return items


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
    start_dt = Config.parse_start_date()
    timeline = sorted(app.config['TIMELINE'], key=lambda i: i['date'], reverse=True)
    gallery = build_gallery_items()
    return render_template('index.html', start_iso=start_dt.isoformat(), timeline=timeline, gallery=gallery)


if __name__ == '__main__':
    app.run(debug=True)
