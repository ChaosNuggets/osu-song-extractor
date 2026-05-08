import re
from pathlib import Path

def main():
    input_dir, output_dir = read_conf_file()
    write_output(input_dir, output_dir)

# Returns the input_dir and output_dir entries in osu-song-extractor.cfg
def read_conf_file() -> tuple[str, str]:
    input_dir = ''
    output_dir = ''

    # Compiling is efficient for loops
    input_dir_pattern = re.compile(r'^input_dir=')
    output_dir_pattern = re.compile(r'^output_dir=')

    with open('osu-song-extractor.cfg', 'r') as file:
        for line in file:
            # strip() removes leading and trailing characters
            # sub('', ...) replaces the matched regex pattern with an empty string
            if input_dir_pattern.search(line):
                input_dir = input_dir_pattern.sub('', line).strip('\n \"\'')
            if output_dir_pattern.search(line):
                output_dir = output_dir_pattern.sub('', line).strip('\n \"\'')

    if not input_dir or not output_dir:
        raise KeyError('Please specify both input_dir and output_dir in the configuration file')
    return input_dir, output_dir

def write_output(input_dir: str, output_dir: str) -> None:
    # A compiled regex pattern for capturing folder ID
    # into group 1 and everything past that into group 2
    subfolder_pattern = re.compile(fr'{input_dir}/(\d+)\s*(.*)')

    # Search each subfolder of the songs folder
    p_in = Path(input_dir)
    for p_in_sub in p_in.iterdir():
        if not p_in_sub.is_dir():
            continue

        # Create the output_subfolder
        input_subfolder = str(p_in_sub)
        output_subfolder = f'{output_dir}/' + subfolder_pattern.sub(r'\2 \1', input_subfolder)
        p_out_sub = Path(output_subfolder)
        p_out_sub.mkdir(parents=True, exist_ok=True)

        # TODO: code up the rest of the plan lol

if __name__ == '__main__':
    main()
