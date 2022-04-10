#!/usr/bin/env python3

# get list of pictures
# draw random pairs
# for pair in pairs
#  display duel, handle key input
#  update scores (for now: +1/-1)
# at the end: save scores in file

import argparse
import logging
import cv2
import itertools

# TODO
class Picture:
    """Represents a picture with a filename and a score"""
    def __init__(self, filename, score=0):
        self.filename = filename
        self.score = score

    
    @property
    def name(self):
        """returns a displayable name"""

        pass
    
    @property
    def img(self):
        """returns an opencv matrix loaded from the filename"""
        return cv2.imread(self.filename)

    


class PictureList(list):
    """a list[Picture] instance with custom methods"""

    @property
    def length(self):
        return len(self)

    @classmethod
    def get_ext(cls, filename):
        if "." not in filename:
            return filename
        return filename.split(".")[-1]
        # print(filename)
        # path.splitext(filename)#[1].lower()

    @classmethod
    def is_img_file(cls, filename):
        extensions = ["jpg", "png", "gif"]
        return cls.get_ext(filename) in extensions

    #TODO
    def random_pairs(self,
            nb_pairs=None,
            no_duplicate=True,
            avoid_leftalones=True) -> list[list[Picture]]:
        """returns a list of random pairs.
        if nb_pairs is left to None:
            if no_duplicate is True:
                returns the max amount of pairs with no duplicate
                if len(self) is odd and avoid_leftalones is True:
                    append an additional pair made of the leftalone and a random Picture already paired.
            else:
                returns an amount of pairs equal to len(self)
        """
        pairs = list(itertools.combinations(self, 2))[:nb_pairs]
        return pairs
    
    #TODO
    def load_from_directory(self, directory):
        """loads itself from the pictures contained in a directory"""
        from os import listdir, path
        logging.debug(f"loading pictures from {directory}")
        # print(listdir(directory))

        

        filenames = [f for f in listdir(directory) if self.is_img_file(f)]
        # print("\n".join([f"{get_ext(f)}" for f in listdir(directory)][:5]))

        self.clear()
        for filename in filenames:
            self.append(Picture(filename))

        logging.debug(f"loaded {self.length} pictures")



# TODO: Improve later. For now, it's functional enough
# TODO: check cointoss.GameParams, write a generic module from it and import it here
class Params:
    """A holder/manager class for the parameters provided by the user via the CLI"""
    def __init__(self):
        # default params
        self.max_rounds = -1
        self.max_choices_per_round = -1
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
        # TODO: automatize by using an argname translater like in cointoss
        parser.add_argument("--max-rounds")
        parser.add_argument("--directory")
        args = parser.parse_args()
        self.params.update_from_argparse_args(args)

    #TODO
    def show_duel(self, pic_list:list[Picture]):
        win_height = 200
        win_width = win_height * 16/9

        # TODO: display both images
        interpolation = cv2.INTER_CUBIC
        im_list = [pic.img for pic in pic_list]
        w_min = min(im.shape[1] for im in im_list)
        im_list_resize = [cv2.resize(im, (w_min, int(im.shape[0] * w_min / im.shape[1])), interpolation=interpolation)
                      for im in im_list]
        duel_img = cv2.hconcat(im_list_resize)

        duel_text = " vs ".join(pic.name for pic in pic_list)

        cv2.imshow(duel_text, duel_img)
        cv2.waitKey(0) # ?
        # get user input, decide winner
        cv2.destroyAllWindow() # ?
        # TODO: adjust pictures scores

    #TODO
    def run(self):

        logging.debug("starting run()")
        self.pictures.load_from_directory(self.params.directory)
        logging.debug("with {} pictures".format(self.pictures.length))


        for round in self.params.max_rounds:
            pairs = self.pictures.random_pairs(
                    nb_pairs=self.params.max_choices_per_round,
                    no_duplicate=True,
                    avoid_leftalones=True)
            for pair in pairs:
                logging.info("dueling {} vs {}".format(pair[0].name, pair[1].name))
                self.show_duel(pair)







def main():
    print("== Picture Tournament begin ==")

    logging.basicConfig(level=logging.DEBUG)
    t = Tournament()
    t.handle_cli_args()
    t.run()

    print("== Picture Tournament end ==")


if __name__ == "__main__":
    main()

