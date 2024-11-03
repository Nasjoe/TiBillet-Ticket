from django.http import HttpRequest
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny

from BaseBillet.views import get_context
from actions.models import Action


# Create your views here.


class ActionsMVT(viewsets.ViewSet):
    authentication_classes = [SessionAuthentication, ]
    permission_classes = [AllowAny,]

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