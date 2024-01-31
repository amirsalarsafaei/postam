from rest_framework import serializers

from user_posts.models import UserPost, Vitrine


class UserPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPost
        fields = [
            'token',
            'title',
            'images',
            'category',
            'id'
        ],
        read_only_fields = ('id',)

    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        # Now you can set the user before saving the instance
        user_post = UserPost(user=user, **validated_data)
        user_post.save()
        return user_post


class CreateVitrineSerializer(serializers.Serializer):
    user_post_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=True,
        allow_empty=False,
        help_text="A list of UserPost IDs to include in the Vitrine."
    )

    def validate_user_post_ids(self, value):
        # Ensure all IDs correspond to posts that belong to the user
        user = self.context['request'].user
        valid_posts = UserPost.objects.filter(user=user, id__in=value)

        # Check if the posts count matches the number of IDs provided
        if valid_posts.count() != len(value):
            raise serializers.ValidationError(
                "One or more UserPosts either do not exist or do not belong to the authenticated user.")

        return valid_posts


class VitrineSerializer(serializers.ModelSerializer):
    posts = UserPostSerializer(many=True, read_only=True)

    class Meta:
        model = Vitrine
        fields = ['slug', 'posts']

class GetVitrineSerializer(serializers.Serializer):
    slug = serializers.UUIDField()

