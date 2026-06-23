# Batch Test Observations

Corpus date: 2026-06-23

## Mandarin

- Basic lyric-style Mandarin conversion is stable and preserves line breaks.
- Classical/literary readings need phrase overrides. The corpus exposed two cases now handled in `MANDARIN_PHRASES`:
  - `敕勒` -> `chì lè`
  - `草低见牛羊` -> `cǎo dī xiàn niú yáng`
- Future Mandarin accuracy work should keep adding phrase-level overrides for song-specific pronunciations and polyphones.

## Cantonese

- The Simplified Chinese to Hong Kong Traditional conversion step helps PyCantonese produce useful Jyutping for simplified input.
- Cantonese nursery-rhyme and colloquial characters such as `瞓` are handled reasonably.
- Some literary or Mandarin-style lyrics still convert mechanically into Cantonese readings. That is acceptable for Jyutping generation, but not the same as translating lyrics into idiomatic Cantonese.

## English

- The common-word respelling table produces much more readable output than raw CMU phoneme fallback.
- The batch exposed useful additions such as `amazing`, `twinkle`, `little`, `acquaintance`, `'twas`, and `'tis`.
- Raw fallback is still serviceable but can look strange for unfamiliar words. The best next step is to keep expanding `ENGLISH_WORDS` from real lyric batches and optionally move the table into an editable JSON file.
