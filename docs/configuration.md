# TODO: ADD EXAMPLES
# Configuration Guide
The configuration file is called osu-song-extractor.cfg. This is the documentation for that file.

# Table of Contents
1. [Configuration Options](#configuration-options)
2. [Replacement Fields](#replacement-fields)

# Configuration Options
There are 5 section headers:

**\[General\], \[one\_bg\_one\_song\], \[mult\_bg\_one\_song\], \[one\_bg\_mult\_song\], \[mult\_bg\_mult\_song\]**

**\[General\]** configurations apply to every beatmap, and one of the four **\[*x*\_bg\_*x*\_song\]** configurations will also apply each beatmap. The beatmaps are categorized based on the number of songs and backgrounds listed in its .osu files.

The purpose of these headers is to apply different behavior depending on the type of beatmap. For example, beatmaps with one background and multiple songs are probably different rates of the same song, so including `"<Version>"` (the difficulty name) in the exported song's filename / metadata may be useful. Likewise, beatmaps with multiple backgrounds and multiple songs are probably map packs.

## \[General\] Options
### input\_dir
This is the path to your Osu Songs folder. There is no default for this option.

Example:
```
input_dir = "C:\Users\{Username}\AppData\Local\osu!\Songs"
```

### output\_dir
This is where the songs will get copied to. There is no default for this option.

Example:
```
output_dir = "C:\Users\{Username}\Music\Extracted-Songs"
```

### export\_into\_subfolders
`True`: export each beatmap into a different subfolder \
`False`: export each beatmap in the top-level output directory \
Default: `True`

### subfolder\_name
Name of each subfolder if `export_into_subfolders` is `True`. Supports [replacement fields](#replacement-fields). \
Default: `"<Artist> - <Title> <BeatmapSetID>"`

### illegal\_char\_override
Sometimes, the values in the .osu file will have illegal filename characters (`<, >, :, ", /, \, |, ?, *`). If you then use a replacement field, this can lead to illegal folder / file names. What should the illegal character(s) be replaced with? \
Default: `"-"`

## \[*x*\_bg\_*x*\_song] Options
### export\_into\_deep\_subfolder
Whether or not to create a deeper subfolder for each audio file. \
Default: `True` for \[mult\_bg\_mult\_song\], `False` for all other beatmap types

### deep\_subfolder\_name
What name to give the deeper subfolders if `export_into_deep_subfolder` is `True`. Supports [replacement fields](#replacement-fields). \
Default: `"<Version>"`

### overrite\_existing\_files
Whether or not to overrite existing files in the output directory with the same filename. Possible values are `True`, `False`. \
Default: `False`

### song\_filename
What name to give the exported song. Supports [replacement fields](#replacement-fields). \
Default: `"<Artist> - <Title>"` if there's only one song, `"<Artist> - <Title> [<Version>]"` for \[one\_bg\_mult\_song\], `"<Artist> - <Version>"` for \[mult\_bg\_mult\_song\]

### meta\_write\_mode
When to overrite the output song's title and artist metadata, based on if it's present in the original file. Possible values are `NEVER`, `IF_MISSING`, `ALWAYS`. \
Default: `IF_MISSING`

### title\_meta
What metadata to write to the exported song's title field. Supports [replacement fields](#replacement-fields). \
Default: `"<Title>"` if there's only one song, `"<Title> [<Version>]"` for \[one\_bg\_mult\_song\], `"<Version>"` for \[mult\_bg\_mult\_song\]

### artist\_meta
What metadata to write to the exported song's artist field. Supports [replacement fields](#replacement-fields). \
Default: `"<Artist>"` 

### bg\_export\_mode
How to export the background. \
`NEVER`: Don't export the background. \
`AS_SEPARATE`: Export as a separate file in the same directory as the output audio file. \
`AS_META_IF_MISSING`: Export as part of the output file's metadata only if it's missing from the original audio file. \
`AS_META_ALWAYS`: Export as part of the output file's metadata even if it already exists in the original audio file. \
Default: `AS_SEPARATE`

### bg\_filename
What name to give the exported background image if `bg_export_mode` is `AS_SEPARATE`. Supports [replacement fields](#replacement-fields). \
Default: `"<BackgroundFilename>"`

# Replacement Fields
Some options support replacement fields, which are denoted by angle brackets `<>`. The following replacement fields are accepted:

**\<AudioFilename\>, \<Title\>, \<Artist\>, \<Version\>, \<BackgroundFilename\>, \<BeatmapID\>, \<BeatmapSetID\>**

Look online for the .osu file format documentation for more details about what each of these mean. Also, the program automatically strips the extension for folders and adds the correct extension for filenames, so no need to worry about that.
