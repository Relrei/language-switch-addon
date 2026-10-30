# SPDX-FileCopyrightText: 2026 togetofu
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""Switch the interface language between two languages in one click.

Blender 2.80 changed the interface and the Python API a lot (and its add-ons use newer Python
syntax), so there are two implementations: modern.py for Blender 2.80 and later (Top Bar buttons,
add-on preferences, workspace tabs) and classic.py for Blender 2.59 to 2.79 (buttons in the Info
header). Only the one for the running version is imported, which is why this file keeps to the
Python 3.2 syntax of Blender 2.59.
"""

bl_info = {
    "name": "Language Switch",
    "author": "togetofu",
    "version": (1, 8, 1),
    "blender": (2, 59, 0),
    "location": "Top Bar (Info header before 2.80), right end; Ctrl+Shift+L",
    "description": "Switch the interface language between two languages",
    "category": "Interface",
}

import bpy

# The oldest version tested, as in bl_info (which Blender removes when loading an extension).
MIN_BLENDER = (2, 59, 0)

if bpy.app.version >= (2, 80, 0):
    # Blender 2.80 to 4.1 refuse to enable an add-on whose bl_info is older than 2.80. They check
    # the module's bl_info, while the add-on list reads the file (so 2.59 does not warn either).
    bl_info["blender"] = (2, 80, 0)
    from . import modern as _impl
elif bpy.app.version >= MIN_BLENDER:
    from . import classic as _impl
else:
    _impl = None

if "_loaded" in locals():
    # Reload Scripts reloads this package only; reload the implementation too.
    try:
        from importlib import reload
    except ImportError:  # Python before 3.4
        from imp import reload
    if _impl is not None:
        _impl = reload(_impl)
_loaded = True


def register():
    # Older versions are not tested: refuse to be enabled there instead of half working.
    if _impl is None:
        raise RuntimeError("Language Switch needs Blender %d.%d or later" % MIN_BLENDER[:2])
    _impl.register()


def unregister():
    if _impl is not None:
        _impl.unregister()
