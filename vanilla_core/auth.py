#

import pyotp
import base64
from .config import config

__all__ = [
    "verify",
    ]

SECRET = base64.b32encode(config.get["OTP_SECRET"])

totp = pyotp.TOTP(SECRET)

def verify(token: str) -> bool:
    return totp.verify(token)
