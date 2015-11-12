# coding: utf-8

# import os
from django.test import LiveServerTestCase
from django.test import Client
from django import forms

from ajaxview.views import Page
from ajaxview.views import View


class NameForm(forms.Form):
    email = forms.EmailField(label='Your name')


class DashboardView(View):
    def get_context_data(self, request):
        return {
            'additional_context': 'additional_context1'
        }


class DashboardView3(View):
    def get_context_data(self, request):
        return {
            'form': NameForm()
        }

    def post_context_data(self, request):
        form = NameForm(self.request.POST)
        form.is_valid()

        return {
            'form': form
        }


class DashboardPage(Page):
    def __init__(self, *args, **kwargs):
        super(DashboardPage, self).__init__(
            template_name="tests/dashboard.html",
            url='test',
            views={
                'view1': DashboardView(template_name='tests/view1.html'),
                'view2': DashboardView(template_name='tests/view2.html'),
                'view3': DashboardView3(template_name='tests/view3.html')
            }
        )

    def get_context_data(self, request):
        return {
            'dashboard_form': NameForm()
        }

    def post_context_data(self, request):
        return {
            'dashboard_form': NameForm(request.POST)
        }


class PageTestCase(LiveServerTestCase):
    def setUp(self):
        self.client = Client()
        self.url = "/test/"
        self.resp = self.client.get('/test/')

    def test_dashboard_inherit(self):
        self.assertTrue('base.html' in self.resp.content)

        # Dashboard
        self.assertTrue('dashboard' in self.resp.content)

    def test_view_urls(self):
        # views urls
        self.assertTrue('?view=view1' in self.resp.content)
        self.assertTrue('?view=view2' in self.resp.content)

    def test_view_rendered(self):
        # views rendered content
        self.assertTrue('view1-content' in self.resp.content)
        self.assertTrue('view2-content' in self.resp.content)

    def test_view_context(self):
        # views rendered content
        self.assertTrue('additional_context1' in self.resp.content)

    def test_ajax_view(self):
        self.resp = self.client.get('/test/?view=view1')
        self.assertEqual(
            'view1-content - additional_context1\n/test/?view=view1',
            self.resp.content
        )

    def test_view_call(self):
        self.resp = self.client.get('/test/?view=1')
        self.assertTrue('view1-content' in self.resp.content)

        self.resp = self.client.get('/test/?view=2')
        self.assertTrue('view2-content' in self.resp.content)

        self.resp = self.client.get('/test/?view=3')
        self.assertTrue('view3-content' in self.resp.content)

    def test_view_post(self):
        # Post on a view
        self.resp = self.client.post('/test/?view=view3', {})
        self.assertTrue('view3-content' in self.resp.content)
        self.assertTrue('errorlist' in self.resp.content)

        self.resp = self.client.post(
            '/test/?view=view3',
            {'email': 'invalid'}
        )
        self.assertTrue('view3-content' in self.resp.content)
        self.assertTrue('Mail' in self.resp.content)

    def test_post(self):
        self.resp = self.client.post('/test/', {})
        self.assertTrue('base.html' in self.resp.content)
        self.assertTrue('dashboard' in self.resp.content)
        self.assertTrue('errorlist' in self.resp.content)

        self.resp = self.client.post(
            '/test/',
            {'email': 'invalid'}
        )
        self.assertTrue('base.html' in self.resp.content)
        self.assertTrue('dashboard' in self.resp.content)
        self.assertTrue('Mail' in self.resp.content)
