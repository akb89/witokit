"""Welcome to WiToKit.

This is the entry point of the application.
"""

import os
import argparse
import multiprocessing
import urllib.request
import functools
import shutil
import re
import bz2
import logging
import logging.config
import pycld2

from tqdm import tqdm
from polyglot.text import Text
from bs4 import BeautifulSoup

import wikiextractor

import witokit.utils.config as cutils
import witokit.utils.files as futils
import witokit.utils.urls as uutils

logging.config.dictConfig(
    cutils.load(
        os.path.join(os.path.dirname(__file__), 'logging', 'logging.yml')))

logger = logging.getLogger(__name__)

__all__ = ('tokenize')


def _download_href(output_dirpath, wiki_dump_url, href):
    url = uutils.get_wiki_arxiv_url(wiki_dump_url, href)
    logger.debug('Downloading {}'.format(url))
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
        for _ in tqdm(pool.imap_unordered(_download_href_to_output_dir,
                                          wiki_arxiv_hrefs),
                      total=len(wiki_arxiv_hrefs)):
            continue


def _collect_wiki_arxiv_hrefs(wiki_dump_url, lang, date):
    wiki_arxiv_hrefs = []
    try:
        logger.info('Collecting arxiv from {}'.format(wiki_dump_url))
        response = urllib.request.urlopen(wiki_dump_url)
        html_doc = response.read()
        soup = BeautifulSoup(html_doc, 'html.parser')
        for link in soup.find_all('a'):
            pattern = uutils.get_wikipedia_multi_pattern(lang, date)
            href = link.get('href')
            if re.match(pattern, href):
                wiki_arxiv_hrefs.append(href)
        if not wiki_arxiv_hrefs:
            logger.info('No multi arxivs found. Trying for single arxiv')
            # If wikipedia arxiv is too small, check for single arxiv
            for link in soup.find_all('a'):
                pattern = uutils.get_wikipedia_single_pattern(lang, date)
                href = link.get('href')
                if re.match(pattern, href):
                    wiki_arxiv_hrefs.append(href)
        if not wiki_arxiv_hrefs:
            logger.warning('No wikipedia arxiv found')
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
    logger.debug('Extracting archive {}'.format(arxiv))
    output_arxiv_filepath = arxiv.rsplit('.bz2')[0]
    with open(arxiv, 'rb') as arxiv_byte_stream:
        with open(output_arxiv_filepath, 'wb') as out_stream:
            for data in iter(lambda: arxiv_byte_stream.read(100 * 1024), b''):
                out_stream.write(inc_decompressor.decompress(data))


def _extract(args):
    logger.info('Extracting .bz2 files from {}'.format(args.bz2_input_dirpath))
    bz2_arxivs = futils.get_bz2_arxivs(args.bz2_input_dirpath)
    total_arxivs = len(bz2_arxivs)
    with multiprocessing.Pool(args.num_threads) as pool:
        for _ in tqdm(pool.imap_unordered(_decompress_arxiv, bz2_arxivs),
                      total=total_arxivs):
            continue


def _preprocess(output_txt_filepath, lowercase, input_xml_filepath):
    """Extract content of wikipedia XML file.

    Extract content of json.text as given by wikiextractor and tokenize
    content with polyglot. Output one-sentence-per-line, lowercase, tokenized
    text.
    """
    logger.debug('Processing content of wikipedia file {}'
                 .format(input_xml_filepath))
    output_filepath = futils.get_output_filepath(input_xml_filepath,
                                                 output_txt_filepath)
    with open(output_filepath, 'w', encoding='utf-8') as output_stream:
        logger.debug('Writing output to file {}'.format(output_filepath))
        for json_object in tqdm(wikiextractor.extract(input_xml_filepath)):
            try:
                print(tokenize(json_object['text'], lowercase),
                      file=output_stream)
            except UnicodeEncodeError as err:
                logger.error('UnicodeEncodeError processing '
                             'json_object[\'text\'] with polyglot: {}'
                             .format(str(err)))
    return input_xml_filepath


