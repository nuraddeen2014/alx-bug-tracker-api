from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from .models import BugPost, BugSolution, Comment, Tag, Upvote

User = get_user_model()


class APITestHelpers:
    def create_user(self, username='user', is_staff=False):
        user = User.objects.create_user(username=username, email=f'{username}@example.com', password='pass')
        if is_staff:
            user.is_staff = True
            user.is_superuser = True
            user.save()
        return user


class BugPostAPITests(APITestCase, APITestHelpers):
    def setUp(self):
        self.user = self.create_user('author')
        self.other = self.create_user('other')
        self.admin = self.create_user('admin', is_staff=True)
        self.post = BugPost.objects.create(title='Bug', description='desc', created_by=self.user)
        self.tag = Tag.objects.create(name='bug', slug='bug')

    def auth_as(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_list_public(self):
        res = self.client.get('/api/bug-post/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_requires_auth(self):
        res = self.client.post('/api/bug-post/', {'title': 'New', 'description': 'X'}, format='json')
        # Depending on auth classes, unauthenticated may return 401 or 403 (CSRF/session). Accept both.
        self.assertIn(res.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))
        self.auth_as(self.other)
        res = self.client.post('/api/bug-post/', {'title': 'New', 'description': 'X'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_update_by_author_allowed(self):
        self.auth_as(self.user)
        res = self.client.patch(f'/api/bug-post/{self.post.id}/', {'title': 'Updated'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated')

    def test_update_by_non_author_forbidden(self):
        self.auth_as(self.other)
        res = self.client.patch(f'/api/bug-post/{self.post.id}/', {'title': 'Hack'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_by_author(self):
        self.auth_as(self.user)
        res = self.client.delete(f'/api/bug-post/{self.post.id}/')
        self.assertIn(res.status_code, (status.HTTP_204_NO_CONTENT, status.HTTP_200_OK))

    def test_add_tags_author_or_admin(self):
        # create a new post to test
        post = BugPost.objects.create(title='T', description='D', created_by=self.user)
        # non-author cannot add tag
        self.auth_as(self.other)
        res = self.client.post(f'/api/bug-post/{post.id}/add_tags/', {'tag': self.tag.id}, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        # author can
        self.auth_as(self.user)
        res = self.client.post(f'/api/bug-post/{post.id}/add_tags/', {'tag': self.tag.id}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        self.assertTrue(post.tags.filter(id=self.tag.id).exists())

    def test_remove_tags_endpoint(self):
        post = BugPost.objects.create(title='T2', description='D2', created_by=self.user)
        post.tags.add(self.tag)
        self.auth_as(self.user)
        # attempt to remove
        res = self.client.post(f'/api/bug-post/{post.id}/remove_tags/', {'tag': self.tag.id}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        self.assertFalse(post.tags.filter(id=self.tag.id).exists())


class BugSolutionAPITests(APITestCase, APITestHelpers):
    def setUp(self):
        self.user = self.create_user('author')
        self.other = self.create_user('other')
        self.solution = None
        self.post = BugPost.objects.create(title='Bug', description='desc', created_by=self.user)

    def auth_as(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_list_public_and_create_requires_auth(self):
        res = self.client.get('/api/bug-solution/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res = self.client.post('/api/bug-solution/', {'description': 'sol', 'bug_post': self.post.id}, format='json')
        # unauthenticated may return 401 or 403
        self.assertIn(res.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))
        self.auth_as(self.other)
        res = self.client.post('/api/bug-solution/', {'description': 'sol', 'bug_post': self.post.id}, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.solution = BugSolution.objects.get(id=res.data['id'])
        self.assertEqual(self.solution.created_by, self.other)

    def test_update_delete_permissions(self):
        self.auth_as(self.other)
        res = self.client.post('/api/bug-solution/', {'description': 's', 'bug_post': self.post.id}, format='json')
        sol_id = res.data['id']
        # non-author cannot update another's solution (OnlyAuthorEditsOrDeletes applies)
        self.auth_as(self.user)
        res = self.client.patch(f'/api/bug-solution/{sol_id}/', {'description': 'X'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_upvote_toggle_and_restrictions(self):
        # create a solution by author
        self.auth_as(self.user)
        res = self.client.post('/api/bug-solution/', {'description': 's', 'bug_post': self.post.id}, format='json')
        sol_id = res.data['id']
        # attempt to upvote own solution -> should 403
        res = self.client.post(f'/api/bug-solution/{sol_id}/upvote/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        # create a vote by other user
        self.auth_as(self.other)
        # authenticated other can upvote (toggle on then off)
        self.auth_as(self.other)
        res = self.client.post(f'/api/bug-solution/{sol_id}/upvote/')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['action'], 'voted')
        # second toggle should unvote
        res2 = self.client.post(f'/api/bug-solution/{sol_id}/upvote/')
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.data['action'], 'unvoted')


class CommentAPITests(APITestCase, APITestHelpers):
    def setUp(self):
        self.user = self.create_user('author')
        self.other = self.create_user('other')
        self.post = BugPost.objects.create(title='B', description='D', created_by=self.user)
        self.auth_as(self.user)
        res = self.client.post('/api/bug-solution/', {'description': 's', 'bug_post': self.post.id}, format='json')
        self.solution_id = res.data['id']

    def auth_as(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_comment_create_and_permissions(self):
        # unauthenticated create forbidden (may be 401 or 403 depending on auth classes)
        self.client.credentials()  # remove credentials
        res = self.client.post('/api/comment/', {'description': 'c', 'bug_solution': self.solution_id}, format='json')
        self.assertIn(res.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))
        # authenticated create
        self.auth_as(self.other)
        res = self.client.post('/api/comment/', {'description': 'c', 'bug_solution': self.solution_id}, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        comment_id = res.data['id']
        # update by non-author should be forbidden
        self.auth_as(self.user)
        res = self.client.patch(f'/api/comment/{comment_id}/', {'description': 'x'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class TagAPITests(APITestCase, APITestHelpers):
    def setUp(self):
        self.user = self.create_user('user')
        self.admin = self.create_user('admin', is_staff=True)

    def auth_as(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_tag_list_public_and_create_admin_only(self):
        res = self.client.get('/api/tag/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # non-admin cannot create
        self.auth_as(self.user)
        res = self.client.post('/api/tag/', {'name': 't', 'slug': 't'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        # admin can
        self.auth_as(self.admin)
        res = self.client.post('/api/tag/', {'name': 't', 'slug': 't'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)


class MiscEndpointsTests(APITestCase):
    def test_health_endpoint(self):
        res = self.client.get('/health/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json(), {'status': 'ok'})

    def test_openapi_schema_available(self):
        res = self.client.get('/openapi/')
        # Accept either 200 OK or 302 if auth redirects; primarily assert it's reachable
        self.assertIn(res.status_code, (status.HTTP_200_OK, status.HTTP_302_FOUND))
