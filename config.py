import os
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "senha123")

    #Data do início do namoro
    START_DATE = os.getenv("START_DATE", "2022-04-16T20:00:00")

    STATIC_DIR = os.path.join(BASE_DIR, 'static')
    UPLOAD_FOLDER = os.path.join(STATIC_DIR, 'uploads')

    IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
    VIDEO_EXTENSIONS = {"mp4", "mov", "webm"}

    TIMELINE = [
        {
            "date": "2021-12-15",
            "title": "Voltamos a nos falar.",
            "desc": "Nossa, como o décimo terceiro ajuda nos boleto, né? Rs.",
            "images": [
                "uploads/teste.jpg",
                "uploads/teste2.jpg",
                "uploads/teste3.jpg"
            ]
        },
        {
            "date": "2021-12-15",
            "title": "Nosso primeiro rolê.",
            "desc": "Cineminha para ver o filme do Homem Aranha.",
            # sem imagem neste
        },
    ]

    @staticmethod
    def parse_start_date():
        return datetime.fromisoformat(Config.START_DATE)
