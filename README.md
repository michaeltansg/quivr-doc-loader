# quivr-doc-loader
Batch document loader into [Quivr](https://github.com/StanGirard/quivr)

## Development using Docker

Run the docker container

```bash
docker-compose up
```

Build the docker image before running the docker container

```bash
docker-compose up --build
```

SSH into the container to run the application.

## Development on macOS

### Python Version and Virtual Environment

`pyenv` is used for this project. This will use the version of python defined in `.python-version` file. Activate the virtual environment and install dependencies like so:

```bash
$ python -m venv venv
$ source venv/bin/activate
$ pip install --upgrade pip
$ pip install -r requirements.txt
```

## Environment Variables

Create a `.env` environment file by making a copy of the `.env.example` file.

```bash
$ cp .env.example .env
```

Replace the environment variables in `.env` for this project.

## Running the app

```bash
$ python app.py
```

Because the application maps the app folder to the local file system. It is possible to make modifications to the source code and rerun the python script without rebuilding the docker image or stopping the container.