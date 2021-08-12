# Starview

A small containerized [Starlette](https://www.starlette.io) application for serving
directory listings. Features a column view of directory hierarchy and a not-awful mobile
interface.

## Usage

```
docker run -it --rm \
    -e TITLE=Starview \
    -v `pwd`:/data \
    -p 8000:8000 \
    ghcr.io/dcwatson/starview
```

This will serve a directory listing of the current directory at http://localhost:8000.
