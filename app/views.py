import logging

from django.http import JsonResponse
from rest_framework import viewsets

from app.models.pokemon import Pokemon
from app.serializers import PokemonSerializer
from app.services.crawler import perform_crawl


class PokemonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Pokemon.objects.all().prefetch_related("abilities", "forms", "moves")
    serializer_class = PokemonSerializer

    def list(self, request, *args, **kwargs):
        perform_crawl(100)
        return super().list(request, *args, **kwargs)
