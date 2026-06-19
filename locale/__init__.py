"""Locale feature package.

This project directory is named ``locale``, which shadows Python's standard
library ``locale`` module when the repository root is on ``sys.path``. Load and
re-export the standard library module's public API so third-party libraries such
as pandas can still import names like ``LC_TIME``.
"""

from __future__ import annotations

import importlib.util
import sysconfig
from pathlib import Path


_stdlib_locale_path = Path(sysconfig.get_path("stdlib")) / "locale.py"
_stdlib_locale_spec = importlib.util.spec_from_file_location(
    "_stdlib_locale",
    _stdlib_locale_path,
)

if _stdlib_locale_spec is None or _stdlib_locale_spec.loader is None:
    raise ImportError(f"Cannot load standard library locale module: {_stdlib_locale_path}")

_stdlib_locale = importlib.util.module_from_spec(_stdlib_locale_spec)
_stdlib_locale_spec.loader.exec_module(_stdlib_locale)

for _name, _value in vars(_stdlib_locale).items():
    if _name.startswith("__") and _name not in {"__all__", "__doc__"}:
        continue
    globals()[_name] = _value

__all__ = getattr(
    _stdlib_locale,
    "__all__",
    [name for name in vars(_stdlib_locale) if not name.startswith("_")],
)
