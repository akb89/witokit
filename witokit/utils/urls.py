"""URL utils."""

import witokit.utils.constants as const

__all__ = ('get_wikipedia_dump_url', 'get_wikipedia_pattern',
           'get_wiki_arxiv_url')


def get_wikipedia_dump_url(lang, date):
    """Return the Wikipedia download URL corresponding to the lang and data."""
    return '{}/{}wiki/{}'.format(const.WIKI_DL_URL, lang, date)


def get_wikipedia_pattern(lang, date):
    """Return a regex pattern matching for wiki .bz2 files to be extracted."""
    return r'({}wiki-{}-pages-articles[0-9]+.xml.*bz2$)'.format(lang, date)


def get_wiki_arxiv_url(wiki_dump_url, href):
    """Return a full URL from the href of a .bz2 archive."""
    return '{}/{}'.format(wiki_dump_url, href)
