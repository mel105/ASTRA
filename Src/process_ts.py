#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 19:44:07 2023

@author: mel
"""

import sys
import Src.pwvPlot as pt
import Src.outliersEstimation as oe
import Src.support as sp

# import os
# from datetime import datetime
import pandas as pd
import math
import plotly.io as pio
import plotly.graph_objects as go
import os

from Src.changePointDetection import changePointDetection
from Src.medianYear import medianYear
# import Src.changePointDetection as chp
pio.renderers.default = 'browser'


class process_ts:

    """
    The class should use config settings and process the time series in context of change point detection and
    time series homogenization. There is an assumption that we have available as analysed series as well as
    reference time series.
    """

    def __init__(self, conf, file_idx):
        """
        Constructor

        Parameters
        ----------
        conf : TYPE config object
            DESCRIPTION. config file
        file_idx : TYPE int
            DESCRIPTION. Index of processed station

        Returns
        -------
        None.

        """

        # input
        self._station = conf.get_inp_file_name()[file_idx]
        self._inp_local_path = conf.get_inp_local_path()

        # output
        self._out_file = conf.get_out_file_name()  # !!
        self._out_local_path = conf.get_out_local_path()

        # general setting
        self._beg = conf.get_beg()
        self._end = conf.get_end()
        self._beg_reset = conf.get_beg()
        self._end_reset = conf.get_end()
        self._preprocess = conf.get_preprocess()

        # conditions
        self._cnd_actual_data = conf.get_cnd_actual_data()
        self._cnd_orig_idx = conf.get_cnd_orig_idx()

        # because i need the config to change point method, then
        self._conf = conf

        # data reading
        print("\n### Data reading ###\n")
        self._dataReading()

        # filling the missing data
        print("\n### Filling the missing data in anlysed series ###\n")
        self._gapsElimination()

        # removing the seasonality
        print("\n### Removing the seasonality ###\n")
        self._removeSeasonality()

        # change point detection
        print("\n### Change point detection ###\n")
        self._detectChangePoints()

        # tech support
        print("\n### Homogenization ###\n")
        self._homogenizationPlot()

        # outliers detection
        print("\n### Outliers Detection ###\n")
        self._outliers()

        # save the reasults
        print("\n### Protocols ###\n")
        self._protocols()

    # public get/set functions
    def get_orig_fig(self):
        return self._fig

    def get_chp_fig(self):
        return self._fig_chp

    def get_chp_full(self):
        return self._fig_full

    def get_adj_fig(self):
        return self._fig_adj

    def get_out_fig(self):
        return self._fig_out

    def get_homo_fig(self):
        return self._fig_repl

    def get_chp(self):
        return self._listOfEpo

    # protected functions

    def _gapsElimination(self):
        """
        The main goal of the function is to identify and eliminate the missing values in the analysed time
        series.
        """

        return 0

    def _detectChangePoints(self):
        """
        Functions prepare the series and run the methods for change point detection

        Returns
        -------
        None.

        """

        # is reconstruction required? That is mean, that differenced series (vals) is homogenized and then the
        # reference series is used to reconstruction
        self._reco = False

        # copy of time series that will be homogenized
        if self._preprocess == 0:

            self._homo = self._data[["Analysed"]].copy()
        else:

            self._homo = self._data[["vals"]].copy()
            self._reco = True

        # change point detection
        chp = changePointDetection(self._conf, self._data)

        # results
        _point, _index, _shift = chp.get_chp()

        # plot
        self._fig_chp = chp.get_chp_plot()
        # self._fig_chp.show()

        # MULTICHANGE POINT DETECTION
        # Spliting the original series into sub-series in case that the chp was detected
        self._listOfEpo = []
        listOfChp = []
        listOfShifts = []
        subseries = []

        if chp.get_chp_result():

            # Homogenization
            self._homo[_index:] = self._homo[_index:]-_shift

            subseries = self._update(self._data, _index, subseries)

            # fill list of change points
            listOfChp.append(_index)
            listOfShifts.append(_shift)
            self._listOfEpo.append(_point)

            # loop over the sub-series
            tst = True
            idx = 0
            while (tst):

                actual_data = pd.DataFrame(subseries[idx])

                if len(actual_data) < self._cnd_actual_data:
                    break
                else:

                    chp = changePointDetection(self._conf, actual_data)

                    if chp.get_chp_result():

                        # Removing the sub-series in case that was already processed
                        subseries.pop(idx)
                        _pt, _idx, _sft = chp.get_chp()

                        if math.isnan(_sft):
                            _sft = 0

                        # plot
                        # fig_chp = chp.get_chp_plot()
                        # fig_chp.show()

                        # find _pt in original series and get index
                        b = self._data[self._data.DATE == _pt]
                        orig_idx = b.index[0]

                        # update list of change point
                        ignore = []
                        for i in listOfChp:

                            if any([orig_idx > i-self._cnd_orig_idx and orig_idx < i+self._cnd_orig_idx]):

                                ignore.append(1)
                            else:

                                ignore.append(0)

                        print(orig_idx)
                        print(ignore)
                        print(listOfChp)
                        cnd = 1

                        if cnd in ignore:

                            # ignore orig_val
                            print()
                        else:

                            listOfChp.append(orig_idx)
                            listOfShifts.append(_sft)
                            self._listOfEpo.append(_pt)

                            # homogenization. MELTODO wrong code. Idx of change point is calculated only in
                            # subseries time interval. Thus, we need to parse this index to the original
                            # series.
                            self._homo[orig_idx:] = self._homo[orig_idx:]-_sft

                        # update
                        subseries = self._update(actual_data, _idx, subseries)
                        idx = 0
                    else:

                        subseries.pop(idx)

                    if len(subseries) == 0:

                        tst = False
                    else:

                        print(" ")

            # plot the figure of detected change point(s)
            fo_full = pt.detections(self._data, listOfChp)

            # fo_full.show()
            self._fig_full = fo_full

        else:

            print("No change point was detected!")
            self._fig_full = go.Figure()

        return 0

    def _update(self, data, idx, subs):
        """
        Function returns actual list of subseries intervals

        Returns
        -------
        None.

        """

        subs_orig = subs.copy()

        listOfSubseries = []

        subdata_1 = data.iloc[:idx]
        subdata_2 = data.iloc[idx:]

        listOfSubseries = [subdata_1, subdata_2]

        # save subseries into the container
        if (len(subs_orig) == 0):
            return listOfSubseries
        else:
            return subs_orig+listOfSubseries

    def _findPosition(self, str, list):
        """
        Function returns the index of position
        """
        return [idx for idx, s in enumerate(list) if str in s][0]

    def _dataDecoding(self, source="ANL"):
        """
        Function returns the decoded data based on inputs. Data is reference and/or analysed.
        """

        if source == "ANL":
            type_of_data = "Analysed"
        else:
            type_of_data = "Reference"

        # SETTING THE FULL PATH TO THE DATA
        # list of files in ANL folder

        anl_files = os.listdir(self._inp_local_path+"/"+source+"/")

        if any(self._station in s for s in anl_files):

            # ok, the ANL folder contains the file with required station's ID
            # now, find the file's position of required station
            pos = self._findPosition(self._station, anl_files)

            # full path of required file
            anl_file = self._inp_local_path+"/"+source+"/"+anl_files[pos]

            # finally find the file extension to decide, which type of decoder we will use
            anl_file_name, anl_file_extension = os.path.splitext(anl_file)
        else:
            print("For required station {0} we do not have any file at {1} adress".format(
                self._station, self._inp_local_path+"/"+source+"/"))

        # ANL data reading
        if anl_file_extension == ".txt":

            # continue to decode TXT file format
            print("Not yet implemented\n")
        elif anl_file_extension == ".npz":

            # continue to decode NPZ file format
            print("Not yet implemented\n")
        elif anl_file_extension == ".csv":

            # continue to decode the CSV file format
            dec = self._read_csv_file(anl_file, type_of_data)
        elif anl_file_extension == ".xlsx":

            # continue to decode the Excel file format
            dec = self._read_xlsx_file(anl_file, type_of_data)
        else:

            print("Program is not able to open and read the required file format!")

        return dec

    def _dataReading(self):
        """
        Function prepares the data for change point detection and its elimination. In next steps:
            1) reading the analysed series
            2) reading the reference data

        """

        anl = self._dataDecoding()

        # PART OF PROGRAM WHERE THE PROCESS IS SPLITED ACCORDING TO THE POSSIBILITY, HOW TO REMOVE THE
        # SEASONAL SIGNAL.
        if self._preprocess == 0:
            # in this process we assume, that the seasonal signal is not removed from the  analysed time
            # series
            print(" -- Seasonal signal is not removed from the analysed time series")
            self._anl = anl.copy()

        elif self._preprocess == 1:
            # in this step we assume that the seasonal signal is removed using the median time series
            print(" -- Seasonal signal is removed using the Median Year time series")

            # at this point, we do not have any reference series. One possible option how to remove seasonal
            # signal and do not affect the potential change points is to eliminat seasonality using the
            # so-called Median year time series.

            my = medianYear(self._conf, anl)
            ref = my.get_median_year()
            ref = ref.rename(columns={"Analysed": "Reference"})
            # fo = my.get_plot()
            # fo.show()

            self._anl = anl.copy()
            self._ref = ref.copy()

            print()
        elif self._preprocess == 2:
            # in this step we assume that the signal is removed by the reference time series.
            print(" -- Seasonal signal is removed using the reference time series")

            ref = self._dataDecoding("REF")

            self._anl = anl.copy()
            self._ref = ref.copy()

        else:
            print(" -- Required process is not defined!")
            sys.exit()

        return 0

    def _removeSeasonality(self):
        """
        The funcion returns the difference of analysed series and reference one. This step means, that the
        seasonality is removed from original analysed series. At this place, the program should know, if the
        reference series is known, or the median series will be used for the seasonality removing or we do not
        touch at the analysed series.

        Returns
        -------
        int
            DESCRIPTION.

        """

        if self._preprocess == 0:
            # in this process we assume, that the seasonal signal is not removed from the  analysed time
            # series

            self._data = self._anl.copy()
            self._data["vals"] = self._data.Analysed.copy()

            # create the plot that compares intakes (GNSSS end ERA5 pwv's time series)
            fo = pt.linePlot(self._data.DATE, self._data.Analysed)

            self._fig = fo

        else:
            # in this step we assume that the seasonal signal is removed using the median time series or
            # reference time series. Both type of series are saved in self._ref object. Thus, we will use only
            # one merge process

            anl = self._anl.copy()
            ref = self._ref.copy()

            # the median is removed from the both types of series
            anl.Analysed = anl.Analysed - anl.Analysed.median()
            ref.Reference = ref.Reference - ref.Reference.median()

            # for purpose of data merging, set index as a key.
            mAnl = anl.set_index("DATE")
            mRef = ref.set_index("DATE")

            mergedSeries = pd.merge(mAnl, mRef, how='inner', left_index=True, right_index=True)
            mergedSeries = mergedSeries.reset_index()

            # drop nonusefull columns, if exists
            mergedSeries = mergedSeries.rename(columns={"DATE_x": "DATE"})
            mergedSeries = mergedSeries.drop(["index", "DATE_y"], axis=1, errors="ignore")

            # mergedSeries.columns = ["DATE", "Analysed", "Reference"]
            mergedSeries["vals"] = mergedSeries["Analysed"] - mergedSeries["Reference"]

            self._data = mergedSeries.copy()

            # create the plot that compares intakes (GNSSS end ERA5 pwv's time series)
            fo = pt.intakes(mergedSeries)

            self._fig = fo
            # fo.show()

        return 0

    def _homogenizationPlot(self):

        self._data["HOM"] = self._homo

        fig_adj = pt.linePlot(self._data.DATE.to_numpy(), self._data.HOM.to_numpy(), "Adjusted Time Series")

        self._fig_adj = fig_adj

    def _outliers(self):

        # outliers identification
        med, _, lowidx, uppidx = oe.outliers(self._data.HOM.to_numpy())

        # outliers presentation
        fo = oe.outliersPlot(self._data.DATE.to_numpy(), self._data.HOM.to_numpy(), lowidx, uppidx)
        self._fig_out = fo

        # replace the outlier values by the median ones
        self._data.loc[lowidx, "HOM"] = med
        self._data.loc[uppidx, "HOM"] = med

        # reconstrunction if is required. That means, that cleaned and homogenized time series is returned
        # to the almost original values.
        if self._reco:
            self._data.HOM = self._data.Reference + self._data.HOM

        # final data presentation
        fo2 = pt.linePlot(self._data.DATE.to_numpy(), self._data.HOM.to_numpy(),
                          "Final Time series (homogenized and cleaned of outliers)")

        self._fig_repl = fo2

        return 0

    def _protocols(self):
        """
        Function covers the protocols generating and saving results into the required formats

        Returns
        -------
        None.

        """

        out_path = self._conf.get_out_local_path()+"/"+self._station
        sp.check_folder(out_path)

        # save the full results into the csv format
        self._data.to_csv(out_path+"/change_point_full.csv", index=False)

        # MELTODO in next future
        # ######################

        # create the protocol that covers only change point informations (loop, intervals, sizes, etc)
        # change_points_info.txt

        # create the protocol that covers list of change points (dates/index/shifts)
        # change_points_list.txt

        # create the protocol that covers list of change points evaulated with log information, if log exists
        # change_points_eval.txt

        # create the protocol that covers statistics of analysed time series before and after the
        # homogenization and/or info about the outliers detection
        # change_point_stat.txt

        # list of time where the change points were detected and their original values.
        # change_point_outliers.csv

        # save the log file (covers the full process of homogenization, what is processed, errors, time of
        # processing etc)
        # change_point_log.txt

        return 0

    def _read_xlsx_file(self, full_file_path, type_of_data="Analysed"):
        """
        The function reads the Excel file and returns the required data formated in dataframe object.
        """

        df = pd.read_excel(full_file_path)

        df.rename(columns={df.columns[1]: type_of_data}, inplace=True)

        return df

    def _read_csv_file(self, full_file_path, type_of_data="Analysed"):
        """
        The function reads the CSV file and returns the required data formated in dataframe object.
        """

        df = pd.read_csv(full_file_path)

        df.rename(columns={df.columns[1]: type_of_data}, inplace=True)

        return df
