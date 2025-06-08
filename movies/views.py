from django.shortcuts import render, redirect ,get_object_or_404
from .models import Movie, Theater, Seat, Booking, ShowTime
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.utils import timezone
from .models import Booking
from django.core.mail import send_mail
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer




def movie_list(request):
    search_query = request.GET.get('search')
    if search_query:
        movies = Movie.objects.filter(name__icontains=search_query)
    else:
        movies = Movie.objects.all()
    return render(request, 'movies/movie_list.html', {'movies': movies})


def theater_list(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)

    
    theaters = Theater.objects.filter(showtimes__movie=movie).distinct()

    return render(request, 'movies/theater_list.html', {
        'movie': movie,
        'theaters': theaters
    })

@login_required(login_url='/login/')
def book_seats(request, theater_id):
    theater = get_object_or_404(Theater, id=theater_id)
    seats = Seat.objects.filter(theater=theater)

    if request.method == 'POST':
        selected_seats = request.POST.getlist('seats')
        error_seats = []
        booked_seats = []

        if not selected_seats:
            return render(request, "movies/seat_selection.html", {
                'theater': theater,
                "seats": seats,
                'error': "No seat selected"
            })

        for seat_id in selected_seats:
            seat = get_object_or_404(Seat, id=seat_id, theater=theater)
            if seat.is_booked:
                error_seats.append(seat.seat_number)
                continue
            try:
                Booking.objects.create(
                    user=request.user,
                    seat=seat,
                    movie=seat.showtime.movie,
                    theater=seat.showtime.theater,
                    showtime=seat.showtime,
                    price=seat.showtime.price
                )
                seat.is_booked = True
                seat.save()
                booked_seats.append(seat)
            except IntegrityError:
                error_seats.append(seat.seat_number)

        if error_seats:
            error_message = f"The following seats are already booked: {', '.join(error_seats)}"
            return render(request, 'movies/seat_selection.html', {
                'theater': theater,
                "seats": seats,
                'error': error_message
            })

        
        if booked_seats:
            channel_layer = get_channel_layer()
            for seat in booked_seats:
                async_to_sync(channel_layer.group_send)(
                    f"seats_{theater.id}",
                    {
                        'type': 'seat_update',
                        'seat_id': seat.id,
                        'is_booked': True,
                    }
                )

            first_seat = booked_seats[0]
            showtime = first_seat.showtime
            seat_numbers = ', '.join(seat.seat_number for seat in booked_seats)

            try:
                send_mail(
                    subject="🎟️ Booking Confirmation - BookMyShow",
                    message=f"Hi {request.user.username},\n\nYour booking was successful!\n\n"
                            f"Movie: {showtime.movie.name}\n"
                            f"Theater: {showtime.theater.name}\n"
                            f"Time: {showtime.time.strftime('%Y-%m-%d %I:%M %p')}\n"
                            f"Seats: {seat_numbers}\n\n"
                            f"Enjoy your show!",
                    from_email="noreply@bookmyshow.com",
                    recipient_list=[request.user.email],
                    fail_silently=False,
                )
                print("📧 Email sent.")
            except Exception as e:
                print("Failed to send email:", e)

            print("Booking and email successful!")

        return redirect('profile')

    return render(request, 'movies/seat_selection.html', {
        'theater': theater,
        "seats": seats
    })
    
@login_required(login_url='/login/')
def profile(request):
    user = request.user
    now = timezone.now()

    
    past_bookings = Booking.objects.filter(user=user, showtime__time__lt=now).order_by('-showtime__time')
    upcoming_bookings = Booking.objects.filter(user=user, showtime__time__gte=now).order_by('showtime__time')

    return render(request, 'movies/profile.html', {
        'past_bookings': past_bookings,
        'upcoming_bookings': upcoming_bookings
    })


def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    return render(request, 'movies/movie_detail.html', {'movie': movie})

@staff_member_required
def admin_dashboard(request):
    total_revenue = Booking.objects.aggregate(total=Sum('price'))['total'] or 0

   
    popular_movies = (
        Booking.objects
        .values('movie__name')
        .annotate(total_bookings=Count('id'))
        .order_by('-total_bookings')[:5]
    )

    
    busiest_theaters = (
        Booking.objects
        .values('theater__name')
        .annotate(total_bookings=Count('id'))
        .order_by('-total_bookings')[:5]
    )

    context = {
        'total_revenue': total_revenue,
        'popular_movies': popular_movies,
        'busiest_theaters': busiest_theaters,
    }

    return render(request, 'movies/admin_dashboard.html', context)


class CustomLoginView(LoginView):
    def get_success_url(self):
        if self.request.user.is_staff:
            return '/movies/admin-dashboard/'
        return '/'
    
@login_required
def recommendations(request):
    user = request.user
    booked_movies = Booking.objects.filter(user=user).values_list('movie__id', flat=True).distinct()

    if booked_movies:
        genres = Movie.objects.filter(id__in=booked_movies).values_list('genre', flat=True).distinct()
        recommended_movies = Movie.objects.filter(genre__in=genres).exclude(id__in=booked_movies).distinct()[:5]
    else:
        
        recommended_movies = Movie.objects.annotate(bookings=Count('booking')).order_by('-bookings')[:5]

    return render(request, 'movies/recommendations.html', {
        'recommended_movies': recommended_movies
    })
