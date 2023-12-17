from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import Http404
from .models import Book, Borrowing, Author, Publisher, Cover, Category
from .forms import (
    LoginForm, 
    AddBookForm, 
    RegistrationForm,
    BorrowingForm, 
    AddAuthorForm, 
    AddPublisherForm, 
    AddCoverForm, 
    ReturnForm, 
    AddCategoryForm, 
    CatalogueForm
    )
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import user_passes_test, login_required
from django.views import View
from django.utils.decorators import method_decorator
from datetime import date
from django.http import Http404
from django.views.generic import ListView, DetailView, CreateView
from django.views.generic.detail import SingleObjectMixin
from . services import (
    CheckBookToBorrow, 
    IfBookIsBorrowed, 
    ShowBorrowErrorMessages, 
    BorrowBook,
    CountBookAfterDeadline, 
    CountAllBooksAfterDeadline,
    CountAuthors,
    CheckUserGroup,
    CountReaders,
    ComputeDaysLeftToReturn,
    GetLast5Borrowings,
    GetLast5UserBorrowings,
    GetReaders,
    ComputeBorrowingDays,
    IfBookExists,
    DeleteObjectView,
    EditObjectView,
    Filter_string_to_base_marks,
    )
from rest_framework import generics,filters
from . serializers import BookSerializer
from library.serializers import BookSerializer
from rest_framework.reverse import reverse
from django_filters.rest_framework import DjangoFilterBackend
import json, re
from urllib.request import urlopen
from django.core.paginator import Paginator
    

class IndexView(View):
    template = "library/index.html"
    def get(self, request, *args, **kwargs):
        return render(request, self.template)
    

class RegistrationView(View):
    form_class = RegistrationForm
    template = "library/registration.html"
    group = "reader_group"
    group_name = "Reader"
    header = "Registration"
    message = "You have successfully signed up!"

    def get(self, request, *args, **kwargs):
        return render(request, self.template, {"form": self.form_class, "header": self.header})
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            group, created = Group.objects.get_or_create(name=self.group_name)
            group.user_set.add(user)
            messages.success(request, self.message)
            login(request, user)
            return redirect('index')
        else:
            return render(request, self.template, {"form": form, "header": self.header})
        

class LibrarianRegistrationView(RegistrationView):
    group = "librarian_group"
    group_name = "Librarian"
    form_class = RegistrationForm
    header = "Registration for librarian"
    context = {
        "form": form_class,
        "header": header,
    }
    message = "You have successfully signed up as librarian!"


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = LoginForm()
        return render(request, 'library/login.html', {'form': form})
    
    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request,username=username,password=password)
            if user:
                login(request, user)
                messages.success(request,f'Hi {username.title()}, welcome back!')
                if CheckUserGroup.is_reader(user):
                    return redirect("reader_dashboard")
                if CheckUserGroup.is_librarian(user):
                    return redirect("librarian_dashboard")
                
        messages.warning(request, f'Invalid username or password', extra_tags="danger")
        return render(request, 'library/login.html', {'form': form})
    

def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully signed out!")
    return redirect("index")
    

@method_decorator(login_required(login_url="/login"), name="dispatch")
class BooksView(ListView):
    template_name = "library/book/books.html"
    context_object_name = "books"
    paginate_by = 15
    model = Book
    def get_queryset(self):
        books = Book.objects.filter(is_deleted=False)
        counter = 1
        for book in books:
            book.counter = counter
            counter += 1
        return books


@method_decorator(login_required(login_url="/login"), name="dispatch")
class BookDetailView(DetailView):
    template_name = "library/book/book_detail.html"
    model = Book
    def dispatch(self, request, *args, **kwargs):
        if self.get_object().is_deleted == True:
            raise Http404("Book does not exist.")
        return super().dispatch(request, *args, **kwargs)
            

@method_decorator(user_passes_test(CheckUserGroup.is_librarian, login_url="/login/", redirect_field_name=None), name="dispatch")
class AuthorsView(ListView):
    template_name = "library/author/authors.html"
    context_object_name = "authors"
    paginate_by = 15
    model = Author
    def get_queryset(self):
        authors = Author.objects.filter(is_deleted=False)
        counter = 1
        for author in authors:
            author.counter = counter
            counter += 1
        return authors
    

