# netease-cloudmusic-playlist-exporter

command line tool to export netease cloudmusic playlists to standard .m3u8

网易云音乐歌单导出工具，导出歌单为标准.m3u8格式

## Features

- Standard .m3u8 with full features according to wikipedia
- Support Windows, require python or WSL python
- Support all cloud music and local music, as long as it can be accessed offline
- Support nt style absolute path and posix style relative path in .m3u8

## Install

```bash
pip install git+https://github.com/mkmark/netease-cloudmusic-playlist-exporter.git
```

## Usage

```bash
ncmplex -h

usage: ncmplex [-h] [-p PLAYLIST] [-l LIB_PATH] [-d DOWNLOAD_PATH] [-e EXPORT_PATH] [-r]
               [-b BASE_PATH]

This tool creates .m3u8 playlists from Netease Cloudmusic webdb.dat.

optional arguments:
  -h, --help            show this help message and exit
  -p PLAYLIST           playlist name, leave blank to export all, can be specified multiple times (default: [])
  -l LIB_PATH           webdb.dat and library.dat directory (default: [auto-generated])
  -d DOWNLOAD_PATH      Cloudmusic download path (default: [auto-generated])
  -e EXPORT_PATH        generated .m3u8 file export path (default: [auto-generated])
  -r                    remove base path and use relative posix path
  -b BASE_PATH          bsse path to be removed with -r (default to EXPORT_PATH)
  -c                    try to fix path case error
  -f ADDITIONAL_PATH_FORMATS
                        try to export tracks that are not found in ncm database, can be specified multiple times. (default: [])
  -v                    print verbose log
```

Note:

- `-d DOWNLOAD_PATH` is required because `web_offline_track` stored in `webdb.dat` is stored with `relative_path` only, and there is no extra information in the database to determine the base path. If not provided, `%USERPROFILE%\Music\CloudMusic\` is used.
- `-r` option is useful to export music to posix system like Mac, Linux, Android and so.
- `-c` option is useful to export music to be used in case-sensitive operation system like Linux and so. Path stored in the database may be in the incorrect case, which is not a problem in Windows or Mac. With `-c` enabled, the app will verify the file name on the disk, thus dramatically increase the processing time.
- `-f` option is useful to export music that is not included in ncm database, but exists on disk, in format that can be specified by `{{title}}`, `{{album}}`, `{{artists}}`. Use first entry found. 

## Example

- export all playlists using default settings.

```bat
ncmplex
```

- export only specific playlists to designated location with custom CloudMusic download path, with songs of posix style relative path and try to fix path case, with additional path that prioritize `.flac` file.

```bat
ncmplex -p 我喜欢的音乐 -p "L - 5s" -d D:\Users\Mark\Music\CloudMusic -e D:\Users\Mark\Music\ -r -c -f D:\Users\Mark\Music\Additional\{{artists}}\{{album}}\{{title}}.flac -f D:\Users\Mark\Music\Additional\{{artists}}\{{album}}\{{title}}.mp3
```

- show help

```bat
ncmplex -h
```

## Reference

- [mkmark / create_m3u_from_NeteaseCloudMusic](https://github.com/mkmark/create_m3u_from_NeteaseCloudMusic)
- [M3U - Wikipedia](https://en.wikipedia.org/wiki/M3U)
