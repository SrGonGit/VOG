import os
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "senha123")

    # Data do início do namoro
    START_DATE = os.getenv("START_DATE", "2022-04-16T20:00:00")

    # Pastas/Extensões
    STATIC_DIR = os.path.join(BASE_DIR, 'static')
    UPLOAD_FOLDER = os.path.join(STATIC_DIR, 'uploads')  # agora só leitura, controlado via Git

    IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
    VIDEO_EXTENSIONS = {"mp4", "mov", "webm"}

    # Conteúdo da Timeline (exemplo)
    # Campo opcional 'image': caminho relativo a static/, ex.: 'uploads/primeiro_encontro.jpg'
    TIMELINE = [
        {
            "date": "2022-06-15",
            "title": "Primeiro encontro",
            "desc": "Café que virou história.",
            "images": [
                "uploads/teste.jpg",
                "uploads/teste2.jpg",
                "uploads/teste3.jpg"
            ]
        },
        {
            "date": "2022-08-10",
            "title": "Viagem X",
            "desc": "Nossa primeira trip.",
            # sem imagem neste
        },
    ]

    @staticmethod
    def parse_start_date():
        return datetime.fromisoformat(Config.START_DATE)
