from json.decoder import JSONDecodeError
import os
import csv

from PIL import Image, UnidentifiedImageError
import requests
from translatepy import Translator
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
trans_cache = {}

# Uses Yandex for translator, which in theory would do better for Russian
ts = Translator()

if not os.path.exists(folder):
    os.makedirs(folder)

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
    for p in tqdm(pokemon, smoothing=0):
        p_id = p["id"]
        try:
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
            try:
                if caption in trans_cache:
                    caption = trans_cache[caption]
                else:
                    trans_caption = ts.translate(caption, "ru").result
                    trans_cache[caption] = trans_caption
                    caption = trans_caption

                bg.save(os.path.join(folder, name))
                w.writerow([name, caption])
            except JSONDecodeError:
                break
                # print(f"Translation failed for: {caption}")
        except UnidentifiedImageError:
            continue
