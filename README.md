# Media Manager

![PyPI - Version](https://img.shields.io/pypi/v/media-manager)
![PyPI - Downloads](https://img.shields.io/pypi/dd/media-manager)
![GitHub Repo stars](https://img.shields.io/github/stars/Knuckles-Team/media-manager)
![GitHub forks](https://img.shields.io/github/forks/Knuckles-Team/media-manager)
![GitHub contributors](https://img.shields.io/github/contributors/Knuckles-Team/media-manager)
![PyPI - License](https://img.shields.io/pypi/l/media-manager)
![GitHub](https://img.shields.io/github/license/Knuckles-Team/media-manager)

![GitHub last commit (by committer)](https://img.shields.io/github/last-commit/Knuckles-Team/media-manager)
![GitHub pull requests](https://img.shields.io/github/issues-pr/Knuckles-Team/media-manager)
![GitHub closed pull requests](https://img.shields.io/github/issues-pr-closed/Knuckles-Team/media-manager)
![GitHub issues](https://img.shields.io/github/issues/Knuckles-Team/media-manager)

![GitHub top language](https://img.shields.io/github/languages/top/Knuckles-Team/media-manager)
![GitHub language count](https://img.shields.io/github/languages/count/Knuckles-Team/media-manager)
![GitHub repo size](https://img.shields.io/github/repo-size/Knuckles-Team/media-manager)
![GitHub repo file count (file type)](https://img.shields.io/github/directory-file-count/Knuckles-Team/media-manager)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/media-manager)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/media-manager)


*Version: 0.72.0*

Manage your media
- Automatically clean file names 
- Set Title and Comment metadata to match filename
- Apply subtitles in media's "Sub" directory automatically
- Move media to desired destination

Supports Media:
- MKV
- MP4

This repository is actively maintained - Contributions are welcome!

<details>
  <summary><b>Usage:</b></summary>

| Short Flag | Long Flag         | Description                             |
|------------|-------------------|-----------------------------------------|
| -h         | --help            | See usage                               |
|            | --subtitle        | Apply Subtitle in local "Sub" directory |
|            | --media-directory | Move media to directory                 |
|            | --music-directory | Move music to directory                 |
|            | --tv-directory    | Move series to directory                |
| -d         | --directory       | Directory to scan for media             |
| -v         | --verbose         | Show Output of FFMPEG                   |

</details>

<details>
  <summary><b>Example:</b></summary>

```bash
media-manager -d "/home/User/Downloads" -m "/media/Movies" -t "/media/TV" -s
```
#### Before
> /home/User/Downloads/The.Lion.King.1993.1080p.[TheBay].YIFY/The.Lion.King.1993.1080p.[TheBay].YIFY.mp4 

#### After
> /media/The Lion King 1993 1080p/The Lion King 1993 1080p.mp4

</details>

<details>
  <summary><b>Installation Instructions:</b></summary>

Install Python Package

```bash
python -m pip install media-manager
```

</details>

<details>
  <summary><b>Repository Owners:</b></summary>


<img width="100%" height="180em" src="https://github-readme-stats.vercel.app/api?username=Knucklessg1&show_icons=true&hide_border=true&&count_private=true&include_all_commits=true" />

![GitHub followers](https://img.shields.io/github/followers/Knucklessg1)
![GitHub User's stars](https://img.shields.io/github/stars/Knucklessg1)
</details>
