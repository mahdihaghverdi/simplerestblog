import asyncio
import base64
import functools
import hashlib
import io

import qrcode
from pyotp import totp

from src.core.schemas import UserSchema


def asingleton(coro):
    sentinel = instance = object()
    lock = asyncio.Lock()

    @functools.wraps(coro)
    async def wrapper(*args, **kwargs):
        nonlocal instance
        if instance is sentinel:
            async with lock:
                if instance is sentinel:
                    instance = await coro(*args, **kwargs)
        return instance

    return wrapper


def create_totp_qr_img(user_schema: UserSchema) -> str:
    provisioning_uri = totp.TOTP(user_schema.totp_hash).provisioning_uri(
        name=user_schema.username, issuer_name="SimpleRESTBlog"
    )
    buffered = io.BytesIO()
    qrcode.make(provisioning_uri).save(buffered)
    qr_img = base64.b64encode(buffered.getvalue()).decode()
    return qr_img


def sha256_username(username):
    return hashlib.sha256(username.encode()).hexdigest()
