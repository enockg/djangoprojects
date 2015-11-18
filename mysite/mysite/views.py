"""Test cases for Zinnia's views"""
  2 from datetime import datetime
  3 
  4 from django.test import TestCase
  5 from django.contrib.auth.models import User
  6 from django.contrib.sites.models import Site
  7 from django.template import TemplateDoesNotExist
  8 from django.utils.translation import ugettext_lazy as _
  9 
 10 from zinnia.models import Entry
 11 from zinnia.models import Category
 12 from zinnia.managers import PUBLISHED
 13 from zinnia.settings import PAGINATION
 14 
 15 
 16 class ZinniaViewsTestCase(TestCase):
 17     """Test cases for generic views used in the application,
 18     for reproducing and correcting issue :
 19     http://github.com/Fantomas42/django-blog-zinnia/issues#issue/3
 20     """
 21     urls = 'zinnia.tests.urls'
 22     fixtures = ['zinnia_test_data.json']
 23 
 24     def setUp(self):
 25         self.site = Site.objects.get_current()
 26         self.author = User.objects.get(username='admin')
 27         self.category = Category.objects.get(slug='tests')
 28 
 29     def create_published_entry(self):
 30         params = {'title': 'My test entry',
 31                   'content': 'My test content',
 32                   'slug': 'my-test-entry',
 33                   'tags': 'tests',
 34                   'creation_date': datetime(2010, 1, 1),
 35                   'status': PUBLISHED}
 36         entry = Entry.objects.create(**params)
 37         entry.sites.add(self.site)
 38         entry.categories.add(self.category)
 39         entry.authors.add(self.author)
 40         return entry
 41 
 42     def check_publishing_context(self, url, first_expected,
 43                                  second_expected=None):
 44         """Test the numbers of entries in context of an url,"""
 45         response = self.client.get(url)
 46         self.assertEquals(len(response.context['object_list']), first_expected)
 47         if second_expected:
 48             self.create_published_entry()
 49             response = self.client.get(url)
 50             self.assertEquals(len(response.context['object_list']), second_expected)
 51 
 52     def test_zinnia_entry_archive_index(self):
 53         self.check_publishing_context('/', 2, 3)
 54 
 55     def test_zinnia_entry_archive_year(self):
 56         self.check_publishing_context('/2010/', 2, 3)
 57 
 58     def test_zinnia_entry_archive_month(self):
 59         self.check_publishing_context('/2010/01/', 1, 2)
 60 
 61     def test_zinnia_entry_archive_day(self):
 62         self.check_publishing_context('/2010/01/01/', 1, 2)
 63 
 64     def test_zinnia_entry_detail(self):
 65         entry = self.create_published_entry()
 66         entry.sites.clear()
 67         # Check a 404 error, but the 404.html may no exist
 68         try:
 69             self.assertRaises(TemplateDoesNotExist, self.client.get,
 70                               '/2010/01/01/my-test-entry/')
 71         except AssertionError:
 72             response = self.client.get('/2010/01/01/my-test-entry/')
 73             self.assertEquals(response.status_code, 404)
 74 
 75         entry.template = 'zinnia/_entry_detail.html'
 76         entry.save()
 77         entry.sites.add(Site.objects.get_current())
 78         response = self.client.get('/2010/01/01/my-test-entry/')
 79         self.assertEquals(response.status_code, 200)
 80         self.assertTemplateUsed(response, 'zinnia/_entry_detail.html')
 81 
 82     def test_zinnia_entry_detail_login(self):
 83         entry = self.create_published_entry()
 84         entry.login_required = True
 85         entry.save()
 86         response = self.client.get('/2010/01/01/my-test-entry/')
 87         self.assertTemplateUsed(response, 'zinnia/login.html')
 88 
 89     def test_zinnia_entry_detail_password(self):
 90         entry = self.create_published_entry()
 91         entry.password = 'password'
 92         entry.save()
 93         response = self.client.get('/2010/01/01/my-test-entry/')
 94         self.assertTemplateUsed(response, 'zinnia/password.html')
 95         self.assertEquals(response.context['error'], False)
 96         response = self.client.post('/2010/01/01/my-test-entry/',
 97                                     {'password': 'bad_password'})
 98         self.assertTemplateUsed(response, 'zinnia/password.html')
 99         self.assertEquals(response.context['error'], True)
