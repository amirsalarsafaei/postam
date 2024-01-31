import base64
import random
import string
from datetime import datetime

from cryptography.fernet import Fernet
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from kenar.clients.finder import finder_client
from kenar.clients.oauth import oauth_client
from oauth.models import OAuth, PermissionTypes

STATE_SALT_LEN = 10

fernet = Fernet(settings.ENCRYPTION_KEY)


def get_oauth(code, *args, **kwargs) -> OAuth:
    token = oauth_client.get_token(
        code=code,
        app_slug=settings.APP_SLUG,
        oauth_api_key=settings.API_KEY
    )

    access_token, refresh_token = token['access_token'], token['refresh_token']
    expires = datetime.fromtimestamp(int(token['expires']), timezone.utc)

    return OAuth(access_token=access_token, refresh_token=refresh_token,
                 expires=expires, *args, **kwargs)


# noinspection PyTypeChecker,PyNoneFunctionAssignment
def create_redirect_link(request, scopes, state_data: str = "") -> str:
    salt = ''.join(random.choices(string.ascii_letters, k=STATE_SALT_LEN))

    if state_data != "":
        encryption = fernet.encrypt(f"{state_data}\n{salt}".encode())
        state = base64.urlsafe_b64encode(
            encryption
        ).decode()
    else:
        state = salt

    oauth_url = oauth_client.create_redirect_link(
        app_slug=settings.APP_SLUG,
        redirect_uri=settings.HOST + reverse('oauth:callback'),
        scopes=scopes,
        state=state
    )

    request.session[settings.OAUTH_INFO_SESSION_KEY] = {
        "state": state,
        "scopes": scopes,
        "oauth_url": oauth_url,
    }

    return oauth_url


def create_phone_scope() -> str:
    return PermissionTypes.USER_PHONE.name


def create_user_addon_scope() -> str:
    return PermissionTypes.USER_ADDON_CREATE.name


def create_get_user_posts_scope() -> str:
    return PermissionTypes.GET_USER_POSTS.name


def create_approved_addon_scope(token: str) -> str:
    return f"{PermissionTypes.ADDON_USER_APPROVED.name}__{token}"


def extract_state_data(state: str) -> str:
    decrypted_state = fernet.decrypt(base64.urlsafe_b64decode(state.encode())).decode()
    if '\n' not in decrypted_state:
        return ""

    return decrypted_state[:decrypted_state.index('\n')]


def get_phone_numbers(access_token):
    return finder_client.get_user(settings.API_KEY, access_token)["phone_numbers"]
