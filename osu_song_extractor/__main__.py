from osu_song_extractor.conf import read_conf_file
from osu_song_extractor.extract import extract_all_beatmaps

def main():
    conf_info = read_conf_file('osu-song-extractor.cfg')
    extract_all_beatmaps(conf_info)

if __name__ == '__main__':
    main()
