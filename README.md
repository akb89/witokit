# WiToKit
[![GitHub release][release-image]][release-url]
[![PyPI release][pypi-image]][pypi-url]
[![Build][travis-image]][travis-url]
[![MIT License][license-image]][license-url]

Welcome to `WiToKit`, a Python toolkit to download and generate
preprocessed Wikipedia dumps for NLP in a single .txt file, one
sentence per line.

*Note: WiToKit currently only supports `xx-pages-articles.xml.xx.bz2` Wikipedia archives corresponding to articles, templates, media/file descriptions, and primary meta-pages. Also, the preprocessing is currently only supported for English. If you'd like support in other languages, please create an issue on Github.*

## Install

```bash
pip3 install witokit
```

On python3.5 you may need to pass on the `--process-dependency-link` flag:
```bash
pip3 install witokit --process-dependency-link
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

**Important** Keep num-threads <= 3 to avoid rejection from Wikimedia servers

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
  --num-threads num_cpu_threads
```

[release-image]:https://img.shields.io/github/release/akb89/witokit.svg?style=flat-square
[release-url]:https://github.com/akb89/witokit/releases/latest
[pypi-image]:https://img.shields.io/pypi/v/witokit.svg?style=flat-square
[pypi-url]:https://pypi.org/project/witokit/
[travis-image]:https://img.shields.io/travis/akb89/witokit.svg?style=flat-square
[travis-url]:https://travis-ci.org/akb89/witokit
[license-image]:http://img.shields.io/badge/license-MIT-000000.svg?style=flat-square
[license-url]:LICENSE.txt
[req-url]:https://requires.io/github/akb89/witokit/requirements/?branch=master
[req-image]:https://img.shields.io/requires/github/akb89/witokit.svg?style=flat-square
