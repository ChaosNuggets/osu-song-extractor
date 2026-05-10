import re
from pathlib import Path
from copy_audio import copy_audio
from read_conf_file import read_conf_file

def main():
    conf_values = read_conf_file('osu-song-extractor.cfg')
    write_output(conf_values)

# Does everything else in the program lmao
def write_output(conf_values: ConfValues) -> None:
    # A compiled regex pattern for capturing the trailing
    # forward or backward slash into group 1, the folder ID
    # into group 2, and everything past that into group 3
    subfolder_pattern = re.compile(fr'{conf_values.input_dir}([\/\\])(\d+)\s*(.*)')

    # Search each subfolder of the songs folder
    p_in = Path(conf_values.input_dir)
    for p_in_sub in p_in.iterdir():
        if not p_in_sub.is_dir():
            continue

        # Create the output subfolder
        input_subfolder = str(p_in_sub)
        output_subfolder = conf_values.output_dir + subfolder_pattern.sub(r'\1\3 \2', input_subfolder)
        p_out_sub = Path(output_subfolder)
        p_out_sub.mkdir(parents=True, exist_ok=True)

        # Copy all the audio
        copy_audio(p_in_sub, p_out_sub)

if __name__ == '__main__':
    main()
