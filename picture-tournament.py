#!/usr/bin/env python3

# get list of pictures
# draw random pairs
# for pair in pairs
#  display duel, handle key input
#  update scores (for now: +1/-1)
# at the end: save scores in file

import argparse
import logging

# TODO
class Picture:
    def __init__(self, name, score=0):
        self.name = name
        self.score = score

class PictureList(list):
    """a list[Picture] instance with custom methods"""

    #TODO
    def random_pairs(self) -> list[list[Picture]]:
        pass
    
    #TODO
    def load_from_directory(self, dirname):
        """loads itself from the pictures contained in a directory"""
        pass



# TODO: Improve later. For now, it's functional enough
# TODO: check cointoss.GameParams, write a generic module from it and import it here
class Params:
    """A holder/manager class for the parameters provided by the user via the CLI"""
    def __init__(self):
        # default params
        self.max_rounds = -1
        self.directory = "."

    def update_from_argparse_args(self, args):
        """Updates this instance from an `arg` object returned by argparse.ArgumentParser.parse_args()"""
        self.__dict__.update(args.__dict__)

# TODO
class Tournament:
    def __init__(self):
        self.params = Params()
        self.pictures = PictureList()

    def handle_cli_args(self):
        """parses the cli arguments and sets global program parameters accordingly"""
        parser = argparse.ArgumentParser()
        parser.add_argument("--max-rounds")
        args = parser.parse_args()

        # print(args.max_rounds)
        # print(args._get_args())
        # print(args.__dict__)
        # print(Params.__dict__)

    def configure_logging(self):
        logging.basicConfig(level=logging.DEBUG)


def main():
    print("== Picture Tournament begin ==")
    t = Tournament()
    t.configure_logging()
    t.handle_cli_args()

    print("== Picture Tournament end ==")


if __name__ == "__main__":
    main()

