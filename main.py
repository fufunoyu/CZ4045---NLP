import getopt
import os
import sys

from django.core.wsgi import get_wsgi_application


def usage():
    print("Usage: python main.py [-h|--help] [initdb]")


def main(argv):

    try:
        opts, remainders = getopt.getopt(argv, "h", ["help", ])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        else:
            assert False, "unhandled option"

    for arg in remainders:

        if arg == 'initdb':
            from dbmgr import db_ops
            db_ops.init_amazon_review_db()
        elif arg == '???':
            sys.exit()


if __name__ == "__main__":

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    application = get_wsgi_application()
    main(sys.argv[1:])
