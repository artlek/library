from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Book, Author, Publisher, Cover, Category
from django.forms import ModelForm


class LoginForm(forms.Form):
    username = forms.CharField(max_length=65, widget=forms.TextInput(attrs={"class": "form-control mx-2 mb-2 gray-text"}))
    password = forms.CharField(max_length=65, widget=forms.TextInput(attrs={"class": "form-control mx-2 mb-2 gray-text", "type": "password"}))
    

class RegistrationForm(UserCreationForm):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields["username"].widget.attrs.update({
			"class": "form-control mx-2 gray-text",
		})
		self.fields["first_name"].widget.attrs.update({
			"class": "form-control mx-2 gray-text",
		})
		self.fields["first_name"].required=True
		self.fields["last_name"].widget.attrs.update({
			"class": "form-control mx-2 gray-text",
		})
		self.fields["last_name"].required=True
		self.fields["email"].widget.attrs.update({
			"class": "form-control mx-2 gray-text",
			"type": "email",
		})
		self.fields["password1"].widget.attrs.update({
			"class": "form-control mx-2 gray-text",
			"type": "password",
		})
		self.fields["password2"].widget.attrs.update({
			"class": "form-control mx-2 gray-text",
			"type": "password",
		})

	class Meta:
		model = User
		fields = ["username", "first_name", "last_name", "email", "password1", "password2"]


class AddBookForm(ModelForm):
    class Meta:
        model = Book
        fields = ["title", "author", "published", "pages", "publisher", "cover", "category", "description"]
        widgets = {
              "title": forms.TextInput(attrs={"class": "form-control gray-text"}),
              "author": forms.Select(attrs={"class": "form-control gray-text"}),
              "published": forms.DateInput(attrs={"type": "date", "class": "form-control gray-text"}),
              "pages": forms.NumberInput(attrs={"class": "form-control gray-text"}),
              "publisher": forms.Select(attrs={"class": "form-control gray-text"}),
              "category": forms.Select(attrs={"class": "form-control gray-text"}),
              "cover": forms.Select(attrs={"class": "form-control gray-text"}),
              "description": forms.Textarea(attrs={"class": "form-control gray-text", "rows": 4}),
		}
        

class AddAuthorForm(ModelForm):
    class Meta:
        model = Author
        fields = ["name", "surname"]
        widgets = {
              "name": forms.TextInput(attrs={"class": "form-control gray-text"}),
              "surname": forms.TextInput(attrs={"class": "form-control gray-text"}),
		}
        

class AddPublisherForm(ModelForm):
    class Meta:
        model = Publisher
        fields = ["name"]
        widgets = {
              "name": forms.TextInput(attrs={"class": "form-control gray-text"}),
		}
        

class AddCoverForm(ModelForm):
    class Meta:
        model = Cover
        fields = ["name"]
        widgets = {
              "name": forms.TextInput(attrs={"class": "form-control gray-text"}),
		}


class AddCategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ["name"]
        widgets = {
              "name": forms.TextInput(attrs={"class": "form-control gray-text"}),
		}
        

class BorrowingForm(forms.Form):
    reader_id = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control mb-2 gray-text"}), min_value=1)
    book_id = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control mb-2 gray-text"}), min_value=1)
    

class ReturnForm(forms.Form):
     book_id = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control mp-2 gray-text"}), min_value=1)


class CatalogueForm(forms.Form):
    search = forms.CharField(max_length=100, min_length=3, widget=forms.TextInput(attrs={"class": "form-control gray-text"}), label="Search for title or book author:")