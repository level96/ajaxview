# coding: utf-8

# import os
from django.test import LiveServerTestCase
from django.test import Client
from django import forms
from django.views.generic.edit import FormMixin
from django.http import JsonResponse

from ajaxview.views import Page
from ajaxview.views import AjaxView


class NameForm(forms.Form):
    email = forms.EmailField(label='E-Mail')


class DashboardView1(AjaxView):
    def get_context_data(self):
        return {
            'additional_context': 'additional_context1'
        }


class DashboardView2(AjaxView):
    template_name = 'tests/view2.html'

    def get_context_data(self):
        return {}


class FormView(AjaxView, FormMixin):
    form_class = NameForm

    def get_context_data(self, *args, **kwargs):
        context = super(FormView, self).get_context_data(**kwargs)
        context['form'] = self.get_form()()
        return context

    def get_form(self):
        return NameForm

    def post(self, request, *args, **kwargs):
        form = self.get_form()(request.POST)
        form.is_valid()
        return JsonResponse({'errors': form.errors})


class DashboardPage(Page):
    def __init__(self, *args, **kwargs):
        view1 = DashboardView1(
            template_name='tests/view1.html',
            title=u"Übersichts-Seite"
        )
        view2 = DashboardView2(title=u"Übersichts-Seite 2")
        view3 = FormView(template_name='tests/view3.html')

        super(DashboardPage, self).__init__(
            template_name="tests/dashboard.html",
            views={'view1': view1, 'view2': view2, 'view3': view3}
        )


class LoginDashboardPage(Page):
    template_name = "tests/dashboard.html"


class NotLoggedIPage(Page):
    template_name = "tests/not-logged-in.html"


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
        self.assertTrue('view1' in self.resp.content)
        self.assertTrue('view2' in self.resp.content)

    def test_view_context(self):
        # views rendered content
        self.assertTrue('additional_context1' in self.resp.content)

    def test_ajax_view(self):
        resp = self.client.get(
            '/test/?view=view1',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertTrue('additional_context1' in resp.content)

    def test_view_call(self):
        resp = self.client.get('/test/?view=view1')
        self.assertEqual(resp.status_code, 400)

        resp = self.client.get(
            '/test/?view=view1',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('view1' in resp.content)

        resp = self.client.get(
            '/test/?view=view2',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertTrue('view2' in resp.content)

        resp = self.client.get(
            '/test/?view=view3',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertTrue('view3' in resp.content)

    def test_page_post_not_supported(self):
        resp = self.client.post('/test/', {})
        self.assertEqual(resp.status_code, 400)

    def test_view_post_bad_request(self):
        resp = self.client.post('/test/?view=view3', {})
        self.assertEqual(resp.status_code, 400)

    def test_view_post(self):
        # Post on a view
        resp = self.client.post(
            '/test/?view=view3',
            {},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertTrue('errors' in resp.content)
        self.assertTrue('email' in resp.content)

        resp = self.client.post(
            '/test/?view=view3',
            {'email': 'invalid'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertTrue('errors' in resp.content)
        self.assertTrue('email' in resp.content)

    def test_user_not_logged_in(self):
        resp = self.client.get('/test-login-required/')
        self.assertEqual(resp.status_code, 302)
