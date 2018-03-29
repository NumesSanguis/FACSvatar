from pathlib import Path
import pandas as pd


# clean csv output of OpenFace, remove irrelevant columns
class FilterCSV:
    def __init__(self, csv_file):  # , dir_processed, col_keep, dir_timestamp
        # dir_processed: where to find .csv files
        # col_keep: columns to keep in .csv file [AU*_r, pose, gaze

        self.df_au = None
        # Action Units and head rotation
        self.col_keep = ['AU.*_r', 'pose_R.*']  # , 'gaze_angle*'

        # skip cleaning and load clean as dataframe
        if Path(csv_file[:-4] + "_clean.csv").exists():
            print("OpenFace .csv already cleaned")
            self.df_au = pd.read_csv(csv_file[:-4] + "_clean.csv")

        # load csv as dataframe and clean
        else:
            print("Cleaning OpenFace .csv")
            self.clean_controller(csv_file)

    # removes space in header, e.g. ' confidence' --> 'confidence'
    def clean_header_space(self):
        self.df_au.columns = self.df_au.columns.str.strip()

    # remove rows where success == 0 and confidence < 0.8
    def clean_unsuccessful(self):
        self.df_au.drop(self.df_au[(self.df_au.success == 0) | (self.df_au.confidence < 0.8)].index,
                        inplace=True)

    # remove unnecessary columns
    def clean_columns(self):
        if len(self.col_keep) >= 1:
            # doesn't include AU28_c (lip suck), which has no AU28_r
            reg = "(frame)|(timestamp)|(confidence)|{}" \
                .format("|".join("({})".format(c) for c in self.col_keep))
        else:
            reg = "(frame)|(timestamp)|(confidence)"
        # print("regex col filter: {}".format(reg))
        self.df_au = self.df_au.filter(regex=reg)

    def match_index_frame(self):
        self.df_au['frame'] -= 1

    # get AU values and set interval from 0-5 to 0-1
    def reset_au_interval(self):
        c = self.df_au.columns.str.contains("AU.*_r")
        self.df_au.loc[:, c] /= 5

    # save cleaned dataframe as csv
    def csv_save(self, csv_file):
        #dir_output = self.dir_processed + '_clean'
        # create dir preprocessed if not existing, Python 3.2+
        #os.makedirs(dir_output, exist_ok=True)

        # df.loc[:, df.columns.str.contains('a')]
        self.df_au.to_csv(csv_file[:-4] + "_clean.csv", index=False)  # , columns=[]

    # calls all cleaning + save functions
    def clean_controller(self, csv_file):
        self.df_au = pd.read_csv(csv_file)

        # removes space in header, e.g. ' confidence' --> 'confidence'
        self.clean_header_space()

        # remove rows with bad AU tracking TODO do something with failed tracking
        #self.clean_unsuccessful()

        # remove non-speech rows based on timestamps provided with dataset
        # self.clean_nonspeech(file)

        # dataframe with only c_keep columns
        self.clean_columns()

        # Set frame -1 to match index
        self.match_index_frame()

        # divide AU*_r by 5 (range from 0-1 instead of 0-5)
        self.reset_au_interval()

        # save cleaned dataframe
        self.csv_save(csv_file)
