from urllib.parse import quote
from io import BytesIO
from PIL import Image

import requests
from requests.exceptions import ConnectionError

URL = "https://collectionapi.metmuseum.org"

def ping():
    """Attempt to reach the museum's base API endpoint.  We generally assume that we aren't connected to the internet if this fails."""
    try:
        requests.get(URL)
        return True
    except ConnectionError:
        return False

def search(term):
    """Return a list of work IDs which match the search term."""
    r = requests.get(URL + "/public/collection/v1/search", params={
            "q": term,
            "medium": "Paintings",
            "hasImages": "True"
        })
    return r.json()["objectIDs"]

def image(objectID):
    """Get the main image associated with an object.  For a painting, this should be a good enough representation of it to display in-frame."""
    object_request = requests.get(URL + "/public/collection/v1/objects/" + quote(str(objectID)))
    image_url = object_request.json()["primaryImage"]
    image_request = requests.get(image_url)
    return Image.open(BytesIO(image_request.content))
