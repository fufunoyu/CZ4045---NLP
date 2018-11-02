import getopt
import os
import sys


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

        if arg == 'analysis':
            pass
        elif arg == 'nounphrase':
            from assignment_solution import noun_phrase_summarizer as nps
            nps.main()
        elif arg == 'chunktagger':
            from assignment_solution import chunktagger as ct
            ct.main()
        elif arg == 'sentiment':
            from assignment_solution import sentiment_word_detection
            sentiment_word_detection.main()
        elif arg == 'application':
            pass
        elif arg == '???':
            sys.exit()


if __name__ == "__main__":

    main(sys.argv[1:])
