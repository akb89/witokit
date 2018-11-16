# WiToKit
Welcome to `WiToKit`, a Python toolkit to download and generate
preprocessed Wikipedia dumps for NLP in a single .txt file, one
sentence per line.

*Note: WiToKit currently only supports `xx-pages-articles.xml.xx.bz2` Wikipedia archives corresponding to articles, templates, media/file descriptions, and primary meta-pages.*

## Install

```
pip3 install witokit
```

## Use

### Download
To download a .bz2-compressed Wikipedia XML dump, do:
```bash
witokit download ⁠\
  --lang lang_wp_code \
  --date wiki_date \
  --output /abs/path/to/output/dir/where/to/store/bz2/archives \
  --num-threads num_cpu_threads
```

For example, to download the latest English Wikipedia, do:
```bash
witokit download ⁠--lang en --date latest --output /abs/path/to/output/dir --num-threads 2
```

The `--lang` parameter expects the WP (language) code corresponding
to the desired Wikipedia archive.
Check out the full list of Wikipedias with their corresponding WP codes [here](https://en.wikipedia.org/wiki/List_of_Wikipedias).

The `--date` parameter expects a string corresponding to one of the dates
found under the Wikimedia dump site corresponding to a given Wikipedia dump
(e.g. https://dumps.wikimedia.org/enwiki/ for the English Wikipedia).

### Extract
To extract the content of the downloaded .bz2 archives, do:

```bash
witokit extract \
  --input /abs/path/to/downloaded/wikipedia/bz2/archives \
  --num-threads num_cpu_threads
```

### Process
To preprocess the content of the extracted XML archives and output a single .txt file, tokenize, one sentence per line:
```bash
witokit process \
  --input /abs/path/to/wikipedia/extracted/xml/archives \
  --output /abs/path/to/single/output/txt/file \
  --lower \  # if set, will lowercase text
  --num-threads num_threads
```
