import os
import re
import json
import xml.etree.ElementTree as ET
import importlib
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, COMM, TPUB, TXXX
from mutagen.easyid3 import EasyID3

# Function to load the configuration (categories and XML database path)
def load_config(config_file):
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)
        
def RegisterCommentKey(lang='\0\0\0', desc=''):
        frameid = ':'.join(('COMM', desc, lang))

        def getter(id3, key):
            frame = id3.get(frameid)
            return None if frame is None else list(frame)

        def setter(id3, key, value):
            id3.add(mutagen.id3.COMM(
                encoding=3, lang=lang, desc=desc, text=value))

        def deleter(id3, key):
            del id3[frameid]

        EasyID3.RegisterKey('comment', getter, setter, deleter)

# Function to extract file paths from the XML database
def extract_file_paths_from_xml(rekordbox_db_path):
    tree = ET.parse(rekordbox_db_path)
    root = tree.getroot()

    file_paths = []
    # Iterate over each TRACK element to extract the Location attribute
    for track in root.iter("TRACK"):
        location = track.get("Location")
        if location:
            # Decode the URL-encoded path and append it to the list
            file_paths.append(location.replace("file://localhost/", "").replace("%20", " "))
    
    return file_paths

def get_file_paths_from_directory(music_directory):
    file_paths = []
    for root_dir, _, files in os.walk(music_directory):
        for file in files:
            if file.lower().endswith(('.flac', '.mp3')):
                file_paths.append(os.path.join(root_dir, file))
    return file_paths

# Function to process the comments and organize them under categories
def process_comments(comments, categories):
    pattern = re.compile(r'/\*(.*?)\*/', re.DOTALL)
    categorized_tags = {category: [] for category in categories}
    categorized_tags['No Category'] = []

    for comment in comments:
        matches = pattern.findall(comment)
        for match in matches:
            # Split tags by " / " and strip extra whitespace
            tags = [tag.strip() for tag in match.split(" / ")]

            # Process each tag separately
            for tag in tags:
                assigned = False
                # Check if the tag matches any category
                for category, category_info in categories.items():
                    if tag in category_info['tags']:
                        categorized_tags[category].append(tag)
                        assigned = True
                        break
                if not assigned:
                    categorized_tags['No Category'].append(tag)
    return categorized_tags

# Function to update metadata fields in FLAC files
def update_metadata_flac(flac_path, categorized_tags, categories, delimiter):
    audio = FLAC(flac_path)
    
    # For each category, update the corresponding metadata field
    for category, category_info in categories.items():
        metadata_field = category_info.get('metadata_field')
        if metadata_field.upper() == 'PUBLISHER': metadata_field = 'LABEL'
        
        if metadata_field:
            # Get the tags for the category and join them into a single string
            tags = categorized_tags.get(category, [])
            if tags:
                # Join the tags with " / " if needed
                audio[metadata_field] = delimiter.join(tags)

    # Save the changes to the FLAC file
    audio.save()

# Function to update metadata fields in MP3 files using Mutagen
def update_metadata_mp3(mp3_path, categorized_tags, categories, delimiter):
    
    # For each category, update the corresponding metadata field
    for category, category_info in categories.items():
        metadata_field = category_info.get('metadata_field')
        
        if metadata_field:
            # Get the tags for the category and join them into a single string
            tags = categorized_tags.get(category, [])        
            if tags and metadata_field.lower() in EasyID3.valid_keys.keys(): #Check if given metadatafield is compatible with EasyID3
                # Join the tags with " / " if needed
                audio = MP3(mp3_path, ID3=EasyID3)
                tag_str = delimiter.join(tags)
                audio[metadatafield] = tag_str
                # Save the changes to the MP3 file
                audio.save()
            elif tags and metadata_field not in EasyID3.valid_keys.keys():
                audio = MP3(mp3_path, ID3=ID3)
                tag_str = delimiter.join(tags)
                mod = 'mutagen.id3.' + metadata_field.upper()
                # Use mutagen's ID3 to set the tag
                if  metadata_field.lower() == 'comment':
                    audio.tags.delall('COMM')
                    audio.tags.add(COMM(encoding=3, text=tag_str))
                elif metadata_field.lower() == 'label' or 'publisher':
                    audio.tags.delall('TPUB')
                    audio.tags.add(TPUB(encoding=3, text=tag_str))
                elif (spec := importlib.util.find_spec(mod)) is not None:
                    module = importlib.import_module(metadata_field, package=mutagen.id3)
                    audio.tags.add(module(encoding=3, text=tag_str))                    
                else:
                    audio.tags.add(TXXX(encoding=3, desc=metadata_field, text=tag_str))
                audio.save()

