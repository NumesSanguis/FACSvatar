import time
import logging
import math
# import asyncio
import pandas as pd
import sys
# import copy
# import json
# from collections import defaultdict
import numpy as np

# own import; if statement for documentation
# if __name__ == '__main__':
sys.path.append("..")
from facsvatarzeromq import time_hns
# else:
#     from modules.facsvatarzeromq import time_hns


class SmoothData:
    """stores received data to smooth data

    Input: data in json format
    Output: data in json format"""

    def __init__(self):
        # store dicts from previous time steps; e.g. [0] = facs, [1] = head_pose
        self.dataframe_list = []
        self.data_list = []  # matrix with previous dict values
        # self.smooth_matrix = np.empty(0)  # matrix with previous dict values
        # self.smooth_AU = None  # AU names
        self.set_new_multiplier()

    def set_new_multiplier(self, no_of_columns=17):
        # set multiplier vector per AU
        self.multiplier = np.ones(no_of_columns)
        if no_of_columns >= 17:  # 17
            # set default blinking (AU45) multiplier; Make sure 16 is AU45; TODO less hacky
            self.multiplier[16] = 1.5
        print(self.multiplier)

    # smoothing function similar to softmax
    def softmax_smooth(self, series, steep=1):
        # series: 1 column as a pandas data series from a dataframe
        # steep: close to 0 means taking average, high steep means only looking at new data

        # sum_0_n(e^(-steepness*n) x_n) / sum_0_n(e^(-steepness*n))
        numerator = 0
        denominator = 0
        for n, x in enumerate(series):  # reversed()
            numerator += math.exp(-steep * n) * x
            denominator += math.exp(-steep * n)  # TODO calculate once
        smooth = numerator / denominator
        return smooth

    # use window of size 'window_size' data to smooth; window=1 is no smoothing
    def trailing_moving_average(self, data_dict, queue_no, window_size=3, steep=1):
        # data_dict: json formatted string containing data
        # queue_no: which data history should be used
        # trail: how many previous dicts should be remembered

        # measure time
        time_begin = time_hns()
        time_now = time_begin

        # no smoothing
        if window_size <= 1:
            return data_dict

        else:
            # convert dict to pandas dataframe
            # d_series = data_dict  # pd.read_json(data_dict, typ='series')

            # create a new queue to store a new type of data when no queue exist yet
            if len(self.dataframe_list) <= queue_no:
                # convert series to data frame
                # d_frame = d_series.to_frame()
                # use labels as column names; switch index with columns
                # d_frame = d_frame.transpose()

                logging.debug(data_dict)
                d_frame = pd.DataFrame.from_dict(data_dict, orient='index')
                d_frame = d_frame.transpose()
                # d_frame = pd.DataFrame.from_dict(list(data_dict.items()))
                logging.debug(d_frame)

                # add calculated denominator as meta-data
                # d_frame.steep = steep

                logging.debug("Add new queue")
                self.dataframe_list.append(d_frame)

                logging.debug("TIME SMOOTH: Dict to pd dataframe: {}".format((time_hns() - time_now) / 1000000))
                time_now = time_hns()

                # return data frame in json format
                return data_dict

            # use [trail] previous data dicts for moving average
            else:
                # transform dict to series
                d_series = pd.Series(data_dict)

                logging.debug("TIME SMOOTH: Dict to pd series: {}".format((time_hns() - time_now) / 1000000))
                time_now = time_hns()

                # get data frame
                d_frame = self.dataframe_list[queue_no]

                # add data series to data frame at first postion
                # d_frame = d_frame.append(d_series, ignore_index=True)  # , ignore_index=True
                d_frame.loc[-1] = d_series  # adding a row
                d_frame.index = d_frame.index + 1  # shifting index
                d_frame = d_frame.sort_index()  # sorting by index

                # drop row when row count longer than trail
                if d_frame.shape[0] > window_size:
                    # drop first row (frame)
                    # d_frame.drop(d_frame.index[0], inplace=True)
                    # drop last row (oldest frame)
                    d_frame.drop(d_frame.tail(1).index, inplace=True)

                # put our data frame back for next time
                self.dataframe_list[queue_no] = d_frame

                logging.debug("TIME SMOOTH: Insert pd series into dataframe: {}"
                              .format((time_hns() - time_now) / 1000000))
                time_now = time_hns()

                # use softmax-like function to smooth
                smooth_data = d_frame.apply(self.softmax_smooth, args=(steep,))  # axis=1,

                logging.debug("TIME SMOOTH: Smooth data: {}".format((time_hns() - time_now) / 1000000))
                time_now = time_hns()

                # apply AU multiplier
                if queue_no == 0:
                    smooth_data = smooth_data * self.multiplier

                    logging.debug("TIME SMOOTH: Multiplier: {}".format((time_hns() - time_now) / 1000000))
                    # time_now = time_hns()

                return smooth_data.to_dict()

    # def softmax_prep(self, row, steep):
    #     self.n_array = np.arange(1, row.shape[0]+1)
    #     self.steep = steep
    #     print(f"n_array: {self.n_array}")
    #     self.denominator = np.exp(-steep * self.n_array)

    def softmax_numerator(self, row, n_array, steep=1):
        # print(f"row: {row}")
        # row = row.flatten()
        # print(f"row: {row}")
        # n_iter = iter()
        # n_list = np.array(range(row.shape[0]))
        # print(f"n_list: {n_list}")
        # n_array = np.arange(1, row.shape[0] + 1)
        # print(f"n_array: {n_array}")

        # steep_array = np.full(row.shape[0], -steep)
        # steep_array = n_array * -steep
        # print(steep_array)

        # math.exp(-steep * n) * x
        # numerator += math.exp(-steep * n_list) * row
        # numerator = sum(math.exp(-steep * n_list) * row)

        # numerator = math.exp(steep_array * n_array) # * row
        numerator = np.sum(np.exp(-steep * n_array) * row)
        # print(numerator)

        return numerator

    # smoothing function similar to softmax
    def softmax_smooth2(self, arr_2d, steep):
        # matrix: numpy matrix
        # steep: close to 0 means taking average, high steep means only looking at new data

        logging.debug("SMOOTHING TIME!")

        # sum_0_n(e^(-steepness*n) x_n) / sum_0_n(e^(-steepness*n))

        time_now = time_hns()

        # print(arr_2d.shape)
        n_array = np.arange(1, arr_2d.shape[0] + 1)
        numerator = np.apply_along_axis(self.softmax_numerator, 0, arr_2d, n_array, steep)
        # print(numerator)
        denominator = np.sum(np.exp(-steep * n_array))

        # smooth_array = np.divide(numerator, denominator)
        smooth_array = numerator / denominator

        logging.debug("\t\tTIME SMOOTH: smooth 2d array: {}".format((time_hns() - time_now) / 1000000))

        # # sum_0_n(e^(-steepness*n) x_n) / sum_0_n(e^(-steepness*n))
        # numerator = 0
        # denominator = 0
        # for n, x in enumerate(series):  # reversed()
        #     numerator += math.exp(-steep * n) * x
        #     denominator += math.exp(-steep * n)  # TODO calculate once
        #
        # # print(f"numerator: {numerator}")
        # # print(f"denominator: {denominator}")
        # smooth = numerator / denominator
        # # print(f"smooth: {smooth}\n")

        return smooth_array

    # use window of size 'window_size' data to smooth; window=1 is no smoothing; no pandas speed up
    def trailing_moving_average2(self, data_dict, queue_no, window_size=3, steep=1):
        # data_dict: json formatted string containing data
        # queue_no: which data history should be used
        # trail: how many previous dicts should be remembered

        # measure time
        time_begin = time_hns()
        time_now = time_begin

        # no smoothing
        if window_size <= 1:
            return data_dict

        else:
            logging.debug("Window size bigger than 1")
            # print(data_dict)
            logging.debug(f"len data_dict:{len(data_dict)}")
            array = np.fromiter(data_dict.values(), dtype=float, count=len(data_dict))  # , count=len(data_dict)
            # print(array)
            array = np.reshape(array, (-1, len(array)))

            logging.debug("\t\tTIME SMOOTH: dict to array: {}".format((time_hns() - time_now) / 1000000))
            time_now = time_hns()

            print(array)

            # create a new queue to store a new type of data when no queue exist yet
            if len(self.data_list) <= queue_no:
                logging.debug("smooth 2d array")
                # if not smooth_matrix.any():
                #     self.smooth_matrix = array

                # self.data_list.append(np.asmatrix(array))
                # array_2d = np.reshape(array, (-1, len(array)))
                self.data_list.append(array)
                # smooth_2d_array = array

                # TODO call calculate denominator

                # change AU intensity with GUI multiplier
                if queue_no == 0:
                    array = array * self.multiplier

                # values back into dict
                data_dict = dict(zip(data_dict.keys(), array.flatten()))
                return data_dict

            # not reached window_size yet
            else:
                logging.debug("queue exists")
                smooth_2d_array = self.data_list[queue_no]
                logging.debug("smooth_2d_array shape: {}".format(smooth_2d_array.shape))

                # matrix not yet window size
                if self.data_list[queue_no].shape[0] <= window_size:
                    # add new array on top
                    smooth_2d_array = np.concatenate((array, smooth_2d_array), axis=0)
                else:
                    # slower; drop last row and put new array above
                    # smooth_2d_array = np.concatenate((array, smooth_2d_array[:-1, :]), axis=0)

                    # faster; replace oldest (lowest) array and shift new below row to top
                    smooth_2d_array[-1] = array
                    smooth_2d_array = np.roll(smooth_2d_array, 1, axis=0)

                logging.debug("stacked")
                logging.debug(smooth_2d_array)
                logging.debug("\n\n\n")

                # store for next message
                self.data_list[queue_no] = smooth_2d_array

                logging.debug("\t\tTIME SMOOTH: stack array: {}".format((time_hns() - time_now) / 1000000))
                time_now = time_hns()

            logging.debug("Smooth matrix")

            # matrix to smoothed array
            # TODO function
            data_smoothed = self.softmax_smooth2(smooth_2d_array, steep)

            # change AU intensity with GUI multiplier
            if queue_no == 0:
                data_smoothed = data_smoothed * self.multiplier

            # values back into dict
            data_dict = dict(zip(data_dict.keys(), data_smoothed))

            logging.debug("\t\tTIME SMOOTH: array to dict: {}\n\n".format((time_hns() - time_now) / 1000000))
            # time_now = time.time_ns()

            return data_dict

            # first message
            # if not self.smooth_AU:
            #     print("\nNot smooth AU")
            #     # arrays = {'names': np.array(list(data_dict.keys()), dtype=str),
            #     #           'values': np.array(list(data_dict.values()), dtype=float)}
            #     # array = np.array(list(data_dict.values()), dtype=float)
            #
            #     self.smooth_AU = np.fromiter(data_dict.items(), dtype='S4')
            #     print(self.smooth_matrix)
            #
            #     print(f"\t\tTIME SMOOTH: Dict to array: {(time.time_ns() - time_now) / 1000000}\n\n")
                # time_now = time.time_ns()

            # sys.exit("smooth matrix: {}".format(self.smooth_matrix))

            # # create a new queue to store a new type of data when no queue exist yet
            # elif len(self.dataframe_list) <= queue_no:
            #     # convert series to data frame
            #     # d_frame = d_series.to_frame()
            #     # use labels as column names; switch index with columns
            #     # d_frame = d_frame.transpose()
            #
            #     print(data_dict)
            #     d_frame = pd.DataFrame.from_dict(data_dict, orient='index')
            #     d_frame = d_frame.transpose()
            #     # d_frame = pd.DataFrame.from_dict(list(data_dict.items()))
            #     print(d_frame)
            #
            #     # add calculated denominator as meta-data
            #     # d_frame.steep = steep
            #
            #     print("Add new queue")
            #     self.dataframe_list.append(d_frame)
            #
            #     print(f"TIME SMOOTH: Dict to pd dataframe: {(time.time_ns() - time_now) / 1000000}")
            #     time_now = time.time_ns()
            #
            #     # return data frame in json format
            #     return data_dict
            #
            # # use [trail] previous data dicts for moving average
            # else:
            #     # transform dict to series
            #     d_series = pd.Series(data_dict)
            #
            #     print(f"TIME SMOOTH: Dict to pd series: {(time.time_ns() - time_now) / 1000000}")
            #     time_now = time.time_ns()
            #
            #     # get data frame
            #     d_frame = self.dataframe_list[queue_no]
            #
            #     # add data series to data frame at first postion
            #     # d_frame = d_frame.append(d_series, ignore_index=True)  # , ignore_index=True
            #     d_frame.loc[-1] = d_series  # adding a row
            #     d_frame.index = d_frame.index + 1  # shifting index
            #     d_frame = d_frame.sort_index()  # sorting by index
            #
            #     # drop row when row count longer than trail
            #     if d_frame.shape[0] > window_size:
            #         # drop first row (frame)
            #         # d_frame.drop(d_frame.index[0], inplace=True)
            #         # drop last row (oldest frame)
            #         d_frame.drop(d_frame.tail(1).index, inplace=True)
            #
            #     # put our data frame back for next time
            #     self.dataframe_list[queue_no] = d_frame
            #
            #     print(f"TIME SMOOTH: Insert pd series into dataframe: {(time.time_ns() - time_now) / 1000000}")
            #     time_now = time.time_ns()
            #
            #     # use softmax-like function to smooth
            #     smooth_data = d_frame.apply(self.softmax_smooth, args=(steep,))  # axis=1,
            #
            #     print(f"TIME SMOOTH: Smooth data: {(time.time_ns() - time_now) / 1000000}")
            #     time_now = time.time_ns()
            #
            #     # apply AU multiplier
            #     if queue_no == 0:
            #         # print("\n\n")
            #         # print(type(smooth_data))
            #         # print(smooth_data)
            #         smooth_data = smooth_data * self.multiplier
            #         # print()
            #         # print(smooth_data)
            #         # sys.exit()
            #
            #         print(f"TIME SMOOTH: Multiplier: {(time.time_ns() - time_now) / 1000000}")
            #         # time_now = time.time_ns()
            #
            #     return smooth_data.to_dict()


if __name__ == '__main__':
    print("Don't run this module standalone")
