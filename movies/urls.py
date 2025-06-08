from django.urls import path
from . import views
from .views import admin_dashboard, recommendations

urlpatterns=[
    path('',views.movie_list,name='movie_list'),
    path('<int:movie_id>/theaters',views.theater_list,name='theater_list'),
    path('theater/<int:theater_id>/seats/book/',views.book_seats,name='book_seats'),
    path('profile/', views.profile, name='profile'),
    path('<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('recommendations/', recommendations, name='recommendations'),
]