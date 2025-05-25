# MyTag Extractor and Converter

Script to read and categorize MyTag data written by Rekordbox to a files comment field, store categorized MyTag info in an XML, and write MyTags to other fields in the files metadata

## Features

- **Automatically Parse and Categorize MyTags**: Automatically parses and categorizes the unorganized list of MyTags that Rekorbox writes to a songs Comments tag
- **Write Tags to the Files Metadata or a Rekorbox Library XML**: Able to write the tag categories to the specified fields in the files metadata or write them to the specified attributes in Rekorbox's XML format (including ones that are only stored in Rekordbox's database and not the file metadata like Lyricist. Remixer, etc.)
- **Multiple Ways to Scan**: The script can either comb through a specified directory where your music files are contained or it can parse an exported XML of your Rekordbox library and only check tracks that are in your library regardless of file location
- **Metadata Writing**: Currently only supports FLAC and MP3 files

## Requirements

- Python 3.x
- `mutagen` library (Install with `pip install mutagen`)

## Configuration

The script relies on a `config.json` file for configuration. The `config.json` file should contain the following structure:
```json
{
    "use_rekordbox_xml": false,
    "rekordbox_db_path": "/path/to/exported/rekordbox.xml",
    "music_directory": "/path/to/your/music/directory",
    "mytag_db_file": "MyTags.xml",
	"tag_delimiter": " / ",
    "categories": {
        "Genre": {
            "tags": [
                "House",
                "Trap",
                "Dubstep",
                "Disco",
                "Drum and Bass"
            ],
            "rekordbox_field": "Genre",
            "metadata_field": "GENRE"
        },
        "Components": {
            "tags": [
                "Synth",
                "Piano",
                "Kick",
                "Hi Hat"
            ],
            "rekordbox_field": "Composer",
            "metadata_field": "COMPOSER"
        },
        "Situation": {
            "tags": [
                "Warm Up",
                "Building",
                "Peak Time",
                "After Hours",
                "Lounge",
                "House Party"
            ],
            "rekordbox_field": "Label",
            "metadata_field": "LABEL"
        },
        "Mood": {
            "tags": [
                "Happy",
                "Melancholy",
                "Emotional",
                "Hype",
                "Angry"
            ],
            "rekordbox_field": "Comments",
            "metadata_field": "COMMENT"
        }
    }
}
```

- **mytag_db_file**: Path to the XML database that will store categorized tags and the associated filepaths.
- **rekordbox_db_path**: Path to a Rekordbox collection that has been exported in XML format (only used if `use_rekordbox_xml` is set to `true`).
- **use_rekordbox_xml**: If `true`, the script extracts file paths from the Rekordbox XML database.
- **categories**: These are the categories you have your MyTags organized into in Rekordbox. Under each category list the associated tags (yes this is tedious to initially set up but it's the only way to properly categorize the list of MyTags due to the way Rekordbox exports them to the Comments tag).

## Installation

1. Download the repository or clone using:
    ```bash
    git clone https://github.com/yourusername/music-tags-metadata-updater.git
    ```

2. Install the required Python dependencies:
    ```bash
    pip install mutagen
    ```

3. Prepare your `config.json` file as described above.

## Usage

Once you have configured the `config.json` file, you can run the script using:

```bash
python mytag_converter.py
```

### How It Works

1. **Extract File Paths**: The script first checks the Rekordbox XML database (Rekordbox XML if `use_rekordbox_xml` is enabled) to extract the paths of FLAC or MP3 files in your library. Otherwise it combs the provided path for any .mp3 and .flac files
2. **Categorize Comments**: The script reads the comments from each file, extracts the MyTags written to the files comment field between `/*' and  '*/`, and then categorizes the tags into the associated categories specified in the config.
4. **Update XML Database and File Metadata**: The script writes the extracted and categorized tags and their associated filepaths to the `mytag_db_file` (XML format) and (if using a Rekorbox Collection XML) updates the songs in Rekordbox XML database and writes the tags to the attributes specified in the config where they can be imported back into the library if desired.

## Notes about ID3 Tags/Metadata

ID3 tags for MP3 are stored as 4 or 5 character Tag IDs. Mutagen has an EasyID3 library that will be used if the metadata field is supported. Note that EasyID3 does not support the "comments" or "publisher" fields but the script is still written so the it writes to the to the MP3s correct ID3 field if those values are specified. "Label" and "Publisher" are treated the same and written to the appropriate field depending on the filetype.
### Currently supported ID3 fields:
album
bpm
compilation
composer
copyright
encodedby
lyricist
length
media
mood
grouping
title
version
artist
albumartist
conductor
arranger
discnumber
organization
tracknumber
author
albumartistsort
albumsort
composersort
artistsort
titlesort
isrc
discsubtitle
language
genre
date
originaldate
performer
musicbrainz_trackid
website
replaygain__gain
replaygain__peak
musicbrainz_artistid
musicbrainz_albumid
musicbrainz_albumartistid
musicbrainz_trmid
musicip_puid
musicip_fingerprint
musicbrainz_albumstatus
musicbrainz_albumtype
releasecountry
musicbrainz_discid
asin
performer
barcode
catalognumber
musicbrainz_releasetrackid
musicbrainz_releasegroupid
musicbrainz_workid
acoustid_fingerprint
acoustid_id

Here is a [list](https://www.exiftool.org/TagNames/ID3.html) of ID3 tag codes. If you exclusively use MP3 for your collection you can specify any 4 character ID3 Tag ID under `Metadata Field`and the script will write the tags to that field.
### Custom Metadata Fields

- It is possible to store the MyTag info in custom user defined metadata fields if desired. Please note that as far as I'm aware no DJ software is currently able to read/search custom fields.

- If the file is MP3 and the specified field is not a valid ID3 Tag Code or a value that is supported by EasyID3 to map to one, then the tags will be entered under the user defined text field (TXXX) using the field name for the description (different from the text value where the tags will be stored)

- If the file is FLAC and the specified field is not a valid recognized metadata field a custom field will be created containing the tags

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
