from django.contrib import admin
from django.template.response import TemplateResponse

from courseapp.settings import TEMPLATES
from .models import Category, Course, Lesson, Tag
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.utils.html import mark_safe
from django.urls import path
from courses import dao

class CourseAppAdminSite(admin.AdminSite):
    site_header = 'Hệ thống khoá học trực tuyến'

    def get_urls(self):
        return [
                path('course-stats/', self.stats_view)
            ] + super().get_urls()

    def stats_view(self, request):
        return TemplateResponse(request, 'admin/stats_view.html', {
            'stats_view':dao.count_courses_by_cate()
        })

admin_site = CourseAppAdminSite(name='myadmin')

class CategoryAdmin(admin.ModelAdmin):
    list_display =['pk', 'name']
    search_fields = ['name']
    search_help_text = 'Tìm kiếm theo tên danh mục'
    list_filter = ['id','name']

class LessonForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = Lesson
        fields = '__all__'

class CourseForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = Course
        fields = '__all__'

class LessonAdmin(admin.ModelAdmin):
    form = LessonForm


class TagInlineAdmin(admin.StackedInline):
    model = Course.tags.through

class CourseAdmin(admin.ModelAdmin):
    readonly_fields = ['img']
    inlines = [TagInlineAdmin]
    form = CourseForm
    exclude = ['tags']

    def img(self, course):
        if course:
            return mark_safe(
                '<img src="/static/{url}" width="120" />' \
                    .format(url=course.image.name)
            )

    class Media:
        css = {
            'all':('/static/css/style.css',)
        }


# Register your models here.
admin_site.register(Category, CategoryAdmin)
admin_site.register(Course, CourseAdmin)
admin_site.register(Lesson, LessonAdmin)
admin_site.register(Tag)