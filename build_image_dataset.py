import os
from PIL import Image
import requests
import csv

graphql_query = """
query {
  pokemon_v2_pokemon {
    pokemon_v2_pokemontypes {
      pokemon_v2_type {
        name
      }
    }
    id
  }
}
"""
r = requests.post(
    "https://beta.pokeapi.co/graphql/v1beta",
    json={
        "query": graphql_query,
    },
)

print(r.text[0:200])
