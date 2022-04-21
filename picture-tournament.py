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
import json
import traceback as tb

#TODO: resize images so that each duelist fits in its half of the window


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
    DEFAULT_SAVE_FILENAME = "default.ptsave"

    def to_text(self) -> str:
        return "\n".join([f"{p.filename} : {p.score}" for p in self])

    def save_to_file(self, filename, sort_by_score=True):
        with open(filename, "w") as f:
            if sort_by_score:
                f.write(self.copy_sorted_by_score().to_text())
            else:
                f.write(self.to_text())
            logging.info(f"saved PictureList as {filename}")


    # TESTME
    def load_from_savefile(self, filename):
        logging.debug(f"loading from savefile {filename}")
        with open(filename, "r") as f:
            for line in f.readlines():
                self.update_from_text_line(line)
                # logging.debug(f"line: {line}")
        logging.debug(self.to_text())

    # TESTME
    def update_from_text_line(self, line:str):
        try:
            assert ":" in line
            parts = [s.strip() for s in line.split(":")]
            assert len(parts) == 2
            filename = parts[0]
            score = int(parts[1])
            self.append(Picture(filename, score))
            # logging.debug(f"{filename} -> {score}")
        except:
            pass
            # logging.error("Failed to update picture list from '{}'".format(line))

    # TESTME
    def remove_picture(self, filename):
        matches = [p for p in self if p.filename == filename]
        if matches:
            self.remove(matches[0])

    def sort_by_score(self):
        self.sort(reverse=True, key=lambda pic:pic.score)

    def sort_by_filename(self):
        self.sort(key=lambda pic:pic.filename)

    #TESTME
    def copy_sorted_by_score(self):
        ret = PictureList(self)
        ret.sort_by_score()
        return ret


    @property
    def length(self):
        return len(self)

    @classmethod
    def is_img_file(cls, filename):
        extensions = ["jpg", "png", "gif"]
        return Picture.get_ext(filename) in extensions

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
        import random
        
        if no_duplicate:
            idlist = list(range(self.length))
            pairs = []
            random.shuffle(idlist)
            print(idlist)

            while True:
                if not idlist:
                    break
                if nb_pairs is not None and len(pairs) >= nb_pairs:
                    break

                if len(idlist) >= 2:
                    ida,idb = idlist.pop(), idlist.pop()
                    pairs.append([self[ida], self[idb]])
                elif len(idlist) == 1:
                    if avoid_leftalones:
                        ida,idb = idlist.pop(), random.randint(0, self.length)
                        pairs.append([self[ida], self[idb]])
            return pairs
        else:
            # TODO: what does this do, already? write it down
            pairs = list(itertools.combinations(self, 2))[:nb_pairs]
            return pairs
    
    def load_from_directory(self, directory):
        """loads itself from the pictures contained in a directory"""
        from os import listdir, path
        logging.debug(f"Loading pictures from '{directory}'")
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

    #TODO class Keys
    class Keys:
        pass

    def __init__(self):
        # default params
        # self.max_rounds = None
        # self.max_choices_per_round = None
        self.directory = "."
        self.no_duplicate = None
        self.loadsave = None
        self.leftkey = "j"
        self.rightkey = "l"
        self.drawkey = "k"
        self.exitkey = "q"
        self.exitnosavekey = "z"
        self.displayscoreskey = "d"
        self.displayhelpkey = "h"
        self.fookey = "m"

    def update_from_argparse_args(self, args):
        """Updates this instance from an `arg` object returned by argparse.ArgumentParser.parse_args()"""
        d = args.__dict__
        try:
            # self.__dict__.update([x for x in args.__dict__ if args.__dict__[x] is not None])
            self.__dict__.update({k:v for k,v in zip(d.keys(), d.values()) if v is not None})
        except:
            print(tb.format_exc())
            print(len(args.__dict__), args.__dict__)
            print(len(self.__dict__), self.__dict__)

