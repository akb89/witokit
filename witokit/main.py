"""Welcome to WiToKit.

This is the entry point of the application.
"""

import os
import argparse
import multiprocessing
import urllib
import functools
import shutil
import re
import bz2
import logging
import logging.config

from bs4 import BeautifulSoup

import spacy
import wikiextractor

import witokit.utils.config as cutils
import witokit.utils.files as futils
import witokit.utils.urls as uutils

logging.config.dictConfig(
    cutils.load(
        os.path.join(os.path.dirname(__file__), 'logging', 'logging.yml')))

logger = logging.getLogger(__name__)


def _download_href(output_dirpath, wiki_dump_url, href):
    url = uutils.get_wiki_arxiv_url(wiki_dump_url, href)
    logger.info('Downloading {}'.format(url))
    output_filepath = futils.get_download_output_filepath(output_dirpath,
                                                          href)
    try:
        urllib.request.urlretrieve(url, output_filepath)
    except urllib.error.HTTPError as error:
        logger.error('Could not download archive from {}'.format(url))
        raise error


def _parallel_download(wiki_arxiv_hrefs, wiki_dump_url, num_threads,
                       output_dirpath):
    with multiprocessing.Pool(num_threads) as pool:
        _download_href_to_output_dir = functools.partial(_download_href,
                                                         output_dirpath,
                                                         wiki_dump_url)
        total_arxivs = len(wiki_arxiv_hrefs)
        arxiv_num = 0
        for _ in pool.imap_unordered(_download_href_to_output_dir,
                                     wiki_arxiv_hrefs):
            arxiv_num += 1
            logger.info('Downloaded {}/{} archives'.format(arxiv_num,
                                                           total_arxivs))


def _collect_wiki_arxiv_hrefs(wiki_dump_url, lang, date):
    wiki_arxiv_hrefs = []
    try:
        response = urllib.request.urlopen(wiki_dump_url)
        html_doc = response.read()
        soup = BeautifulSoup(html_doc, 'html.parser')
        for link in soup.find_all('a'):
            pattern = uutils.get_wikipedia_pattern(lang, date)
            href = link.get('href')
            if re.match(pattern, href):
                wiki_arxiv_hrefs.append(href)
    except urllib.error.HTTPError as error:
        logger.error('HTTPError using lang = \'{}\' and date = \'{}\'. '
                     'Could not retrieve any Wikipedia data at URL = {}'
                     .format(lang, date, wiki_dump_url))
        raise error
    return wiki_arxiv_hrefs


def _download(args):
    wiki_dump_url = uutils.get_wikipedia_dump_url(args.lang, args.date)
    logger.info('Downloading Wikipedia .bz2 archives from {}'
                .format(wiki_dump_url))
    wiki_arxiv_hrefs = _collect_wiki_arxiv_hrefs(wiki_dump_url, args.lang,
                                                 args.date)
    _parallel_download(wiki_arxiv_hrefs, wiki_dump_url, args.num_threads,
                       args.output_dirpath)


def _decompress_arxiv(arxiv):
    inc_decompressor = bz2.BZ2Decompressor()
    logger.info('Extracting archive {}'.format(arxiv))
    output_arxiv_filepath = arxiv.rsplit('.bz2')[0]
    with open(arxiv, 'rb') as arxiv_byte_stream:
        with open(output_arxiv_filepath, 'wb') as out_stream:
            for data in iter(lambda: arxiv_byte_stream.read(100 * 1024), b''):
                out_stream.write(inc_decompressor.decompress(data))


def _extract(args):
    logger.info('Extracting .bz2 files from {}'.format(args.bz2_input_dirpath))
    bz2_arxivs = futils.get_bz2_arxivs(args.bz2_input_dirpath)
    total_arxivs = len(bz2_arxivs)
    arxiv_num = 0
    with multiprocessing.Pool(args.num_threads) as pool:
        for _ in pool.imap_unordered(_decompress_arxiv, bz2_arxivs):
            arxiv_num += 1
            logger.info('Extracted {}/{} archives'.format(arxiv_num,
                                                          total_arxivs))


