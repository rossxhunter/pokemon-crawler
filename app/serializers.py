from rest_framework import serializers

from app.models.ability import Ability
from app.models.form import Form
from app.models.move import Move
from app.models.pokemon import Pokemon


class AbilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Ability
        fields = "__all__"


class FormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Form
        fields = "__all__"


class MoveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Move
        fields = "__all__"


class PokemonSerializer(serializers.ModelSerializer):
    abilities = AbilitySerializer(many=True)
    forms = FormSerializer(many=True)
    moves = MoveSerializer(many=True)

    class Meta:
        model = Pokemon
        fields = ["id", "name", "description", "abilities", "forms", "moves"]
