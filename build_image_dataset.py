import os
import csv

from PIL import Image
import requests
from translatepy.translators.google import GoogleTranslateV2
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

# Create a cache for known translated captions
dl = GoogleTranslateV2()
trans_cache = {}

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

        # https://stackoverflow.com/a/9459208
        bg = Image.new("RGB", (size, size), (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        name = f"{p_id}.png"

        type_str = " and ".join(
            [
                f'{t["pokemon_v2_type"]["name"].title()}-type'
                for t in p["pokemon_v2_pokemontypes"]
            ]
        )
        caption = f"A {type_str} Pokémon"
        if caption in trans_cache:
            caption = trans_cache[caption]
        else:
            trans_caption = dl.translate(caption, "ru").result
            trans_cache[caption] = trans_caption
            caption = trans_caption

        bg.save(os.path.join(folder, name))
        w.writerow([name, caption])
