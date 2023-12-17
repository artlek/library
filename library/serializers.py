from rest_framework import serializers
from . models import Book


class BookSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.name')
    author_surname = serializers.ReadOnlyField(source='author.surname')
    category = serializers.ReadOnlyField(source='category.name')
    class Meta:
        model = Book
        fields = ['id', 'title', 'author_name', 'author_surname', 'category', 'pages', 'is_borrowed']