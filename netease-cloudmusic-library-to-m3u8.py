import os
import subprocess
import json
import sqlite3
import re
import argparse

def get_playlistsd(webdb_dat_path):
    """
    Returns
    playlistsd[pid] = {
        'playlist_name': playlist_name,
        'tids': list()
    }
    """
    playlistsd = {}
    # connect to webdb.dat
    con = sqlite3.connect(webdb_dat_path)
    cur = con.cursor()
    # get pids and playlist_names
    web_playlist = cur.execute(
        'SELECT pid, playlist \
         FROM web_playlist')
    for pid, playlist_info in web_playlist:
        playlist_infod = json.loads(playlist_info)
        playlist_name = playlist_infod['name']
        playlistsd[pid] = {
            'playlist_name': playlist_name,
            'tids': list()
        }
    # get tids of pid
    for pid in playlistsd:
        web_playlist_track = cur.execute(
            'SELECT pid, tid \
             FROM web_playlist_track \
             WHERE pid = ' + str(pid) + '\
             ORDER BY "order" ASC')
        for pid, tid in web_playlist_track:
            playlistsd[pid]['tids'].append(tid)
    con.close();   
    return playlistsd
        
def get_track_infod(webdb_dat_path, library_dat_path, download_path):
    """
    Returns 
    track_info[tid] = {
        'path': path,
        'track_name': track_name,
        'artists_name': artists_name,
        'duration': duration
    }
    """
    track_infod = {}
    # first get track, note these information may be incorrect due to duplication and out of date
    con = sqlite3.connect(library_dat_path)
    cur = con.cursor()
    library_dat_track = cur.execute(
        'SELECT file, tid, title, artist, duration \
         FROM track'
    )
    for file, tid, title, artist, duration in library_dat_track:
        if file == '' or tid == '':
            continue
        else:
            tid = int(tid)
            track_infod[tid] = {}
            track_infod[tid]['path'] = file
            track_infod[tid]['track_name'] = title
            if len(artist.split(",")) > 1:
                track_infod[tid]['artists_name'] = artist.split(",")[1]
            track_infod[tid]['duration'] = str(round(duration/1000))
    con.close();

    # then get web_offline_track
    con = sqlite3.connect(webdb_dat_path)
    cur = con.cursor()
    
    web_offline_track = cur.execute(
        'SELECT track_id, detail, track_name, artist_name, relative_path \
         FROM web_offline_track'
    )
    for tid, detail, track_name, artists_name, relative_path in web_offline_track:
        if relative_path == '':
            continue
        else:
            track_infod[tid] = {}
            track_infod[tid]['path'] = download_path + relative_path
            track_infod[tid]['track_name'] = track_name
            track_infod[tid]['artists_name'] = artists_name
            track_infod[tid]['duration'] = str(round(json.loads(detail)['duration']/1000))

    # then get web_cloud_track
    web_cloud_track = cur.execute(
        'SELECT id, name, artist, track, file \
         FROM web_cloud_track'
    )
    for tid, name, artist, track, file in web_cloud_track:
        if file == '':
            continue
        else:
            track_infod[tid] = {}
            track_infod[tid]['path'] = file
            track_infod[tid]['track_name'] = name
            if len(artist.split(",")) > 1:
                track_infod[tid]['artists_name'] = artist.split(",")[1]
            track_infod[tid]['duration'] = str(round(json.loads(track)['duration']/1000))
    con.close();

    return track_infod
    
def get_pids_of_playlist_names(playlist_names, playlistsd):
    def get_all_pids(playlistsd):
        return [pid for pid in playlistsd]

    def get_pid_of_playlist_name(playlist_name, playlistsd):
        for pid in playlistsd:
            if playlistsd[pid]['playlist_name'] == playlist_name:
                return pid

    if playlist_names == []:
        pids = get_all_pids(playlistsd)
    else:
        pids = [get_pid_of_playlist_name(playlist_name, playlistsd) for playlist_name in playlist_names]
    return pids
        