100         response = self.client.post('/2010/01/01/my-test-entry/',
101                                     {'password': 'password'})
102         self.assertEquals(response.status_code, 302)
103 
104     def test_zinnia_entry_channel(self):
105         self.check_publishing_context('/channel-test/', 2, 3)
106 
107     def test_zinnia_category_list(self):
108         self.check_publishing_context('/categories/', 1)
109         entry = Entry.objects.all()[0]
110         entry.categories.add(Category.objects.create(title='New category',
111                                                      slug='new-category'))
112         self.check_publishing_context('/categories/', 2)
113 
114     def test_zinnia_category_detail(self):
115         self.check_publishing_context('/categories/tests/', 2, 3)
116 
117     def test_zinnia_category_detail_paginated(self):
118         """Test case reproducing issue #42 on category
119         detail view paginated"""
120         for i in range(PAGINATION):
121             params = {'title': 'My entry %i' % i,
122                       'content': 'My content %i' % i,
123                       'slug': 'my-entry-%i' % i,
124                       'creation_date': datetime(2010, 1, 1),
125                       'status': PUBLISHED}
126             entry = Entry.objects.create(**params)
127             entry.sites.add(self.site)
128             entry.categories.add(self.category)
129             entry.authors.add(self.author)
130         response = self.client.get('/categories/tests/')
131         self.assertEquals(len(response.context['object_list']), PAGINATION)
132         response = self.client.get('/categories/tests/?page=2')
133         self.assertEquals(len(response.context['object_list']), 2)
134         response = self.client.get('/categories/tests/page/2/')
135         self.assertEquals(len(response.context['object_list']), 2)
136 
137     def test_zinnia_author_list(self):
138         self.check_publishing_context('/authors/', 1)
139         entry = Entry.objects.all()[0]
140         entry.authors.add(User.objects.create(username='new-user',
141                                               email='new_user@example.com'))
142         self.check_publishing_context('/authors/', 2)
143 
144     def test_zinnia_author_detail(self):
145         self.check_publishing_context('/authors/admin/', 2, 3)
146 
147     def test_zinnia_tag_list(self):
148         self.check_publishing_context('/tags/', 1)
149         entry = Entry.objects.all()[0]
150         entry.tags = 'tests, tag'
151         entry.save()
152         self.check_publishing_context('/tags/', 2)
153 
154     def test_zinnia_tag_detail(self):
155         self.check_publishing_context('/tags/tests/', 2, 3)
156 
157     def test_zinnia_entry_search(self):
158         self.check_publishing_context('/search/?pattern=test', 2, 3)
159         response = self.client.get('/search/?pattern=ab')
160         self.assertEquals(len(response.context['object_list']), 0)
161         self.assertEquals(response.context['error'], _('The pattern is too short'))
162         response = self.client.get('/search/')
163         self.assertEquals(len(response.context['object_list']), 0)
164         self.assertEquals(response.context['error'], _('No pattern to search found'))
165 
166     def test_zinnia_sitemap(self):
167         response = self.client.get('/sitemap/')
168         self.assertEquals(len(response.context['entries']), 2)
169         self.assertEquals(len(response.context['categories']), 1)
170         entry = self.create_published_entry()
171         entry.categories.add(Category.objects.create(title='New category',
172                                                      slug='new-category'))
173         response = self.client.get('/sitemap/')
174         self.assertEquals(len(response.context['entries']), 3)
175         self.assertEquals(len(response.context['categories']), 2)
176 
177     def test_zinnia_trackback(self):
178         # Check a 404 error, but the 404.html may no exist
179         try:
180             self.assertRaises(TemplateDoesNotExist, self.client.post,
181                               '/trackback/404/')
182         except AssertionError:
183             response = self.client.post('/trackback/404/')
184             self.assertEquals(response.status_code, 404)
185         self.assertEquals(self.client.post('/trackback/test-1/').status_code, 302)
186         self.assertEquals(self.client.get('/trackback/test-1/').status_code, 302)
187         entry = Entry.objects.get(slug='test-1')
188         entry.pingback_enabled = False
189         entry.save()
190         self.assertEquals(self.client.post('/trackback/test-1/', {'url': 'http://example.com'}).content,
191                           '<?xml version="1.0" encoding="utf-8"?>\n<response>\n  \n  <error>1</error>\n  '
192                           '<message>Trackback is not enabled for Test 1</message>\n  \n</response>\n')
193         entry.pingback_enabled = True
194         entry.save()
195         self.assertEquals(self.client.post('/trackback/test-1/', {'url': 'http://example.com'}).content,
196                           '<?xml version="1.0" encoding="utf-8"?>\n<response>\n  \n  <error>0</error>\n  \n</response>\n')
197         self.assertEquals(self.client.post('/trackback/test-1/', {'url': 'http://example.com'}).content,
198                           '<?xml version="1.0" encoding="utf-8"?>\n<response>\n  \n  <error>1</error>\n  '
199                           '<message>Trackback is already registered</message>\n  \n</response>\n')