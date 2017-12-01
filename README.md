# Goodreads Bot for Reddit!

## Requirements:

#### System Requirements:

- Python 3.6+
- Requires [Pandoc](http://pandoc.org/):

    - OS X: `brew install pandoc`
    - Ubuntu/Debian: `sudo apt-get install pandoc`

#### Python Requirements:
    `pip install -r requirements.txt`

### Docker

- Rename `envlist-sample` to `envlist`
- Build docker image: `docker build -t reddit-goodreads .`
- Run: `docker run --mount source=reddit-goodreads,target=/home/ubuntu/db --env-file ./envlist --rm -it reddit-goodreads:latest`


## Todo:
- ~~Add Peewee Support~~
- ~~Log all successful comments~~
- ~~Use Oauth~~
- ~~Handle HTTP Exceptions (`requests`) and log it~~ (not needed)
- Log all fails, exceptions
- ~~Custom reply to those who reply to bot~~
- ~~Remove HTTP tags in the response. Better, change <br> to \n and rest all to markdown conversion~~

## LICENSE

The mighty MIT License. Check `LICENSE` file.
