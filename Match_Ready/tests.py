from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from Match_Ready.models import Team, Match, Coach, Player, Fan
import json


class ViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="test_user", password="123")
        self.superuser = User.objects.create_superuser(username='admin', password='1234', email='admine@email.co.uk')
        self.team1 = Team.objects.create(name='test_team_1', team_id='1')
        self.team2 = Team.objects.create(name='test_team_2', team_id='2')
        # Just setting up a user, superuser, and two teams to test out functionality



    def test_creating_player(self): #These three tests just make sure a player, coach and fan can be made without issue from a blank user with no role
        self.client.login(username='test_user', password='123')
        player = Player.objects.create(user=self.user)
        self.assertTrue(Player.objects.filter(user=self.user).exists())

    def test_creating_coach(self):
        self.client.login(username='test_user', password='123')
        coach = Coach.objects.create(user=self.user)
        self.assertTrue(Coach.objects.filter(user=self.user).exists())

    def test_creating_fan(self):
        self.client.login(username='test_user', password='123')
        fan = Fan.objects.create(user=self.user)
        self.assertTrue(Fan.objects.filter(user=self.user).exists())




    def test_index_guest(self):
        response = self.client.get(reverse('Match_Ready:index'))
        self.assertEqual(response.status_code, 200)  # 200 is the HTTP status code for OK
        self.assertContains(response, 'Guest')
        # Testing that the index page shows 'Guest' if no one is logged in

    def test_index_logged_in(self):
        self.client.login(username='test_user', password='123')
        response = self.client.get(reverse('Match_Ready:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test_user')
        # Test to see if index shows the username when logged in




    def test_contact_superuser(self):
        response = self.client.get(reverse('Match_Ready:contact'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.superuser, response.context['superusers'])
        # Checks the contact page to see if the superuser is included in the context



    def test_add_match_post(self):
        post_data = {'team1':self.team1.team_id, 'team2':self.team2.team_id, 'match_date':timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
        response = self.client.post(reverse('Match_Ready:add_match'), post_data)
        self.assertEqual(response.status_code, 302) #the code for a redirect for html
        self.assertTrue(Match.objects.filter(team1=self.team1, team2 = self.team2).exists())
        #checks match to see if the new match that was just posted is present in the db and returns a boolean 

    def test_add_match_fail(self):
        post_data = {'team1':'yabadabadoo', 'team2':'shinglebop', 'match_date':timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
        response = self.client.post(reverse('Match_Ready:add_match'), post_data)
        self.assertEqual(response.status_code, 200) 
        self.assertIn('errors', response.context)
        #checks for bad data being put into the form




    def test_login_post(self):
        post_data = {'username':'test_user', 'password':'123'}
        response = self.client.post(reverse('Match_Ready:login'), post_data)
        self.assertEqual(response.status_code, 302)
        #since the response redirects you we know that login works otherwise you would have code 200 (not redirect)

    # def test_login_fail(self):
    #     post_data = {'username':'Luffy', 'password':'onepiece'}
    #     response = self.client.post(reverse('Match_Ready:login'), post_data)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn('errors', response.context)

    #     Just need to change some things arround in views for this to work nicely
    #     gotta alter login to have the error messages in the context dict rather than template logic like it currently is



    def test_logout(self):
        self.client.login(username = 'test_user', password = '123')
        response = self.client.get(reverse('Match_Ready:logout'))
        self.assertEqual(response.status_code, 302)

        #checking if the index page says guest as the user is no longer logged in
        response = self.client.get(reverse('Match_Ready:index'))
        self.assertEqual(response.status_code, 200) 
        self.assertContains(response, 'Guest')



    def test_fixtures(self):
        post_data = {'team1':self.team1.team_id, 'team2':self.team2.team_id, 'match_date':timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
        response = self.client.post(reverse('Match_Ready:add_match'), post_data)
        #creating a new match to see if fixtures page works

        response = self.client.post(reverse('Match_Ready:fixtures'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('upcoming_matches', response.context)
        #testing to see the that response had something 



    def test_my_team_no_team(self):
        self.client.login(username = 'test_user', password = '123')
        player = Player.objects.create(user=self.user)

        response = self.client.get(reverse('Match_Ready:my_team'))
        self.assertEqual(response.status_code, 302)



    def test_find_team(self):
        self.client.login(username = 'test_user', password = '123')
        player = Player.objects.create(user=self.user) #makes the test user a player


        post_data = {'team_id':self.team1.team_id}
        response = self.client.post(reverse('Match_Ready:find_team'), post_data)
        self.assertEqual(response.status_code, 302)
        
        player.refresh_from_db()
        self.assertEqual(player.team, self.team1)

    def test_find_team_fail(self):
        self.client.login(username = 'test_user', password = '123')
        player = Player.objects.create(user=self.user) #makes the test user a player

        post_data = {'team_id':'wimbolWomble'}
        response = self.client.post(reverse('Match_Ready:find_team'), post_data)
        self.assertEqual(response.status_code, 302)
        
        player.refresh_from_db()
        self.assertNotEqual(player.team, self.team1)



    def test_create_team(self):
        self.client.login(username='test_user', password='123')
        coach = Coach.objects.create(user=self.user)
        #making a coach to make the team :)

        post_data = {'team_name':'test_team_3', 'team_ID':'3'}
        response = self.client.post(reverse('Match_Ready:create_team'), post_data)
        self.assertEqual(response.status_code, 302)

        self.assertTrue(Team.objects.filter(name='test_team_3', team_id='3').exists())


    def test_create_team_fail_dupe(self):
        self.client.login(username='test_user', password='123')
        coach = Coach.objects.create(user=self.user)

        post_data = {'team_name':'test_team_3', 'team_ID':'3'} 
        response = self.client.post(reverse('Match_Ready:create_team'), post_data)
        self.assertEqual(response.status_code, 302)

        post_data = {'team_name':'test_team_3_dupe', 'team_ID':'3'} #making a dupe of the team to test failure
        response = self.client.post(reverse('Match_Ready:create_team'), post_data)
        self.assertEqual(response.status_code, 200)


        self.assertFalse(Team.objects.filter(name='test_team_3_dupe', team_id='3').exists()) #checking for the dupe and errors in the context dict
        self.assertIn('errors', response.context) 


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