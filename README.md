# Curses txt reader
[![License: MPL 2.0](https://img.shields.io/badge/License-MPL_2.0-brightgreen.svg)](https://opensource.org/licenses/MPL-2.0)
[![PyPI version](https://badge.fury.io/py/curtxt-reader.svg)](https://badge.fury.io/py/curtxt-reader)
## About
A simple(?) ncurses-based plain text reader written in python.
## Instalation
From PyPI:  
	
    $ pip install curtxt-reader

From source:

    $ git clone https://github.com/1256-bits/curses-txt-reader.git
    $ cd curses-txt-reader
    $ pip install .

## Usage
Curses txt reader accepts text from both stdin via pipes  
	
    $ echo something | curtxt

and a (single) file
	
    $ curtxt file.txt
    
When presented with both stdin and a file at the same time it will open the file.
Curses txt reader does not accept multiple files. Use cat instead.
Previously opened files will open on the same page they were left off
### Controls:
* Arrow Up/Down - page up and down
* [page number]g - go to a page with specified number
* Q - quit (Ctrl+C is also fine)
* B - toggle progress bar
* Home - got to the first page
* End - go to the last page
### Command line options:

    -h, --help - pring help message and exit
    -v, --version - print version number and exit
    -c, --clear - clear history file
