from pathlib import Path
import os
from unittest import result

file = open("results_22 - Done/CuratedList.tsv", "r+")
# file.write("123\n")

file.seek(0, os.SEEK_END)

        # This code means the following code skips the very last character in the file -
        # i.e. in the case the last line is null we delete the last line
        # and the penultimate one
pos = file.tell() - 3
file.seek(pos)
# Read each character in the file one at a time from the penultimate
# character going backwards, searching for a newline character
# If we find a new line, exit the search
while pos > 0 and file.read(1) != "\n":
    pos -= 1
    print(pos)
    file.seek(pos, os.SEEK_SET)

# So long as we're not at the start of the file, delete all the characters ahead
# of this position
# if pos > 0:
#     file.seek(pos, os.SEEK_SET)
line = file.readline()
file.seek(pos)
file.close()
