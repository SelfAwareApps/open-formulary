"""
Dump our formularies
"""
import json
import sys

from form.db import db

def main():
    """
    Dump formularies to JSON


    Return: int
    Exceptions: None
    """
    formularies = [f for f in db.formularies.find()]
    for f in formularies:
        del f['_id']

    print json.dumps(formularies, indent=2)
    return 0

if __name__ == '__main__':
    sys.exit(main())
