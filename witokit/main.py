"""Welcome to WiToKit.

This is the entry point of the application.
"""

import os
import argparse
import multiprocessing
import functools
import shutil
import logging
import logging.config

import witokit.utils.config as cutils
import witokit.utils.files as futils
import witokit.utils.wikipedia as wutils

logging.config.dictConfig(
    cutils.load(
        os.path.join(os.path.dirname(__file__), 'logging', 'logging.yml')))

logger = logging.getLogger(__name__)


def _extract(args):
    logger.info('Extracting content of wikipedia archive under {}'
                .format(args.wiki_input_dirpath))
    input_filepaths = futils.get_input_filepaths(args.wiki_input_dirpath)
    total_arxivs = len(input_filepaths)
    arxiv_num = 0
    with multiprocessing.Pool(args.num_threads) as pool:
        extract = functools.partial(wutils.extract,
                                    args.wiki_output_filepath)
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
    parser_extract = subparsers.add_parser(
        'extract', formatter_class=argparse.RawTextHelpFormatter,
        help='extract content from Wikipedia XML dump')
    parser_extract.set_defaults(func=_extract)
    parser_extract.add_argument('-i', '--input', required=True,
                                dest='wiki_input_dirpath',
                                help='absolute path to directory containing '
                                     'Wikipedia XML files')
    parser_extract.add_argument('-o', '--output', required=True,
                                dest='wiki_output_filepath',
                                help='absolute path to output .txt file')
    parser_extract.add_argument('-n', '--num_threads', type=int,
                                required=False, default=1,
                                dest='num_threads',
                                help='number of CPU threads to be used')
    args = parser.parse_args()
    args.func(args)
