from select import select
from urllib3 import request

from courses.models import Category, Course, Tag, Lesson, User, Comment
from rest_framework import serializers


class CategorySerializers(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class TagSeriliazer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class BaseSeriliazer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField(source='image')
    tags = TagSeriliazer(many=True)

class LessonSeriliazer(BaseSeriliazer):
    def get_image(self, lesson):
        request = self.context.get('request')
        if request and lesson.image:
            return request.build_absolute_uri(f'/static/{lesson.image}')

    class Meta:
        model = Lesson
        fields = ['id','subject','image','tags']

class LessonDetailSerializer(LessonSeriliazer):
    liked = serializers.SerializerMethodField()

    def get_liked(self, lesson):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return lesson.like_set.filter(user=request.user, active=True).exists()
        return False

    class Meta:
        model = LessonSeriliazer.Meta.model
        fields = LessonSeriliazer.Meta.fields + ['liked']

class CourseSeriliazers(BaseSeriliazer):

    def get_image(self, course):
        request = self.context.get('request')
        if request and course.image:
            return request.build_absolute_uri(f'/static/{course.image}')

    class Meta:
        model = Course
        fields = '__all__'

class UserSeriliazer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name','last_name','username','password','email','avatar']
        extra_kwargs = {
            'password' : {
                'write_only' : True
            }
        }

    def create(self, validated_data):
        data = validated_data.copy()

        user = User(**data)
        user.set_password(data['password'])
        user.save()

        return user

class CommentSerializer(serializers.ModelSerializer):
    user = UserSeriliazer()

    class Meta:
        model = Comment
        fields = ['id', 'content','user']