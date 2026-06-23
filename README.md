# Lyrics Converter

Convert lyric text files into romanized or phonetic lyrics.

Implemented modes:

- `mandarin`: Mandarin lyrics to tone-mark pinyin.
- `cantonese`: Cantonese lyrics to Jyutping with tone numbers.
- `english`: English lyrics to readable phonetic respelling.
- `minnan`: Taiwanese Hokkien lyrics to Tailo romanization.

The Minnan/Tailo mode uses `taibun` as the first-pass conversion engine. Use a custom dictionary for song-specific corrections.

## Install

```bash
python3 -m pip install -r requirements.txt
```

## Usage

```bash
python3 convert.py --mode mandarin "test_data/original_examples/国语转拼音/原歌词.txt" output.txt
python3 convert.py --mode cantonese "test_data/original_examples/粤语转拼音/原歌词.txt" output.txt
python3 convert.py --mode english "test_data/original_examples/英语音译改写/原歌词.txt" output.txt
python3 convert.py --mode minnan "test_data/original_examples/闽南语转台罗拼音/原歌词.txt" output.txt
```

List available converters:

```bash
python3 convert.py --list-modes
```

## Visual App

Start the production-facing workspace:

```bash
streamlit run app.py
```

The app supports lyric text upload, direct paste input, converter selection, optional custom JSON dictionaries, side-by-side preview, and result download.

## Project Structure

```text
lyrics_converter/
  core.py
  registry.py
  utils.py
  converters/
    mandarin.py
    cantonese.py
    english.py
    minnan.py
convert.py
app.py
test_data/
  original_examples/
  corpus/
  outputs/
```

See `ARCHITECTURE.md` for how to add new converters.

For English, section labels such as `[Verse]` and `[Chorus]` are added with a simple heuristic. Disable them with:

```bash
python3 convert.py --mode english --no-english-sections "test_data/original_examples/英语音译改写/原歌词.txt" output.txt
```

## Custom Dictionaries

Pass `--custom-dict custom.json` to override readings.

For Mandarin or Cantonese:

```json
{
  "不了": "bù le",
  "誰": "seoi4"
}
```

For English:

```json
{
  "through": "throo",
  "baby": "bay-bee"
}
```
