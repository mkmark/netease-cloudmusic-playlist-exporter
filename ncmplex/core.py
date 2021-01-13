# -*- coding: utf-8 -*-
import json
import sqlite3
import re

def get_playlistsd(webdb_dat_path):
    """
    Returns
    playlistsd[pid] = {
        'playlist_name': playlist_name,
        "track_count": track_count,
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
        track_count = playlist_infod['trackCount']
        playlistsd[pid] = {
            'playlist_name': playlist_name,
            "track_count": track_count,
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
    def get_all_non_empty_pids(playlistsd):
        pids = []
        for pid in playlistsd:
            if (playlistsd[pid]['track_count'] != 0):
                pids.append(pid)

    def get_non_empty_pid_of_playlist_name(playlist_name, playlistsd):
        for pid in playlistsd:
            if (playlistsd[pid]['playlist_name'] == playlist_name) & (playlistsd[pid]['track_count'] != 0):
                return pid
        print(playlist_name + " not found")
        exit()

    if playlist_names == []:
        pids = get_all_non_empty_pids(playlistsd)
    else:
        pids = [get_non_empty_pid_of_playlist_name(playlist_name, playlistsd) for playlist_name in playlist_names]
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
        _str = re.sub(r'[\/]', '／', _str)
        _str = re.sub(r'[\\]', '＼', _str)
        _str = re.sub(r'[\"]', '＂', _str)
        _str = re.sub(r'[\:]', '：', _str)
        _str = re.sub(r'[\*]', '＊', _str)
        _str = re.sub(r'[\?]', '？', _str)
        _str = re.sub(r'[\<]', '《', _str)
        _str = re.sub(r'[\>]', '》', _str)
        _str = re.sub(r'[\|]', '｜', _str)
        return _str
    
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

def get_relative_path(m3u8d, base_path):
    def replace_ignore_case(old, new, text):
        idx = 0
        while idx < len(text):
            index_l = text.lower().find(old.lower(), idx)
            if index_l == -1:
                return text
            text = text[:index_l] + new + text[index_l + len(old):]
            idx = index_l + len(new) 
        return text

    for pid in m3u8d:
        for tid in m3u8d[pid]['tracks']:
            # remove base path
            m3u8d[pid]['tracks'][tid]['path'] = replace_ignore_case(base_path, "", m3u8d[pid]['tracks'][tid]['path'])
            # nt to posix path
            m3u8d[pid]['tracks'][tid]['path'] = m3u8d[pid]['tracks'][tid]['path'].replace("\\", "/")
    return m3u8d