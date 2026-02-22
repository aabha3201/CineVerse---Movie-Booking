from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings as django_settings

def index(request):
    return render(request, 'index.html')


def page(request):
    movies = Movie.objects.all()
    return render(request, 'page.html', {"movies": movies})


def detail_page(request, id):
    mov = Movie.objects.all()
    m = Movie.objects.get(id=id)
    movies = []
    for i in mov:
        if i != m:
            movies.append(i)
    movie_cast = MovieCast.objects.filter(movie=m)
    return render(request, 'detail_page.html', {"movie_id": m, "cast": movie_cast, "movies": movies})


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect("/")
        else:
            messages.info(request, 'Invalid credentials')
            return redirect('login')
    else:
        return render(request, 'login.html')


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.info(request, 'Username already taken!')
                return redirect('signup')
            elif User.objects.filter(email=email).exists():
                messages.info(request, 'Email already exists')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                messages.info(request, 'User Created!')
                return render(request, 'confirmation.html')
        else:
            messages.info(request, 'Passwords do not match')
            return render(request, 'signup.html')
    else:
        return render(request, 'signup.html')


def confirmation(request):
    return render(request, 'confirmation.html')


def logout(request):
    auth.logout(request)
    return redirect("/")


def prebooking(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            movies = Movie.objects.all()
            return render(request, 'prebooking.html', {"movies": movies})

        if request.method == 'POST':
            movie = request.POST["movies"]
            date = request.POST["date"]
            return redirect("booking/" + movie + "/" + date + "/")
    else:
        return redirect('/login')


def booking(request, movie, date):
    if request.user.is_authenticated:
        seats = Seat.objects.all().order_by("seat_identity")
        booked_seats = []
        m = Movie.objects.get(name=movie)

        if request.method == "POST":
            selected_seats = request.POST.get("abc").split(";")
            selected_seats.pop()

            booked_list = []
            for i in selected_seats:
                seat = Seat.objects.get(seat_identity=i)
                Booking.objects.create(customer=request.user, seat=seat, movie=m, date=date)
                booked_list.append(i)

            # Try to send confirmation email
            if request.user.email:
                try:
                    seat_str = ", ".join(booked_list)
                    total = len(booked_list) * 100
                    subject = "CineVerse Booking Confirmation - {}".format(movie)
                    message = (
                        "Hi {},\n\n"
                        "Your booking has been confirmed! Here are your details:\n\n"
                        "Movie: {}\n"
                        "Date: {}\n"
                        "Seats: {}\n"
                        "Tickets: {}\n"
                        "Total: Rs.{}\n\n"
                        "Enjoy the show!\n"
                        "- CineVerse Team"
                    ).format(request.user.username, movie, date, seat_str, len(booked_list), total)
                    send_mail(
                        subject,
                        message,
                        django_settings.DEFAULT_FROM_EMAIL,
                        [request.user.email],
                        fail_silently=True,
                    )
                except Exception:
                    pass

            # Redirect to booking success page
            return render(request, 'booking_success.html', {
                "movie": movie,
                "date": date,
                "seats": booked_list,
                "total": len(booked_list) * 100,
                "ticket_count": len(booked_list),
            })

        X = Booking.objects.filter(movie=m, date=date)
        for i in X:
            booked_seats.append(i.seat.seat_identity)
        return render(request, 'booking.html', {"movie": movie, "date": date, "seats": seats, "booked_seats": booked_seats})
    else:
        return redirect('/login')
