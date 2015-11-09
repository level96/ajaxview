# coding: utf-8

from django.views.generic import View
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

PANE_IDENTIFIER = 'pane'


class AbstractView(View):
    template_name = None
    panes = {}
    context = {}
    url = None

    def __init__(self, template_name, panes, url, *args, **kwargs):
        self.template_name = template_name
        self.url = reverse(url)

        self.panes = panes

        self.context.update({
            'views': self.panes,
            'current_view': self
        })

    def setup_views(self, request):
        [
            view.set_up(request, name, self)
            for name, view in self.panes.items()
        ]

    def get(self, request, *args, **kwargs):
        self.setup_views(request)
        ajax_pane = request.GET.get('pane', None)

        if ajax_pane and ajax_pane in self.panes:
            return self.panes[ajax_pane].get()

        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        self.setup_views(request)
        ajax_pane = request.GET.get(PANE_IDENTIFIER, None)

        if ajax_pane and ajax_pane in self.panes:
            return self.panes[ajax_pane].post()

        return render(request, self.template_name, self.context)


class AbstractPane(View):
    template_name = None
    view = None
    name = None
    request = {}
    context = {}

    def __init__(self, template_name, *args, **kwargs):
        self.template_name = template_name
        self.context = {'current_pane': self}
        self.view = None
        self.name = None
        self.request = {}

    def set_up(self, request, name, view):
        self.request = request
        self.view = view
        self.name = name

    def get_url(self):
        return u"{}?{}={}".format(self.view.url, PANE_IDENTIFIER, self.name)

    def render(self):
        return mark_safe(self.get().content)

    def get(self, *args, **kwargs):
        return render(self.request, self.template_name, self.context)

    def post(self, *args, **kwargs):
        return render(self.request, self.template_name, self.context)
