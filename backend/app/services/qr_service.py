import base64
import io
import secrets

import qrcode

from app.core.config import get_settings


def generate_qr_token() -> str:
    return secrets.token_urlsafe(24)


def build_public_url(token: str) -> str:
    settings = get_settings()
    return f"{settings.public_base_url}/public/vacancy/{token}"


def generate_qr_base64(content: str) -> str:
    image = qrcode.make(content)
    output = io.BytesIO()
    image.save(output, format="PNG")
    return base64.b64encode(output.getvalue()).decode("utf-8")
