import re
import time

from django.contrib.auth.models import User
from django.core import signing
from django.test import TestCase

from .forms import SPAM_ERROR
from .models import Comment, Post


def comment_data(seconds_ago=10, **fields):
    """Valid comment form data, as if the form was rendered `seconds_ago` (the spam time trap needs >= 3)."""
    return {'name': 'Bob', 'email': 'bob@example.com', 'body': 'Hello',
            'ts': signing.dumps(int(time.time()) - seconds_ago), **fields}


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
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertNotContains(response, '{#')  # multi-line {# #} isn't a Django comment; it leaks as text

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

    def test_api_lists_only_approved_comments(self):
        Comment.objects.create(post=self.published, name='Spammer', email='s@example.com', body='spam', active=False)
        names = [c['name'] for c in self.client.get('/api/comments/').json()]
        self.assertEqual(names, ['Ann'])

    def test_api_hides_commenter_email(self):
        comments = self.client.get('/api/comments/').json()
        self.assertTrue(comments)
        self.assertTrue(all('email' not in c for c in comments))

    def test_comment_post_awaits_moderation(self):
        self.client.post('/published/', comment_data())
        comment = Comment.objects.get(name='Bob')
        self.assertEqual(comment.post, self.published)
        self.assertFalse(comment.active)

    def test_htmx_comment_post_returns_just_the_confirmation(self):
        response = self.client.post('/published/', comment_data(), HTTP_HX_REQUEST='true')
        self.assertContains(response, 'Comment received')
        self.assertNotContains(response, '<html')
        self.assertIn('HX-Request', response['Vary'])

    def test_htmx_invalid_comment_returns_form_with_errors(self):
        response = self.client.post('/published/', comment_data(name='', email='not-an-email', body=''), HTTP_HX_REQUEST='true')
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


class ReplyTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = User.objects.create(username='author')
        cls.post = Post.objects.create(title='Post', slug='post', author=author, content='x', status=1)
        cls.other = Post.objects.create(title='Other', slug='other', author=author, content='x', status=1)
        cls.top = Comment.objects.create(post=cls.post, name='Ann', email='a@example.com', body='Top', active=True)

    def reply(self, parent, slug='post', **headers):
        return self.client.post(f'/{slug}/', comment_data(body='A reply', parent=parent), **headers)

    def test_reply_is_saved_under_its_parent_awaiting_moderation(self):
        response = self.reply(self.top.pk, HTTP_HX_REQUEST='true')
        self.assertContains(response, 'Comment received')
        reply = Comment.objects.get(name='Bob')
        self.assertEqual((reply.parent, reply.post, reply.active), (self.top, self.post, False))

    def test_invalid_parents_are_rejected(self):
        nested = Comment.objects.create(post=self.post, parent=self.top, name='R', email='r@example.com', body='r', active=True)
        unapproved = Comment.objects.create(post=self.post, name='U', email='u@example.com', body='u', active=False)
        elsewhere = Comment.objects.create(post=self.other, name='E', email='e@example.com', body='e', active=True)
        for parent in (nested.pk, unapproved.pk, elsewhere.pk, 99999):
            with self.subTest(parent=parent):
                self.reply(parent)
                self.assertFalse(Comment.objects.filter(name='Bob').exists())

    def test_only_approved_replies_are_shown(self):
        Comment.objects.create(post=self.post, parent=self.top, name='Approved replier', email='r@example.com', body='r', active=True)
        Comment.objects.create(post=self.post, parent=self.top, name='Pending replier', email='p@example.com', body='p', active=False)
        response = self.client.get('/post/')
        self.assertContains(response, 'Approved replier')
        self.assertNotContains(response, 'Pending replier')
        self.assertContains(response, '2 comments')  # Ann + the approved reply

    def test_reply_forms_have_unique_element_ids(self):
        Comment.objects.create(post=self.post, name='Cat', email='c@example.com', body='Second', active=True)
        ids = re.findall(r'\sid="([^"]+)"', self.client.get('/post/').content.decode())
        self.assertEqual(len(ids), len(set(ids)), [i for i in ids if ids.count(i) > 1])


class SpamTrapTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = User.objects.create(username='author')
        Post.objects.create(title='Post', slug='post', author=author, content='x', status=1)

    def assert_rejected(self, data):
        response = self.client.post('/post/', data, HTTP_HX_REQUEST='true')
        self.assertContains(response, SPAM_ERROR.replace("'", '&#x27;'))
        self.assertFalse(Comment.objects.exists())

    def test_filled_honeypot_is_rejected(self):
        self.assert_rejected(comment_data(website='https://spam.example'))

    def test_submitting_too_fast_is_rejected(self):
        self.assert_rejected(comment_data(seconds_ago=1))

    def test_missing_or_forged_timestamp_is_rejected(self):
        for ts in ('', 'not-signed', signing.dumps(0)[:-3] + 'abc'):
            with self.subTest(ts=ts):
                self.assert_rejected(comment_data(ts=ts))

    def test_honeypot_is_rendered_but_hidden_from_keyboards(self):
        html = self.client.get('/post/').content.decode()
        self.assertRegex(html, r'<input[^>]*name="website"[^>]*tabindex="-1"|<input[^>]*tabindex="-1"[^>]*name="website"')

    def test_normal_comment_still_goes_through(self):
        response = self.client.post('/post/', comment_data(), HTTP_HX_REQUEST='true')
        self.assertContains(response, 'Comment received')
        self.assertEqual(Comment.objects.count(), 1)
