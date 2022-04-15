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
import os

# TODO
class Picture:
    """Represents a picture with a filename and a score"""
    def __init__(self, filename, score=0):
        self.filename = filename
        self.score = score

    
    @property
    def name(self):
        """returns a displayable name"""
        if "." not in self.filename:
            return self.filename
        return self.filename.split(".")[0]


    @classmethod
    def get_ext(cls, filename):
        if "." not in filename:
            return filename
        return filename.split(".")[-1]
    
    def image(self, directory=None):
        """returns an opencv matrix loaded from the filename"""
        if not directory:
            return cv2.imread(self.filename)
        else:
            return cv2.imread(os.path.join(directory, self.filename))

    


class PictureList(list):
    """a list[Picture] instance with custom methods"""

    def to_text(self) -> str:
        return "\n".join([f"{p.filename} : {p.score}" for p in self])

    def load_from_savefile(self, save_file_name):
        with open(save_file_name, "r") as f:
            for line in f.readlines():
                self.update_from_text_line()

    def update_from_text_line(self, line:str):
        try:
            assert ":" in line
            parts = [s.strip() for s in line.split(":")]
            assert len(parts) == 2
            filename = parts[0]
            score = int(parts[1])
        except:
            logging.error("Failed to update picture list from '{}'".format(line))

    def remove_picture(self, filename):
        matches = [p for p in self if p.filename == filename]
        if matches:
            self.remove(matches[0])



    @property
    def length(self):
        return len(self)


    @classmethod
    def is_img_file(cls, filename):
        extensions = ["jpg", "png", "gif"]
        return Picture.get_ext(filename) in extensions

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
        # self.max_rounds = None
        # self.max_choices_per_round = None
        self.directory = "."
        self.leftkey = "j"
        self.rightkey = "l"
        self.drawkey = "k"
        self.exitkey = "q"

    def update_from_argparse_args(self, args):
        """Updates this instance from an `arg` object returned by argparse.ArgumentParser.parse_args()"""
        self.__dict__.update(args.__dict__)

# TODO
class Tournament:
    def __init__(self):
        self.params = Params()
        self.pictures = PictureList()
        self.quicksave_filename = "quicksave.ptsave"

    def clean_exit(self):
        self.quicksave()
        exit(0)

    #TODO
    def save_to_file(self, filename):
        pass

    def quicksave(self):
        self.save_to_file(self.quicksave_filename)


    def handle_cli_args(self):
        """parses the cli arguments and sets global program parameters accordingly"""
        parser = argparse.ArgumentParser()
        # TODO: automatize by using an argname translater like in cointoss
        # parser.add_argument("--max-rounds")
        parser.add_argument("--directory")
        args = parser.parse_args()
        self.params.update_from_argparse_args(args)

    #TODO
    def show_duel(self, pic_list:list[Picture]):
        win_height = 200
        win_width = win_height * 16/9

        # TODO: display both images
        interpolation = cv2.INTER_CUBIC
        im_list = [pic.image(self.params.directory) for pic in pic_list]
        filenames = [pic.filename for pic in pic_list]

        # print(filenames)
        # print(im_list)

        # assert None not in im_list
        # logging.debug(f"im_list : {im_list}")
        # logging.debug(f"len(im_list): {len(im_list)}")
        w_min = min(im.shape[1] for im in im_list)
        im_list_resize = [cv2.resize(im, (w_min, int(im.shape[0] * w_min / im.shape[1])), interpolation=interpolation)
                      for im in im_list]
        duel_img = cv2.hconcat(im_list_resize)

        duel_text = " vs ".join(pic.name for pic in pic_list)

        cv2.imshow(duel_text, duel_img)
        while True:
            key = cv2.waitKey(0)

            # get user input, decide winner
            # TODO: adjust pictures scores
            if key == ord(self.params.leftkey):
               pic_list[0].score += 1
               logging.info(f"{pic_list[0].name} chosen.")
            elif key == ord(self.params.rightkey):
               pic_list[1].score += 1
               logging.info(f"{pic_list[1].name} chosen.")
            elif key == ord(self.params.drawkey):
               logging.info(f"draw.")
            elif key == ord(self.params.exitkey):
                self.clean_exit()
                break
            else:
                logging.warning(f"unknown key: {key}")
                continue
            break

        cv2.destroyAllWindows()

    #TODO
    def run(self):

        logging.debug("starting run()")
        self.pictures.load_from_directory(self.params.directory)
        logging.debug("with {} pictures".format(self.pictures.length))


        while True:
            pairs = self.pictures.random_pairs(
                    nb_pairs=None,
                    no_duplicate=True,
                    avoid_leftalones=True)
            for pair in pairs:
                logging.info("dueling {} vs {}".format(pair[0].name, pair[1].name))
                self.show_duel(pair)

            break







def main():
    print("== Picture Tournament begin ==")

    logging.basicConfig(level=logging.DEBUG)
    t = Tournament()
    t.handle_cli_args()
    t.params.directory = "images"
    t.run()

    print("== Picture Tournament end ==")


if __name__ == "__main__":
    main()

