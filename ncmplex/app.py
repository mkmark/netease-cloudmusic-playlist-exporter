# -*- coding: utf-8 -*-
import os
import subprocess
import argparse

if __package__ is None:
    from core import *
else:
    from .core import *

# set default values
# see if is wsl or windows
# os.name == 'posix'
if os.name == 'posix':
    windows_username = subprocess.getoutput('cmd.exe /c echo $USER').title()
    default_library_path = '/mnt/c/Users/' + windows_username + '/AppData/Local/Netease/CloudMusic/Library/'
    default_download_path = "C:\\Users\\" + windows_username + "\\Music\\CloudMusic\\"
    default_export_path = '/mnt/c/Users/' + windows_username + '/Music/'
else:
# os.name == 'nt'
    #windows_username = os.environ['USERNAME']
    default_library_path = os.path.expanduser('~') + "\\AppData\\Local\\Netease\CloudMusic\\Library\\"
    default_download_path = os.path.expanduser('~') + "\\Music\\CloudMusic\\"
    default_export_path = os.path.expanduser('~') + "\\Music\\"

# parse args
parser = argparse.ArgumentParser(description="""
This tool creates .m3u8 playlists from Netease Cloudmusic webdb.dat.
""")
parser.add_argument("-p", default = [], \
                          dest = "PLAYLIST", \
                          help = "playlist name, leave blank to export all, can be specified multiple times (default: [])", \
                          action = 'append', \
                          required = False)
parser.add_argument("-l", default = default_library_path, \
                          dest = "LIB_PATH", \
                          help = "webdb.dat and library.dat directory (default: " + default_library_path + ")", \
                          required = False)
parser.add_argument("-d", default = default_download_path, \
                          dest = "DOWNLOAD_PATH", \
                          help = "Cloudmusic download path (default: " + default_download_path + ")", \
                          required = False)
parser.add_argument("-e", default = default_export_path, \
                          dest = "EXPORT_PATH", \
                          help = "generated .m3u8 file export path (default: " + default_export_path + ")", \
                          required = False)
parser.add_argument("-r", default = False, \
                          dest = "USE_RELATIVE_PATH", \
                          help = "specify to remove base path and use relative posix path", \
                          action='store_const', \
                          const = True, \
                          required = False)
parser.add_argument("-b", help = "specify base path to be removed with -r (default to EXPORT_PATH)", \
                          dest = "BASE_PATH", \
                          required = False)

def main():
    args = parser.parse_args()
    playlist_names = args.PLAYLIST
    download_path = args.DOWNLOAD_PATH
    export_path = args.EXPORT_PATH
    use_relative_path = args.USE_RELATIVE_PATH
    if args.BASE_PATH == None:
        base_path = args.EXPORT_PATH
    else:
        base_path = args.BASE_PATH

    library_dat_path = args.LIB_PATH + 'library.dat'
    webdb_dat_path = args.LIB_PATH + 'webdb.dat'

    if not os.path.exists(webdb_dat_path):
        print(webdb_dat_path + " doesn't exist. Type -h for help.")
        return

    if not os.path.exists(export_path):
        print(export_path + " doesn't exist. Type -h for help.")
        return

    # process
    # get all playlists
    playlistsd = get_playlistsd(webdb_dat_path)
    # get all tracks
    track_infod = get_track_infod(webdb_dat_path, library_dat_path, download_path)
    # get desired playlist pids
    pids = get_pids_of_playlist_names(playlist_names, playlistsd)
    # assemble m3u8 dict
    m3u8d = get_m3u8d(pids, playlistsd, track_infod)
    # get m3u8 with relative path 
    if use_relative_path: 
        m3u8d = get_relative_path(m3u8d, base_path)
    # export
    export(m3u8d, export_path)

if __name__ == '__main__':
    main()