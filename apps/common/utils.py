import json

import httpx
from httpx import ConnectTimeout
from rest_framework.exceptions import ValidationError

from django.conf import settings
from django.core.cache import caches
from django.utils.translation import gettext_lazy as _



async def send_sms(phone, message):
    sn = "8687"
    if phone[4:6] in ["99", "77", "95", "20", "90", "91", "50", "93", "94", "88", "97"]:
        sn = "8687"
    elif phone[4:6] in ["98", "33"]:
        sn = "6500"

    async with httpx.AsyncClient() as client:
        try:
            await client.get(settings.SMS_URL, params={"sn": sn, "msisdn": phone[1:], "message": message}, timeout=5)
        except ConnectTimeout:
            raise ValidationError(
                detail={"sms_provider": _("Can not connect to sms provider.")}, code="connection_error"
            )
        except Exception as e:  # noqa
            raise ValidationError(detail={"sms_provider": _("Something went wrong with sms provider.")}, code="error")


async def octo_send_sms(phone, message):
    body_data = {
        "phone_number": phone[1:],
        "channels": ["sms"],
        "channel_options": {"sms": {"text": message, "ttl": 300}},
    }
    username = settings.OCTO_SMS_LOGIN
    password = settings.OCTO_SMS_PASSWORD
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                settings.OCTO_SMS_SEND_URL,
                json=body_data,
                auth=(username, password),
                timeout=5,
            )
        except ConnectTimeout:
            raise ValidationError(
                detail={"sms_provider": _("Can not connect to sms provider while sending sms")},
                code="connection_error",
            )
        except Exception as e:  # noqa
            raise ValidationError(
                detail={"sms_provider": _("Something went wrong with sms provider while sending sms")}, code="error"
            )
    if response.status_code == 200 and response.json().get("error_code") is not None:
        raise ValidationError(
            detail={"sms_provider": _("Bad response from sms provider while sending sms")}, code="bad_response"
        )
    elif response.status_code != 200:
        raise ValidationError(
            detail={"sms_provider": _("Bad status code from sms provider while sending sms")}, code="bad_status_code"
        )
