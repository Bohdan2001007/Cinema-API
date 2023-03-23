from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.serializers import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Genre, Actor, CinemaHall, Movie, MovieSession, Ticket, Order
from .serializers import (
    GenreSerializer,
    ActorSerializer,
    CinemaHallSerializer,
    MovieSerializer,
    MovieSessionSerializer,
    TicketSerializer,
    OrderSerializer, MovieListSerializer
)
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

User = get_user_model()


class CinemaHallModelTestCase(TestCase):
    def test_cinema_hall_creation(self):
        hall = CinemaHall.objects.create(name="Hall 1", rows=10, seats_in_row=20)
        self.assertEqual(hall.name, "Hall 1")
        self.assertEqual(hall.rows, 10)
        self.assertEqual(hall.seats_in_row, 20)
        self.assertEqual(hall.capacity, 200)


class GenreModelTestCase(TestCase):
    def test_genre_creation(self):
        genre = Genre.objects.create(name="Action")
        self.assertEqual(genre.name, "Action")


class ActorModelTestCase(TestCase):
    def test_actor_creation(self):
        actor = Actor.objects.create(first_name="Brad", last_name="Pitt")
        self.assertEqual(actor.first_name, "Brad")
        self.assertEqual(actor.last_name, "Pitt")
        self.assertEqual(actor.full_name, "Brad Pitt")


class MovieModelTestCase(TestCase):
    def test_movie_creation(self):
        movie = Movie.objects.create(title="Test Movie", description="Test Movie Description", duration=120)
        self.assertEqual(movie.title, "Test Movie")
        self.assertEqual(movie.description, "Test Movie Description")
        self.assertEqual(movie.duration, 120)


class MovieSessionModelTestCase(TestCase):
    def test_movie_session_creation(self):
        hall = CinemaHall.objects.create(name="Hall 1", rows=10, seats_in_row=20)
        movie = Movie.objects.create(title="Test Movie", description="Test Movie Description", duration=120)
        session = MovieSession.objects.create(movie=movie, cinema_hall=hall, show_time="2023-03-22T12:00:00Z")
        self.assertEqual(session.movie, movie)
        self.assertEqual(session.cinema_hall, hall)


class OrderModelTestCase(TestCase):
    def test_order_creation(self):
        user = User.objects.create_user(email="test@example.com", password="testpass")
        order = Order.objects.create(user=user)
        self.assertEqual(order.user, user)


class TicketModelTestCase(TestCase):
    def test_ticket_creation(self):
        user = User.objects.create_user(email="test@example.com", password="testpass")
        hall = CinemaHall.objects.create(name="Hall 1", rows=10, seats_in_row=20)
        movie = Movie.objects.create(title="Test Movie", description="Test Movie Description", duration=120)
        session = MovieSession.objects.create(movie=movie, cinema_hall=hall, show_time="2023-03-22T12:00:00Z")
        order = Order.objects.create(user=user)
        ticket = Ticket.objects.create(movie_session=session, order=order, row=1, seat=1)
        self.assertEqual(ticket.movie_session, session)
        self.assertEqual(ticket.order, order)
        self.assertEqual(ticket.row, 1)
        self.assertEqual(ticket.seat, 1)


class GenreSerializerTestCase(TestCase):
    def test_genre_serializer(self):
        genre = Genre.objects.create(name="Drama")
        serializer = GenreSerializer(genre)
        data = serializer.data
        expected_data = {"id": genre.id, "name": "Drama"}
        self.assertEqual(data, expected_data)


class ActorSerializerTestCase(TestCase):
    def test_actor_serializer(self):
        actor = Actor.objects.create(first_name="Tom", last_name="Hanks")
        serializer = ActorSerializer(actor)
        data = serializer.data
        expected_data = {
            "id": actor.id,
            "first_name": "Tom",
            "last_name": "Hanks",
            "full_name": "Tom Hanks",
        }
        self.assertEqual(data, expected_data)


class CinemaHallSerializerTestCase(TestCase):
    def test_cinema_hall_serializer(self):
        cinema_hall = CinemaHall.objects.create(name="Hall 1", rows=10, seats_in_row=15)
        serializer = CinemaHallSerializer(cinema_hall)
        data = serializer.data
        expected_data = {
            "id": cinema_hall.id,
            "name": "Hall 1",
            "rows": 10,
            "seats_in_row": 15,
            "capacity": 150,
        }
        self.assertEqual(data, expected_data)


class MovieSerializerTestCase(TestCase):
    def test_movie_serializer(self):
        genre = Genre.objects.create(name="Drama")
        actor = Actor.objects.create(first_name="Tom", last_name="Hanks")
        movie = Movie.objects.create(title="Forrest Gump", description="A great movie", duration=120)
        movie.genres.add(genre)
        movie.actors.add(actor)
        movie.save()

        serializer = MovieSerializer(movie)
        data = serializer.data
        expected_data = {
            "id": movie.id,
            "title": "Forrest Gump",
            "description": "A great movie",
            "duration": 120,
            "genres": [genre.id],
            "actors": [actor.id],
        }
        self.assertEqual(data, expected_data)


