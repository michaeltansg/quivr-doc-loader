# quivr-doc-loader
Batch document loader into [Quivr](https://github.com/StanGirard/quivr)

## Setup

### Python Version and Virtual Environment

`pyenv` is used for this project. This will use the version of python defined in `.python-version` file. Activate the virtual environment and install dependencies like so:

```bash
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