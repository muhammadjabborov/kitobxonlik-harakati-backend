import random
import string
import sys

from asgiref.sync import sync_to_async

from django.conf import settings
from django.core.cache import cache
from django.utils.crypto import get_random_string

from apps.common.utils import octo_send_sms


def is_code_valid(cache_key: str, code: str) -> bool:
    if getattr(settings, "STAGE", "development") == "development" and code == getattr(
        settings, "DEV_OTP_CODE", "7777"
    ):
        return True
    valid_code = cache.get(cache_key)
    return valid_code == code


class CacheTypes:
    auth_sms_code = "auth_sms_code"


def generate_cache_key(type_, *args):
    return f"{type_}{''.join(args)}"


class MessageProvider:
    auth_code_message = "Kitobxonlik harakatiga kirishni tasdiqlash uchun kod: {}\npqT/VR+ITq7"
    static_code = "7777"
    test_phone = "+998999999999"

    def __init__(self):
        self.session = get_random_string(length=16)
        self.production_mode = settings.STAGE == "production" and "test" not in sys.argv

    def generate_code(self):
        if self.production_mode:
            return "".join(random.choice(string.digits) for _ in range(4))
        return self.static_code

    async def send_sms(self, phone):
        if phone == self.test_phone:
            self.production_mode = False

        code = self.generate_code()
        message = self.auth_code_message.format(code)

        if self.production_mode:
            await octo_send_sms(phone, message)

        await sync_to_async(cache.set)(
            generate_cache_key(CacheTypes.auth_sms_code, phone, self.session),
            code,
            timeout=120,
        )