class MovieSessionSerializerTestCase(TestCase):
    def test_movie_session_serializer(self):
        movie = Movie.objects.create(title="Forrest Gump", description="A great movie", duration=120)
        cinema_hall = CinemaHall.objects.create(name="Hall 1", rows=10, seats_in_row=15)
        movie_session = MovieSession.objects.create(show_time="2023-01-01T10:00:00Z", movie=movie, cinema_hall=cinema_hall)

        serializer = MovieSessionSerializer(movie_session)
        data = serializer.data
        expected_data = {
            "id": movie_session.id,
            "show_time": "2023-01-01T10:00:00Z",
            "movie": movie.id,
            "cinema_hall": cinema_hall.id,
        }
        self.assertEqual(data, expected_data)


class TestOrderSerializer(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword"
        )

        self.movie = Movie.objects.create(title="Forrest Gump", description="A great movie", duration=120)
        self.cinema_hall = CinemaHall.objects.create(name="Hall 1", rows=10, seats_in_row=15)
        self.movie_session = MovieSession.objects.create(show_time="2023-01-01T10:00:00Z", movie=self.movie, cinema_hall=self.cinema_hall)

    def test_order_serializer(self):
        order = Order.objects.create(user=self.user)
        ticket = Ticket.objects.create(movie_session=self.movie_session, order=order, row=1, seat=1)

        serializer = OrderSerializer(order)
        data = serializer.data
        expected_data = {
            "id": order.id,
            "tickets": [
                {
                    "id": ticket.id,
                    "row": 1,
                    "seat": 1,
                    "movie_session": self.movie_session.id
                },
            ],
            "created_at": order.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        }
        self.assertEqual(data, expected_data)


class TicketSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@example.com", password="testpassword")
        self.movie = Movie.objects.create(title="Forrest Gump", description="A great movie", duration=120)
        self.cinema_hall = CinemaHall.objects.create(name="Hall 1", rows=10, seats_in_row=15)
        self.movie_session = MovieSession.objects.create(movie=self.movie, cinema_hall=self.cinema_hall, show_time="2023-01-01T10:00:00Z")
        self.order = Order.objects.create(user=self.user)
        self.ticket = Ticket.objects.create(movie_session=self.movie_session, order=self.order, row=1, seat=1)

    def test_ticket_serializer(self):
        ticket_data = {
            "row": 2,
            "seat": 2,
            "movie_session": self.movie_session.id
        }

        serializer = TicketSerializer(data=ticket_data)
        is_valid = serializer.is_valid()
        self.assertTrue(is_valid)

        validated_data = serializer.validated_data
        self.assertEqual(validated_data["row"], 2)
        self.assertEqual(validated_data["seat"], 2)
        self.assertEqual(validated_data["movie_session"], self.movie_session)

        # Test ValidationError for invalid row or seat number
        invalid_ticket_data = {
            "row": 0,
            "seat": 2,
            "movie_session": self.movie_session.id
        }
        invalid_serializer = TicketSerializer(data=invalid_ticket_data)
        with self.assertRaises(ValidationError):
            invalid_serializer.is_valid(raise_exception=True)


class MovieViewSetTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@gmail.com', password='testpass')
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client = APIClient()

        self.genre1 = Genre.objects.create(name='Comedy')
        self.genre2 = Genre.objects.create(name='Action')
        self.actor1 = Actor.objects.create(first_name='Tom', last_name='Hanks')
        self.actor2 = Actor.objects.create(first_name='Brad', last_name='Pitt')
        self.cinema_hall1 = CinemaHall.objects.create(name='Cinema 1', rows=10, seats_in_row=20)
        self.cinema_hall2 = CinemaHall.objects.create(name='Cinema 2', rows=11, seats_in_row=20)

        self.movie1 = Movie.objects.create(
            title='Forrest Gump',
            description='A man with a low IQ has accomplished great things in his life and been present during significant historic events.',
            duration=142,
        )
        self.movie1.cinema_hall = self.cinema_hall1
        self.movie1.start_time = '2023-04-01T15:00:00Z'
        self.movie1.end_time = '2023-04-01T17:00:00Z'
        self.movie1.actors.add(self.actor1)
        self.movie1.genres.add(self.genre1)

        self.movie2 = Movie.objects.create(
            title='Forrest',
            description='A man wit a low IQ has accomplished great things in his life and been present during significant historic events.',
            duration=142,
        )
        self.movie2.cinema_hall = self.cinema_hall2
        self.movie2.start_time = '2023-04-01T16:00:00Z'
        self.movie2.end_time = '2023-04-01T18:00:00Z'
        self.movie2.actors.add(self.actor2)
        self.movie2.genres.add(self.genre2)

    def test_list_movies(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        url = reverse('cinema:movie-list')
        response = self.client.get(url, format='json')
        serializer = MovieListSerializer(
            Movie.objects.prefetch_related("genres", "actors"), many=True
        )
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_movies_filtered_by_title(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        url = reverse('cinema:movie-list') + '?title=Forrest'
        response = self.client.get(url, format='json')
        serializer = MovieListSerializer(
            Movie.objects.filter(title__icontains='Forrest').prefetch_related("genres", "actors"), many=True
        )
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_movies_filtered_by_genre(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        url = reverse('cinema:movie-list') + f'?genres={self.genre1.pk}'
        response = self.client.get(url, format='json')
        serializer = MovieListSerializer(
            Movie.objects.filter(genres=self.genre1).prefetch_related("genres", "actors"), many=True
        )
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_movies_filtered_by_actor(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        url = reverse('cinema:movie-list') + f'?actors={self.actor2.pk}'
        response = self.client.get(url, format='json')
        serializer = MovieListSerializer(
            Movie.objects.filter(actors=self.actor2).prefetch_related("genres", "actors"), many=True
        )
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
