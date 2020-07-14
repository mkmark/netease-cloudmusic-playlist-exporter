# netease-cloudmusic-library-to-m3u8
command line tool to export netease cloudmusic playlists to standard .m3u8

## Features
- Standard .m3u8 with full features
- Support WIndows and WSL python. Generated files are nt styled. Can be easy adapted for linux and mac though
- Support all cloud music and local music, as long as it can be accessed offline

## Usage
```bash
python netease-cloudmusic-library-to-m3u8.py -h

usage: netease-cloudmusic-library-to-m3u8.py [-h] [-p P] [-w W] [-d D] [-e E]

This script creates .m3u8 playlists from Netease Cloudmusic webdb.dat.

optional arguments:
  -h, --help  show this help message and exit
  -p P        playlist name, leave blank to export all, can be specified
              multiple times or as an array (default: [])
  -w W        webdb.dat path (default: [auto-generated])
  -d D        Cloudmusic download path (default:
              [auto-generated])
  -e E        generated .m3u8 file export path (default:
              [auto-generated])
```

## Example
- export all playlists using default settings.
```bat
python netease-cloudmusic-library-to-m3u8.py
```
- export only specific playlists to designated location with custom download path
```bat
python netease-cloudmusic-library-to-m3u8.py -p 我喜欢的音乐 -p 'L - 5s' -d D:\Users\Mark\Music\Cloudmusic -e D:\Users\Mark\Music\Playlists\
```
- show help
```bat
python netease-cloudmusic-library-to-m3u8.py -h
```

## Reference
[mkmark / create_m3u_from_NeteaseCloudMusic](https://github.com/mkmark/create_m3u_from_NeteaseCloudMusic)
[M3U - Wikipedia](https://en.wikipedia.org/wiki/M3U)