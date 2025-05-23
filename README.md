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
    \"mytag_db_file\": \"path/to/your/mytag_db.xml\",
    \"rekordbox_db_path\": \"path/to/your/rekordbox_db.xml\",
    \"use_rekordbox_xml\": true,
    \"categories\": {
        \"MOOD\": {
            \"tags\": [\"Mood1\", \"Mood2\"],
            \"metadata_field\": \"COMPOSER\",
			\"rekordbox_field\": \"Composer\"
        },
        \"SITUATION\": {
            \"tags\": [\"Situation1\", \"Situation2\"],
            \"metadata_field\": \"LABEL\",
			\"rekordbox_field\": \"LABEL\"
        },
        \"GENRE\": {
            \"tags\": [\"Rock\", \"Pop\"],
            \"metadata_field\": \"GENRE\",
			\"rekordbox_field\": \"Genre\"
        }
    }
}
```

- **mytag_db_file**: Path to the XML database that will store categorized tags and the associated filepaths.
- **rekordbox_db_path**: Path to a Rekordbox collection that has been exported in XML format (only used if `use_rekordbox_xml` is set to `true`).
- **use_rekordbox_xml**: If `true`, the script extracts file paths from the Rekordbox XML database.
- **categories**: These are the categories you have your MyTags organized into in Rekordbox. Under each category list the associated tags (yes this is tedious to initially set up but it's the only way to properly categorize the list of MyTags due to the way Rekordbox exports them to the Comments tag).

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/music-tags-metadata-updater.git
    ```

2. Install the required dependencies:
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

## Example Workflow

1. Set up your `config.json` with the correct paths and categories.
2. Run the script to automatically process your music library.
3. The script will categorize tags from file comments and write them to the metadata fields in both FLAC and MP3 files.
4. It will also update your Rekordbox XML database with the new metadata tags in the fields specified in the config (this assumes .

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
"