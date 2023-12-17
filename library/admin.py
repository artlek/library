from django.contrib import admin
from .models import Book, Author, Publisher, Cover, Category


class BookAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "published", "pages"]


class AuthorAdmin(admin.ModelAdmin):
    list_display = ["name", "surname"]


class PublisherAdmin(admin.ModelAdmin):
    list_display = ["name"]


class CoverAdmin(admin.ModelAdmin):
    list_display = ["name"]


class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]


admin.site.register(Book, BookAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Publisher, PublisherAdmin)
admin.site.register(Cover, CoverAdmin)
admin.site.register(Category, CoverAdmin)
admin.site.site_header = "Library App - admin panel"