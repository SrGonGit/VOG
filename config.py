import os
from datetime import datetime

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "troque-esta-chave")
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

    # Data do início do namoro (AAAA-MM-DDTHH:MM:SS) em UTC ou local
    START_DATE = os.getenv("START_DATE", "2022-06-15T20:00:00")

    # Timeline inicial (pode puxar do DB depois)
    TIMELINE = [
        {"date": "2022-06-15", "title": "Primeiro encontro", "desc": "Café que virou história."},
        {"date": "2022-08-10", "title": "Viagem X", "desc": "Nossa primeira trip."},
    ]

    @staticmethod
    def parse_start_date():
        # Tenta parse flexível
        return datetime.fromisoformat(Config.START_DATE)
