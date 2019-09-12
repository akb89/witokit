"""Tokenize a batch of .txt files with polyglot."""

import os
import functools
import multiprocessing

import witokit


def _process(lowercase, output_dirpath, input_filepath):
    output_filepath = os.path.join(
        output_dirpath,
        '{}.tkz.txt'.format(os.path.basename(input_filepath).split('.txt')[0]))
    processing_input = []
    with open(input_filepath, 'r', encoding='utf-8') as input_stream:
        for line in input_stream:
            processing_input.append(line.strip())
    with open(output_filepath, 'w', encoding='utf-8') as output_stream:
        tokenized_txt = witokit.tokenize(' '.join(processing_input), lowercase)
        print(tokenized_txt, file=output_stream)
    return input_filepath


if __name__ == '__main__':
    BATCH_DIRPATH = '/Users/akb/Github/witokit/data/'
    OUTPUT_DIRPATH = '/Users/akb/Github/witokit/data/'
    LOWERCASE = True
    NUM_THREADS = 1

    assert os.path.exists(BATCH_DIRPATH)
    assert os.path.exists(OUTPUT_DIRPATH)

    txt_filepaths = [os.path.join(BATCH_DIRPATH, filename) for filename in
                     os.listdir(BATCH_DIRPATH) if not filename.startswith('.')]

    file_num = 0
    with multiprocessing.Pool(NUM_THREADS) as pool:
        process = functools.partial(_process, LOWERCASE, OUTPUT_DIRPATH)
        for filepath in pool.imap_unordered(process, txt_filepaths):
            file_num += 1
            print('Done processing file {}'.format(filepath))
            print('Completed processing of {}/{} files'
                  .format(file_num, len(txt_filepaths)))