# Function to update the XML database with the tags
def update_xml(mytag_db_file, rekordbox_db_path, file_paths, categories, delimiter, use_rekordbox_xml):
    # Check if the XML file exists
    if os.path.exists(mytag_db_file):
        tree = ET.parse(mytag_db_file)
        root = tree.getroot()
    else:
        # If the XML file doesn't exist, create a new root element
        root = ET.Element("MusicTags")
        tree = ET.ElementTree(root)

    # Process each file path and write its categorized tags to the XML
    for file_path in file_paths:
        if os.path.exists(file_path) and file_path.lower().endswith(('.flac', '.mp3')):
            file_element = None
            comments = []
            
            # Load the FLAC or MP3 file and get the comments
            if file_path.lower().endswith('.flac'):
                audio = FLAC(file_path)
                comments = audio.get('comment', [])
            elif file_path.lower().endswith('.mp3'):
                audio = MP3(file_path, ID3=ID3)
                # Extract all 'COMM' frames and get the text from them
                comments = [frame.text for frame in audio.tags.getall('COMM')]  # Extract comments from MP3

            # Flatten the list of comments (if any)
            flattened_comments = []
            for comment in comments:
                if isinstance(comment, list):
                    flattened_comments.extend(comment)  # If it's a list, extend the list
                else:
                    flattened_comments.append(comment)  # Otherwise, just append it as-is

            # Categorize the tags from the comments
            categorized_tags = process_comments(flattened_comments, categories)

            # Check if the file path already exists in the XML
            for song in root.findall("Song"):
                if song.find("FilePath").text == file_path:
                    file_element = song
                    break

            if file_element is None:
                # If the file is not in the XML, add a new Song element
                file_element = ET.SubElement(root, "Song")
                file_path_element = ET.SubElement(file_element, "FilePath")
                file_path_element.text = file_path

            # Now, update the tags under each category in the XML
            for category, category_info in categories.items():
                category_element = file_element.find(category)
                if category_element is None:
                    category_element = ET.SubElement(file_element, category)

                # Add tags to the category element if not already present
                existing_tags = {tag_element.text for tag_element in category_element.findall("Tag")}
                for tag in categorized_tags.get(category, []):
                    if tag not in existing_tags:
                        tag_element = ET.SubElement(category_element, "Tag")
                        tag_element.text = tag

            # Write the updated XML back to the file
            ET.indent(tree, '  ')
            tree.write(mytag_db_file, encoding="utf-8", xml_declaration=True)

            # Now, update the metadata field in the FLAC or MP3 file
            if file_path.lower().endswith('.flac'):
                update_metadata_flac(file_path, categorized_tags, categories, delimiter)
            elif file_path.lower().endswith('.mp3'):
                update_metadata_mp3(file_path, categorized_tags, categories, delimiter)
            
            if use_rekordbox_xml:
                update_track_in_xml(rekordbox_db_path, file_path, categorized_tags, categories, delimiter) # After updating the FLAC or MP3 metadata, write the tags back to the the songs TRACK element in the original Rekordbox XML if use_rekordbox_xml is enabled
           

# Function to update the TRACK tags in the original XML database
def update_track_in_xml(rekordbox_db_path, file_path, categorized_tags, categories, delimiter):
    # Parse the XML database
    tree = ET.parse(rekordbox_db_path)
    root = tree.getroot()

    # Find the TRACK element that corresponds to the given FLAC or MP3 file
    for track in root.iter("TRACK"):
        location = track.get("Location")
        if location and location == f"file://localhost/{file_path.replace(' ', '%20')}":
            # For each category, update the corresponding tags
            for category, category_info in categories.items():
                rekordbox_field = category_info.get('rekordbox_field')
                if rekordbox_field:
                    # Prepare tags as a string separated by "; "
                    tags = categorized_tags.get(category, [])
                    if tags:
                        # Set the tags as an attribute in the TRACK element
                        track.set(rekordbox_field, delimiter.join(tags))

            # Write the updated XML back to the database file
            ET.indent(tree, '  ')
            tree.write(rekordbox_db_path, encoding="utf-8", xml_declaration=True)

# Main function to load config and start the process
def main():
    config_file = 'config.json'  # Path to your config file

    # Load the categories, XML database path, and XML output path from the config file
    config = load_config(config_file)
    mytag_db_file = config.get('mytag_db_file')  # Get XML output file path
    categories = config.get('categories')  # Get categories from config
    use_rekordbox_xml = config.get('use_rekordbox_xml')
    delimiter = str(config.get('tag_delimiter'))
    # Check if XML database path is provided and valid
    rekordbox_db_path = config.get('rekordbox_db_path')  # Path to the XML database
    music_directory = config.get('music_directory')
    if use_rekordbox_xml:
        if not rekordbox_db_path or not os.path.exists(rekordbox_db_path):
            print(f"Invalid or missing XML database file: {rekordbox_db_path}")
            return
        else:
            file_paths = extract_file_paths_from_xml(rekordbox_db_path) # Extract file paths from the XML database
    elif not use_rekordbox_xml and os.path.exists(music_directory):
        file_paths = get_file_paths_from_directory(music_directory) # Extract file paths from the specified directory
    else:
        print(f"Invalid or missing music directory path: {music_directory}")
        return

    # Process the FLAC and MP3 files and update the XML
    update_xml(mytag_db_file, rekordbox_db_path, file_paths, categories, delimiter, use_rekordbox_xml)
    print(f'File metadata updated and MyTag Db generated: {mytag_db_file}')

# Run the script
if __name__ == '__main__':
    main()
