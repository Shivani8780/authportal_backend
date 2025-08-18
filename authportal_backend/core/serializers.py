from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import EBooklet, UserEBookletSelection

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    dob = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'phone_number', 'dob')

    def create(self, validated_data):
        dob = validated_data.pop('dob', None)
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            phone_number=validated_data.get('phone_number', ''),
            dob=dob
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class EBookletSerializer(serializers.ModelSerializer):
    class Meta:
        model = EBooklet
        fields = ('id', 'name', 'pdf_file')

class UserEBookletSelectionSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    ebooklet = serializers.PrimaryKeyRelatedField(queryset=EBooklet.objects.all())

    class Meta:
        model = UserEBookletSelection
        fields = ('id', 'user', 'ebooklet', 'payment_verified', 'approved', 'selected_at')

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'dob', 'gender']
