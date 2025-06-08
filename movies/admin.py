from django.contrib import admin
from .models import Movie, Theater, Seat, Booking, ShowTime  # include ShowTime

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['name', 'rating', 'cast', 'description','trailer_url']

@admin.register(Theater)
class TheaterAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(ShowTime)
class ShowTimeAdmin(admin.ModelAdmin):
    list_display = ['movie', 'theater', 'time']
    list_filter = ['movie', 'theater']
    search_fields = ['movie__name', 'theater__name']

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ['theater', 'seat_number', 'is_booked']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'seat', 'movie', 'theater', 'booked_at']
