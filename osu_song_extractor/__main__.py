from read_conf_file import read_conf_file
from write_output import write_output

def main():
    conf_info = read_conf_file('osu-song-extractor.cfg')
    write_output(conf_info)

if __name__ == '__main__':
    main()
