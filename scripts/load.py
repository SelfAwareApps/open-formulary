"""
Load sample formularies
"""
import json
import sys

from form.db import db

def main():
    """
    Load JSON formularies into the DB

    Return: int
    Exceptions: None
    """
    formularies = json.loads(open(sys.argv[-1], 'r').read())
    for f in formularies:
        indb = db.formularies.find_one({'name': f['name'], 'owner': f['owner']})
        if not indb:
            print 'Inserting', f['name']
            db.formularies.insert(f)
        else:
            print 'Found', f['name'], '- skipping'

    return 0

if __name__ == '__main__':
    sys.exit(main())
