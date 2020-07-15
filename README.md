# netease-cloudmusic-library-to-m3u8
command line tool to export netease cloudmusic playlists to standard .m3u8

## Features
- Standard .m3u8 with full features
- Support WIndows and WSL python
- Support all cloud music and local music, as long as it can be accessed offline
- For songs support nt style absolute path and posix style relative path

## Usage
```bash
python netease-cloudmusic-library-to-m3u8.py -h

usage: netease-cloudmusic-library-to-m3u8.py [-h] [-p PLAYLIST] [-l LIB_PATH] [-d DOWNLOAD_PATH] [-e EXPORT_PATH] [-r]
                                             [-b BASE_PATH]

This script creates .m3u8 playlists from Netease Cloudmusic webdb.dat.

optional arguments:
optional arguments:
  -h, --help        show this help message and exit
  -p PLAYLIST       playlist name, leave blank to export all, can be specified multiple times (default: [])
  -l LIB_PATH       webdb.dat and library.dat directory (default: [auto-generated])
  -d DOWNLOAD_PATH  Cloudmusic download path (default: [auto-generated])
  -e EXPORT_PATH    generated .m3u8 file export path (default: [auto-generated])
  -r                specify to remove base path and use relative posix path
  -b BASE_PATH      specify base path to be removed with -r (default to export_path)
```

## Example
- export all playlists using default settings.
```bat
python netease-cloudmusic-library-to-m3u8.py
```

- export only specific playlists to designated location with custom Cloudmusic download path, with songs of posix style relative path
```bat
python netease-cloudmusic-library-to-m3u8.py -p 我喜欢的音乐 -p 'L - 5s' -d D:\Users\Mark\Music\Cloudmusic -e D:\Users\Mark\Music\Playlists\ -r
```

- show help
```bat
python netease-cloudmusic-library-to-m3u8.py -h
```

## Reference
- [mkmark / create_m3u_from_NeteaseCloudMusic](https://github.com/mkmark/create_m3u_from_NeteaseCloudMusic)
- [M3U - Wikipedia](https://en.wikipedia.org/wiki/M3U)