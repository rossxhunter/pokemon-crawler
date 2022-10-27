from app.models.pokemon import Pokemon
from app.services.crawler import perform_crawl
from django.test import TestCase


class CrawlerTestCase(TestCase):
    def setUp(self):
        perform_crawl(12)

    def test_pokemon_count(self):
        pokemon_count = Pokemon.objects.count()
        self.assertEqual(pokemon_count, 12)
