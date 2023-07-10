from rest_framework import serializers
from django.contrib.auth.models import User
from users.models import Profile
from api.relations import CustomMultiLookupHyperlink
from .validators import validate_email


class UserRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[validate_email])
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        password = validated_data.pop('password')

        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        Profile.objects.create(user=user)

        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('bio', 'avatar')


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer with only essential fields to decrease response size
    and minimize database queries
    """

    url = serializers.HyperlinkedIdentityField(
        view_name='user-detail', lookup_field='username'
    )
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'profile']

    def to_representation(self, instance):
        """
        Exclude fields with private information to users which are not
        owners of this account
        """
        representation = super().to_representation(instance)

        # Check if the user making the request is the owner of the object
        user = self.context['request'].user

        if instance != user:
            representation.pop('email')

        return representation


class UserDetailSerializer(UserSerializer):
    """
    Serializer with a list of recipes to be loaded individually
    """

    email = serializers.EmailField(validators=[validate_email])
    recipes = CustomMultiLookupHyperlink(
        view_name='recipe-detail',
        lookup_kwarg_fields=('author__username', 'slug'),
        many=True,
        read_only=True,
    )

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'profile', 'recipes')

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile')
        profile = Profile.objects.get(user=instance)

        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        profile.bio = profile_data.get('bio', profile.bio)
        profile.avatar = profile_data.get('avatar', profile.avatar)
        profile.save()

        return instance


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    repeat_new_password = serializers.CharField(write_only=True)


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class NewPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    repeat_new_password = serializers.CharField(write_only=True)


class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
