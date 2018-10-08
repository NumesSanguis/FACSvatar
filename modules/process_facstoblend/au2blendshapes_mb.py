import os
from os.path import join
import sys
import json
from collections import defaultdict


# change AU values from OpenFace to Blend Shape (Shape Key) values understood by Unity / Blender / Unreal
# for characters created in Blender + Manual Bastioni addon
class AUtoBlendShapes:
    def __init__(self, au_folder="AU_json"):
        # call function for dictionary of values for changing AU to blendshapes
        self.au_dict = self.load_json(au_folder)
        print(self.au_dict)

        # frame tracker for index in dataframe
        self.frame_tracker = 0

        # AU to blendshapes
        self.blendshape_dict_new = json.load(open(join('blendshapes_MB.json'), 'r'))

    # open all AU .json file in directory
    def load_json(self, json_dir):
        au_dict = {}
        for au_filename in os.listdir(json_dir):
            au_filepath = join(json_dir, au_filename)
            e_item, extension = os.path.splitext(au_filename)
            if "json" in extension:
                #self.expressions_labels.add(e_item)
                # add "_min" or "_max" to blenshape + double value (because it uses 0.5 as cutoff)
                au_dict[e_item] = self.json_blendshape_matcher(self.load_au(au_filepath))
        return au_dict

    # extract "structural" data for how to change blend shapes per AU
    def load_au(self, filepath):
        try:
            json_file = json.load(open(filepath, 'r'))
        except:
            sys.exit(f"json file corrupted: {filepath}")

        #if "structural" in json_file:
        return json_file["structural"]

    # json dict of blendshape names
    def load_blendshape_dict(self):
        # load json as dict
        # if not self.blendshape_dict:
        #     self.blendshape_dict_new = json.load(open(join('blendshapes.json'), 'r'))

        # reset dict to default 0; make thread safe (untested) deep copy
        self.blendshape_dict = json.loads(json.dumps(self.blendshape_dict_new))

    # add "_min" or "_max" to blendshape + value conversion (because it uses 0.5 as cutoff for min/max)
    # based on Manuel Bastioni v1.6.0
    def json_blendshape_matcher(self, json_MB):
        # json_MB: JSON based on Manuel Bastioni used in Blender

        # create new dict
        dict_blendshape = {}

        # add values to new dict; based on manuelbastioni/animationengine.py
        for name, value in json_MB.items():
            if value < 0.5:
                name = name + "_min"
                value = (0.5 - value) * 2
            else:
                name = name + "_max"
                value = (value - 0.5) * 2

            # make dict less ugly
            dict_blendshape[name] = round(value, 5)

        return dict_blendshape

    # https://stackoverflow.com/a/35689816/3399066
    # sum 2 dicts
    # def npe_method(self, tests):
    #     ret = defaultdict(int)
    #     for d in tests:
    #         for k, v in d.items():
    #             ret[k] += v
    #     return dict(ret)

    # receive AU values and change to blendshapes
    def calc_blendshapes(self, facs_dict):
        # get a clean blendshape dict
        self.load_blendshape_dict()

        # loop over AU values from OpenFace data frame
        for au, au_v in facs_dict.items():
            # only loop over AU values
            if au.startswith('AU'):
                # check if we have AU convert file
                if au in self.au_dict:
                    # don't waste computing power when nothing changes
                    # TODO make if statement about difference previous AU
                    if au_v > 0.001:
                        # remove '_r'
                        #au = au[:-2]
                        #print(au, au_v)

                        # loop over all blendshapes related to that AU
                        #print(self.au_dict[au])
                        # TODO error: KeyError: 'AU'
                        for exp, exp_v in self.au_dict[au].items():
                            #print(exp, exp_v)
                            # multiply AU value with au_dict to get blendshape values and
                            # add blendshape values to total blendshape_dict
                            self.blendshape_dict[exp] += round(exp_v * au_v, 5)
                            #print(self.blendshape_dict[exp])

                else:
                    print("No json file found for {}".format(au))

        # TODO resolve _min _max (only 1 can have value, so subtract from each other)

        # TODO limit blendshape value to max 1
        #min(current_val + sk_value, 1.0)

        # TODO? return None for non-changed values

    # iterate over AU data extracted by OpenFace
    def output_blendshapes(self, facs_dict):
        print("Frame: {}".format(self.frame_tracker))
        self.calc_blendshapes(facs_dict)  # next(self.df_au.itertuples())
        self.frame_tracker += 1

        return self.blendshape_dict  # self.blend_val