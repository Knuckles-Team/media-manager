# Media Manager
*Version: 0.0.3*

Manage your media
- Automatically clean file names 
- Set Title and Comment metadata to match filename
- Apply subtitles in media's "Sub" directory automatically
- Move media to desired destination

### Usage:
| Short Flag | Long Flag   | Description                                 |
|------------|-------------|---------------------------------------------|
| -h         | --help      | See usage                                   |
| -s         | --subtitle  | Apply Subtitle in local "Sub" directory     |
| -m         | --move      | Movie media to final destination            |
| -d         | --directory | Directory to scan for media                 |


### Example:
```bash
media-manager -d "/home/User/Downloads" -m "/media/" -s
```
#### Before
> /home/User/Downloads/The.Lion.King.1993.1080p.[TheBay].YIFY/The.Lion.King.1993.1080p.[TheBay].YIFY.mp4 

#### After
> /media/The Lion King 1993 1080p/The Lion King 1993 1080p.mp4

#### Build Instructions
Build Python Package

```bash
sudo chmod +x ./*.py
sudo pip install .
python setup.py bdist_wheel --universal
# Test Pypi
twine upload --repository-url https://test.pypi.org/legacy/ dist/* --verbose -u "Username" -p "Password"
# Prod Pypi
twine upload dist/* --verbose -u "Username" -p "Password"
```
