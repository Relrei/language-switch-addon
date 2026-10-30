# Language Switch

A free Blender add-on that switches the interface language between two languages in one click.

[日本語の説明は下にあります](#日本語)

![Buttons in English and in Japanese](images/04-buttons.png)

## Features

- Two buttons at the right end of the Top Bar (**EN** / **JA** by default).
- **Ctrl+Shift+L** toggles between the two languages.
- The first language follows the language set in Blender (Preferences > Interface > Language), so you only choose the language to switch to. Both can also be chosen by hand.
- Switching to a translated language also turns on the translation of the interface, tooltips and reports, so the switch is visible right away.
- The language is a normal Blender preference, so it is saved with your preferences.

| English | Japanese |
|---|---|
| ![English interface](images/01-english.png) | ![Japanese interface](images/02-japanese.png) |

## Install

Download a zip from [Releases](../../releases) (do not unpack it).

- **As an extension (recommended)**: `language_switch-<version>-extension.zip`
  Edit > Preferences > Get Extensions > the menu at the top right > **Install from Disk...**
- **As a legacy add-on**: `language_switch.zip`
  Edit > Preferences > Add-ons > the menu at the top right > **Install from Disk...**, then enable **Language Switch**.

Install only one of the two.

## Settings

Edit > Preferences > Add-ons > **Language Switch**

![Preferences](images/03-preferences.png)

- **Use Blender's Language Setting** (on by default): the first button is the language set in Preferences > Interface > Language (shown greyed out). Change it there as usual, for example to French, and the buttons become **FR** / **JA**. The add-on remembers it while the second language is shown, also across restarts, and "Automatic" comes back as "Automatic".
- **First Language**: the first button, when the option above is off (English by default).
- **Second Language**: the second button (Japanese by default).

Pressing Ctrl+Shift+L while another language is shown goes back to the first language.

## Compatibility

Requires Blender 4.5 or later.

Tested with:

- Blender 4.5.15 LTS on Linux
- Blender 5.2.0 LTS and 5.2.1 LTS on Linux
- Blender 5.3 Alpha on Linux
- Blender 5.2.3 LTS for Windows, run under Wine on Linux (not yet tested on a real Windows PC)

The add-on is pure Python and has no platform-specific code.

## License

GPL-2.0-or-later. See [LICENSE](LICENSE).

---

## 日本語

Blender のインターフェースの言語を、2 つの言語の間でワンクリックで切り替える無料のアドオンです。

![日本語表示の右上](images/05-topright-4k.png)

### できること

- 上の帯の右端に 2 つのボタン(既定は **EN** / **JA**)が出ます。
- **Ctrl+Shift+L** で 2 つの言語を切り替えます。
- 元の言語は Blender の言語の設定(設定 > インターフェース > 言語)に自動で合うので、選ぶのは変えたい言語だけです。両方を自分で選ぶこともできます。
- 翻訳のある言語へ切り替えると、インターフェース・ツールチップ・レポートの翻訳も一緒に ON になります。
- 言語は Blender の普通の設定なので、他の設定と一緒に保存されます。

### 入れ方

[Releases](../../releases) から zip を落とします(展開はしません)。

- **拡張機能として(おすすめ)**: `language_switch-<版>-extension.zip`
  編集 > プリファレンス > エクステンションを入手 > 右上のメニュー > **ディスクからインストール...**
- **従来のアドオンとして**: `language_switch.zip`
  編集 > プリファレンス > アドオン > 右上のメニュー > **ディスクからインストール...** の後、**Language Switch** を有効にします。

どちらか片方だけを入れてください。

### 設定

編集 > プリファレンス > アドオン > **Language Switch**

- **Use Blender's Language Setting**(既定は ON): 1 つ目のボタンは「設定 > インターフェース > 言語」で選んだ言語になります(灰色で表示)。そこでいつもどおり、例えばフランス語に変えると、ボタンは **FR** / **JA** になります。第 2 言語の表示中もその言語を覚えていて、再起動しても戻れます。「自動」は「自動」のまま戻ります。
- **First Language**: 上のチェックを外した時の、1 つ目のボタンの言語(既定は英語)。
- **Second Language**: 2 つ目のボタンの言語(既定は日本語)。

どちらでもない言語を表示している時に Ctrl+Shift+L を押すと、1 つ目の言語に戻ります。

### 対応する版

Blender 4.5 以降で動きます。

試した版:

- Linux の Blender 4.5.15 LTS
- Linux の Blender 5.2.0 LTS・5.2.1 LTS
- Linux の Blender 5.3 Alpha
- Windows 版 Blender 5.2.3 LTS(Linux の Wine の上で。本物の Windows ではまだ試していません)

Python だけで書かれていて、OS ごとに違う部品はありません。

### ライセンス

GPL-2.0-or-later です。[LICENSE](LICENSE) を見てください。
