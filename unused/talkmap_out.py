# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Leaflet cluster map of talk locations
#
# Assuming you are working in a Linux or Windows Subsystem for Linux environment, you may need to install some dependencies. Assuming a clean installation, the following will be needed:
#
# ```bash
# sudo apt install jupyter
# sudo apt install python3-pip
# pip install python-frontmatter getorg --upgrade
# ```
#
# After which you can run this from the `_talks/` directory, via:
#
# ```bash
#  jupyter nbconvert --to notebook --execute talkmap.ipynb --output talkmap_out.ipynb
# ```
#  
# The `_talks/` directory contains `.md` files of all your talks. This scrapes the location YAML field from each `.md` file, geolocates it with `geopy/Nominatim`, and uses the `getorg` library to output data, HTML, and Javascript for a standalone cluster map.

# %%
# Start by installing the dependencies
# !pip install python-frontmatter getorg --upgrade
import frontmatter
import glob
import getorg
from geopy import Nominatim
from geopy.exc import GeocoderTimedOut

# %%
# Collect the Markdown files
g = glob.glob("_talks/*.md")

# %%
# Set the default timeout, in seconds
TIMEOUT = 5

# Prepare to geolocate
geocoder = Nominatim(user_agent="academicpages.github.io")
location_dict = {}
location = ""
permalink = ""
title = ""

# %% [markdown]
# In the event that this times out with an error, double check to make sure that the location is can be properly geolocated.

# %%
# Perform geolocation
for file in g:
    # Read the file
    data = frontmatter.load(file)
    data = data.to_dict()

    # Press on if the location is not present
    if 'location' not in data:
        continue

    # Prepare the description
    title = data['title'].strip()
    venue = data['venue'].strip()
    location = data['location'].strip()
    description = f"{title}<br />{venue}; {location}"

    # Geocode the location and report the status
    try:
        location_dict[description] = geocoder.geocode(location, timeout=TIMEOUT)
        print(description, location_dict[description])
    except ValueError as ex:
        print(f"Error: geocode failed on input {location} with message {ex}")
    except GeocoderTimedOut as ex:
        print(f"Error: geocode timed out on input {location} with message {ex}")
    except Exception as ex:
        print(f"An unhandled exception occurred while processing input {location} with message {ex}")

# %%
# Save the map
m = getorg.orgmap.create_map_obj()
getorg.orgmap.output_html_cluster_map(location_dict, folder_name="talkmap", hashed_usernames=False)

# %%
