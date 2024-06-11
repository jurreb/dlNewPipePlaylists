#!/usr/bin/env python3
from io import StringIO
from sqlite3 import Error
import csv
import sqlite3
import sys
import os
import subprocess
from termcolor import colored
import glob
import shutil


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
 
    return None


def get_rows(db_file):
    conn = create_connection(db_file)

    cmds = """
    select 
            playlists.name as playlist_name,
            title,
            url--,
            --stream_type,
            --duration,
            --uploader,
            --streams.thumbnail_Url,
            --playlists.thumbnail_url as playlist_thumbnail_url
    from streams 
    inner join playlist_stream_join on playlist_stream_join.stream_id = streams.uid
    inner join playlists on playlists.uid == playlist_stream_join.playlist_id
    order by playlists.name
    """
    cur = conn.cursor()
    cur.execute(cmds)
    rows = cur.fetchall()
    return rows


def main(db_file):
    allPlaylists = set()
#    exportPlaylists = ['žur playlista', 'žur jedenje', 'žur od polpetih do šestih, popevke, jugo', 'žur zbiranje, jazz in popevke', 'žur ples', 'Valentin&Marjetka', 'Valentin&Marjetka poroka']
    exportPlaylists = ['Valentin&Marjetka']
    root_dl_dir = './dl/'
    root_out_dir = './out/'
#    executable = 'youtube-dl'
    executable = 'yt-dlp' #set executable to use for download (youtube-dl not working on 11.6.2024)

    rows = get_rows(db_file)

    f = StringIO()
    wr = csv.writer(f)
    wr.writerow([
#        'url', 'title', 'stream_type', 'duration', 'uploader',
#        'stream_thumbnail_url', 'playlist_name', 'playlist_thumbnail_url'])
         'playlist_name', 'title', 'url'])

    # print list of mp3 files
    print()
    print(colored('--- existing mp3 files on disk ---', 'green'))
    for filename in glob.iglob(root_dl_dir + '**/*.mp3', recursive=True):
        print(filename)

    # run youtube-dl for all playlists
    print()
    print(colored('--- downloading now ---', 'blue'))
    i = 0
    playlist_name = ''
    for row in rows:
        if playlist_name != row[0]:
            i = 0 
        i = i + 1
        playlist_name = row[0]
        title = row[1]
        url = row[2]

        allPlaylists.add(playlist_name)
        if playlist_name in exportPlaylists:
            if not os.path.isdir(os.path.join(root_dl_dir, playlist_name)):
                os.makedirs(os.path.join(root_dl_dir, playlist_name))
            wr.writerow(row)
            command = executable + '|-f|bestaudio|--add-metadata|--extract-audio|--audio-format|mp3|--audio-quality|0|-o|' + os.path.join(root_dl_dir, playlist_name) + '/' + str(i).zfill(3) + ' - %(title)s.%(ext)s|-k|--no-post-overwrites|' + url 

#            result = subprocess.run((command + '|--get-filename').split('|'), stdout=subprocess.PIPE)
#            result = subprocess.run((command + '|--get-title').split('|'), stdout=subprocess.PIPE)
#            filename = result.stdout
#            print(filename)

            print(colored(title, 'magenta'))
            print(colored(command, 'yellow'))
            subprocess.run(command.split('|'), shell=False)
            print()

    # copy all mp3 files to root_out_dir
    print()
    print(colored('--- copying mp3 files on disk ---', 'green'))
    for src_filename in glob.iglob(root_dl_dir + '**/*.mp3', recursive=True):
        dest_filename = src_filename.replace(root_dl_dir, root_out_dir, 1) 
        print(src_filename + colored(' ==> ', 'cyan') + dest_filename)
        dest_dirname = os.path.dirname(dest_filename)
        if not os.path.isdir(dest_dirname):
            os.makedirs(dest_dirname)
        shutil.copyfile(src_filename, dest_filename)

    print(colored('--- all playlists in newpipe.db ---', 'red'))
    print(allPlaylists)
    print(colored('--- export playlists ---', 'green'))
    print(exportPlaylists)
    print(colored('--- exported songs ---', 'blue'))
    print(f.getvalue())




if __name__ == '__main__':
    main(sys.argv[1])