def get_m3u8d(pids, playlistsd, track_infod):
    """
    Returns m3u8d[pid]{
        'playlist_name': playlistsd[pid]['playlist_name'],
        'tracks'[tid]: {
            'path': path,
            'track_name': track_name,
            'artists_name': artists_name,
            'duration': duration
        }
    }
    """
    m3u8d = {}
    for pid in pids:
        m3u8d[pid] = {
            'playlist_name': playlistsd[pid]['playlist_name'],
            'tracks': {}
        }
        tids = playlistsd[pid]["tids"]
        for tid in tids:
            if tid in track_infod.keys():
                m3u8d[pid]['tracks'][tid] = {}
                path = track_infod[tid]['path']
                if path != None:
                    m3u8d[pid]['tracks'][tid] = track_infod[tid]
    return m3u8d

def export(m3u8d, export_path):
    def make_string_windows_compatible(_str):
        return re.sub(r'[\\\/\:\*\?\"\<\>\|]', '_', _str)
        # https://en.wikipedia.org/wiki/M3U

    for pid in m3u8d:
        playlist_name = make_string_windows_compatible(m3u8d[pid]['playlist_name'])
        file_name = playlist_name + '.m3u8'
        file_path = export_path + file_name
        with open(file_path, 'w', encoding='utf-8', errors='ignore') as m3u8_file:
            m3u8_file_content = '#EXTM3U\n'
            for tid in m3u8d[pid]['tracks']:
                m3u8_file_content = m3u8_file_content + '#EXTINF:' + \
                                    m3u8d[pid]['tracks'][tid]['duration'] + ', ' + \
                                    m3u8d[pid]['tracks'][tid]['artists_name'] + ' - ' + \
                                    m3u8d[pid]['tracks'][tid]['track_name'] + '\n' + \
                                    m3u8d[pid]['tracks'][tid]['path'] + '\n'
            m3u8_file.write(m3u8_file_content)
    print("Files saved at " + export_path)


def main():
    # see if is wsl or windows
    # os.name == 'posix'
    if os.name == 'posix':
        windows_username = subprocess.getoutput('cmd.exe /c echo $USER').title()
        default_library_path = '/mnt/c/Users/' + windows_username + '/AppData/Local/Netease/CloudMusic/Library/'
        default_download_path = "C:\\Users\\" + windows_username + "\\Music\\CloudMusic\\"
        default_export_path = '/mnt/c/Users/' + windows_username + '/Music/Playlists/'
    else:
    # os.name == 'nt'
        #windows_username = os.environ['USERNAME']
        default_library_path = os.path.expanduser('~') + "\\AppData\\Local\\Netease\CloudMusic\\Library\\"
        default_download_path = os.path.expanduser('~') + "\\Music\\CloudMusic\\"
        default_export_path = os.path.expanduser('~') + "\\Music\\Playlists\\"

    # parse args
    parser = argparse.ArgumentParser(description="""
    This script creates .m3u8 playlists from Netease Cloudmusic webdb.dat.
    """)
    parser.add_argument("-p", default = [], \
                              help = "playlist name, leave blank to export all, can be specified multiple times or as an array (default: [])", \
                              action = 'append', \
                              required = False)
    parser.add_argument("-l", default = default_library_path, \
                              help = "webdb.dat and library.dat directory (default: " + default_library_path + ")", \
                              required = False)
    parser.add_argument("-d", default = default_download_path, \
                              help = "Cloudmusic download path (default: " + default_download_path + ")", \
                              required = False)
    parser.add_argument("-e", default = default_export_path, \
                              help = "generated .m3u8 file export path (default: " + default_export_path + ")", \
                              required = False)
    args = parser.parse_args()
    playlist_names = args.p
    download_path = args.d
    export_path = args.e

    library_dat_path = args.l + 'library.dat'
    webdb_dat_path = args.l + 'webdb.dat'

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
    print(pids)
    # assemble m3u8 dict
    m3u8d = get_m3u8d(pids, playlistsd, track_infod)

    # export
    export(m3u8d, export_path)

if __name__ == '__main__':
    main()