@method_decorator(user_passes_test(CheckUserGroup.is_librarian, login_url="/login/", redirect_field_name=None), name="dispatch")
class PublishersView(ListView):
    template_name = "library/publisher/publishers.html"
    context_object_name = "publishers"
    model = Publisher
    paginate_by = 15
    def get_queryset(self):
        publishers = Publisher.objects.filter(is_deleted=False)
        counter = 1
        for publisher in publishers:
            publisher.counter = counter
            counter += 1
        return publishers


@method_decorator(user_passes_test(CheckUserGroup.is_librarian, login_url="/login/", redirect_field_name=None), name="dispatch")
class CoversView(ListView):
    template_name = "library/cover/covers.html"
    context_object_name = "covers"
    model = Cover
    paginate_by = 5
    def get_queryset(self):
        covers = Cover.objects.filter(is_deleted=False)
        counter = 1
        for cover in covers:
            cover.counter = counter
            counter += 1
        return covers
    

@method_decorator(user_passes_test(CheckUserGroup.is_librarian, login_url="/login/", redirect_field_name=None), name="dispatch")
class CategoriesView(ListView):
    template_name = "library/category/categories.html"
    context_object_name = "categories"
    model = Category
    paginate_by = 15
    def get_queryset(self):
        categories = Category.objects.filter(is_deleted=False)
        counter = 1
        for category in categories:
            category.counter = counter
            counter += 1
        return categories


@method_decorator(user_passes_test(CheckUserGroup.is_librarian, login_url="/login/", redirect_field_name=None), name="dispatch")
class AddBookView(CreateView):
    model = Book
    template_name = "library/book/add_book.html"
    form_class = AddBookForm
    def get_success_url(self):
        return reverse("books")
    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, "Book has been successfully added.")
        return super().form_valid(form)
    

@method_decorator(user_passes_test(CheckUserGroup.is_librarian, login_url="/login/", redirect_field_name=None), name="dispatch")
class AddAuthorView(CreateView):
    model = Author
    template_name = "library/author/add_author.html"
    form_class = AddAuthorForm
    def get_success_url(self):
        return reverse("authors")
    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, "Author has been successfully added.")
        return super().form_valid(form)
    

@method_decorator(user_passes_test(CheckUserGroup.is_librarian, login_url="/login/", redirect_field_name=None), name="dispatch")
class AddCoverView(View):
    model = Cover
    template = "library/cover/add_cover.html"
    form_class = AddCoverForm
    def post(self, request, *args, **kwargs):
        form_class = self.form_class(request.POST)
        if form_class.is_valid():
            if Cover.objects.filter(name=self.request.POST.get("name")):
                messages.warning(request, "The kind of cover with given name already exists.", extra_tags="danger")
            else:
                cover = Cover(name=self.request.POST.get("name"))
                cover.save()
                messages.add_message(self.request, messages.SUCCESS, "Kind of cover has been successfully added.")
                return redirect("covers")
        return render(request, self.template, {'form': form_class})
    def get(self, request, *args, **kwargs):
        return render(request, self.template, {'form': self.form_class})


@method_decorator(user_passes_test(CheckUserGroup.is_librarian, login_url="/login/", redirect_field_name=None), name="dispatch")
class AddPublisherView(View):
    model = Publisher
    template = "library/publisher/add_publisher.html"
    form_class = AddPublisherForm
    def post(self, request, *args, **kwargs):
        form_class = self.form_class(request.POST)
        if form_class.is_valid():
            if Publisher.objects.filter(name=self.request.POST.get("name")):
                messages.warning(request, "Publisher with given name already exists.", extra_tags="danger")
            else:
                publisher = Publisher(name=self.request.POST.get("name"))
                publisher.save()
                messages.add_message(self.request, messages.SUCCESS, "Publisher has been successfully added.")
                return redirect("publishers")
        return render(request, self.template, {'form': form_class})
    def get(self, request, *args, **kwargs):
        return render(request, self.template, {'form': self.form_class})
    
