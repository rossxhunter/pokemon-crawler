from concurrent.futures import as_completed

import requests
from app.models.ability import Ability
from app.models.form import Form
from app.models.move import Move
from app.models.pokemon import Pokemon
from requests_futures.sessions import FuturesSession

session = FuturesSession()

pokeapi_base_url = "https://pokeapi.co/api/v2/"


def perform_crawl(num_pokemon):
    all_pokemon = get_all_pokemon(num_pokemon)
    pokemon_details = get_pokemon_details(all_pokemon)
    update_pokemon_db(pokemon_details)


def update_pokemon_db(pokemon):
    update_abilities(pokemon)
    update_forms(pokemon)
    update_moves(pokemon)
    update_pokemon(pokemon)
    update_pokemon_attributes(pokemon)


def update_pokemon_attributes(pokemon):
    pokemon_abilities = []
    pokemon_forms = []
    pokemon_moves = []
    all_pokemon = {p.name: p for p in Pokemon.objects.all()}
    all_abilities = {a.name: a for a in Ability.objects.all()}
    all_forms = {f.name: f for f in Form.objects.all()}
    all_moves = {m.name: m for m in Move.objects.all()}
    for p in pokemon:
        pokemon = all_pokemon[p["name"]]
        pokemon_abilities.extend(get_pokemon_abilities(p, pokemon, all_abilities))
        pokemon_forms.extend(get_pokemon_forms(p, pokemon, all_forms))
        pokemon_moves.extend(get_pokemon_moves(p, pokemon, all_moves))
    Pokemon.abilities.through.objects.bulk_create(
        pokemon_abilities, ignore_conflicts=True
    )
    Pokemon.forms.through.objects.bulk_create(pokemon_forms, ignore_conflicts=True)
    Pokemon.moves.through.objects.bulk_create(pokemon_moves, ignore_conflicts=True)


def get_pokemon_abilities(p, pokemon, all_abilities):
    pokemon_abilities = []
    for a in p["abilities"]:
        ability = all_abilities[a]
        pokemon_abilities.append(
            Pokemon.abilities.through(pokemon=pokemon, ability=ability)
        )
    return pokemon_abilities


def get_pokemon_forms(p, pokemon, all_forms):
    pokemon_forms = []
    for f in p["forms"]:
        form = all_forms[f]
        pokemon_forms.append(Pokemon.forms.through(pokemon=pokemon, form=form))
    return pokemon_forms


def get_pokemon_moves(p, pokemon, all_moves):
    pokemon_moves = []
    for m in p["moves"]:
        pass
        move = all_moves[m]
        pokemon_moves.append(Pokemon.moves.through(pokemon=pokemon, move=move))
    return pokemon_moves


def update_pokemon(pokemon):
    pokemon_objects = []
    for p in pokemon:
        pokemon_objects.append(Pokemon(name=p["name"], description=p["description"]))
    Pokemon.objects.bulk_create(pokemon_objects, ignore_conflicts=True)


def update_abilities(pokemon):
    abilities = set([a for p in pokemon for a in p["abilities"]])
    ability_objects = []
    for a in abilities:
        ability_objects.append(Ability(name=a))
    Ability.objects.bulk_create(ability_objects, ignore_conflicts=True)


def update_forms(pokemon):
    forms = set([f for p in pokemon for f in p["forms"]])
    form_objects = []
    for f in forms:
        form_objects.append(Form(name=f))
    Form.objects.bulk_create(form_objects, ignore_conflicts=True)


def update_moves(pokemon):
    moves = set([m for p in pokemon for m in p["moves"]])
    move_objects = []
    for m in moves:
        move_objects.append(Move(name=m))
    Move.objects.bulk_create(move_objects, ignore_conflicts=True)


# Using a quick async solution here for network requests. Was going to switch over to celery but didn't have time
def get_pokemon_details(pokemon):
    pokemon_details = {}
    species_responses = []
    single_pokemon_responses = []
    for p in pokemon:
        pokemon_species_endpoint = f"{pokeapi_base_url}/pokemon-species/{p['name']}"
        species_responses.append(session.get(pokemon_species_endpoint))
        pokemon_details_endpoint = f"{pokeapi_base_url}/pokemon/{p['name']}"
        single_pokemon_responses.append(session.get(pokemon_details_endpoint))
        pokemon_details[p["name"]] = {"name": p["name"]}

    for future in as_completed(species_responses):
        response = future.result()
        description = get_pokemon_species_details(response)
        response_pokemon_name = response.request.url.split("/")[-1]
        pokemon_details[response_pokemon_name]["description"] = description
    for future in as_completed(single_pokemon_responses):
        response = future.result()
        abilities, forms, moves = get_single_pokemon_details(response)
        response_pokemon_name = response.request.url.split("/")[-1]
        pokemon_details[response_pokemon_name].update(
            {"abilities": abilities, "forms": forms, "moves": moves}
        )

    return pokemon_details.values()


def get_pokemon_species_details(response):
    if response.status_code == 200:
        response_json = response.json()
        flavor_text_entries = response_json["flavor_text_entries"]
        english_descriptions = [
            entry["flavor_text"]
            for entry in flavor_text_entries
            if entry["language"]["name"] == "en"
        ]
        if english_descriptions:
            # Just using the first available english description
            return english_descriptions[0]
        return ""
    raise Exception


def get_single_pokemon_details(response):
    if response.status_code == 200:
        response_json = response.json()
        abilities = [a["ability"]["name"] for a in response_json["abilities"]]
        forms = [f["name"] for f in response_json["forms"]]
        moves = [m["move"]["name"] for m in response_json["moves"]]
        return abilities, forms, moves
    raise Exception


def get_all_pokemon(num_pokemon):
    all_pokemon = []
    all_pokemon_endpoint = f"{pokeapi_base_url}/pokemon"
    offset = 0
    result_limit = num_pokemon
    finished_crawling = False
    while not finished_crawling:
        pokemon_response = requests.get(
            all_pokemon_endpoint, params={"limit": result_limit, "offset": offset}
        )
        if pokemon_response.status_code == 200:
            pokemon_json = pokemon_response.json()
            all_pokemon.extend(pokemon_json["results"])
            current_pokemon_length = len(all_pokemon)
            if pokemon_json["next"] and current_pokemon_length < num_pokemon:
                all_pokemon_endpoint = pokemon_json["next"]
                offset = current_pokemon_length
            else:
                finished_crawling = True
    return all_pokemon
