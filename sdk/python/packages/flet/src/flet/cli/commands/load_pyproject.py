from __future__ import annotations

import contextlib
import typing
from pathlib import Path

import tomlkit


class NoData(Exception):
    pass


T = typing.TypeVar("T")
_no_default = object()
_pyproject_data_cache: dict[Path, tomlkit.TOMLDocument | None] = {}
default_path = Path.cwd() / "pyproject.toml"


def _load_pyproject(pyproject_path: Path) -> tomlkit.TOMLDocument | None:
    with contextlib.suppress(KeyError):
        return _pyproject_data_cache[pyproject_path]

    try:
        pyproject_data = tomlkit.loads(pyproject_path.read_text("utf-8"))
    except Exception:
        pyproject_data = None

    _pyproject_data_cache[pyproject_path] = pyproject_data
    return pyproject_data


def _load(
    path: str,
    type: type[T] | typing.Callable[..., T],
    project_path: Path | None = None,
    of_flet: bool = True
) -> T:
    pyproject_data = _load_pyproject(project_path or default_path)
    if pyproject_data is None:
        raise NoData

    try:
        path_sep = ["tool", "flet"] if of_flet else []
        path_sep += path.split(".")

        data = pyproject_data
        for current in path_sep:
            data = data[current]  # type: ignore
    except Exception as exc:
        raise NoData from exc

    return type(data)


def load_default(
    path: str,
    default: T = _no_default,
    type: type[T] = str,
    project_path: Path | None = None,
) -> dict[str, T]:
    try:
        data = _load(path, type, project_path)
    except NoData:
        return {} if default is _no_default else {"default": default}
    else:
        return {"default": data}
