__author__ = 'cephalopodblue'
import sys
import FindData
import FindMetadata
import argparse
import tempfile as tempfile
import os as os

def main():
    parser = argparse.ArgumentParser(description='Find data from audio file.')
    parser.add_argument('input_file', help="Input audio file.")
    parser.add_argument('-f', '--file', dest='output_file', help="Print output to specified file")
    parser.add_argument('-p', '--plot', help="Plot the power levels of the audio file.",
                        action='store_true')
    args = parser.parse_args()

    temp = tempfile.mkstemp()

    if args.plot:
        FindData.find_data(args.input_file, plotting=True)
    elif args.output_file:
        sys.stdout = open(args.output_file, 'w+')

    FindData.find_data(args.input_file, temp[1])
    file = open(temp[1], 'r')
    audio_info = file.read()
    file.close()
    os.close(temp[0])
    os.remove(temp[1])
    formatted = "{\n\"audio_info\": " + audio_info + ",\"metadata\": "
    print formatted
    metadata = FindMetadata.find_metadata(args.input_file)
    print "\n}"

    file.close()

main()