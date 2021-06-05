# -*- coding: utf-8 -*-
import json
import sqlite3
import re
import glob
import logging
import os

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

def make_artist_windows_compatible(_str):
    _str = re.sub(r'[\/]', ',', _str)
    _str = re.sub(r'[\\]', ',', _str)
    _str = re.sub(r'[\"]', '＂', _str)
    _str = re.sub(r'[\:]', '：', _str)
    _str = re.sub(r'[\*]', '＊', _str)
    _str = re.sub(r'[\?]', '？', _str)
    _str = re.sub(r'[\<]', '《', _str)
    _str = re.sub(r'[\>]', '》', _str)
    _str = re.sub(r'[\|]', '｜', _str)
    return _str

def get_playlistsd(webdb_dat_path):
    logging.debug("get_playlistsd %s", webdb_dat_path)
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
        
def get_track_infod(webdb_dat_path, library_dat_path, download_path, additional_path_formats):
    logging.debug("get_track_infod %s, %s, %s", webdb_dat_path, library_dat_path, download_path)
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

    # get web_offline_track
    con = sqlite3.connect(webdb_dat_path)
    cur = con.cursor()
    
    web_offline_track = cur.execute(
        'SELECT track_id, detail, track_name, artist_name, relative_path \
         FROM web_offline_track'
    )
    for tid, detail, track_name, artists_name, relative_path in web_offline_track:
        album_name = json.loads(detail)["album"]["name"]
        track_infod[tid] = {}
        track_infod[tid]['path'] = download_path + relative_path
        track_infod[tid]['track_name'] = track_name
        track_infod[tid]['artists_name'] = artists_name
        track_infod[tid]['duration'] = str(round(json.loads(detail)['duration']/1000))
        track_infod[tid]['album_name'] = album_name

    # then get track, note these information may be incorrect due to duplication and out of date
    con = sqlite3.connect(library_dat_path)
    cur = con.cursor()
    library_dat_track = cur.execute(
        'SELECT file, tid, title, album, artist, duration \
         FROM track'
    )
    for file, tid, title, album, artist, duration in library_dat_track:
        if file == '' or tid == '':
            continue
        else:
            tid = int(tid)
            track_infod[tid] = {}
            track_infod[tid]['track_name'] = title
            track_infod[tid]['album_name'] = album
            if len(artist.split(",")) > 1:
                track_infod[tid]['artists_name'] = artist.split(",")[1]
            track_infod[tid]['duration'] = str(round(duration/1000))
            if not 'path' in track_infod[tid]:
                track_infod[tid]['path'] = file
    con.close();

    # then get web_cloud_track
    # web_cloud_track = cur.execute(
    #     'SELECT id, name, artist, track, file \
    #      FROM web_cloud_track'
    # )
    # for tid, name, artist, track, file in web_cloud_track:
    #     if file == '':
    #         continue
    #     else:
    #         track_infod[tid] = {}
    #         track_infod[tid]['path'] = file
    #         track_infod[tid]['track_name'] = name
    #         if len(artist.split(",")) > 1:
    #             track_infod[tid]['artists_name'] = artist.split(",")[1]
    #         track_infod[tid]['duration'] = str(round(json.loads(track)['duration']/1000))
    # con.close();

    # if force_format is specified, take a guess for tid not in the track_infod
    con = sqlite3.connect(webdb_dat_path)
    cur = con.cursor()
    if additional_path_formats != []:
        web_track = cur.execute(
            'SELECT tid, track \
            FROM web_track'
        )
        for tid, db_track_json in web_track:
            if tid == '':
                continue
            else:
                tid = int(tid)
                db_trackd = json.loads(db_track_json)
                # extract info
                title = db_trackd["name"]
                artist_num = len(db_trackd["artists"])
                artists_path = ','.join([db_trackd["artists"][i]["name"] for i in range(artist_num)])
                artists = '/'.join([db_trackd["artists"][i]["name"] for i in range(artist_num)])
                album_name = db_trackd["album"]["name"]
                # the same rules have to be applied when organizing music
                for additional_path_format in additional_path_formats:
                    # if not found yet
                    if tid not in track_infod:
                        track_infod[tid] = {}
                        track_infod[tid]['track_name'] = title
                        track_infod[tid]['artists_name'] = artists
                        track_infod[tid]['duration'] = str(round(db_trackd["duration"]/1000))
                        track_infod[tid]['album_name'] = album_name
                    if 'path' not in track_infod[tid]:
                        path = additional_path_format.replace("{{title}}", make_string_windows_compatible(title)).replace("{{album}}", make_string_windows_compatible(album_name)).replace("{{artists}}", make_artist_windows_compatible(artists_path))
                        logging.info("checking additional track: %s", path)
                        if os.path.isfile(path):
                            track_infod[tid]['path'] = path
                            logging.info("additional track found: %s", path)

    return track_infod

