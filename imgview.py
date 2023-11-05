import time
from os import environ, path
from math import floor
from random import randrange
import multiprocessing
import tkinter as tk
from PIL import ImageTk

from simpleaudio import WaveObject

import nga

# Step 1: Wait for internet
while not nga.ping():
    print("Failed to connect to Metropolitan Museum of Art API.  Retrying in ten seconds.  Press Ctrl-C to exit to shell, where you can configure Wi-Fi.")
    time.sleep(10)

nga.prep_data()

# Step 2: Load painting IDs
current_search_term = ""
current_search_in_book_titles = False
painting_ids = []

def get_painting(width, height):
    global painting_ids # Yes I know this is bad practice -- shut up.  It's simple and this will never be too complicated to refactor.
    global current_search_term
    while True:
        id_id = randrange(len(painting_ids))
        painting_id = painting_ids[id_id]
        del painting_ids[id_id]
        if len(painting_ids) == 0:
            painting_ids = nga.search(current_search_term) # In theory I could cache this, but in practice it's more exciting to do it this way -- maybe the Met adds a new painting!
        try:
            image = nga.image(painting_id, width, height)
            return image
        except Exception:
            print("Bad image!  Trying again.")
            continue

# Step 3: Construct window
root = tk.Tk()
root.title("HannibalViewer")
panel = tk.Label(root, image = None)
panel.configure(background = "black")

def update_panel():
    painting = get_painting(root.winfo_screenwidth(), root.winfo_screenheight())
##    painting_width, painting_height = painting.size
##    window_width, window_height = root.winfo_screenwidth(), root.winfo_screenheight()
##    painting_aspect_ratio = painting_width / painting_height
##    window_aspect_ratio = window_width / window_height
##    if painting_aspect_ratio > window_aspect_ratio: #Painting is wide and squat compared to window
##        painting = painting.resize((window_width, floor(window_width / painting_aspect_ratio)))
##    else: # Painting is tall and narrow compared to window
##        painting = painting.resize((floor(window_height * painting_aspect_ratio), window_height))
    new_img = ImageTk.PhotoImage(painting)
    panel.configure(image = new_img)
    panel.image = new_img

panel.pack(fill="both", expand="yes")

# Step 4: Communicate with voice-assistant process by continually polling a file
filepath = environ.get("PAINTING_SEARCH_FILE_PATH", "searchkey")

if not path.isfile(filepath):
    with open(filepath, 'w') as file:
        file.write(environ.get("PAINTING_INIT", "mythological"))

last_file_update_time = -1

PAINTING_UPDATE_INTERVAL = 600
last_painting_update_time = time.time()

good = WaveObject.from_wave_file("good.wav")
bad = WaveObject.from_wave_file("bad.wav")

def poll_and_update():
    global painting_ids
    global current_search_term
    global current_search_in_book_titles
    global last_file_update_time
    global last_painting_update_time
    
    updating_painting = False
    
    if path.getmtime(filepath) != last_file_update_time:
        last_file_update_time = path.getmtime(filepath)
        panel.configure(image = None) # TODO: Add a nice "Loading..." image here.  Something artistic.
        with open(filepath, 'r') as file:
            line = file.readline().strip()
            new_search_term = line[1:]
            new_search_in_book_titles = (line[0] == "1")
            new_painting_ids = nga.search(new_search_term, new_search_in_book_titles)
            if len(new_painting_ids) > 0:
                current_search_term = new_search_term
                current_search_in_book_titles = new_search_in_book_titles
                painting_ids = new_painting_ids
                good.play()
                updating_painting = True
            else:
                bad.play()
                # TODO: Add an image to indicate failure to find anything rather than just blacking out the screen.
    elif time.time() - last_painting_update_time > PAINTING_UPDATE_INTERVAL:
        last_painting_update_time = time.time()
        updating_painting = True
    
    if len(painting_ids) > 0 and updating_painting:
        update_panel()

    root.after(100, poll_and_update)

root.after(100, poll_and_update)

root.mainloop()
