# Media Manager
*Version: 0.0.1*

Manage your video files by changing the metadata and adding subtitles

### Usage:
| Short Flag | Long Flag   | Description                                 |
|------------|-------------|---------------------------------------------|
| -h         | --help      | See usage                                   |
| -a         | --audio     | Download audio only                         |
| -c         | --channel   | YouTube Channel/User - Downloads all videos |
| -f         | --file      | File with video links                       |
| -l         | --links     | Comma separated links                       |
| -d         | --directory | Location to save videos                     |


### Example:
```bash
media-manager 
```

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
