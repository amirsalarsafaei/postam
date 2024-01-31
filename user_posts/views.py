from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound, PermissionDenied, APIException, AuthenticationFailed, NotAuthenticated
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from user_posts.models import UserPost, Vitrine
from user_posts.serializers import UserPostSerializer, CreateVitrineSerializer, VitrineSerializer, GetVitrineSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_posts(request):
    serializer = UserPostSerializer(UserPost.objects.filter(user=request.user), many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_vitrine(request):
    # Initialize serializer with request data
    serializer = CreateVitrineSerializer(data=request.data, context={'request': request})

    # Check if the data is valid (this will call the validate_user_post_ids method)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user_posts = serializer.validated_data['user_post_ids']

    vitrine = Vitrine.objects.create()
    vitrine.posts.set(user_posts)
    vitrine.save()

    return Response({'message': 'Vitrine created successfully!', 'vitrine_slug': vitrine.slug},
                    status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_vitrines(request):
    serializer = VitrineSerializer(data=request.data, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_vitrine(request, slug):
    serializer = GetVitrineSerializer(data=get_object_or_404(Vitrine, slug=slug))
    return Response(serializer.data, status=status.HTTP_200_OK)
