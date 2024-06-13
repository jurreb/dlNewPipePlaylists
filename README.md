# dlNewPipePlaylists
download video from youtube to mp3

## usage
run in terminal: python3 script.py newpipe.db

## newpipe.db
sample database included in this repo.  
passed as command line argument to script.py.  
playlist information will be extracted from this file.  
this file is exported from newpipe (settings->backup and restore->export).  

## script.py
python script which does the work.

## prerequisites
- python3
- script.py uses youtube-dl or yt-dlp to download youtube videos as mp3 files
