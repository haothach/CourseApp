from email.policy import default
from tkinter.constants import CASCADE
from tkinter.font import names
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import model_to_dict
from ckeditor.fields import RichTextField
from cloudinary.models import CloudinaryField

class User(AbstractUser):
    avatar = CloudinaryField('avatar',null=True)

class BaseModel(models.Model):
    created_date = models.DateField(auto_now_add=True, null=True)
    updated_date = models.DateField(auto_now=True, null=True)
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True

class Category(BaseModel):
    name = models.CharField(max_length=50, null=False)

    def __str__(self):
        return self.name

class Course(BaseModel):
    subject = models.CharField(max_length=255, null=False)
    description = RichTextField()
    image = models.ImageField(upload_to='course/%Y/%m')
    category = models.ForeignKey(Category, on_delete=models.RESTRICT)
    tags = models.ManyToManyField('Tag')

    def __str__(self):
        return self.subject

    class Meta:
        unique_together = ('subject', 'category')

class Lesson(BaseModel):
    subject =  models.CharField(max_length=255,null=False)
    content = RichTextField()
    image = models.ImageField(upload_to='lesson/%Y/%m')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    tags = models.ManyToManyField('Tag')

    class Meta:
        unique_together = ('subject', 'course')

class Tag(BaseModel):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Interation(BaseModel):
    user = models.ForeignKey(User,on_delete=models.CASCADE, null=False)
    lesson = models.ForeignKey(Lesson,on_delete=models.CASCADE, null=False)

    class Meta:
        abstract = True

class Comment(Interation):
    content = models.CharField(max_length=255,null=False)

class Like(Interation):
    active = models.BooleanField(default=True)

    class Meta:
        unique_together =('user','lesson')

class Rating(Interation):
    rate = models.SmallIntegerField(default=0)