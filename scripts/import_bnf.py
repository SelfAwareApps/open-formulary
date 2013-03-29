"""
Standalone script to import

* a CSV of drugs based on BNF Code, Drug Name.
* a JSON file containing the BNF taxonomy
"""
import sys

import ffs

from form.db import db

DATA = (ffs.Path(__file__).parent / '../data/').abspath

def load_drugs():
    """
    Take the CSV of drugs, parse it into dicts for our Drug entries,
    then load them into the database

    Return: None
    Exceptions: None
    """
    drugfile = DATA / 'drug.names.csv'
    db.drugs.drop()
    with drugfile.csv() as csv:
        for drug in csv:
            name = drug[1].replace('_', ' ')
            db.drugs.save(dict(code=drug[0], name=name))
    return

def load_structure():
    """
    Take the JSON file of drugs, clean it, and load it into
    the database.

    Return: None
    Exceptions: None
    """
    structfile = DATA / 'bnf.json'
    print structfile
    struct = structfile.json_load()
    map(lambda x: x.pop('_id'), struct)
    db.struct.drop()
    db.struct.insert(struct)
    return


def main():
    """
    Commandline entrypoint


    Return: int
    Exceptions: None
    """
    load_structure()
    load_drugs()
    for s in db.drugs.find().limit(5):
        print s, "\n"
    return 0

if __name__ == '__main__':
    sys.exit(main())
