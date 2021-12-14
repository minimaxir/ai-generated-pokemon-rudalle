import os
import csv

from PIL import Image
import requests
from translators import google
from tqdm import tqdm

folder = "images"
size = 256

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

# Normally we'd get this via PokeAPI GraphQL
# but it currently returns "null" for sprites.
image_url = (
    "https://raw.githubusercontent.com/PokeAPI/sprites/master/"
    "sprites/pokemon/other/official-artwork/{0}.png"
)

r = requests.post(
    "https://beta.pokeapi.co/graphql/v1beta",
    json={
        "query": graphql_query,
    },
)

pokemon = r.json()["data"]["pokemon_v2_pokemon"]

with open("data_desc.csv", "w", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["name", "caption"])
    for p in tqdm(pokemon[0:20], smoothing=0):
        p_id = p["id"]
        img = Image.open(requests.get(image_url.format(p_id), stream=True).raw)
        img = img.resize((size, size), Image.ANTIALIAS)
        img = Image.blend(Image.new("RGBA", (size, size), (255, 255, 255, 0)), img, 1)
        name = f"{p_id}.png"

        type_str = "/".join(
            [t["pokemon_v2_type"]["name"].title() for t in p["pokemon_v2_pokemontypes"]]
        )
        caption = f"A {type_str} Pokémon"
        caption = google(caption, from_language="en", to_language="ru")

        img.save(os.path.join(folder, name))
        w.writerow([name, caption])
