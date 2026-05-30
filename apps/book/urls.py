from django.urls import path
from django.views.decorators.cache import cache_page

from apps.book.api_endpoints import AudioBookDetailView, AudioBookListView, BookDetailView, BookListView, HomeBookListView
from apps.book.api_endpoints import PlanToReadListAPIView, PlanToReadCreateAPIView, PlanToReadDeleteAPIView

app_name = "book"

urlpatterns = [
    path("BookList/", BookListView.as_view(), name="book-list"),
    path("HomeBookList/", cache_page(60 * 60)(HomeBookListView.as_view()), name="home-book-list"),
    path("BookDetail/<str:book_identifier>/", BookDetailView.as_view(), name="book-detail"),
    path("AudioBookList/<str:book_identifier>/", AudioBookListView.as_view(), name="audio-book-list"),
    path("AudioBookDetail/<int:pk>/", AudioBookDetailView.as_view(), name="audio-book-detail"),
    path("PlanToReadList/", PlanToReadListAPIView.as_view(), name="plan-to-read-list"),
    path("PlanToReadCreate/", PlanToReadCreateAPIView.as_view(), name="plan-to-read-create"),
    path("PlanToReadDelete/<int:book_id>/", PlanToReadDeleteAPIView.as_view(), name="plan-to-read-delete"),
]
