# quivr-doc-loader
Batch document loader into [Quivr](https://github.com/StanGirard/quivr)

## Setup

Build and run the docker container

```bash
docker build -t quivr-doc-loader . && docker run -d -p 8022:22 -v .:/app --name doc-loader quivr-doc-loader
```

SSH into the container then continue with the following setup.

### Python Version and Virtual Environment

`pyenv` is used for this project. This will use the version of python defined in `.python-version` file. Activate the virtual environment and install dependencies like so:

```bash
$ bash
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

### Environment Variables

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