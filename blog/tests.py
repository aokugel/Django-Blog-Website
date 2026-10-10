from django.contrib.auth.models import User
from django.test import TestCase

from .models import Comment, Post


class SiteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = User.objects.create(username='author')
        cls.published = Post.objects.create(title='Published', slug='published', author=author, content='<p>Hi</p>', status=1)
        cls.draft = Post.objects.create(title='Draft', slug='draft', author=author, content='Secret', status=0)
        Comment.objects.create(post=cls.published, name='Ann', email='ann@example.com', body='Nice', active=True)

    def test_pages_render(self):
        for url in ['/', '/contact/', '/published/']:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_draft_is_hidden(self):
        self.assertEqual(self.client.get('/draft/').status_code, 404)

    def test_covid_page_is_gone(self):
        self.assertEqual(self.client.get('/covid/').status_code, 404)

    def test_about_link_points_at_oldest_published_post(self):
        newer = Post.objects.create(title='Newer', slug='newer', author=self.published.author, content='x', status=1)
        response = self.client.get('/')
        self.assertContains(response, 'href="/published/">About</a>')
        self.assertNotContains(response, f'href="/{newer.slug}/">About</a>')

    def test_api_hides_drafts(self):
        slugs = [p['slug'] for p in self.client.get('/api/posts/').json()]
        self.assertEqual(slugs, ['published'])

    def test_api_hides_commenter_email(self):
        comments = self.client.get('/api/comments/').json()
        self.assertTrue(comments)
        self.assertTrue(all('email' not in c for c in comments))

    def test_comment_post_awaits_moderation(self):
        self.client.post('/published/', {'name': 'Bob', 'email': 'bob@example.com', 'body': 'Hello'})
        comment = Comment.objects.get(name='Bob')
        self.assertEqual(comment.post, self.published)
        self.assertFalse(comment.active)
