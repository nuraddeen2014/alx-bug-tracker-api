from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()


class AccountsAPITests(APITestCase):
    def setUp(self):
        self.register_url = '/auth/register/'
        self.login_url = '/auth/login/'
        self.logout_url = '/auth/logout/'
        self.profile_url = '/auth/users/me/'
        self.users_list_url = '/auth/users/'
        self.token_url = '/api/api-token-auth/'

        # create a normal user
        self.user = User.objects.create_user(username='user', email='user@example.com', password='pass')
        # create admin
        self.admin = User.objects.create_superuser(username='admin', email='admin@example.com', password='pass')

    def test_register_creates_user_and_returns_token(self):
        payload = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'secret'
        }
        res = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)
        self.assertIn('user', res.data)
        self.assertEqual(res.data['user']['username'], 'newuser')

    def test_login_success_and_token(self):
        res = self.client.post(self.login_url, {'username': 'user', 'password': 'pass'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_login_failure(self):
        res = self.client.post(self.login_url, {'username': 'user', 'password': 'wrong'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_token_endpoint_returns_token(self):
        # obtain token via DRF built-in endpoint
        res = self.client.post(self.token_url, {'username': 'user', 'password': 'pass'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_logout_deletes_token(self):
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        # logout
        res = self.client.post(self.logout_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # token should be deleted
        self.assertFalse(Token.objects.filter(user=self.user).exists())

    def test_profile_get_and_patch(self):
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        # GET
        res = self.client.get(self.profile_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['username'], 'user')
        # PATCH: change name
        res = self.client.patch(self.profile_url, {'first_name': 'New'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['first_name'], 'New')
        # PATCH: attempt to change username (read-only)
        res = self.client.patch(self.profile_url, {'username': 'hacker'}, format='json')
        # username should remain unchanged
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'user')

    def test_admin_users_list_and_detail_permission(self):
        # non-admin cannot access
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        res = self.client.get(self.users_list_url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # admin can access list and detail
        admin_token, _ = Token.objects.get_or_create(user=self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {admin_token.key}')
        res = self.client.get(self.users_list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # detail
        res = self.client.get(f'{self.users_list_url}{self.user.id}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['username'], 'user')