@method_decorator(user_passes_test(CheckUserGroup.is_librarian, login_url="/login/", redirect_field_name=None), name="dispatch")
class AddCategoryView(View):
    model = Category
    template = "library/category/add_category.html"
    form_class = AddCategoryForm
    def post(self, request, *args, **kwargs):
        form_class = self.form_class(request.POST)
        if form_class.is_valid():
            if Category.objects.filter(name=self.request.POST.get("name")):
                messages.warning(request, "Category with given name already exists.", extra_tags="danger")
            else:
                category = Category(name=self.request.POST.get("name"))
                category.save()
                messages.add_message(self.request, messages.SUCCESS, "Category has been successfully added.")
                return redirect("categories")
        return render(request, self.template, {'form': form_class})
    def get(self, request, *args, **kwargs):
        return render(request, self.template, {'form': self.form_class})
    

@method_decorator(user_passes_test(CheckUserGroup.is_librarian, login_url="/login/", redirect_field_name=None), name="dispatch")
class EditBookView(EditObjectView):
    model = Book
    template_name = "library/book/edit_book.html"
    form_class = AddBookForm
    context_object_name = "book_object"
    success_path = "edit_book"
    success_message = "Book has been successfully edited."
    failed_message = "Book does not exist."
    

@method_decorator(user_passes_test(CheckUserGroup.is_librarian, login_url="/login/", redirect_field_name=None), name="dispatch")
class EditAuthorView(EditObjectView):
    model = Author
    template_name = "library/author/edit_author.html"
    form_class = AddAuthorForm
    context_object_name = "author_object"
    success_path = "edit_author"
    success_message = "Author has been successfully edited."
    failed_message = "Author does not exist."
    

@method_decorator(user_passes_test(CheckUserGroup.is_librarian, login_url="/login/", redirect_field_name=None), name="dispatch")
class EditCoverView(EditObjectView):
    model = Cover
    template_name = "library/cover/edit_cover.html"
    form_class = AddCoverForm
    context_object_name = "cover_object"
    success_path = "edit_cover"
    success_message = "Kind of cover has been successfully edited."
    failed_message = "Kind of cover does not exist."
    

@method_decorator(user_passes_test(CheckUserGroup.is_librarian, login_url="/login/", redirect_field_name=None), name="dispatch")
class EditPublisherView(EditObjectView):
    model = Publisher
    template_name = "library/publisher/edit_publisher.html"
    form_class = AddPublisherForm
    context_object_name = "publisher_object"
    success_path = "edit_publisher"
    success_message = "Publisher has been successfully edited."
    failed_message = "Publisher does not exist."
    

@method_decorator(user_passes_test(CheckUserGroup.is_librarian, login_url="/login/", redirect_field_name=None), name="dispatch")
class EditCategoryView(EditObjectView):
    model = Category
    template_name = "library/category/edit_category.html"
    form_class = AddCategoryForm
    context_object_name = "category_object"
    success_path = "edit_category"
    success_message = "Category has been successfully edited."
    failed_message = "Category does not exist."
    

@method_decorator(user_passes_test(CheckUserGroup.is_librarian, login_url="/login/", redirect_field_name=None), name="dispatch")
class DeleteBookView(View, SingleObjectMixin):
    model = Book
    def get(self, request, *args, **kwargs):
        if self.get_object().is_deleted == True:
            raise Http404("Book does not exist.")
        book = self.get_object()
        if IfBookIsBorrowed.check(book.id):
            messages.warning(request, "The book is already borrowed. You can not delete it.", extra_tags="danger")
            return redirect("edit_book", pk=book.id)
        else:
            book.is_deleted = True
            book.save(update_fields=["is_deleted"])
            messages.add_message(self.request, messages.SUCCESS, "Book " + book.title + " has been successfully deleted.")
            return redirect("books")
        

@method_decorator(user_passes_test(CheckUserGroup.is_librarian, login_url="/login/", redirect_field_name=None), name="dispatch")
class DeleteAuthorView(DeleteObjectView):
    model = Author
    path = "authors"
    failed_message = "Author does not extst."
    success_message = "Author has been successfully deleted."
    

@method_decorator(user_passes_test(CheckUserGroup.is_librarian, login_url="/login/", redirect_field_name=None), name="dispatch")
class DeletePublisherView(DeleteObjectView):
    model = Publisher
    path = "publishers"
    failed_message = "Publisher does not extst."
    success_message = "Publisher has been successfully deleted."
    

