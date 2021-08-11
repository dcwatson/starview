import os

from starlette.applications import Starlette
from starlette.config import Config
from starlette.responses import FileResponse, PlainTextResponse
from starlette.routing import Route
from starlette.templating import Jinja2Templates

config = Config(".env")

DEBUG = config("DEBUG", cast=bool, default=False)
DIRECTORY = config("DIRECTORY", default="/data")
DOTFILES = config("DOTFILES", cast=bool, default=False)
IGNORECASE = config("IGNORECASE", cast=bool, default=True)
DIRSFIRST = config("DIRSFIRST", cast=bool, default=True)
TITLE = config("TITLE", default="Files")

templates = Jinja2Templates(directory="templates")


def filesize(num, suffix="B"):
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, "Y", suffix)


def sort_key(entry):
    name = entry["name"]
    if IGNORECASE:
        name = name.lower()
    if DIRSFIRST:
        return (not entry["is_dir"], name)
    return name


def get_entries(root, parts, selected=None):
    entries = []
    root_path = os.path.normpath(os.path.join(root, *parts))
    for name in os.listdir(root_path):
        if name.startswith(".") and not DOTFILES:
            continue
        path = os.path.join(root_path, name)
        is_dir = os.path.isdir(path)
        href = "/" + "/".join(parts + [name])
        if is_dir:
            href += "/"
        entries.append(
            {
                "name": name,
                "href": href,
                "is_dir": is_dir,
                "is_link": os.path.islink(path),
                "size": os.path.getsize(path),
            }
        )
    entries.sort(key=sort_key)
    return entries


def check_path(path):
    parts = []
    for part in path.split(os.path.sep):
        if part in (".", ""):
            continue
        elif part == "..":
            raise ValueError("Parent directory references (..) not allowed.")
        else:
            parts.append(part)
    return parts


async def serve(request):
    path_parts = check_path(request.path_params["path"])
    rel_path = os.path.sep.join(path_parts)
    title = "{} :: {}".format(TITLE, rel_path) if rel_path else TITLE
    # Absolutize (and normalize) the root DIRECTORY path.
    root = os.path.abspath(DIRECTORY)
    # Compute the requested path and make sure it's within DIRECTORY.
    path = os.path.normpath(os.path.join(root, rel_path))
    if not path.startswith(root):
        return PlainTextResponse("Invalid directory.", status_code=400)
    if os.path.isdir(path):
        hierarchy = []
        selected = None
        # TODO: run this in a ThreadPoolExecutor.
        while path_parts:
            entries = get_entries(root, path_parts, selected=selected)
            href = "/" + "/".join(path_parts) + "/"
            selected = path_parts.pop()
            hierarchy.insert(0, (selected, href, entries))
        # Always add the root directory at the start.
        entries = get_entries(root, [], selected=selected)
        hierarchy.insert(0, (TITLE, "/", entries))
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "hierarchy": hierarchy,
                "title": title,
            },
        )
    else:
        # Otherwise just serve the file.
        return FileResponse(path)


app = Starlette(
    debug=True,
    routes=[
        Route("/{path:path}", serve),
    ],
)
