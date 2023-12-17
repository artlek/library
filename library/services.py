from . models import Book, Borrowing, Author
from django.contrib.auth.models import User
from django.contrib import messages
import datetime
from datetime import date
from django.views import View
from django.views.generic.detail import SingleObjectMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.http import Http404
from django.views.generic import UpdateView
import re


class CheckUserGroup():
    def is_librarian(user):
        return user.groups.filter(name='Librarian').exists()
    def is_reader(user):
        return user.groups.filter(name='Reader').exists()


class IfBookExists():
    def check(book_id):
        return True if Book.objects.filter(pk=book_id, is_deleted=False).exists() else False
    

class IfBookIsBorrowed():
    def check(book_id):
        return True if Book.objects.filter(pk=book_id, is_borrowed=True).exists() else False


class CheckBookToBorrow():
    def check(user, book_id):
        if CheckUserGroup.is_reader(user):
            if IfBookExists.check(book_id):
                if IfBookIsBorrowed.check(book_id):
                    return False
                else:
                    return True
            else:
                return False
        else:
            return False
        

class ShowBorrowErrorMessages:
    def show(request, reader_id, book_id):
        if not (User.objects.filter(pk=reader_id).exists() and CheckUserGroup.is_reader(User.objects.get(pk=reader_id))):
            messages.warning(request, "Reader with given id does not exist", extra_tags="danger")
        if not IfBookExists.check(book_id):
            messages.warning(request, "Book with give id does not exist", extra_tags="danger")
        if IfBookIsBorrowed.check(book_id):
            messages.warning(request, "Book with given id is already borrowed", extra_tags="danger")
        

class BorrowBook():
    def borrow(reader_id, book_id):
        reader = User.objects.get(pk=reader_id)
        book = Book.objects.get(pk=book_id)
        book.is_borrowed = True
        borrowing = Borrowing(book=book, user=reader)
        book.save()
        borrowing.save()


# returns queryset of borrowed user books
class GetUserBookList():
    def get(user):
        borrowings = Borrowing.objects.filter(user=user, return_date__exact=None)
        book_ids = []
        for borrowing in borrowings:
            book_ids.append(borrowing.book.id)
        books = Book.objects.filter(id__in=book_ids)
        return books
    

# returns number of unreturned user books within given days
class CountBookAfterDeadline():
    def count(user_id, days):
        if Borrowing.objects.filter(user_id=user_id, return_date__exact=None).exists():
            deadline_date = date.today() - datetime.timedelta(days=days)
            books = Borrowing.objects.filter(user_id=user_id, return_date__exact=None, borrow_date__lt=deadline_date).count()
            return books
        else:
            return 0


# returns number of unreturned all books within given days
class CountAllBooksAfterDeadline():
    def count(days):
        if Borrowing.objects.filter(return_date__exact=None).exists():
            deadline_date = date.today() - datetime.timedelta(days=days)
            books = Borrowing.objects.filter(return_date__exact=None, borrow_date__lt=deadline_date).count()
            return books
        else:
            return 0
        

# returns number of all authors
class CountAuthors():
    def count():
        return Author.objects.filter(is_deleted=False).count()


# returns number of all readers
class CountReaders():
    def count():
        users = User.objects.filter(is_active=True)
        reader_counter = 0
        for user in users:
            if CheckUserGroup.is_reader(user):
                reader_counter += 1
        return reader_counter


# returns count of remaining days to return a book. If negative - a book is after deadline
class ComputeDaysLeftToReturn():
    def compute(borrowing, deadline):
        return deadline - ComputeBorrowingDays.compute(borrowing)
        
        
# returns count of borrowing days (how many days reader keeps a book)
class ComputeBorrowingDays():
    def compute(borrowing):
        TODAY = date.today()
        if borrowing.borrow_date == date.today() or borrowing.borrow_date == borrowing.return_date:
            return 1
        if borrowing.return_date == None:
            borrowing_days = str(TODAY - borrowing.borrow_date)
        else:
            borrowing_days = str(borrowing.return_date - borrowing.borrow_date)
        return int(borrowing_days.partition(" day")[0]) + 1
        

class GetLast5Borrowings():
    def __init__(self):
        self.objects = Borrowing.objects.filter().order_by("-borrow_date")[:5]
    def show(self):
        return self.objects
    

class GetLast5UserBorrowings(GetLast5Borrowings):
    def __init__(self, user_id):
        self.objects = Borrowing.objects.filter(user_id=user_id).order_by("-borrow_date")[:5]


# returns all reader objects
class GetReaders():
    def get():
        users = User.objects.filter()
        readers = []
        for user in users:
            if CheckUserGroup.is_reader(user):
                readers.append(user)
        return readers
    

# deletes model object from database (sets 'is_deleted' property to True)
class DeleteObjectView(View, SingleObjectMixin):
    def get(self, request, *args, **kwargs):
        if self.get_object().is_deleted == True:
            raise Http404(self.failed_message)
        object = self.get_object()
        object.is_deleted = True
        object.save(update_fields=["is_deleted"])
        messages.add_message(self.request, messages.SUCCESS, self.success_message)
        return redirect(self.path)
    

# edits model object
class EditObjectView(UpdateView):
    def get_success_url(self):
        return reverse(self.success_path, kwargs={"pk": self.object.pk})
    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, self.success_message)
        return super().form_valid(form)
    def dispatch(self, request, *args, **kwargs):
        if self.get_object().is_deleted == True:
            raise Http404(self.failed_message)
        return super().dispatch(request, *args, **kwargs)
    

# removes all unwanted marks (like /\=$?:# and space) from string
class Filter_string_to_base_marks():
    def filter(string):
        output = re.sub(re.compile('[\\\%=&?:#/}{]'), "", string)
        output = re.sub(re.compile('\s'), "%20", output)
        return output