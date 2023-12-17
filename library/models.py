from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.timezone import now
from django.contrib.auth.models import User

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey("Author", on_delete=models.CASCADE)
    published = models.DateField()
    added = models.DateField(default=now)
    pages = models.IntegerField(validators=[
        MinValueValidator(1),
        MaxValueValidator(2000)
    ])
    publisher = models.ForeignKey("Publisher", on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    cover = models.ForeignKey("Cover", on_delete=models.CASCADE)
    category = models.ForeignKey("Category", on_delete=models.CASCADE)
    is_borrowed = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    

class Category(models.Model):
    name = models.CharField(max_length=50)
    is_deleted = models.IntegerField(default=False)

    def __str__(self):
        return self.name
    

class Author(models.Model):
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name + " " + self.surname


class Publisher(models.Model):
    name = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Cover(models.Model):
    name = models.CharField(max_length=50)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
    
class Borrowing(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    borrow_date = models.DateField(default=now)
    return_date = models.DateField(default=None, null=True)