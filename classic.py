# SPDX-FileCopyrightText: 2026 togetofu
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""Language Switch for Blender 2.59 to 2.79 (see __init__.py for 2.80 and later).

Two buttons at the right end of the Info header ("EN" and "JA" by default) and one shortcut,
Ctrl+Shift+L, which toggles between the two. Both languages can be chosen in the add-on
preferences from Blender 2.67 (before that they are English and Japanese). Switching to a
translated language also turns on International Fonts and the translation of the interface and
tooltips, which is what makes the switch visible.

Keeps to the Python 3.2 syntax of Blender 2.59.
"""

import zlib

import bpy
from bpy.props import EnumProperty, StringProperty

# Blender before 2.64 named the languages in capitals instead of with locale names.
_OLD_CODES = {
    'ENGLISH': "EN", 'JAPANESE': "JA", 'DUTCH': "NL", 'ITALIAN': "IT", 'GERMAN': "DE",
    'FINNISH': "FI", 'SWEDISH': "SV", 'FRENCH': "FR", 'SPANISH': "ES", 'CATALAN': "CA",
    'CZECH': "CS", 'BRAZILIAN_PORTUGUESE': "PT", 'SIMPLIFIED_CHINESE': "ZH",
    'TRADITIONAL_CHINESE': "ZH", 'RUSSIAN': "RU", 'CROATIAN': "HR", 'SERBIAN': "SR",
    'UKRAINIAN': "UK", 'POLISH': "PL", 'ROMANIAN': "RO", 'ARABIC': "AR", 'BULGARIAN': "BG",
    'GREEK': "EL", 'KOREAN': "KO",
}
# Switching the language does nothing on screen unless these are on (names differ by version).
_TRANSLATE_SETTINGS = (
    "use_international_fonts", "use_translate_interface", "use_translate_buttons",
    "use_translate_toolbox", "use_translate_tooltips",
)

# Python 3.2 leaves __package__ unset in a submodule, so take it from the module name.
_PACKAGE = __name__.rpartition(".")[0]

_keymaps = []
_classes = []


def _system(context=None):
    return (context or bpy.context).user_preferences.system


def _languages():
    """{identifier: name} of the languages this build offers."""
    system = _system()
    translations = getattr(bpy.app, "translations", None)
    if translations is not None and hasattr(bpy.types.UILayout, "enum_item_name"):
        # The language list is built at run time, so the RNA only lists "Default".
        result = {}
        for identifier in ['DEFAULT'] + list(translations.locales):
            name = bpy.types.UILayout.enum_item_name(system, "language", identifier)
            if name:
                result[identifier] = name
        return result
    try:
        prop = system.bl_rna.properties["language"]
        return dict((item.identifier, item.name) for item in prop.enum_items)
    except Exception:
        return {}


def _english():
    return 'en_US' if 'en_US' in _languages() else 'ENGLISH'


def _default_second():
    return 'ja_JP' if 'ja_JP' in _languages() else 'JAPANESE'


def _is_english(language):
    return (not language) or language == 'ENGLISH' or language.startswith("en")


def _resolve(language):
    """Resolves "Automatic" to the language Blender uses."""
    if language == 'DEFAULT':
        translations = getattr(bpy.app, "translations", None)
        return (translations and translations.locale) or _english()
    return language


def current_language(context=None):
    return _resolve(_system(context).language)


def _prefs(context=None):
    try:
        return (context or bpy.context).user_preferences.addons[_PACKAGE].preferences
    except (KeyError, AttributeError):
        return None


def first_language(context=None):
    prefs = _prefs(context)
    language = prefs.first_language if prefs else _english()
    return language if language in _languages() else _english()


def second_language(context=None):
    prefs = _prefs(context)
    language = prefs.second_language if prefs else _default_second()
    return language if language in _languages() else _default_second()


def short_code(language):
    """"ja_JP" -> "JA", "JAPANESE" -> "JA"."""
    if language in _OLD_CODES:
        return _OLD_CODES[language]
    return (language or "?").split("_")[0].split("@")[0].upper()[:2]


def set_language(context, language):
    system = _system(context)
    if not _is_english(_resolve(language)):
        for name in _TRANSLATE_SETTINGS:
            if hasattr(system, name):
                setattr(system, name, True)
    system.language = language


class WM_OT_falcon_language_set(bpy.types.Operator):
    """Set the interface language"""
    bl_idname = "wm.falcon_language_set"
    bl_label = "Set Interface Language"

    language = StringProperty(name="Language", description="Language identifier, e.g. en_US")

    def execute(self, context):
        if self.language not in _languages():
            self.report({'WARNING'}, "Language not available: %s" % self.language)
            return {'CANCELLED'}
        set_language(context, self.language)
        return {'FINISHED'}


class WM_OT_falcon_language_toggle(bpy.types.Operator):
    """Switch the interface language between the first and the second language"""
    bl_idname = "wm.falcon_language_toggle"
    bl_label = "Toggle Interface Language"

    def execute(self, context):
        first = first_language(context)
        second = second_language(context)
        # Any language other than the first one goes back to the first one.
        target = second if current_language(context) == _resolve(first) else first
        if target not in _languages():
            self.report({'WARNING'}, "Language not available: %s" % target)
            return {'CANCELLED'}
        set_language(context, target)
        return {'FINISHED'}


def _operator_parameters():
    try:
        return set(bpy.types.UILayout.bl_rna.functions["operator"].parameters.keys())
    except Exception:
        return set()


def draw_header(self, context):
    current = current_language(context)
    parameters = _operator_parameters()
    row = self.layout.row(align=True)
    for language in (first_language(context), second_language(context)):
        options = {"text": short_code(language)}
        if "translate" in parameters:
            options["translate"] = False
        if "depress" in parameters:
            options["depress"] = current == _resolve(language)
        props = row.operator("wm.falcon_language_set", **options)
        props.language = language


def _language_items():
    # Numbered by a hash of the identifier, so the stored value does not depend on the order of
    # the languages in a build.
    return [
        (identifier, name, "", zlib.crc32(identifier.encode()) & 0x7FFFFFFF)
        for identifier, name in sorted(_languages().items(), key=lambda kv: kv[1])
        if identifier != 'DEFAULT'
    ]


def _preferences_class():
    """The add-on preferences (Blender 2.67 and later), or None."""
    if not hasattr(bpy.types, "AddonPreferences"):
        return None
    items = _language_items()

    class FalconLanguagePreferences(bpy.types.AddonPreferences):
        bl_idname = _PACKAGE

        first_language = EnumProperty(
            name="First Language", description="Language of the first button",
            items=items, default=_english())
        second_language = EnumProperty(
            name="Second Language", description="Language of the second button",
            items=items, default=_default_second())

        def draw(self, context):
            layout = self.layout
            layout.prop(self, "first_language")
            layout.prop(self, "second_language")
            if self.first_language == self.second_language:
                layout.label(text="Choose two different languages", icon='ERROR')
            layout.label(text="Ctrl+Shift+L switches between these two languages")

    return FalconLanguagePreferences


def register():
    _classes[:] = [WM_OT_falcon_language_set, WM_OT_falcon_language_toggle]
    preferences = _preferences_class()
    if preferences is not None:
        _classes.insert(0, preferences)
    for cls in _classes:
        bpy.utils.register_class(cls)
    bpy.types.INFO_HT_header.append(draw_header)
    keyconfig = bpy.context.window_manager.keyconfigs.addon
    if keyconfig is not None:  # None in background mode
        keymap = keyconfig.keymaps.new(name="Window", space_type='EMPTY')
        item = keymap.keymap_items.new(WM_OT_falcon_language_toggle.bl_idname, 'L', 'PRESS',
                                       ctrl=True, shift=True)
        _keymaps.append((keymap, item))


def unregister():
    for keymap, item in _keymaps:
        try:
            keymap.keymap_items.remove(item)
        except Exception:
            pass
    _keymaps[:] = []
    bpy.types.INFO_HT_header.remove(draw_header)
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
    _classes[:] = []