@method_decorator(user_passes_test(CheckUserGroup.is_librarian, login_url="/login/", redirect_field_name=None), name="dispatch")
class DeleteCoverView(DeleteObjectView):
    model = Cover
    path = "covers"
    failed_message = "Kind of cover does not extst."
    success_message = "Kind of cover has been successfully deleted."
    

@method_decorator(user_passes_test(CheckUserGroup.is_librarian, login_url="/login/", redirect_field_name=None), name="dispatch")
class DeleteCategoryView(DeleteObjectView):
    model = Category
    path = "categories"
    failed_message = "Category does not extst."
    success_message = "Category has been successfully deleted."
        

@method_decorator(user_passes_test(CheckUserGroup.is_librarian, login_url="/login/", redirect_field_name=None), name="dispatch")
class BorrowBookView(View):
    template = "library/book/borrow_book.html"
    form_class = BorrowingForm
    def get(self, request, *args, **kwargs):
        return render(request, self.template, {'form': self.form_class})
    def post(self, request, *args, **kwargs):
        reader_id = request.POST.get("reader_id")
        book_id = request.POST.get("book_id")
        form_class = BorrowingForm(request.POST)
        if form_class.is_valid():
            if request.POST.get("check") == "check":
                if User.objects.filter(pk=reader_id).exists() and CheckBookToBorrow.check(User.objects.get(pk=reader_id), book_id):
                    context = {
                        "form": form_class,
                        "user": User.objects.get(pk=reader_id),
                        "book": Book.objects.get(pk=book_id),
                    }
                    return render(request, self.template, context)
                else:
                    ShowBorrowErrorMessages.show(request, reader_id, book_id)
            if request.POST.get("borrow") == "borrow":
                if User.objects.filter(pk=reader_id).exists() and CheckBookToBorrow.check(User.objects.get(pk=reader_id), book_id):
                    BorrowBook.borrow(reader_id, book_id)
                    book = Book.objects.get(pk=book_id)
                    messages.add_message(self.request, messages.SUCCESS, "Book " + book.title + " has been borrowed")
                    return render(request, self.template, {'form': self.form_class})
                else:
                    ShowBorrowErrorMessages.show(request, reader_id, book_id)
        return render(request, self.template, {'form': form_class})
    

@method_decorator(user_passes_test(CheckUserGroup.is_librarian, login_url="/login/", redirect_field_name=None), name="dispatch")
class NewReturnView(View):
    template = "library/book/return_book.html"
    form_class = ReturnForm
    def get(self, request, *args, **kwargs):
        return render(request, self.template, {'form': self.form_class})
    def post(self, request, *args, **kwargs):
        book_id = request.POST.get("book_id")
        form_class = ReturnForm(request.POST)
        if form_class.is_valid():
            if IfBookExists.check(book_id):
                book = Book.objects.get(pk=book_id)
                if IfBookIsBorrowed.check(book_id):
                    book.is_borrowed = False
                    borrowing = Borrowing.objects.get(book_id=book_id, return_date__exact=None)
                    borrowing.return_date = date.today()
                    book.save(update_fields=["is_borrowed"])
                    borrowing.save(update_fields=["return_date"])
                    messages.add_message(self.request, messages.SUCCESS, "Book " + book_id + ": " + book.title + " has been returned.")
                    return render(request, self.template, {'form': self.form_class})
                else:
                    messages.warning(request, "Book " + book_id + ": " + book.title + " is not borrowed. You can not return it.", extra_tags="danger")
            else:
                messages.warning(request, "Book with id " + book_id + " does not exist.", extra_tags="danger")
        return render(request, self.template, {'form': self.form_class(request.POST)})


@method_decorator(login_required(login_url="/login"), name="dispatch")
class ProfileView(View):
    template_name = "library/profile.html"
    def get(self, request, *args, **kwargs):
        user = self.request.user
        context = {
            "user": user,
            }
        return render(request, self.template_name, context)
    

