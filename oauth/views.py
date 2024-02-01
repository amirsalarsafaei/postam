import logging
import re

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from rest_framework.exceptions import NotFound, PermissionDenied, APIException, AuthenticationFailed
import oauth.controller as oauth_controller
from kenar.clients.finder import finder_client
from oauth.models import Scope, OAuth
from oauth.serializers import StateCodeSerializer
from user_posts.serializers import UserPostSerializer

logger = logging.getLogger(__name__)

scope_regex = re.compile(r"^(?P<permission_type>([A-Z]+_)*([A-Z]+))(__(?P<resource_id>.+))?$")


@api_view(['GET'])
def start_oauth(request):
    url = oauth_controller.create_redirect_link(
        request=request,
        scopes=(oauth_controller.create_phone_scope(), oauth_controller.create_get_user_posts_scope()),
    )

    return Response({
        "url": url
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@transaction.atomic
def oauth_callback(request):
    oauth_session = request.session.get(settings.OAUTH_INFO_SESSION_KEY, None)
    if oauth_session is None:
        raise NotFound("oauth session not found")

    del (request.session[settings.OAUTH_INFO_SESSION_KEY])

    state_in_session, scopes, oauth_url = oauth_session["state"], \
        oauth_session["scopes"], oauth_session["oauth_url"]

    serializer = StateCodeSerializer(data=request.data)

    serializer.is_valid(raise_exception=True)

    code = serializer.validated_data['code']
    state = serializer.validated_data['state']
    if code is None or state is None:
        return AuthenticationFailed("code or state can't be empty")

    if state != state_in_session:
        return AuthenticationFailed("invalid state")

    oauth_data = oauth_controller.get_oauth(code=code)
    try:
        phones = oauth_controller.get_phone_numbers(oauth_data.access_token)
    except Exception as e:
        logger.error("got exception while getting phone number", e)
        return Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    phone = phones[0]

    user, created = User.objects.get_or_create(username=phone)
    login(request, user)
    oauth_data.user = user
    oauth_data.save()

    scopes_permissions = []
    for s in scopes:
        scope_match_groups = scope_regex.search(s).groupdict()
        scopes_permissions.append(scope_match_groups['permission_type'])

        Scope.objects.create(
            permission_type=scope_match_groups['permission_type'],
            resource_id=scope_match_groups.setdefault('resource_id', None),
            oauth=oauth_data
        )

    posts = finder_client.get_user_posts(api_key=settings.API_KEY, access_token=oauth_data.access_token)

    for post in posts['posts']:
        serializer = UserPostSerializer(data=post, context={'request': request})
        serializer.save()

    return Response({}, status=status.HTTP_200_OK)
