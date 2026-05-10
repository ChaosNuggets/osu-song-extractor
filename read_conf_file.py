from dataclasses import dataclass, asdict
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

# Stores all the configuraiton options
@dataclass
class ConfValues:
    # input_dir is your Osu Songs folder, output_dir is where it will get copied to
    # Make it mandatory for these two options to be in the config file,
    # other options have defaults
    input_dir: str = ''
    output_dir: str = ''

    # When to overrite the output song metadata, based on if it's present in the original file.
    # Possible values are NEVER, IF_MISSING, ALWAYS.
    # Default = IF_MISSING
    meta_write_mode: MetaWriteMode = MetaWriteMode.IF_MISSING

    # Whether or not to overrite existing files in the output directory
    # with the same filename. Possible values are True, False.
    # Default = False
    overrite_existing_files: bool = False

    # How to export the background - never, as a separate file in the same directory as the output audio file,
    # or as part of the output file's metadata.
    # Possible values are NEVER, AS_SEPARATE, AS_META
    # Default: AS_SEPARATE
    bg_export_mode: BGExportMode = BGExportMode.AS_SEPARATE

    # True: export each beatmap into a different subfolder
    # False: export each beatmap in the top-level output directory
    # Default = True
    export_into_subfolders: bool = True

    # Name of each subfolder with support for replacement fields extracted from the beatmap's .osu file.
    # Possible replacement fields are <AudioFilename>, <Title>, <Artist>, <Version>, <BackgroundFilename>, <BeatmapID>, <BeatmapSetID>
    # See the .osu file format documentation online for more details about what each of these mean.
    # Default = "<Artist> - <Title> <BeatmapSetID>"
    subfolder_name: str = r'<Artist> - <Title> <BeatmapSetID>'

    # Sometimes, the values in the .osu file will have illegal filename characters (<, >, :, ", /, \, |, ?, *). If you then use a
    # replacement field, this can lead to an illegal folder / file name. What should the illegal character(s) be replaced with?
    # Default = "-"
    illegal_char_override: str = '-'
    
    # one_bg_one_song:
    # mult_bg_one_song = 
    # one_bg_mult_song = 
    # mult_bg_mult_song =

    # Fills in ConfValues based on the option and value specified
    # in the config file
    def init_from_conf(self, option: str, value: str) -> None:
        match option:
            case 'input_dir':
                self.input_dir = value.strip('\n \"\'').rstrip('/\\')
            case 'output_dir':
                self.output_dir = value.strip('\n \"\'').rstrip('/\\')
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
