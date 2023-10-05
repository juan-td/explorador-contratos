import json
import pandas as pd
from sodapy import Socrata

client = Socrata("www.datos.gov.co", None)
metadata = client.get_metadata("jbjy-vk9h")

with open(
    "/Users/juantoro/Documents/Miscellaneous/explorador-contratos/data/metadata.json",
    "w",
    encoding="utf-8",
) as file:
    json.dump(metadata, file, ensure_ascii=False)
