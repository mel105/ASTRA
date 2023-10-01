#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 19:44:07 2023

@author: mel
"""

# import os
import sys
import statistics as stat
# import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
# import os
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from Src.changePointDetection import changePointDetection
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

        # because i need the config to change point method, then
        self._conf = conf

        # data reading
        self._dataReading()

        # change point detection
        self._detectChangePoints()

        # tech support
        self._homogenizationPlot()

        self._outliers()
        self._outliersPlot()
        self._outlierReplacement()

    # public get/set functions
    def get_orig_fig(self):
        return self._fig

    def get_chp_fig(self):
        return self._fig_chp

    def get_adj_fig(self):
        return self._fig_adj

    def get_out_fig(self):
        return self._fig_out

    def get_homo_fig(self):
        return self._fig_repl

    # protected functions

    def _detectChangePoints(self):
        """
        Functions prepare the series and run the methods for change point detection

        Returns
        -------
        None.

        """

        # copy of time series that will be homogenized
        self._homo = self._data[["pwv GNSS"]].copy()

        # change point detection
        chp = changePointDetection(self._conf, self._data)

        # results
        _point, _index, _shift = chp.get_chp()

        # plot
        self._fig_chp = chp.get_chp_plot()

        # MULTICHANGE POINT DETECTION
        # Spliting the original series into sub-series in case that the chp was detected
        # listOfChp = []
        subseries = []

        if chp.get_chp_result():

            # Homogenization
            self._homo[_index:] = self._homo[_index:]+_shift

            subseries = self._update(self._data, _index, subseries)

            # pokial kontainer subseries nie je prazdny, tak iterurej
            tst = True
            idx = 0
            while (tst):

                # MELTODO: POZOR NA CONF. Potrebuje ho len kvoli beg, end. Ale ak zmenim rozsah casovej rady
                # tak mi tento konf je k nicomu.
                actual_data = pd.DataFrame(subseries[idx])
                chp = changePointDetection(self._conf, actual_data)

                if chp.get_chp_result():
                    # odtranenie tej subserie, ktora uz bola spracovana
                    subseries.pop(idx)
                    _, _idx, _sft = chp.get_chp()

                    # homogenization. MELTODO Tu je to spatne. To z dovodu, ze idx  spocitam len v
                    # subintervale musim mu nejak priradit idx original.
                    self._homo[_idx:] = self._homo[_idx:]+_sft

                    # update
                    subseries = self._update(actual_data, _idx, subseries)
                    idx = 0
                else:
                    subseries.pop(idx)

                if len(subseries) == 0:
                    tst = False
                else:
                    print("Iteration")
        else:
            print("No change point was detected!")

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
        # for key, val in enumerate(listOfSubseries):
        #    subs[key] = val

        if (len(subs_orig) == 0):
            return listOfSubseries
        else:
            return subs_orig+listOfSubseries

    def _dataReading(self):
        """
        Function prepares the data for LOKI application. In next stpers: 1) reading the GNSS and ERA5 data,
        2) creatinf the difference time series, 3) prepare the txt file in format: yyyy-mm-dd hh-mm-ss dpwv
        4) prepare the plot of differences


        Returns
        -------
        int
            DESCRIPTION.

        """

        # analysed time series
        self._read_npz_file()
        # for purpose of chp detection, just create the copy of gnss df
        self._anl = self._gnss[["epochs", "pwv"]].copy()
        # for purpose of data merging
        self._gnss = self._gnss.set_index("epochs")

        if self._anl.empty:
            print("No analysed data!")
        else:
            print("Analysed data reading: OK")

        # reference time series
        self._read_txt_file()
        # for purpose as in gnss case
        self._ref = self._era5[["epochs", "pwv"]].copy()
        # for purpose of data merging
        self._era5 = self._era5.set_index("epochs")

        if self._ref.empty:
            print("No reference data!")
        else:
            print("Reference data reading: OK")

        # time series difference
        mergedSeries = pd.merge(self._gnss, self._era5, how='inner', left_index=True, right_index=True)
        mergedSeries = mergedSeries.reset_index()
        mergedSeries.columns = ["epochs", "pwv GNSS", "sigma GNSS", "pwv ERA5"]
        mergedSeries["dpwv"] = mergedSeries["pwv GNSS"] - mergedSeries["pwv ERA5"]
        self._data = mergedSeries.copy()

        # fig creation
        fig = make_subplots(rows=2, cols=1)
        fig.add_trace(go.Scatter(x=mergedSeries.epochs,
                      y=mergedSeries["pwv GNSS"], mode="lines"), row=1, col=1)
        fig.add_trace(go.Scatter(x=mergedSeries.epochs,
                      y=mergedSeries["pwv ERA5"], mode="lines"), row=1, col=1)
        fig.add_trace(go.Scatter(x=mergedSeries.epochs, y=mergedSeries.dpwv, mode="lines"), row=2, col=1)
        fig.update_layout(
            title="Input time series comparision",
            autosize=False,
            width=800,
            height=400,
            yaxis=dict(
                autorange=True,
                showgrid=True,
                zeroline=True,
                dtick=250,
                gridcolor="rgb(255, 255, 255)",
                gridwidth=1,
                zerolinecolor="rgb(255, 255, 255)",
                zerolinewidth=2,
            ),
            margin=dict(l=40, r=30, b=80, t=100,),
            paper_bgcolor="rgb(243, 243, 243)",
            plot_bgcolor="rgb(243, 243, 243)",
            showlegend=False,
        )
        fig.update_xaxes(title_text=" ", row=1, col=1)
        fig.update_xaxes(title_text="Time [#6 hours]", row=2, col=1)
        fig.update_yaxes(title_text="PWV [mm]", row=1, col=1)
        fig.update_yaxes(title_text="DIFF PWV [mm]", row=2, col=1)

        # fig.show()

        self._fig = fig

        return 0

    def _homogenizationPlot(self):

        self._data["HOM"] = self._homo

        # adjusted series
        fig_adj = go.Figure()
        fig_adj.add_trace(go.Scatter(x=self._data["epochs"], y=self._data.HOM, mode="lines"))
        fig_adj.update_layout(
            title="Adjusted time series",
            autosize=False,
            width=800,
            height=400,
            yaxis=dict(
                autorange=True,
                showgrid=True,
                zeroline=True,
                dtick=250,
                gridcolor="rgb(255, 255, 255)",
                gridwidth=1,
                zerolinecolor="rgb(255, 255, 255)",
                zerolinewidth=2,
            ),
            margin=dict(l=40, r=30, b=80, t=100,),
            paper_bgcolor="rgb(243, 243, 243)",
            plot_bgcolor="rgb(243, 243, 243)",
            showlegend=False,
        )

        fig_adj.show()
        self._fig_adj = fig_adj

    def _outliers(self):

        # Outliers replacing by median
        self._med1 = stat.median(self._data.HOM)

        self._data["RED"] = abs(self._data.HOM-self._med1)

        MAD = stat.median(self._data.RED)

        # Tukey's fence
        low = self._med1 - 4.45*MAD
        upp = self._med1 + 4.45*MAD

        # outlier indexes
        self._lowidx = self._data.HOM.lt(low)
        self._uppidx = self._data.HOM.gt(upp)

    def _outliersPlot(self):

        fig_out = go.Figure()
        fig_out.add_trace(go.Scatter(x=self._data.epochs, y=self._data.HOM, mode="lines"))
        fig_out.add_trace(go.Scatter(x=self._data.epochs[self._lowidx],
                                     y=self._data.HOM[self._lowidx], mode="lines"))
        fig_out.add_trace(go.Scatter(x=self._data.epochs[self._uppidx],
                                     y=self._data.HOM[self._uppidx], mode="markers"))
        fig_out.update_layout(
            title="Presentation the outliers in analysed time series",
            autosize=False,
            width=800,
            height=400,
            yaxis=dict(
                autorange=True,
                showgrid=True,
                zeroline=True,
                dtick=250,
                gridcolor="rgb(255, 255, 255)",
                gridwidth=1,
                zerolinecolor="rgb(255, 255, 255)",
                zerolinewidth=2,
            ),
            margin=dict(l=40, r=30, b=80, t=100,),
            paper_bgcolor="rgb(243, 243, 243)",
            plot_bgcolor="rgb(243, 243, 243)",
            showlegend=False,
        )
        fig_out.show()
        self._fig_out = fig_out

    def _outlierReplacement(self):

        # replace the outlier values by the median ones
        self._data.loc[self._lowidx, "HOM"] = self._med1
        self._data.loc[self._uppidx, "HOM"] = self._med1

        fig_repl = go.Figure()
        fig_repl.add_trace(go.Scatter(x=self._data.epochs, y=self._data.HOM, mode="lines"))
        fig_repl.update_layout(
            title="Time series cleaned of outliers",
            autosize=False,
            width=800,
            height=400,
            yaxis=dict(
                autorange=True,
                showgrid=True,
                zeroline=True,
                dtick=250,
                gridcolor="rgb(255, 255, 255)",
                gridwidth=1,
                zerolinecolor="rgb(255, 255, 255)",
                zerolinewidth=2,
            ),
            margin=dict(l=40, r=30, b=80, t=100,),
            paper_bgcolor="rgb(243, 243, 243)",
            plot_bgcolor="rgb(243, 243, 243)",
            showlegend=False,
        )
        fig_repl.show()
        self._fig_repl = fig_repl

    def _read_txt_file(self):
        """
        Function reads the txt files

        Returns
        -------
        int
            DESCRIPTION.

        """

        # dfull contains full data over the years with 5 min time resolution
        self._beg = self._beg_reset
        self._end = self._end_reset
        self._dffull = pd.DataFrame()

        while self._beg <= self._end:

            year = self._beg

            mFile = Path("Data/ERA5/"+str(year)+"/"+self._station+".txt")
            if mFile.is_file():

                data = pd.read_csv("Data/ERA5/"+str(year)+"/"+self._station +
                                   ".txt", sep="       ", encoding="ascii", engine='python', header=None,
                                   names=["epochs", "pwv"])
            else:

                self._beg += 1
                continue

            data["epochs"] = pd.to_datetime(data["epochs"], format="%Y-%m-%d %H:%M:%S", errors='coerce')

            self._dffull = pd.concat([self._dffull, data])
            self._beg += 1

        # check dffill size
        if self._dffull.empty:

            print("No TXT data! Check the Data folder and/or config.json file!")
            sys.exit()
        else:
            # fiter data and then reduce the number of data
            idxs = ((self._dffull["epochs"].dt.hour == 0) | (self._dffull["epochs"].dt.hour == 6) | (
                self._dffull["epochs"].dt.hour == 12) | (self._dffull["epochs"].dt.hour == 18)) & \
                (self._dffull["epochs"].dt.minute == 0)

            self._era5 = self._dffull[idxs].copy()
            # substract the median from the pwv vector
            self._era5.pwv = self._era5.pwv - self._era5.pwv.median()

            self._era5 = self._era5.reset_index()
            self._era5 = self._era5.drop(columns="index")

        return 0

    def _read_npz_file(self):
        """
        The funtion process the npz file
        """

        # dfull contains full data over the years with 5 min time resolution
        self._dffull = pd.DataFrame()
        while self._beg <= self._end:

            year = self._beg

            mFile = Path("Data/GNSS/"+str(year)+"/"+self._station+".npz")
            if mFile.is_file():

                data = np.load("Data/GNSS/"+str(year)+"/"+self._station+".npz", allow_pickle=True)
            else:
                self._beg += 1
                continue

            df = pd.DataFrame()

            for key, val in data.items():

                df[key] = val

            self._dffull = pd.concat([self._dffull, df])
            self._beg += 1

        # check dffill size
        if self._dffull.empty:

            print("No NPZ data! Check the Data folder and/or config.json file!")
            sys.exit()
        else:
            # fiter data and then reduce the number of data
            idxs = ((self._dffull["epochs"].dt.hour == 0) | (self._dffull["epochs"].dt.hour == 6) | (
                self._dffull["epochs"].dt.hour == 12) | (self._dffull["epochs"].dt.hour == 18)) & \
                (self._dffull["epochs"].dt.minute == 0)

            self._gnss = self._dffull[idxs].copy()
            # substract the median from the pwv vector
            self._gnss.pwv = self._gnss.pwv - self._gnss.pwv.median()

            self._gnss = self._gnss.reset_index()
            self._gnss = self._gnss.drop(columns="index")

        return 0
