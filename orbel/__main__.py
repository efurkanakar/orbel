"""Module executed when running ``python -m orbel``."""

from __future__ import annotations

import sys

from orbel_app.app import main


if __name__ == "__main__":
    sys.exit(main())

