from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from Match_Ready.models import Team, Match, Coach, Player, Fan

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

