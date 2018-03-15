# Server
For server development


## Requirements
- ubuntu 16.04
- python 3.5


## Dependencies
1. Creating virtual environment
- `virtualenv env --python=python3.5`
- `source env/bin/activate`

2. Installing dependencies
- `pip3 install -r requirements.txt`

3. if you get the (FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg')
- `sudo apt-get install libav-tools`


## Run server
- `python3 main.py`
