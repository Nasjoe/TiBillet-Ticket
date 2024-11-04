import logging

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

from BaseBillet.views import get_context
from actions.models import Action, Vote

logger = logging.getLogger(__name__)


# Create your views here.


class ActionsMVT(viewsets.ViewSet):
    authentication_classes = [SessionAuthentication, ]
    permission_classes = [AllowAny, ]

    def list(self, request: HttpRequest):
        template_context = get_context(request)
        template_context["actions"] = Action.objects.filter(parent__isnull=True).prefetch_related('children')
        response = render(
            request, "action/list.html",
            context=template_context,
        )
        # Pour rendre la page dans un iframe, on vide le header X-Frame-Options pour dire au navigateur que c'est ok.
        response['X-Frame-Options'] = '' if template_context.get('embed') else 'DENY'
        return response

    @action(methods=['GET'], detail=True)
    def vote(self, request, pk=None):
        logger.info('pk : {pk}')
        action = get_object_or_404(Action, pk=pk)
        user = request.user
        if user.is_authenticated:
            Vote.objects.get_or_create(user=user, action=action)
            action.refresh_from_db()

        # Return the button with the updated vote count
        html_content = f'<button class="btn btn-small btn-success">{action.votes.count()}</button>'
        return HttpResponse(html_content, content_type="text/html")
