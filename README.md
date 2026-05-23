# Osu-Song-Extractor
This is a highly configurable program extracts all songs from osu!. Unlike other projects, this is not a simple "export all .mp3 files" program. It reads each .osu file, gets the audio and background filenames from it, categorizes each beatmap set as containing a single song, rates, or a map pack, and exports accordingly. Many configuration options support replacement fields, so whether you want your exported song filenames to be `"<Artist> - <Title>"` or `"<AudioFilename>"`, this program supports it.

# Features
- Cross platform (works on Windows and Linux; MacOS probably works too but untested)
- Different configuration options depending on whether the beatmap set contains one song, contains rates, or is a map pack.
- [Replacement field](docs/configuration.md#replacement-fields) support
- Export background as metadata or as a separate file
- Configurable audio file metadata for Title and Artist fields
- Optional subfolder and deep subfolder export control

See [the configuration guide](docs/configuration.md) for more information.

![docs/export_as_meta.jpg](docs/export_as_meta.jpg)
*example exported songs folder*

# Requirements
- Python 3.12+ (Python 3.11 probably works but untested)
- An Osu Songs folder (doesn't require Osu to be installed!)

# Installation
1. Clone this repository and cd into it (or go to Releases and download the source code). In the terminal or command prompt, run:
```sh
git clone https://github.com/ChaosNuggets/osu-song-extractor.git && cd osu-song-extractor
```
2. Create a Python virtual environment:
```sh
python -m venv .venv
```
3. Activate the virtual environment.
    - On Windows:
    ```sh
    .venv\Scripts\activate
    ```
    - On Linux / MacOS:
    ```sh
    .venv/bin/activate
    ```
4. Install the required dependencies:
```sh
pip install -r requirements.txt
```

# Usage
1. Edit osu\_song\_extractor.cfg and fill in input\_dir and output\_dir. Example:
```
input_dir = "C:\Users\{Username}\AppData\Local\osu!\Songs"
output_dir = "C:\Users\{Username}\Music\Extracted-Songs"
```
2. Activate the virtual environment.
3. Run the Python module:
```
python -m osu_song_extractor
```

# Configuration
See [the configuration guide](docs/configuration.md). Tl;dr: see [examples](docs/configuration.md#examples).

# Bugs / Enhancement / Help Requests
Osu beatmaps are crazy things with lots of edge cases (apostrophes in filenames get replaced with underscores, filenames are case insensitive, etc.). If you find a beatmap or something else that doesn't work with this tool, feel free to submit an issue with the bug tag. Also, if you would like to request more features, feel free to submit an issue with the enhancement tag. If you would like help running this tool, you can add me on discord: chaosnuggets.

# Troubleshooting
If you're on Windows and getting a FileNotFoundError, this is probably due to Windows' file path limit of 260 characters. There are two ways to fix this:

**Option 1:** [Change your registry settings to enable long paths](https://learn.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation?tabs=powershell#registry-setting-to-enable-long-paths).

**Option 2:** Change your configuration settings so your exported filenames have less characters.

# Dev Stuff: Running Tests
1. Download the [mania freedom dive beatmap](https://osu.ppy.sh/beatmapsets/173612), change the `.osz` extension to `.zip`, and extract it into `tests/test_extract/Songs`.
2. Activate the virtual environment and install pytest:
```
pip install pytest
```
3. Run pytest while showing print statements:
```
python -m pytest -s
```
4. (Optional): Download more beatmaps you want to test and put them in `tests/test_extract/Songs`.
