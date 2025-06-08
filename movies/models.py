from django.db import models
from django.contrib.auth.models import User 


class Movie(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="movies/")
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    cast = models.TextField()
    description = models.TextField(blank=True, null=True) 
    trailer_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class Theater(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class ShowTime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='showtimes')
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE, related_name='showtimes')
    time = models.DateTimeField()
    price = models.DecimalField(max_digits=6, decimal_places=2, default=200.00)

    def __str__(self):
        return f"{self.movie.name} at {self.theater.name} on {self.time.strftime('%Y-%m-%d %H:%M')}"



class Seat(models.Model):
    showtime = models.ForeignKey(ShowTime, on_delete=models.CASCADE, related_name='seats')
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=10)
    is_booked = models.BooleanField(default=False)



class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    showtime = models.ForeignKey(ShowTime, on_delete=models.CASCADE, null=True)  # <-- Add this
    booked_at = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=200.00)

    def __str__(self):
        return f'Booking by {self.user.username} for {self.seat.seat_number} at {self.theater.name}'