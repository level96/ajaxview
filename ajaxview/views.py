# coding: utf-8

from django.views.generic import TemplateView
from django.shortcuts import render
from django.http import HttpResponseBadRequest
from django.utils.safestring import mark_safe

VIEW_IDENTIFIER = 'view'


class Page(TemplateView):
    views = {}
    context = {}
    url = None

    def __init__(self, template_name=None, views=None, *args, **kwargs):
        super(Page, self).__init__(*args, **kwargs)

        self.template_name = template_name
        self.views = views

        self.context = {
            'views': self.views,
            'current_view': self
        }

    def __setup_views(self, request):
        for name, view in self.views.items():
            view.set_up(request, name, self)

        self.url = request.path

    def get_url(self):
        return self.url

    def get(self, request, *args, **kwargs):
        self.__setup_views(request)
        ajax_view = request.GET.get(VIEW_IDENTIFIER, None)
        if ajax_view and ajax_view in self.views:
            if not request.is_ajax():
                return HttpResponseBadRequest()
            return self.views[ajax_view].get(request)

        self.context.update(self.get_context_data(**kwargs))
        return self.render_to_response(self.context)

    def post(self, request, *args, **kwargs):
        self.__setup_views(request)
        ajax_view = request.GET.get(VIEW_IDENTIFIER, None)
        if ajax_view and ajax_view in self.views:
            if not request.is_ajax():
                return HttpResponseBadRequest()
            return self.views[ajax_view].post(request, *args, **kwargs)

        return HttpResponseBadRequest("This View does not support POST")


class AjaxView(object):
    template_name = None
    page = None
    title = ''
    name = ''
    request = {}
    context = {}

    def __init__(self, template_name=None, title='', *args, **kwargs):
        if template_name:
            self.template_name = template_name
        self.title = title
        self.context = {
            'self': self,
            'title': self.title
        }

    def set_up(self, request, name, page):
        self.request = request
        self.page = page
        self.name = name
        if not self.title:
            self.title = name

    def get_url(self):
        return u"{}?{}={}".format(
            self.page.get_url(),
            VIEW_IDENTIFIER,
            self.name
        )

    def render(self):
        return mark_safe(self.get(self.request).content)

    def get(self, request, *args, **kwargs):
        self.context.update(self.get_context_data(*args, **kwargs))
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        raise NotImplementedError('This function is not implemented now')