def tokenize(raw_text, lowercase):
    """Tokenize raw_text with polyglot."""
    output = []
    try:
        text = Text(raw_text)
        for sent in text.sentences:
            if lowercase:
                tokens = [token.lower().strip() for token in sent.words]
            else:
                tokens = [token.strip() for token in sent.words]
            output.append(' '.join(tokens))
    except ValueError as err:
        logger.debug('Skipping empty text sequence')
    except pycld2.error as err:
        logger.debug('{}. Skipping sequence'.format(str(err)))
    return '\n'.join(output)


def _process(args):
    logger.info('Processing content of wikipedia archives under {}'
                .format(args.wiki_input_dirpath))
    if args.lower:
        logger.info('Lowercasing archives')
    input_filepaths = futils.get_input_filepaths(args.wiki_input_dirpath)
    total_arxivs = len(input_filepaths)
    with open(args.wiki_output_filepath, 'w', encoding='utf-8') as output_strm:
        with multiprocessing.Pool(processes=args.num_threads) as pool:
            preprocess = functools.partial(
                _preprocess, args.wiki_output_filepath, args.lower)
            for _ in tqdm(pool.imap_unordered(preprocess, input_filepaths),
                          total=total_arxivs):
                continue
        # concatenate all .txt files into single output .txt file
        logger.info('Concatenating tmp files...')
        tmp_filepaths = futils.get_tmp_filepaths(args.wiki_input_dirpath)
        for tmp_filepath in tqdm(tmp_filepaths, total=len(tmp_filepaths)):
            with open(tmp_filepath, 'r', encoding='utf-8') as tmp_stream:
                for line in tmp_stream:
                    line = line.strip()
                    if line:
                        print(line, file=output_strm)
        logger.info('Done processing content of Wikipedia archives')
        shutil.rmtree(futils.get_tmp_dirpath(args.wiki_input_dirpath))


def _sample(args):
    if not 0 < args.percent < 100:
        raise Exception('Specified percent param should be in ]0, 100[')
    logger.info('Sampling input file {}'.format(args.input_filepath))

    logger.info('Counting number of lines in file...')
    if args.input_filepath.endswith('.txt'):
        input_basename = args.input_filepath.split('.txt')[0]
    else:
        input_basename = args.input_filepath
    with open(args.input_filepath, 'r', encoding='utf-8') as input_stream:
        count = sum(1 for x in input_stream)
        logger.info('Total lines = {}'.format(count))
    final_count = count * args.percent / 100
    sampling = count / final_count
    logger.info('Sampling file to {} lines with balance = {}'
                .format(int(final_count), args.balance))
    if args.balance:
        output_filepath = '{}.sample{}.balanced.txt'.format(input_basename,
                                                            args.percent)
        with open(args.input_filepath, 'r', encoding='utf-8') as input_stream:
            with open(output_filepath, 'w', encoding='utf-8') as output_stream:
                for idx, line in enumerate(input_stream):
                    if idx % round(sampling) == 0:
                        print(line.strip(), file=output_stream)
    else:
        output_filepath = '{}.sample{}.txt'.format(input_basename,
                                                   args.percent)
        with open(args.input_filepath, 'r', encoding='utf-8') as input_stream:
            with open(output_filepath, 'w', encoding='utf-8') as output_stream:
                for idx, line in enumerate(input_stream):
                    if idx >= final_count:
                        break
                    print(line.strip(), file=output_stream)
    logger.info('Done sampling file to {}'.format(output_filepath))


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
    parser_process.add_argument('-l', '--lower', action='store_true',
                                help='whether or not to lowercase splits')
    parser_process.add_argument('-n', '--num-threads', type=int, default=1,
                                help='number of CPU threads to be used')
    parser_sample = subparsers.add_parser(
        'sample', formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help='sample a given .txt file deterministically')
    parser_sample.set_defaults(func=_sample)
    parser_sample.add_argument('-i', '--input', required=True,
                               dest='input_filepath',
                               help='absolute path to .txt file to sample')
    parser_sample.add_argument('-p', '--percent', required=True, type=float,
                               help='percentage of input file to keep')
    parser_sample.add_argument('-b', '--balance', action='store_true',
                               help='whether or not to balance the sampling'
                                    'within the corpus or to take the top'
                                    'p% sentences')
    args = parser.parse_args()
    args.func(args)
