from django.urls import path

from apps.book.api_endpoints import AudioBookDetailView, AudioBookListView, BookDetailView, BookListView

app_name = "book"

urlpatterns = [
    path("BookList/", BookListView.as_view(), name="book-list"),
    path("BookDetail/<str:book_identifier>/", BookDetailView.as_view(), name="book-detail"),
    path("AudioBookList/<str:book_identifier>/", AudioBookListView.as_view(), name="audio-book-list"),
    path("AudioBookDetail/<int:pk>/", AudioBookDetailView.as_view(), name="audio-book-detail"),
]
