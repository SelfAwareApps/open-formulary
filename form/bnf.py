"""
Abstractions over the BNF
"""
import collections

from db import db

coll = db.struct

def get_structure(raw=False):
    """
    Return the Chapters, sections and paragraph structure of the
    BNF codes.

    By default, return the drugs as well. if RAW is True, return
    just the names.

    Arguments:
    - `raw`: bool [False]

    Return: dict, dict, dict
    Exceptions: None
    """
    coll = db.struct
    if raw:
        coll = db.rawstruct
    chapters = dict(
        [(c['chapter'], c['title']) for c in coll.find({'level': 'chapter'})]
        )
    sections = collections.defaultdict(dict)
    for c in coll.find({'level': 'section'}):
        sections[c['chapter']][c['section']] = c['title']

    paras = coll.find({'level': 'paragraph'}).sort('bnf')

    return chapters, sections, paras

def walk():
    """
    Using the Python idiom (or something a bit like it anyway) for walking over
    trees, walk through the BNF.

    >> for chapter, sections in bnf.walk():
    ...    print chapter['bnf'], chapter['title']
    ...    for section, paragraphs, drugs in sections:
    ...        print section['bnf'], section['title'], len(drugs)
    ...        for paragraph in paragraphs:
    ...            print paragraph['bnf'], paragraph['title']

    Exceptions: None
    """
    def sectioniterator(sections):
        "Internal iterator for sections"
        for section in sections:
            paragraphs = coll.find({'level': 'paragraph',
                                    'chapter': section['chapter'],
                                    'section': section['section']}).sort('bnf')
            yield section, paragraphs, section.get('sectdrugs', [])

    chapters = coll.find({'level': 'chapter'}).sort('bnf')
    for chapter in chapters:
        sections = coll.find({'level': 'section',
                              'chapter': chapter['chapter']}).sort('bnf')
        yield chapter, sectioniterator(sections)

if __name__ == '__main__':
    for chapter, sections in walk():
        print 'Chapter', chapter['bnf'], chapter['title']
        for section, paragraphs, drugs in sections:
            print 'Section', section['bnf'], section['title'], len(drugs)
            for paragraph in paragraphs:
                print 'P', paragraph['bnf'], paragraph['title'], len(drugs)