def _preprocess(output_txt_filepath, lowercase, input_xml_filepath):
    """Extract content of wikipedia XML file.

    Extract content of json.text as given by wikiextractor and tokenize
    content with spacy. Output one-sentence-per-line, lowercase, tokenized
    text.
    """
    logger.info('Extracting content of wikipedia file {}'
                .format(input_xml_filepath))
    output_filepath = futils.get_output_filepath(input_xml_filepath,
                                                 output_txt_filepath)
    spacy_nlp = spacy.load('en_core_web_sm')
    spacy_nlp.max_length = 10000000  # avoid bug with very long input
    with open(output_filepath, 'w', encoding='utf-8') as output_stream:
        logger.info('Writing output to file {}'.format(output_filepath))
        for json_object in wikiextractor.extract(input_xml_filepath):
            doc = spacy_nlp(json_object['text'])
            for sent in doc.sents:
                if lowercase:
                    tokens = [token.text.lower().strip() for token in sent]
                else:
                    tokens = [token.text.strip() for token in sent]
                output_sent = ' '.join(tokens)
                print(output_sent, file=output_stream)
    return input_xml_filepath


def _process(args):
    logger.info('Processing content of wikipedia archives under {}'
                .format(args.wiki_input_dirpath))
    if args.lower:
        logger.info('Lowercasing archives')
    input_filepaths = futils.get_input_filepaths(args.wiki_input_dirpath)
    total_arxivs = len(input_filepaths)
    arxiv_num = 0
    with multiprocessing.Pool(args.num_threads) as pool:
        extract = functools.partial(_preprocess,
                                    args.wiki_output_filepath, args.lower)
        for process in pool.imap_unordered(extract, input_filepaths):
            arxiv_num += 1
            logger.info('Done extracting content of {}'.format(process))
            logger.info('Completed extraction of {}/{} archives'
                        .format(arxiv_num, total_arxivs))
    # concatenate all .txt files into single output .txt file
    logger.info('Concatenating tmp files...')
    tmp_filepaths = futils.get_tmp_filepaths(args.wiki_output_filepath)
    with open(args.wiki_output_filepath, 'w', encoding='utf-8') as output_strm:
        for tmp_filepath in tmp_filepaths:
            with open(tmp_filepath, 'r') as tmp_stream:
                for line in tmp_stream:
                    line = line.strip()
                    print(line, file=output_strm)
    logger.info('Done extracting content of Wikipedia archives')
    shutil.rmtree(futils.get_tmp_dirpath(args.wiki_output_filepath))


def main():
    """Launch WiToKit."""
    parser = argparse.ArgumentParser(prog='witokit')
    subparsers = parser.add_subparsers()
    parser_download = subparsers.add_parser(
        'download', formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help='download a given .bz2-compressed Wikipedia XML dump')
    parser_download.set_defaults(func=_download)
    parser_download.add_argument('-l', '--lang', default='en',
                                 help='the language ISO code of the '
                                      'Wikipedia dump to download')
    parser_download.add_argument('-d', '--date', default='latest',
                                 help='the date of the Wikipedia dump to '
                                      'download')
    parser_download.add_argument('-o', '--output', required=True,
                                 dest='output_dirpath',
                                 help='absolute path to output directory '
                                      'where to save downloaded files')
    parser_download.add_argument('-n', '--num-threads', type=int, default=1,
                                 help='number of CPU threads to use')
    parser_extract = subparsers.add_parser(
        'extract', formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help='extract content of Wikipedia .bz2 archives')
    parser_extract.set_defaults(func=_extract)
    parser_extract.add_argument('-i', '--input', required=True,
                                dest='bz2_input_dirpath',
                                help='absolute path to directory containing '
                                     'Wikipedia .bz2 archives')
    parser_extract.add_argument('-n', '--num-threads', type=int, default=1,
                                help='number of CPU threads to use')
    parser_process = subparsers.add_parser(
        'process', formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help='(pre-)process content of a Wikipedia XML dump')
    parser_process.set_defaults(func=_process)
    parser_process.add_argument('-i', '--input', required=True,
                                dest='wiki_input_dirpath',
                                help='absolute path to directory containing '
                                     'Wikipedia XML files')
    parser_process.add_argument('-o', '--output', required=True,
                                dest='wiki_output_filepath',
                                help='absolute path to output .txt file')
    parser_process.add_argument('-lc', '--lower', action='store_true',
                                help='whether or not to lowercase splits')
    parser_process.add_argument('-n', '--num-threads', type=int, default=1,
                                help='number of CPU threads to be used')
    args = parser.parse_args()
    args.func(args)
