# Configuration Guide
The configuration file is called osu-song-extractor.cfg. This is the documentation for that file.

# Replacement Fields
Some options support replacement fields. The following replacement fields are accepted:

**\<AudioFilename\>, \<Title\>, \<Artist\>, \<Version\>, \<BackgroundFilename\>, \<BeatmapID\>, \<BeatmapSetID\>**

Look online for the .osu file format documentation for more details about what each of these mean. Also, the program automatically strips the extension for folders and adds the correct extension for filenames, so no need to worry about that.

# Configuration Options
There are 5 section headers:

**\[General\], \[one\_bg\_one\_song\], \[mult\_bg\_one\_song\], \[one\_bg\_mult\_song\], \[mult\_bg\_mult\_song\]**

**\[General\]** configurations apply to every beatmap, and one of the four **\[*x*\_bg\_*x*\_song\]** configurations will also apply each beatmap. The beatmaps are categorized based on the number of songs and backgrounds listed in its .osu files.

The purpose of these headers is to apply different behavior depending on the type of beatmap. For example, beatmaps with one background and multiple songs are probably different rates of the same song, so including "\<Version\>" (the difficulty name) in the exported song's filename / metadata may be useful.

# TODO: KEEP WRITING HERE
## [General]
# input\_dir is the path to your Osu Songs folder, output\_dir is where it will get copied to
# There is no default for these two options
input\_dir = "~/Music/Songs"
output\_dir = "~/Music/Extracted-Songs/"

# True: export each beatmap into a different subfolder
# False: export each beatmap in the top-level output directory
# Default: True
export\_into\_subfolders = True

# Name of each subfolder with support for replacement fields extracted from the beatmap's .osu file.
# Supports replacement fields, see top of document for a list of all replacement fields
# Default: "\<Artist\> - \<Title\> \<BeatmapSetID\>"
subfolder\_name = "\<Artist\> - \<Title\> \<BeatmapSetID\>"

# Sometimes, the values in the .osu file will have illegal filename characters (\<, \>, :, ", /, \\, |, ?, \*). If you then use a
# replacement field, this can lead to an illegal folder / file name. What should the illegal character(s) be replaced with?
# Default: "-"
illegal\_char\_override = "-"

# Configuration options that only apply to beatmaps with one background and one song
[one\_bg\_one\_song]
# Whether or not to create a deeper subfolder for each audio file.
# Default: True for mult\_bg\_mult\_song, False for all other beatmap types
export\_into\_deep\_subfolder = False

# What name to give the deeper subfolder.
# Supports replacement fields, see top of document for a list of all replacement fields
# Default: "\<Version\>"
deep\_subfolder\_name = "\<Version\>"

# Whether or not to overrite existing files in the output directory
# with the same filename. Possible values are True, False.
# Default: False
overrite\_existing\_files = False

# What name to give the exported song (program puts the audio extension for you, no need to list that)
# Supports replacement fields, see top of document for a list of all replacement fields
# Default: "\<Artist\> - \<Title\>" if there's only one song,
#          "\<Artist\> - \<Title\> [\<Version\>]" for one\_bg\_mult\_song, "\<Version\>" for mult\_bg\_mult\_song
song\_filename = "\<Artist\> - \<Title\>"

# When to overrite the output song metadata, based on if it's present in the original file.
# Possible values are NEVER, IF\_MISSING, ALWAYS.
# Default: IF\_MISSING
meta\_write\_mode = IF\_MISSING 

# What metadata to write to the exported song's title field.
# Supports replacement fields, see top of document for a list of all replacement fields
# Default: "\<Title\>" for one\_bg\_one\_song and mult\_bg\_one\_song,
#          "\<Title\> [\<Version\>]" for one\_bg\_mult\_song, "\<Version\>" for mult\_bg\_mult\_song
title\_meta = "\<Title\>"

# What metadata to write to the exported song's artist field.
# Supports replacement fields, see top of document for a list of all replacement fields
# Default: "\<Artist\>" for everything besides mult\_bg\_mult\_song,
# "" for mult\_bg\_mult\_song (blank string means don't modify this field)
artist\_meta = "\<Artist\>"

# How to export the background - never, as a separate file in the same directory as the output audio file,
# or as part of the output file's metadata.
# Possible values are NEVER, AS\_SEPARATE, AS\_META
# Default: AS\_SEPARATE
bg\_export\_mode = AS\_SEPARATE

# What name to give the exported background image (if exporting as separate file)
# Supports replacement fields, see top of document for a list of all replacement fields
# Default: \<BackgroundFilename\>
bg\_filename = "\<BackgroundFilename\>"
