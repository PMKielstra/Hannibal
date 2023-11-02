from os import path
from io import BytesIO
from PIL import Image

from git import Repo
import requests
from requests.exceptions import ConnectionError
import numpy as np
import pandas as pd

repo_url = "https://github.com/NationalGalleryOfArt/opendata"
repo_folder = "ngadata"

def ping():
    """Attempt to reach the museum's base API endpoint.  We generally assume that we aren't connected to the internet if this fails."""
    try:
        requests.get("https://nga.gov")
        return True
    except ConnectionError:
        return False

art = None

def prep_data():
    global art

    print("Synchronizing art data with NGA...")
    repo = Repo(".")
    assert len(repo.submodules) == 1 # Just one submodule -- NGA data
    repo.submodules[0].update(to_latest_revision=True)

    print("Loading art data...")
    images = pd.read_csv(repo_folder + "/data/published_images.csv")
    artworks = pd.read_csv(repo_folder + "/data/objects.csv")
    bibliographies = pd.read_csv(repo_folder + "/data/objects_text_entries.csv")
    primary_images = images.loc[images["viewtype"] == "primary"].rename({"depictstmsobjectid": "objectid"},axis=1)
    primary_images.rename({"depictstmsobjectid": "objectid"},axis=1)
    paintings = artworks.loc[artworks["visualbrowserclassification"] == "painting"]
    bibliographies = bibliographies.groupby(["objectid"]).sum()
    art = pd.merge(paintings, primary_images, how="inner", on=["objectid"])
    art = pd.merge(art, bibliographies, how="left", on=["objectid"])
    cols = art.select_dtypes(include=[object]).columns
    art[cols] = art[cols].apply(lambda x: x.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.lower())
    print(f"Loaded details of {len(art)} paintings into {sum(art.memory_usage(deep=True))/(1024 * 1024):.1f}MB RAM")
    print("Ready to search")

def search(term, search_in_book_history=False):
    """Returns a list of work IDs which match the search term."""
    mask = np.column_stack([art[col].str.contains(f"{term}", na=False) for col in art.select_dtypes(include=[object]) if search_in_book_history or col != "text"])
    return list(np.where(mask.any(axis=1))[0])

def image(objectID, screen_width, screen_height):
    base_url = art.iloc[objectID]["iiifurl"]
    image_url = f"{base_url}/full/!{screen_width},{screen_height}/0/default.jpg"
    image_request = requests.get(image_url)
    return Image.open(BytesIO(image_request.content))
    
    
