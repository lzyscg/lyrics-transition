# Architecture

The project is split into three layers:

1. `lyrics_converter/`
   Core conversion package. UI and CLI both call this layer.

2. `convert.py` / `lyrics_converter/cli.py`
   Command-line entrypoint for batch jobs and automation.

3. `app.py`
   Streamlit visual workspace for production users.

## Converter Contract

Every converter lives in `lyrics_converter/converters/` and subclasses `LyricsConverter`.

Minimum shape:

```python
class NewConverter(LyricsConverter):
    metadata = ConverterMetadata(
        id="new_mode",
        name="显示名称",
        description="说明",
    )

    def convert(self, text, custom_dict=None, options=None):
        return converted_text
```

Then register it in `lyrics_converter/registry.py`.

## Minnan/Tailo

The Minnan converter lives in `lyrics_converter/converters/minnan.py` and uses `taibun` for the first-pass Tailo conversion.

Song-specific corrections should be handled with custom dictionaries first. If a correction becomes broadly useful, promote it into the converter or a shared dictionary file.

## Homophone Replacement

The homophone converter is implemented in Python under:

```text
lyrics_converter/converters/homophone.py
lyrics_converter/homophone/
```

It follows the earlier standalone project's logic, but does not depend on that project or its Node/Vite code:

1. Get one pinyin key per Chinese character.
2. Generate candidate characters from common characters, manual candidates, and `pypinyin`'s dictionary.
3. Filter candidates by tone, polyphony, blocked characters, and stroke count.
4. Rank by manual priority, commonness, simplicity, and recent repetition.
5. Preserve all non-Chinese characters, whitespace, punctuation, and line breaks.

## Shared Utilities

Common line/token handling is in:

```text
lyrics_converter/utils.py
```

Use these helpers for CJK run splitting, punctuation preservation, phrase override normalization, and rendering converted tokens back into lyric lines.
