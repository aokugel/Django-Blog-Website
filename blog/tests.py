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
        html = self.client.get('/').content.decode()
        self.assertRegex(html, r'href="/published/"[^>]*>About</a>')
        self.assertNotRegex(html, rf'href="/{newer.slug}/"[^>]*>About</a>')

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

    def test_htmx_comment_post_returns_just_the_confirmation(self):
        response = self.client.post('/published/', {'name': 'Bob', 'email': 'bob@example.com', 'body': 'Hello'}, HTTP_HX_REQUEST='true')
        self.assertContains(response, 'Comment received')
        self.assertNotContains(response, '<html')
        self.assertIn('HX-Request', response['Vary'])

    def test_htmx_invalid_comment_returns_form_with_errors(self):
        response = self.client.post('/published/', {'name': '', 'email': 'not-an-email', 'body': ''}, HTTP_HX_REQUEST='true')
        self.assertContains(response, 'This field is required.')
        self.assertContains(response, 'Enter a valid email address.')
        self.assertNotContains(response, '<html')
        self.assertFalse(Comment.objects.filter(email='not-an-email').exists())

    def test_comments_paginate_with_load_more(self):
        for n in range(2, 13):  # 12 approved comments in total, with Ann
            Comment.objects.create(post=self.published, name=f'Reader {n}', email='r@example.com', body='Hi', active=True)
        page_one = self.client.get('/published/')
        self.assertContains(page_one, '12 comments')
        self.assertContains(page_one, 'Load more comments')
        self.assertNotContains(page_one, 'Reader 11')

        page_two = self.client.get('/published/?page=2', HTTP_HX_REQUEST='true')
        self.assertContains(page_two, 'Reader 11')
        self.assertContains(page_two, 'Reader 12')
        self.assertNotContains(page_two, 'Load more comments')
        self.assertNotContains(page_two, '<html')
