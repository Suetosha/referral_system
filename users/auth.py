import random
import uuid

from django.core.cache import cache


def generate_verification_code():
    return str(random.randint(1000, 9999))


def generate_invite_code():
    return str(uuid.uuid4())[:6].upper()


def save_code_to_cache(phone, code):
    cache.set(f'code_{phone}', code, timeout=300)


def get_code_from_cache(phone):
    return cache.get(f'code_{phone}')
