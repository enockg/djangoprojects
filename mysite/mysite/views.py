"""Views for Zinnia entries"""
from django.views.generic.dates import BaseDateDetailView

from zinnia.models.entry import Entry
from zinnia.views.mixins.archives import ArchiveMixin
from zinnia.views.mixins.entry_cache import EntryCacheMixin
from zinnia.views.mixins.entry_preview import EntryPreviewMixin
from zinnia.views.mixins.entry_protection import EntryProtectionMixin
from zinnia.views.mixins.callable_queryset import CallableQuerysetMixin
from zinnia.views.mixins.templates import EntryArchiveTemplateResponseMixin
from django.template.defaultfilters import slugify
from django.http import HttpResponsePermanentRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.base import View
from django.views.generic.base import TemplateResponseMixin

import django_comments as comments


class EntryDateDetail(ArchiveMixin,
                      EntryArchiveTemplateResponseMixin,
                      CallableQuerysetMixin,
                      BaseDateDetailView):
    """
    Mixin combinating:
    - ArchiveMixin configuration centralizing conf for archive views
    - EntryArchiveTemplateResponseMixin to provide a
      custom templates depending on the date
    - BaseDateDetailView to retrieve the entry with date and slug
    - CallableQueryMixin to defer the execution of the *queryset*
      property when imported
    """
    queryset = Entry.published.on_site


class EntryDetail(EntryCacheMixin,
                  EntryPreviewMixin,
                  EntryProtectionMixin,
                  EntryDateDetail):
    """
    Detailled archive view for an Entry with password
    and login protections and restricted preview.
    """
	class CommentSuccess(TemplateResponseMixin, View):
    """
    View for handing the publication of a Comment on an Entry.
    Do a redirection if the comment is visible,
    else render a confirmation template.
    """
    template_name = 'comments/zinnia/entry/posted.html'

    def get_context_data(self, **kwargs):
        return {'comment': self.comment}

    def get(self, request, *args, **kwargs):
        self.comment = None

        if 'c' in request.GET:
            try:
                self.comment = comments.get_model().objects.get(
                    pk=request.GET['c'])
            except (ObjectDoesNotExist, ValueError):
                pass
        if self.comment and self.comment.is_public:
            return HttpResponsePermanentRedirect(
                self.comment.get_absolute_url(
                    '#comment-%(id)s-by-') + slugify(self.comment.user_name))

        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)