# TODO display user interface keys on the image
class Tournament:
    """Main class meant to be initialized and run in the main function"""

    def __init__(self):
        self.params = Params()
        self.pictures = PictureList()
        self.DEFAULT_SAVE_FILENAME = "quicksave.ptsave"

    def print_scores(self, sort_by_score=True, max_lines=None):
        pics = None
        if sort_by_score:
            pics = self.pictures.copy_sorted_by_score()
        else:
            pics = self.pictures.copy()
        if max_lines is not None:
            pics = pics[:max_lines]

        print("<Scores>")
        print(pics.to_text())
        print("</Scores>")

    def clean_exit(self):
        self.quicksave()
        exit(0)

    #testme
    def save_to_file(self, filename):
        self.pictures.save_to_file(filename)

    #testme
    def save_to_file(self, filename):
        self.pictures.save_to_file(filename)

    def quicksave(self):
        import time
        timestr = time.strftime("%Y-%m-%d_%H-%M-%S")
        self.save_to_file(f"{self.params.directory}_{timestr}.ptsave")

    def handle_cli_args(self):
        """parses the cli arguments and sets global program parameters accordingly"""
        parser = argparse.ArgumentParser()
        # TODO: automatize by using an argname translater like in cointoss
        # parser.add_argument("--max-rounds")
        parser.add_argument("--directory")
        parser.add_argument("--loadsave")
        args = parser.parse_args()
        self.params.update_from_argparse_args(args)



    def display_help(self):
        print("=== picture-tournament help ===")
        print("  keybindings:")
        print("  - {}: choose the image on the left".format(self.params.leftkey))
        print("  - {}: choose the image on the right".format(self.params.rightkey))
        print("  - {}: choose neither, make it a draw".format(self.params.drawkey))

    def show_duel(self, pic_list:list[Picture]):
        """Displays all images in `pic_list` i a row within the same window"""
        victory_gain = 1
        loss_gain = -1


        def resize_to_fit(img, wmax, hmax):
            # img_list_resized = [cv2.copyMakeBorder(src, top, bottom, left, right, borderType)]
            # img_list_resized = [cv2.resize(im, (int(im.shape[1] * resize_ratio), int(im.shape[0] * resize_ratio)), interpolation=cv2.INTER_CUBIC) for im in img_list]

            resize_ratio = min(wmax/img.shape[1], hmax/img.shape[0])
            # print("resize_ratio:", resize_ratio)
            # print("resized dims:", img.shape[1] * resize_ratio, img.shape[0] * resize_ratio)
            return cv2.resize(img, (int(img.shape[1] * resize_ratio), int(img.shape[0] * resize_ratio)), interpolation=cv2.INTER_CUBIC)



        # rigidly set window dimensions
        win_height = 900
        win_width = int(win_height * 16/9)
        # set up the window
        duel_text = " vs ".join(pic.name for pic in pic_list)
        window_title = f"picture-tournament - {duel_text}"
        cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_title, win_width, win_height)
        x,y,win_width,win_height = cv2.getWindowImageRect(window_title)


        img_list = [pic.image(self.params.directory) for pic in pic_list]
        filenames = [pic.filename for pic in pic_list]

        # print(filenames)
        # print(img_list)

        # assert None not in img_list
        # logging.debug(f"img_list : {img_list}")
        # logging.debug(f"len(img_list): {len(img_list)}")


        # All images must have the same height

        imgs_biggest_width = min(img.shape[1] for img in img_list)
        imgs_biggest_height = min(img.shape[0] for img in img_list)

        img_max_width = win_width // 2
        img_max_height = win_height
        resize_ratio = min(img_max_width/imgs_biggest_width, img_max_height/imgs_biggest_height)


        #TODO: ensure all images have the same height, otherwise it cannot hconcat!
        # resize all images so that they fit
        # img_list_resized = [cv2.resize(im, (imgs_biggest_width, int(im.shape[0] * imgs_biggest_width / im.shape[1])), interpolation=cv2.INTER_CUBIC) for im in img_list]
        # img_list_resized = [cv2.resize(im, (int(im.shape[1] * resize_ratio), int(im.shape[0] * resize_ratio)), interpolation=cv2.INTER_CUBIC) for im in img_list]
        img_list_resized = [resize_to_fit(img, img_max_width, img_max_height) for img in img_list]


        duel_img = cv2.hconcat(img_list_resized)


        # display constructed final picture
        cv2.imshow(window_title, duel_img)

        # handle keypresses
        while True:
            key = cv2.waitKey(0)

            # get user input, decide winner
            # TODO: adjust pictures scores
            if key == ord(self.params.leftkey):
               pic_list[0].score += victory_gain
               pic_list[1].score += loss_gain
               logging.info(f"{pic_list[0].name} chosen.")
            elif key == ord(self.params.rightkey):
               pic_list[1].score += victory_gain
               pic_list[0].score += loss_gain
               logging.info(f"{pic_list[1].name} chosen.")
            elif key == ord(self.params.drawkey):
               logging.info(f"draw.")
            elif key == ord(self.params.exitkey):
                self.clean_exit()
                break
            elif key == ord(self.params.exitnosavekey):
                exit(0)
                break
            elif key == ord(self.params.displayscoreskey):
                self.print_scores()
                break
            elif key == ord(self.params.displayhelpkey):
                self.display_help()
                break
            else:
                logging.warning(f"unknown key: {key}")
                continue
            break

        cv2.destroyAllWindows()


    #TODO: handle other methods than rounds/matches
    def run(self, nb_rounds, nb_matches=None):
        """main method, runs the tournament by asking the user to choose between two pictures.
        Args:
            - nb_rounds: number of rounds to go for
            - nb_matches: max number of matches for each round. If None, does the max amount of matches
        """


        logging.debug("<Tournament.run()>")

        if self.params.loadsave is not None:
            self.pictures.load_from_savefile(self.params.loadsave)
        else:
            self.pictures.load_from_directory(self.params.directory)

        logging.debug("Loaded {} pictures".format(self.pictures.length))

        duels_done = 0
        for round_id in range(nb_rounds):
            logging.info("ROUND {}".format(round_id))
            pairs = self.pictures.random_pairs(
                    nb_pairs=None,
                    # no_duplicate=False,
                    no_duplicate=True,
                    avoid_leftalones=True)
            if nb_matches is None:
                nb_matches = len(pairs)
            # logging.debug("result of random_pairs(): {}".format(
            #     "\n".join([str(x) for x in pairs])))
            # logging.debug("result of random_pairs(): {}".format(pairs))
            # logging.debug("/result")
            for match_id,pair in enumerate(pairs):
                total_duels = nb_matches * nb_rounds
                duels_pct = int(100 * (duels_done / total_duels))
                logging.info("[{}%] round {}/{}, match {}/{}: dueling {} vs {}".format(duels_pct, round_id, nb_rounds, match_id, nb_matches, pair[0].name, pair[1].name))
                self.show_duel(pair)
                duels_done += 1
            self.quicksave()

        logging.debug("</Tournament.run()>")

def main():
    print("== Picture Tournament begin ==")

    logging.basicConfig(level=logging.DEBUG)
    t = Tournament()
    t.handle_cli_args()
    print(t.params.directory)

    # for experimental purposes
    if t.params.directory == ".":
        t.params.directory = "images"
    print(t.params.directory)

    t.run(nb_rounds=2, nb_matches=10)
    t.print_scores()

    print("== Picture Tournament end ==")


if __name__ == "__main__":
    main()

