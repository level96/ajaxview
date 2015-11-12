# coding: utf-8

from django.views.generic import View
from django.shortcuts import render
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

VIEW_IDENTIFIER = 'view'


class Page(View):
    template_name = None
    views = {}
    context = {}
    url = None

    def __init__(self, template_name, views, url, *args, **kwargs):
        self.template_name = template_name
        self.url = reverse(url)

        self.views = views

        self.context.update({
            'views': self.views,
            'current_view': self
        })

    def setup_views(self, request):
        [
            view.set_up(request, name, self)
            for name, view in self.views.items()
        ]

    def get_context_data(self, request, *args, **kwargs):
        return {}  # pragma: no cover

    def post_context_data(self, request, *args, **kwargs):
        return {}  # pragma: no cover

    def get(self, request, *args, **kwargs):
        self.setup_views(request)
        ajax_view = request.GET.get(VIEW_IDENTIFIER, None)

        if ajax_view and ajax_view in self.views:
            return self.views[ajax_view].get(request)

        self.context.update(self.get_context_data(request, *args, **kwargs))
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        self.setup_views(request)
        ajax_view = request.GET.get(VIEW_IDENTIFIER, None)

        if ajax_view and ajax_view in self.views:
            return self.views[ajax_view].post(request)

        self.context.update(self.post_context_data(request, *args, **kwargs))
        return render(request, self.template_name, self.context)


class View(View):
    template_name = None
    page = None
    name = None
    request = {}
    context = {}

    def __init__(self, template_name, *args, **kwargs):
        self.template_name = template_name
        self.context = {'current_view': self}
        self.page = None
        self.name = None
        self.request = {}

    def set_up(self, request, name, page):
        self.request = request
        self.page = page
        self.name = name

    def get_context_data(self, request, *args, **kwargs):
        return {}  # pragma: no cover

    def post_context_data(self, request, *args, **kwargs):
        return {}  # pragma: no cover

    def get_url(self):
        return u"{}?{}={}".format(self.page.url, VIEW_IDENTIFIER, self.name)

    def render(self):
        return mark_safe(self.get(self.request).content)

    def get(self, request, *args, **kwargs):
        self.context.update(self.get_context_data(request, *args, **kwargs))
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        self.context.update(self.post_context_data(request, *args, **kwargs))
        return render(request, self.template_name, self.context)
