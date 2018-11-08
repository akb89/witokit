"""Files utils."""

import os
import natsort

__all__ = ('get_input_filepaths', 'get_output_filepath',
           'get_tmp_filepaths', 'get_tmp_dirpath')


def get_tmp_dirpath(output_txt_filepath):
    """Return absolute path to output_txt_dirpath/tmp/."""
    return os.path.join(os.path.dirname(output_txt_filepath), 'tmp')


def get_tmp_filepaths(output_txt_filepath):
    """Return all .txt files under the output_txt_dirpath/tmp/ dir."""
    tmp_dirpath = get_tmp_dirpath(output_txt_filepath)
    return natsort.natsorted([os.path.join(tmp_dirpath, filename) for filename
                              in os.listdir(tmp_dirpath)],
                             alg=natsort.ns.IGNORECASE)


def get_output_filepath(input_xml_filepath, output_txt_filepath):
    """Return filepath to output_txt_dirpath/tmp/input_xml_filename.

    Create tmp dir if not exists.
    """
    tmp_dirpath = get_tmp_dirpath(output_txt_filepath)
    os.makedirs(tmp_dirpath, exist_ok=True)
    output_filename = os.path.basename(input_xml_filepath)
    output_txt_filepath = os.path.join(
        tmp_dirpath, '{}.txt'.format(output_filename))
    return output_txt_filepath


def get_input_filepaths(dirpath):
    """Return a list of absolute XML filepaths from a given dirpath.

    List all the files under a specific directory.
    """
    return [os.path.join(dirpath, filename) for filename in
            os.listdir(dirpath) if '.xml' in filename]