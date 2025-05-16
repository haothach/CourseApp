from http.client import responses
from lib2to3.fixes.fix_input import context

from django.contrib.auth.models import Permission
from rest_framework import viewsets, generics, status, parsers, permissions
from rest_framework.response import Response
from courses import serializers, paginators, perms
from courses.models import Category, Course, Lesson, User, Comment, Like
from rest_framework.decorators import action

# Create your views here.
class CategoryViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializers
    pagination_class = paginators.CategoryPaginator

    def get_queryset(self):
        queries = self.queryset

        q = self.request.query_params.get("q")
        if q:
            queries = queries.filter(name__icontains=q)
        return queries

class CourseViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Course.objects.filter(active = True).all()
    serializer_class = serializers.CourseSeriliazers
    pagination_class = paginators.CoursePaginator

    def get_queryset(self):
        queries = self.queryset

        q = self.request.query_params.get("q")
        category_id = self.request.query_params.get("category_id")
        if q:
            queries = queries.filter(subject__icontains=q)

        if category_id:
            queries = queries.filter(category__id=category_id)
        return queries

    @action(methods=['get'], detail=True)
    def lessons(self, request, pk):
        lessons = self.get_object().lesson_set.filter(active=True).all()

        return Response(serializers.LessonSeriliazer(lessons, many=True, context={'request':request}).data, status=status.HTTP_200_OK)

class LessonViewSet(viewsets.ViewSet, generics.RetrieveAPIView):
    queryset = Lesson.objects.filter(active=True).all()
    serializer_class = serializers.LessonDetailSerializer
    permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        if self.action in ['add_comments']:
            return [permissions.IsAuthenticated()]

        return [permission() for permission in self.permission_classes]

    def retrieve(self, request, *args, **kwargs):
        lesson = self.get_object()
        serializer = self.serializer_class(lesson, context={'request': request})
        return Response(serializer.data)

    @action(methods=['post'], url_path='comments', detail=True)
    def add_comments(self, request, pk):
        c = comments = Comment.objects.create(user=request.user, lesson=self.get_object(), content=request.data.get('content'))

        return Response(serializers.CommentSerializer(c).data, status=status.HTTP_201_CREATED)

    @action(methods=['get'], url_path='comments_get', detail=True)
    def get_comments(self, request, pk):
        lesson = self.get_object()
        comments = lesson.comment_set.filter(
            active=True).all()  # nếu có trường `active`, nếu không thì bỏ `.filter(active=True)`
        serializer = serializers.CommentSerializer(comments, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['post'], url_path='likes', detail=True)
    def like(self, request, pk):
        like, created = Like.objects.get_or_create(user=request.user, lesson=self.get_object())
        if not created:
            like.active = not like.active
            like.save()
        return Response(serializers.LessonDetailSerializer(self.get_object(), context= {'request':request}).data, status=status.HTTP_200_OK)

class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True).all()
    serializer_class = serializers.UserSeriliazer
    parser_classes = [parsers.MultiPartParser]

    def get_permissions(self):
        if self.action.__eq__('current-user'):
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    @action(methods=['get'], url_name='current-user', detail=False)
    def current_user(self, request):
        return Response(serializers.UserSeriliazer(request.user).data)

class CommentViewSet(viewsets.ViewSet, generics.DestroyAPIView, generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    permission_classes = [perms.OwnewAuthenticated]