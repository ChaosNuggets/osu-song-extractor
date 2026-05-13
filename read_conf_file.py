# Possible replacement fields are:
# <AudioFilename>, <Title>, <Artist>, <Version>,
# <BackgroundFilename>, <BeatmapID>, <BeatmapSetID>
# Look online for the .osu file format documentation for more details about what each of these mean.
# The program automatically strips the extension for folders and adds the correct extension for filenames

from dataclasses import dataclass, asdict, field
import re
from enum import Enum, auto

# Enum that stores whether the user wants to always write the song metadata,
# write the metadata only if missing, or never write the metadata
class MetaWriteMode(Enum):
    NEVER = auto()
    IF_MISSING = auto()
    ALWAYS = auto()

# Stores how the user wants to export their backgrounds (never,
# as a separate file in the same directory, or as metadata inside of the audio file)
class BGExportMode(Enum):
    NEVER = auto()
    AS_SEPARATE = auto()
    AS_META = auto()

# Stores configuration options for each type of beatmap
@dataclass
class BeatmapTypeConf:
    # Whether or not to create a deeper subfolder for each audio file.
    # Default: True for mult_bg_mult_song, False for all other beatmap types
    export_into_deep_subfolder: bool = False

    # What name to give the deeper subfolder.
    # Supports replacement fields, see top of document for a list of all replacement fields
    # Default: "<Version>"
    deep_subfolder_name: str = r'<Version>'

    # Whether or not to overrite existing files in the output directory
    # with the same filename. Possible values are True, False.
    # Default: False
    overrite_existing_files: bool = False

    # What name to give the exported song (program puts the audio extension for you, no need to list that)
    # Default: "<Artist> - <Title>" if there's only one song,
    #          "<Artist> - <Title> [<Version>]" for one_bg_mult_song, "<Version>" for mult_bg_mult_song
    song_filename: str = r'<Artist> - <Title>'

    # When to overrite the output song metadata, based on if it's present in the original file.
    # Possible values are NEVER, IF_MISSING, ALWAYS.
    # Default: IF_MISSING
    meta_write_mode: MetaWriteMode = MetaWriteMode.IF_MISSING 

    # What metadata to write to the exported song's title field.
    # Default: "<Title>" for one_bg_one_song and mult_bg_one_song,
    #          "<Title> [<Version>]" for one_bg_mult_song, "<Version>" for mult_bg_mult_song
    title_meta: str = r'<Title>'

    # What metadata to write to the exported song's artist field.
    # Default: "<Artist>"
    artist_meta: str = r'<Artist>'

    # How to export the background - never, as a separate file in the same directory as the output audio file,
    # or as part of the output file's metadata.
    # Possible values are NEVER, AS_SEPARATE, AS_META
    # Default: AS_SEPARATE
    bg_export_mode: BGExportMode = BGExportMode.AS_SEPARATE
    
    # What name to give the exported background image (if exporting as separate file)
    # Default: <BackgroundFilename>
    bg_filename: str = r'<BackgroundFilename>'

# Stores all the configuration options
@dataclass
class ConfValues:
    # input_dir is your Osu Songs folder, output_dir is where it will get copied to
    # Make it mandatory for these two options to be in the config file,
    # other options have defaults
    input_dir: str = ''
    output_dir: str = ''

    # True: export each beatmap into a different subfolder
    # False: export each beatmap in the top-level output directory
    # Default: True
    export_into_subfolders: bool = True

    # Name of each subfolder with support for replacement fields extracted from the beatmap's .osu file.
    # Supports replacement fields, see top of document for a list of all replacement fields
    # Default: "<Artist> - <Title> <BeatmapSetID>"
    subfolder_name: str = r'<Artist> - <Title> <BeatmapSetID>'

    # Sometimes, the values in the .osu file will have illegal filename characters (<, >, :, ", /, \, |, ?, *). If you then use a
    # replacement field, this can lead to an illegal folder / file name. What should the illegal character(s) be replaced with?
    # Default: "-"
    illegal_char_override: str = '-'
    
    # The configuration options specific to all 4 beatmap types
    one_bg_one_song: BeatmapTypeConf = field(default_factory=BeatmapTypeConf)
    mult_bg_one_song: BeatmapTypeConf = field(default_factory=BeatmapTypeConf)
    one_bg_mult_song: BeatmapTypeConf = field(default_factory=BeatmapTypeConf)
    mult_bg_mult_song: BeatmapTypeConf = field(default_factory=BeatmapTypeConf)

    # Fills in the special defaults for one_bg_mult_song and mult_bg_mult_song
    def __post_init__(self):
        self.one_bg_mult_song.song_filename = r'<Artist> - <Title> [<Version>]'
        self.one_bg_mult_song.title_meta = r'<Title> [<Version>]'

        self.mult_bg_mult_song.export_into_deep_subfolder = True
        self.mult_bg_mult_song.song_filename = r'<Version>'
        self.mult_bg_mult_song.title_meta = r'<Version>'

    # Fills in ConfValues based on the option and value specified
    # in the config file
    def init_from_conf(self, option: str, value: str) -> None:
        match option:
            case 'input_dir':
                self.input_dir = value.strip('\n \"').rstrip('/\\')
            case 'output_dir':
                self.output_dir = value.strip('\n \"').rstrip('/\\')
            case _:
                raise KeyError(f'Unknown config option "{option}"')

# Returns the input_dir and output_dir entries in osu-song-extractor.cfg
def read_conf_file(conf_file: str) -> ConfValues:
    conf_values = ConfValues()

    # Compiling is efficient for loops
    # Pattern looks for "<config_option>=<value>" and places
    # config option in first group and value in second group
    conf_pattern = re.compile(r'^([^=#]*)=([^#\n]*)')

    # Search for configuration option pattern in file
    with open(conf_file, 'r') as file:
        for line in file:
            conf_match = conf_pattern.search(line)
            if not conf_match:
                continue

            # Parse the configuration option
            option = conf_match.group(1).strip()
            value = conf_match.group(2).strip()
            conf_values.init_from_conf(option, value)

    # Raise an error if something is missing from the config file
    for key, value in asdict(conf_values).items():
        if not value:
            raise KeyError(f'Please specify {key} in the configuration file')
    return conf_values
