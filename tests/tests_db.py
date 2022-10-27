from app.models.pokemon import Pokemon
from django.test import TestCase


class PokemonTestCase(TestCase):
    def setUp(self):
        Pokemon.objects.create(
            name="rossmon", description="A super cool pokemon with sharp teeth"
        )

    def test_pokemon_added_correctly(self):
        rossmon = Pokemon.objects.get(name="rossmon")
        self.assertEqual(rossmon.description, "A super cool pokemon with sharp teeth")
