import re

def main():
    input_dir, output_dir = read_conf_file()
    print(input_dir)
    print(output_dir)

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

if __name__ == '__main__':
    main()
