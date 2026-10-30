# SPDX-FileCopyrightText: 2026 togetofu
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""Language Switch for Blender 2.80 and later (see __init__.py for the older versions).

Switches the interface language between two languages in one click.

Two buttons at the right end of the Top Bar ("EN" and "JA" by default) and one shortcut,
Ctrl+Shift+L, which toggles between the two. The first language is the one set in Preferences >
Interface > Language ("Use Blender's Language Setting", on by default) or one chosen in the add-on
preferences (English by default); the second one is Japanese unless another one is chosen there.
Switching to a translated language also turns on the translation of the interface, tooltips and
reports (Preferences > Interface > Translation), which is what makes the switch visible; new data
names are left alone.

The preference is changed like any other one, so it is saved with the preferences as usual.
Written for Falcon Engine; the idea (a one-click language toggle) is the same as the language
switch add-ons on extensions.blender.org, no code is taken from them.
"""

import bpy
try:
    from bpy.app.translations import pgettext_rpt as rpt_
except ImportError:  # Blender before 4.0 does not translate reports
    from bpy.app.translations import pgettext_tip as rpt_
from bpy.app.translations import pgettext_tip as tip_
from bpy.props import BoolProperty, EnumProperty, StringProperty

ENGLISH = 'en_US'
DEFAULT_FIRST = ENGLISH
DEFAULT_SECOND = 'ja_JP'
SHORTCUT = dict(type='L', value='PRESS', ctrl=True, shift=True)
# The workspace tabs of the startup file and of the bundled app templates. Blender names them in
# the language in effect when a file is created and never renames them, so they are renamed here
# (only when "Translate Workspace Tabs" is on, since the names are saved in the file).
WORKSPACE_NAMES = (
    "2D Animation", "2D Full Canvas", "Animation", "Compositing", "Geometry Nodes", "Layout",
    "Masking", "Modeling", "Motion Tracking", "Rendering", "Scripting", "Sculpting", "Shading",
    "Storyboarding", "Texture Paint", "UV Editing", "Video Editing",
)

_keymaps = []
# Blender keeps no reference to the items of a dynamic enum, so they are kept here.
_language_items_store = []


def _languages():
    """{identifier: name} of the languages this build offers."""
    # The items of the language enum are dynamic, and Blender 4.5 lists only the static one
    # ("Automatic") in bl_rna, so the identifiers come from the translations instead.
    try:
        view = bpy.context.preferences.view
        identifiers = ['DEFAULT', ENGLISH, *bpy.app.translations.locales]
        names = {identifier: bpy.types.UILayout.enum_item_name(view, "language", identifier)
                 for identifier in identifiers}
        return {identifier: name for identifier, name in names.items() if name}
    except Exception:
        return {}


def _is_english(language):
    return (not language) or language.startswith("en") or language in {'C', 'POSIX'}


def _prefs(context=None):
    context = context or bpy.context
    addon = context.preferences.addons.get(__package__)
    return addon.preferences if addon else None


def _resolve(language):
    """Resolves "Automatic" to the language Blender uses."""
    if language == 'DEFAULT':
        return bpy.app.translations.locale or ENGLISH
    return language


def current_language(context=None):
    """The language in effect (resolves "Automatic" to what Blender uses)."""
    context = context or bpy.context
    return _resolve(context.preferences.view.language)


def _chosen(context, name, default):
    prefs = _prefs(context)
    language = getattr(prefs, name) if prefs else default
    return language if language in _languages() else default


def first_language(context=None):
    """The first language: the one set in Preferences > Interface when "Use Blender's Language
    Setting" is on (the last one set there while the second language is shown), else the one
    chosen in the add-on preferences (English by default). May be "DEFAULT" (Automatic)."""
    context = context or bpy.context
    prefs = _prefs(context)
    if prefs and prefs.use_blender_language:
        language = context.preferences.view.language
        if _resolve(language) != second_language(context):
            return language
        return prefs.home_language if prefs.home_language in _languages() else ENGLISH
    return _chosen(context, "first_language", DEFAULT_FIRST)


def first_language_resolved(context=None):
    """The first language with "Automatic" resolved. While another language is shown, Blender
    resolves "Automatic" to that one, so the language it stood for is the remembered one."""
    context = context or bpy.context
    language = first_language(context)
    prefs = _prefs(context)
    if (language == 'DEFAULT' and prefs and prefs.use_blender_language
            and context.preferences.view.language != 'DEFAULT' and prefs.home_resolved):
        return prefs.home_resolved
    return _resolve(language)


def second_language(context=None):
    """The second language chosen in the add-on preferences (Japanese by default)."""
    return _chosen(context, "second_language", DEFAULT_SECOND)


def short_code(language):
    """"ja_JP" -> "JA", "zh_HANS" -> "ZH", "pt_BR" -> "PT"."""
    return (language or "?").split("_")[0].split("@")[0].upper()


def _workspace_names(view):
    """{English name: name in the current language} of the standard workspace tabs."""
    translations = bpy.app.translations
    workspace = getattr(translations.contexts, "id_workspace", "WorkSpace")
    use_new_dataname = view.use_translate_new_dataname
    # pgettext_data() translates only while new data names are translated.
    view.use_translate_new_dataname = True
    try:
        return {name: translations.pgettext_data(name, workspace) for name in WORKSPACE_NAMES}
    finally:
        view.use_translate_new_dataname = use_new_dataname


def _rename_workspaces(old, new):
    """Renames the tabs still named as in `old` (or in English) to their name in `new`; tabs
    renamed by the user are left alone."""
    for workspace in bpy.data.workspaces:
        for name in WORKSPACE_NAMES:
            if workspace.name in (old[name], name) and workspace.name != new[name]:
                workspace.name = new[name]
                break


def set_language(context, language, remember=True):
    view = context.preferences.view
    prefs = _prefs(context)
    old_workspace_names = _workspace_names(view) if prefs and prefs.translate_workspaces else None
    if (remember and prefs and prefs.use_blender_language
            and current_language(context) != second_language(context)):
        # The language set in Blender, to come back to from the second language.
        prefs.home_language = view.language
        prefs.home_resolved = current_language(context)
    if not _is_english(_resolve(language)):
        # Otherwise the switch would change nothing on screen.
        view.use_translate_interface = True
        view.use_translate_tooltips = True
        if hasattr(view, "use_translate_reports"):  # Blender 4.0 and later
            view.use_translate_reports = True
        if hasattr(view, "use_international_fonts"):  # Blender 2.80 to 2.82
            view.use_international_fonts = True
    view.language = language
    if old_workspace_names is not None:
        _rename_workspaces(old_workspace_names, _workspace_names(view))


def _translate_workspaces_update(self, context):
    if self.translate_workspaces:
        # Bring the tabs named in English to the language shown now.
        english = {name: name for name in WORKSPACE_NAMES}
        _rename_workspaces(english, _workspace_names(context.preferences.view))


def _language_items(self, context):
    languages = _languages()
    # Numbered by identifier: the names follow the interface language, so their order changes.
    numbers = {identifier: index for index, identifier in enumerate(sorted(languages))}
    _language_items_store[:] = [
        (identifier, name, "", numbers[identifier])
        for identifier, name in sorted(languages.items(), key=lambda kv: kv[1])
        if identifier != 'DEFAULT'
    ]
    return _language_items_store


def _language_choice(stored_name, other_name):
    """Getter and setter of an enum that shows the identifier kept in `stored_name`."""

    def get(self):
        stored = getattr(self, stored_name)
        for identifier, _name, _description, number in _language_items_store or _language_items(self, None):
            if identifier == stored:
                return number
        return 0

    def set(self, value):
        for identifier, _name, _description, number in _language_items_store or _language_items(self, None):
            if number == value:
                context = bpy.context
                current = current_language(context)
                switch = current == getattr(self, stored_name) and current != getattr(self, other_name)
                setattr(self, stored_name, identifier)
                # Already showing the old language (and it is not the other one too): show the new
                # one right away.
                if switch:
                    set_language(context, identifier, remember=False)
                return

    return get, set


_first_get, _first_set = _language_choice("first_language", "second_language")
_second_get, _second_set = _language_choice("second_language", "first_language")


class FalconLanguagePreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    use_blender_language: BoolProperty(
        name="Use Blender's Language Setting",
        description="Use the language set in Preferences > Interface > Language as the first language",
        default=True,
    )
    translate_workspaces: BoolProperty(
        name="Translate Workspace Tabs",
        description="Also rename the standard workspace tabs (Layout, Modeling...) when switching. "
                    "Tab names are saved in the file",
        default=False,
        update=_translate_workspaces_update,
    )
    # The language set in Blender before switching to the second one ("DEFAULT" for Automatic).
    home_language: StringProperty(
        name="Home Language",
        default="",
    )
    # What "Automatic" stood for when it was remembered.
    home_resolved: StringProperty(
        name="Home Language (Resolved)",
        default="",
    )
    # Stored as the identifier ("ja_JP"), so it survives builds whose language lists differ.
    first_language: StringProperty(
        name="First Language",
        default=DEFAULT_FIRST,
    )
    first_language_choice: EnumProperty(
        name="First Language",
        description="Language of the first button",
        items=_language_items,
        get=_first_get,
        set=_first_set,
    )
    second_language: StringProperty(
        name="Second Language",
        default=DEFAULT_SECOND,
    )
    second_language_choice: EnumProperty(
        name="Second Language",
        description="Language of the second button",
        items=_language_items,
        get=_second_get,
        set=_second_set,
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.prop(self, "use_blender_language")
        if self.use_blender_language:
            # Shown greyed out: it follows Preferences > Interface > Language.
            first = first_language_resolved(context)
            split = layout.split(factor=0.4)
            split.enabled = False
            row = split.row()
            row.alignment = 'RIGHT'
            row.label(text=tip_("First Language"))
            split.label(text=_languages().get(first, first), translate=False)
        else:
            layout.prop(self, "first_language_choice")
        layout.prop(self, "second_language_choice")
        if first_language_resolved(context) == second_language(context):
            layout.label(text=tip_("Choose two different languages"), icon='ERROR')
        layout.prop(self, "translate_workspaces")
        layout.label(text=tip_("Ctrl+Shift+L switches between these two languages"))


class WM_OT_falcon_language_set(bpy.types.Operator):
    """Set the interface language"""
    bl_idname = "wm.falcon_language_set"
    bl_label = "Set Interface Language"
    bl_options = {'INTERNAL'}

    language: StringProperty(
        name="Language",
        description="Language identifier, e.g. en_US or ja_JP",
        options={'SKIP_SAVE'},
    )

    @classmethod
    def description(cls, context, properties):
        name = _languages().get(properties.language, properties.language)
        return tip_("Switch the interface to %s") % name

    def execute(self, context):
        if self.language not in _languages():
            self.report({'WARNING'}, rpt_("Language not available: %s") % self.language)
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
        # Any language other than the first one (the second one, or one chosen elsewhere) goes
        # back to the first one.
        target = second if current_language(context) == first_language_resolved(context) else first
        if target not in _languages():
            self.report({'WARNING'}, rpt_("Language not available: %s") % target)
            return {'CANCELLED'}
        set_language(context, target)
        return {'FINISHED'}


def draw_topbar(self, context):
    region = getattr(context, "region", None)
    if region is None or region.alignment != 'RIGHT':
        return
    current = current_language(context)
    row = self.layout.row(align=True)
    second = second_language(context)
    for language, resolved in ((first_language(context), first_language_resolved(context)),
                               (second, second)):
        props = row.operator("wm.falcon_language_set", text=short_code(resolved),
                             translate=False, depress=current == resolved)
        props.language = language


classes = (
    FalconLanguagePreferences,
    WM_OT_falcon_language_set,
    WM_OT_falcon_language_toggle,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_HT_upper_bar.append(draw_topbar)
    keyconfig = bpy.context.window_manager.keyconfigs.addon
    if keyconfig is not None:  # None in background mode
        keymap = keyconfig.keymaps.new(name="Window", space_type='EMPTY')
        item = keymap.keymap_items.new(WM_OT_falcon_language_toggle.bl_idname, **SHORTCUT)
        _keymaps.append((keymap, item))


def unregister():
    for keymap, item in _keymaps:
        try:
            keymap.keymap_items.remove(item)
        except Exception:
            pass
    _keymaps.clear()
    bpy.types.TOPBAR_HT_upper_bar.remove(draw_topbar)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
