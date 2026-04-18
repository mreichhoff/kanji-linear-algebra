# 漢字 Linear Algebra

Multiply Japanese or Chinese characters by their radicals to discover new characters. What happens when 木 × 木 = 林? Type any characters to find out.

https://github.com/user-attachments/assets/4eefc227-f859-403b-b37a-17a6df0a22e6



## How It Works

Enter CJK characters as a column vector and a row vector. The app computes their "product": for each pair of characters, it finds all characters composed of those two components using [Ideographic Description Sequences](https://en.wikipedia.org/wiki/Ideographic_Description_Characters_(Unicode_block)). For example, 木 × 木 yields 林 because 林 = ⿰木木.

Radical variants are mapped to their base forms (e.g. 氵→水, 灬→火), so 水 × 火 → 淡 works even though 淡 is technically ⿰氵炎.

Other mathematical operations may be coming soon.

## Running Locally

Open `index.html` in a browser. No build step or server needed. It's a single HTML file plus a generated `data.js`.

### Regenerating data

If you want to rebuild `data.js` from the source dictionaries:

```sh
python3 preprocess.py
```

This requires `ids.txt`, `zh-defs.json`, and `jp-defs.json` in the project root.

## Acknowledgements

This project uses the following data sources:

- **[CJKVI IDS Database](https://github.com/cjkvi/cjkvi-ids)** — Character decomposition data (IDS). Derived from the [CHISE project](http://www.chise.org/), licensed under GPLv2.
- **[CC-CEDICT](https://cc-cedict.org/wiki/)** — Chinese-English dictionary. Licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
- **[JMdict](https://www.edrdg.org/jmdict/j_jmdict.html)** — Japanese-English dictionary. Licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) by the [Electronic Dictionary Research and Development Group](https://www.edrdg.org/).
- **[KANJIDIC2](https://www.edrdg.org/wiki/index.php/KANJIDIC_Project)** — Kanji dictionary. Licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) by the [Electronic Dictionary Research and Development Group](https://www.edrdg.org/).
