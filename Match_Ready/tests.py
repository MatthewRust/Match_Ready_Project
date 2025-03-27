from django.test import TestCase, Client # Import Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Team, Match, Player # Import your models
from django.utils import timezone
import json # To parse JSON responses

# Create your tests here.

class AttendMatchAjaxViewTests(TestCase):

    def setUp(self):
        # Create necessary objects for tests
        self.client = Client() # Test client instance

        # Create teams
        self.team1 = Team.objects.create(name="Test Team 1", team_id="T1")
        self.team2 = Team.objects.create(name="Test Team 2", team_id="T2")

        # Create a user and player
        self.test_user = User.objects.create_user(username='testplayer', password='password123')
        self.test_player = Player.objects.create(user=self.test_user, team=self.team1)

        # Create another user for different scenarios if needed
        self.other_user = User.objects.create_user(username='otherplayer', password='password123')

        # Create a match
        self.match = Match.objects.create(
            team1=self.team1,
            team2=self.team2,
            match_date=timezone.now() + timezone.timedelta(days=7)
        )

        # URL for the AJAX view
        self.attend_url = reverse('Match_Ready:attend_match_ajax')

    def test_attend_match_success(self):
        """ Test attending a match successfully via AJAX POST """
        # Log the user in
        self.client.login(username='testplayer', password='password123')

        initial_attendees = self.match.attendees
        initial_attendees_list_count = self.match.attendees_list.count()

        # Make the POST request (test client handles CSRF for logged-in users)
        response = self.client.post(self.attend_url, {'match_id': self.match.id})

        # Check response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['message'], 'You are now attending!')
        self.assertEqual(response_data['new_count'], initial_attendees + 1)

        # Check database state
        self.match.refresh_from_db() # Reload match data from DB
        self.assertEqual(self.match.attendees, initial_attendees + 1)
        self.assertEqual(self.match.attendees_list.count(), initial_attendees_list_count + 1)
        self.assertIn(self.test_user, self.match.attendees_list.all())

    def test_attend_match_not_logged_in(self):
        """ Test attending when not logged in (should redirect) """
        response = self.client.post(self.attend_url, {'match_id': self.match.id})

        # @login_required redirects to LOGIN_URL
        # For AJAX, this typically results in a 302 for the server,
        # but the JS often sees it as an error. We test the server response.
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('Match_Ready:login'), response.url) # Check it redirects to login

    def test_attend_match_get_request(self):
        """ Test sending GET request (should be disallowed) """
        self.client.login(username='testplayer', password='password123')
        response = self.client.get(self.attend_url, {'match_id': self.match.id})

        # @require_POST returns 405 Method Not Allowed for GET
        self.assertEqual(response.status_code, 405)

    def test_attend_match_missing_id(self):
        """ Test POST request without match_id """
        self.client.login(username='testplayer', password='password123')
        response = self.client.post(self.attend_url, {}) # No match_id data

        self.assertEqual(response.status_code, 400) # Bad Request
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'error')
        self.assertEqual(response_data['message'], 'Missing match ID')

    def test_attend_match_invalid_id(self):
        """ Test POST request with a non-existent match_id """
        self.client.login(username='testplayer', password='password123')
        invalid_id = self.match.id + 999 # An ID that likely doesn't exist
        response = self.client.post(self.attend_url, {'match_id': invalid_id})

        self.assertEqual(response.status_code, 404) # Not Found
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'error')
        self.assertEqual(response_data['message'], 'Match not found')

    def test_attend_match_already_attending(self):
        """ Test attending a match when already attending """
        self.client.login(username='testplayer', password='password123')

        # Manually add user first
        self.match.add_attendee(self.test_user)
        initial_attendees = self.match.attendees

        # Try to attend again
        response = self.client.post(self.attend_url, {'match_id': self.match.id})

        self.assertEqual(response.status_code, 400) # Bad Request
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'error')
        self.assertEqual(response_data['message'], 'You are already marked as attending.')
        self.assertTrue(response_data['already_attending'])

        # Verify count didn't change
        self.match.refresh_from_db()
        self.assertEqual(self.match.attendees, initial_attendees)

# === Add other test classes for your other views ===
# Example:
# class IndexViewTests(TestCase):
#     def test_index_view_loads(self):
#         client = Client()
#         response = client.get(reverse('Match_Ready:index'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'Match_Ready/index.html')
#         # Add more assertions about context or content