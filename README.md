# Pokemon Crawler

Project started from https://docs.docker.com/compose/django/

Some useful commands:

* `docker-compose up`
* `docker-compose exec web bash`
* `docker-compose exec web python -m pip install -r requirements.txt`

On M1 Mac, you may have to run "export DOCKER_DEFAULT_PLATFORM=linux/amd64" before rebuilding the image, due to a bug in libpg