@method_decorator(user_passes_test(CheckUserGroup.is_librarian, login_url="/login/", redirect_field_name=None), name="dispatch")
class LibrarianDashboardView(View):
    template_name = "library/librarian/librarian_dashboard.html"
    books_total = Book.objects.filter(is_deleted=False).count()
    borrowed_books_count = Book.objects.filter(is_borrowed=True).count()
    books_after_deadline = CountAllBooksAfterDeadline.count(30)
    authors = CountAuthors.count()
    readers = CountReaders.count()
    last5borrowings = GetLast5Borrowings().show()
    context = {
        "books_total": books_total,
        "borrowed_books_count": borrowed_books_count,
        "books_after_deadline": books_after_deadline,
        "authors": authors,
        "readers": readers,
        "last5borrowings": last5borrowings,
        }
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)
    

@method_decorator(user_passes_test(CheckUserGroup.is_reader, login_url="/login/", redirect_field_name=None), name="dispatch")
class ReaderDashboardView(View):
    template_name = "library/reader/reader_dashboard.html"
    deadline_days = 30
    def get(self, request, *args, **kwargs):
        books_total = Borrowing.objects.filter(user_id=request.user.id).count()
        borrowed_books_count = Borrowing.objects.filter(user_id=request.user.id, return_date__exact=None).count()
        books_after_deadline = CountBookAfterDeadline.count(request.user.id, self.deadline_days)
        last5borrowings = GetLast5UserBorrowings(request.user.id).show()
        context = {
            "books_total": books_total,
            "borrowed_books_count": borrowed_books_count,
            "books_after_deadline": books_after_deadline,
            "last5borrowings": last5borrowings,
            }
        return render(request, self.template_name, context)
    

@method_decorator(login_required(login_url="/login"), name="dispatch")
class BorrowingsView(ListView):
    model = Borrowing
    deadline = 30
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if CheckUserGroup.is_librarian(self.request.user):
            self.template_name = "library/librarian/librarian_borrowings.html"
            borrowings = Borrowing.objects.filter().order_by("-borrow_date")
        if CheckUserGroup.is_reader(self.request.user):
            self.template_name = "library/reader/reader_borrowings.html"
            borrowings = Borrowing.objects.filter(user_id=self.request.user.id).order_by("-borrow_date")
        for borrowing in borrowings:
            if borrowing.return_date == None:
                borrowing.days_left = ComputeDaysLeftToReturn.compute(borrowing, self.deadline)
            borrowing.borrowing_days = ComputeBorrowingDays.compute(borrowing)
        context["borrowings"] = borrowings
        return context
    

@method_decorator(user_passes_test(CheckUserGroup.is_librarian, login_url="/login/", redirect_field_name=None), name="dispatch")
class ReadersView(View):
    template_name = "library/reader/readers.html"
    def get(self, request, *args, **kwargs):
        readers = GetReaders.get()
        paginator = Paginator(readers, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        context = {
            "readers": readers,
            "page_obj": page_obj
            }
        return render(request, self.template_name, context)
    

class BookViewApi(generics.ListAPIView):
    queryset = Book.objects.filter(is_deleted=False)
    serializer_class = BookSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'author__name', 'author__surname']
    filterset_fields = ['is_borrowed']


class BookCatalogueView(View):
    def generate_url(self, request, search_text):
        url_elements = [
            request.scheme,
            "://",
            request.META["HTTP_HOST"],
            "/books-api/?format=json&search=",
            search_text
        ]
        url = "".join(url_elements)
        return url
    template = "library/catalogue/book_catalogue.html"
    form_class = CatalogueForm
    search_text = ""
    def get(self, request, *args, **kwargs):
        if self.form_class(request.GET).is_valid():
            if request.GET.get("search"):
                self.search_text = Filter_string_to_base_marks.filter(request.GET.get("search"))
                self.form_class = CatalogueForm(request.GET)
        else:
            if request.GET.get("search"):
                self.form_class = CatalogueForm(request.GET)
        response = urlopen(self.generate_url(request, self.search_text))
        data_json = json.loads(response.read())
        counter = 1
        for obj in data_json:
            obj["counter"] = counter
            counter += 1
        paginator = Paginator(data_json, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        context = {
            "form": self.form_class,
            "books": page_obj,
            "search_text": self.search_text,
        }
        return render(request, self.template, context)