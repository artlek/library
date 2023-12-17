# LIBRARY APPLICATION
Library App is very simple app to manage books in a library. It may be helpful for a librarian but also for readers. Main function is adding books to the database with attributes like book title, author, publisher or number of pages. As a librarian you can borrow a book to a reader and return it. As a reader you got list of books with all informations about them. Library App also shows you count of days left to return borrowed book and informs you how many days you keep it.

To start you have to register as a librarian by registration form. If the database is empty you have to fill it with information about books, authors etc. It is possible only by user with librarian group. To borrow a book, first, any reader must by registered in the app. Second, the librarian can borrow a book to a reader by clicking 'borrow a book' button in 'borrowings' menu link. When it is done the borrowed book will be shown in list of borrowed books. Next the book can be returned.

Library App has Book Catalogue - additional API interface which uses Django REST framework. It is created only to browse book list and check availability of a book. You can use it without loggin in. 

Library Application uses technologies like Django, Django REST framework, Bootstrap and CSS. It is created only for education purposes. 

## How to use it
Is recommended use Docker to try this app.
1. Install Docker, run Docker Desktop.
2. Download this repository and unzip it.
3. Open app folder in terminal.
4. Build image in Docker by command: <code>docker-compose up --build -d</code>.
5. Now you can test the app - open localhost:8000 in your webbrowser.

App database is populated with base data. To test the app log in with 'librarian' username and 'brakhasla' password or 'reader' and 'brakhasla'. All data is fictitious.