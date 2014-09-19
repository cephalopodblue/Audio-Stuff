__author__ = 'cephalopodblue'
import mutagen
import json
import os
import sys

_file_types = {'.wma': 'wma', '.mp3': 'id3', '.m4a': 'aac', '.flac': 'vorbis'}
_disallowed_attributes = {0x0001: "ASFByteArrayAttribute"}

def _get_data(file_name):
    metadata = mutagen.File(file_name)
    short_name = os.path.basename(file_name)
    print("{\n")
    print("\t\"file\": " + "\"" + short_name + "\",\n")
    print("\t\"raw_meta\": {\n")
    return metadata

def get_data_vorbis(file_name):
    """Get data from a file with vorbis metadata.

    Formats with vorbis metadata include flac,"""

    file = _get_data(file_name)
    first = True
    for tag_name in file:
        try:
            tag = json.dumps(file[tag_name])
        except TypeError:
            tag = json.dumps(str(file[tag_name]))
        if not first:
            print ","
        print "\t\t\"" + tag_name + "\": " + tag,
        first = False

    print("\n\t}")
    print("}")

def get_data_id3(file_name):
    """Get data from a file with ID3v2 formatted metadata.

    Formats with ID3 metadata include mp3,"""
    get_data_vorbis(file_name)

def get_data_aac(file_name):
    """Get data from an AAC file."""
    get_data_vorbis(file_name)

def get_data_wma(file_name):
    """Get JSON-formatted metadata from a WMA file."""

    first = True
    file = _get_data(file_name)

    for tag_name in file:
        for tag in file[tag_name]:
            if isinstance(tag, mutagen.asf.ASFBaseAttribute):
                if not tag.TYPE in _disallowed_attributes:
                    tag = tag.value
                    if not first:
                        print ","
                    print "\t\t\"" + tag_name + "\": " + json.dumps(tag),
            else:
                if not first:
                    print ","
                print "\t\t\"" + tag_name + "\": " + json.dumps(tag),
            first = False
    print "\t}"
    print "}"

def find_metadata(file_name):
    """Attempts to discover file type and find metadata for it."""

    ext = os.path.splitext(file_name)[1].lower()
    if ext in _file_types:
        if _file_types[ext]  == "vorbis":
            get_data_vorbis(file_name)
        elif _file_types[ext]  == "id3":
            get_data_id3(file_name)
        elif _file_types[ext]  == "aac":
            get_data_aac(file_name)
        elif _file_types[ext]  == "wma":
            get_data_wma(file_name)