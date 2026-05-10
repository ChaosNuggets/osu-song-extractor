import re
from pathlib import Path
from copy_audio import copy_audio
from dataclasses import dataclass, asdict

def main():
    input_dir, output_dir = read_conf_file('osu-song-extractor.cfg')
    write_output(input_dir, output_dir)

@dataclass
class ConfValues:
    input_dir: str = ''
    output_dir: str = ''

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
    # input_dir_pattern = re.compile(r'^input_dir\s*=')
    # output_dir_pattern = re.compile(r'^output_dir\s*=')

    # Search for configuration option pattern in file
    with open(conf_file, 'r') as file:
        for line in file:
            conf_match = conf_pattern.search(line)
            if not conf_match:
                continue

            # strip() removes leading and trailing characters
            # parse the configuration option if there's a match
            option = conf_match.group(1).strip()
            value = conf_match.group(2).strip()
            conf_values.init_from_conf(option, value)

            # sub('', ...) replaces the matched regex pattern with an empty string
            # if input_dir_pattern.search(line):
            #     input_dir = input_dir_pattern.sub('', line).strip('\n \"\'').rstrip('/\\')
            # if output_dir_pattern.search(line):
            #     output_dir = output_dir_pattern.sub('', line).strip('\n \"\'').rstrip('/\\')

    for key, value in asdict(conf_values).items():
        if not value:
            raise KeyError(f'Please specify {key} in the configuration file')
    return conf_values

# Does everything else in the program lmao
def write_output(input_dir: str, output_dir: str) -> None:
    # A compiled regex pattern for capturing the trailing
    # forward or backward slash into group 1, the folder ID
    # into group 2, and everything past that into group 3
    subfolder_pattern = re.compile(fr'{input_dir}([\/\\])(\d+)\s*(.*)')

    # Search each subfolder of the songs folder
    p_in = Path(input_dir)
    for p_in_sub in p_in.iterdir():
        if not p_in_sub.is_dir():
            continue

        # Create the output subfolder
        input_subfolder = str(p_in_sub)
        output_subfolder = output_dir + subfolder_pattern.sub(r'\1\3 \2', input_subfolder)
        p_out_sub = Path(output_subfolder)
        p_out_sub.mkdir(parents=True, exist_ok=True)

        # Copy all the audio
        copy_audio(p_in_sub, p_out_sub)

if __name__ == '__main__':
    main()
