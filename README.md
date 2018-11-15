# WiToKit
Welcome to `WiToKit`, a Python toolkit to generate a tokenized dump of Wikipedia.

## Install

```
pip install witokit
```

## Use

### Download
To download a .bz2-compressed Wikipedia XML dump, do:
```bash

```

if you want to have a full download progress bar you can always use the shell
(on UNIX), with:
```bash
wget -r -np -nH --cut-dirs=2 -R "index.html*" --accept-regex="https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles[0-9]+.xml.*bz2\$" https://dumps.wikimedia.org/enwiki/latest/
```


### Extract
To extract the content of the .bz2 archives, do:

```bash

```

On UNIX, you can also use pbzip2 extract the content of an archive in parrallel:
```bash
find /abs/path/to/data/wikipedia/201XXXXX -type f -name "*.bz2" | xargs -n1 -I file pbzip2 -p55 -d file
```

### Process
To (pre-)process the content of the extracted archive (tokenize and lowercase)
with spacy, do:

### ___
Extract the content of the downloaded XML files into a single .txt file,
once sentence per line, tokenized with spacy.io, and lowercased.

```
witokit extract -i /abs/path/to/wikipedia/xml/dumps/ -o /abs/path/to/output/txt/file
-n number_of_threads_to_use
```