def get_correct_case_track_infod(track_infod):
    logging.debug("get_correct_case_track_infod %s", track_infod)
    def get_correct_case_path(path):
        try:
            r = glob.glob(re.sub(r'([^:/\\])(?=[/\\]|$)|\[', r'[\g<0>]', path))
        except:
            r = ""
            logging.warning("path not found %s", path)
        return r and r[0] or path

    for tid in track_infod.keys():
        if 'path' in track_infod[tid]:
            track_infod[tid]['path'] = get_correct_case_path(track_infod[tid]['path'])
    return(track_infod)
    
def get_pids_of_playlist_names(playlist_names, playlistsd):
    logging.debug("get_pids_of_playlist_names %s, %s", playlist_names, playlistsd)
    def get_all_non_empty_pids(playlistsd):
        pids = []
        for pid in playlistsd:
            if (playlistsd[pid]['track_count'] != 0):
                pids.append(pid)
        return pids

    def get_non_empty_pid_of_playlist_name(playlist_name, playlistsd):
        for pid in playlistsd:
            if (playlistsd[pid]['playlist_name'] == playlist_name) & (playlistsd[pid]['track_count'] != 0):
                return pid
        logging.error("Playlist not found: %s", playlist_name)
        exit()

    if playlist_names == []:
        pids = get_all_non_empty_pids(playlistsd)
    else:
        pids = [get_non_empty_pid_of_playlist_name(playlist_name, playlistsd) for playlist_name in playlist_names]
    return pids
        
def get_m3u8d(pids, playlistsd, track_infod):
    logging.debug("get_m3u8d %s, %s, %s", pids, playlistsd, track_infod)
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
                if 'path' in track_infod[tid]:
                    m3u8d[pid]['tracks'][tid] = track_infod[tid]
                else:
                    artists_name = 'NULL'
                    album_name = 'NULL'
                    track_name = 'NULL'
                    if 'artists_name' in track_infod[tid]:
                        artists_name = track_infod[tid]['artists_name']
                    if 'album_name' in track_infod[tid]:
                        album_name = track_infod[tid]['album_name']
                    if 'track_name' in track_infod[tid]:
                        track_name = track_infod[tid]['track_name']
                    logging.warning("track not found: %s", artists_name + ' - ' + album_name + ' - ' + track_name)
            else:
                logging.warning("tid not found: %s", tid)
    return m3u8d

def export(m3u8d, export_path):
    logging.debug("export %s, %s", m3u8d, export_path)
    
    # https://en.wikipedia.org/wiki/M3U
    for pid in m3u8d:
        playlist_name = make_string_windows_compatible(m3u8d[pid]['playlist_name'])
        file_name = playlist_name + '.m3u8'
        file_path = export_path + file_name
        with open(file_path, 'w', encoding='utf-8', errors='ignore') as m3u8_file:
            m3u8_file_content = '#EXTM3U\n'
            for tid in m3u8d[pid]['tracks']:
                if 'path' in m3u8d[pid]['tracks'][tid]:
                    artists_name = 'NULL'
                    album_name = 'NULL'
                    if 'artists_name' in m3u8d[pid]['tracks'][tid]:
                        artists_name = m3u8d[pid]['tracks'][tid]['artists_name']
                    if 'album_name' in m3u8d[pid]['tracks'][tid]:
                        album_name = m3u8d[pid]['tracks'][tid]['album_name']
                    m3u8_file_content = m3u8_file_content + '#EXTINF:' + \
                                        m3u8d[pid]['tracks'][tid]['duration'] + ', ' + \
                                        artists_name + ' - ' + \
                                        album_name + '\n' + \
                                        m3u8d[pid]['tracks'][tid]['path'] + '\n'
            m3u8_file.write(m3u8_file_content)
    logging.info("Files saved at %s", export_path)

def get_relative_path(m3u8d, base_path):
    logging.debug("get_relative_path %s, %s", m3u8d, base_path)
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
            if 'path' in m3u8d[pid]['tracks'][tid]:
                m3u8d[pid]['tracks'][tid]['path'] = replace_ignore_case(base_path, "", m3u8d[pid]['tracks'][tid]['path'])
                # nt to posix path
                m3u8d[pid]['tracks'][tid]['path'] = m3u8d[pid]['tracks'][tid]['path'].replace("\\", "/")
    return m3u8d
