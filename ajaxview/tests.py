# coding: utf-8

# import os
from django.test import LiveServerTestCase
from django.test import Client
from django import forms

from ajaxview.views import AbstractView
from ajaxview.views import AbstractPane


class NameForm(forms.Form):
    your_name = forms.EmailField(label='Your name')


class DashboardPane1(AbstractPane):
    def get(self):
        self.context.update({
            'additional_context': 'additional_context1'
        })
        return super(DashboardPane1, self).get(self.request)


class DashboardPane3(AbstractPane):
    def get(self):
        self.context.update({
            'form': NameForm()
        })
        return super(DashboardPane3, self).get()

    def post(self):
        form = NameForm(self.request.POST)
        form.is_valid()

        self.context.update({
            'form': form
        })
        return super(DashboardPane3, self).post()


class DashboardView(AbstractView):
    def __init__(self, *args, **kwargs):
        super(DashboardView, self).__init__(
            template_name="tests/dashboard.html",
            url='test',
            panes={
                'pane1': DashboardPane1(template_name='tests/pane1.html'),
                'pane2': DashboardPane1(template_name='tests/pane2.html'),
                'pane3': DashboardPane3(template_name='tests/pane3.html')
            }
        )


class AbstractViewTestCase(LiveServerTestCase):
    def setUp(self):
        self.client = Client()
        self.url = "/test/"
        self.resp = self.client.get('/test/')

    def test_dashboard_inherit(self):
        self.assertTrue('base.html' in self.resp.content)

        # Dashboard
        self.assertTrue('dashboard' in self.resp.content)

    def test_pane_urls(self):
        # Panes urls
        self.assertTrue('?pane=pane1' in self.resp.content)
        self.assertTrue('?pane=pane2' in self.resp.content)

    def test_pane_rendered(self):
        # Panes rendered content
        self.assertTrue('pane1-content' in self.resp.content)
        self.assertTrue('pane2-content' in self.resp.content)

    def test_pane_context(self):
        # Panes rendered content
        self.assertTrue('additional_context1' in self.resp.content)

    def test_ajax_pane(self):
        self.resp = self.client.get('/test/?pane=pane1')
        self.assertEqual(
            'pane1-content - additional_context1\n/test/?pane=pane1',
            self.resp.content
        )

    def test_pane_post(self):
        # Panes rendered content
        pass
        # self.assertTrue('additional_context1' in self.resp.content)
