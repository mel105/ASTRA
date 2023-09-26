#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 19:44:07 2023

@author: mel
"""

# import os
import sys
import statistics as stat
import matplotlib.pyplot as plt
import os
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import Src.changePointDetection as chp
pio.renderers.default = 'browser'


class process_ts:

    """
    The class should use config settings and process the time series
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

        if self._preprocess:
            # prepare data for LOKI. Meaning, create the differences time series given as ERA-GNSS.
            self._dataToLOKI()
        else:
            # read the npz file> GNSS data
            self._read_npz_file()

            # median year estimation
            self._create_median_year()

            # change point detection
            self._detectChangePoints()

            # ts homogenization
            self._homogenization()

    # public get/set functions
    def get_full_data(self):
        """
        Function returns the original data with original time resolution

        Returns
        -------
        None.

        """

        return self._dffull

    def get_flt_data(self):
        """
        Function returns the filtered/reduced dataframe that contains another usefull columns

        Returns
        -------
        None.

        """

        return self._dfflt

    def get_my_data(self):
        """
        Function returns the median year series

        Returns
        -------
        None.

        """

        return self._dfmedian

    def get_orig_fig(self):
        if self._preprocess:
            return go.Figure()
        else:
            return self._fig1

    def get_chp_fig(self):
        if self._preprocess:
            return go.Figure()
        else:
            return self._fig2

    def get_out_fig(self):
        if self._preprocess:
            return go.Figure()
        else:
            return self._fig3

    def get_homo_fig(self):
        if self._preprocess:
            return go.Figure()
        else:
            return self._fig4

    # protected functions

    def _detectChangePoints(self):
        """
        Functions prepare the series and run the methods for change point detection

        Returns
        -------
        None.

        """

        # Do we have available the reference time series? If we do not, then distribute the median series via
        # whole data range

        dis = pd.DataFrame()
        dis["epochs"] = pd.date_range(start="1/1/"+str(self._beg_reset),
                                      end="1/1/"+str(self._end_reset+1), freq="6h")
        dis["YM"] = dis.epochs.dt.strftime("%m-%d-%H")

        med = pd.merge(dis, self._dfmedian, on="YM")
        med = med.sort_values("epochs")

        ref = med[["epochs", "pwv"]].copy()
        anl = self._dfflt[["epochs", "pwv"]].copy()

        chp.changePointDetection(self._conf, anl, ref)

        # In case, the plot is required
# =============================================================================
#         fo_data = go.Figure()
#         fo_data.add_trace(go.Scatter(x=anl.epochs, y=anl.pwv, mode="lines"))
#         fo_data.add_trace(go.Scatter(x=ref.epochs, y=ref.pwv, mode="lines"))
#         fo_data.update_layout(
#             title="Analysed series vs reference time series",
#             autosize=False,
#             width=800,
#             height=400,
#             yaxis=dict(
#                 autorange=True,
#                 showgrid=True,
#                 zeroline=True,
#                 dtick=250,
#                 gridcolor="rgb(255, 255, 255)",
#                 gridwidth=1,
#                 zerolinecolor="rgb(255, 255, 255)",
#                 zerolinewidth=2,
#             ),
#             margin=dict(l=40, r=30, b=80, t=100,),
#             paper_bgcolor="rgb(243, 243, 243)",
#             plot_bgcolor="rgb(243, 243, 243)",
#             showlegend=False,
#         )
#         fo_data.show()
# =============================================================================

        return 0

    def _dataToLOKI(self):
        """
        Function prepares the data for LOKI application. In next stpers: 1) reading the GNSS and ERA5 data,
        2) creatinf the difference time series, 3) prepare the txt file in format: yyyy-mm-dd hh-mm-ss dpwv
        4) prepare the plot of differences


        Returns
        -------
        int
            DESCRIPTION.

        """

        self._read_npz_file()
        self._gnss = self._dfflt.copy()
        self._gnss = self._gnss.set_index("epochs")

        self._read_txt_file()
        self._era5 = self._dfflt.copy()
        self._era5 = self._era5.set_index("epochs")

        # time series difference
        mergedSeries = pd.merge(self._gnss, self._era5, how='inner', left_index=True, right_index=True)
        mergedSeries = mergedSeries.reset_index()
        mergedSeries.columns = ["epochs", "index GNSS", "pwv GNSS", "sigma GNSS", "index ERA5", "pwv ERA5"]
        mergedSeries["dpwv"] = mergedSeries["pwv ERA5"] - mergedSeries["pwv GNSS"]

        # plot the series
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=mergedSeries.epochs, y=mergedSeries.dpwv, mode="lines"))
        fig.update_layout(
            title="ERA5 - GNSS difference time serties",
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

        fig.show()

        # save the differenced time eries
        mergedSeries = mergedSeries.drop(
            ["index GNSS", "index ERA5", "pwv GNSS", "pwv ERA5", "sigma GNSS"], axis=1)
        mergedSeries.to_csv(r"Res/toLOKI/"+self._station+"_dpwv.txt", header=None, index=None, sep='\t')

        return 0

    def _homogenization(self):

        # if the list of change points exists, read the list
        chppath = 'Data/LOKI/LOKI.chp'
        chpCols = ['STATION', 'IDX', 'DATE', 'SHIFT']
        if os.path.exists(chppath):

            # self._dfchp = pd.read_csv(chppath, header=None, names=chpCols, skiprows=1)
            self._dfchp = pd.read_csv(chppath, sep="  ", header=None, names=chpCols, engine="python")

        # Find actually analysed station in the list of change points and provide the time series adjusting.
        # if the change poinst exist

        # copy of fitered series
        tsAdj = self._dfflt.pwv.copy()

        # plot the data (TODO PLOTS in own class and manage from config.)
        # original series+detected change point
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=self._dfflt.epochs, y=self._dfflt.pwv, mode="lines"))
        # Test if Station exists in the list of change points
        if((self._dfchp['STATION'].eq(self._station)).any()):

            # TODO: probably bad altitide from programming point of view to adjust over loop. Reconstruct!!!
            for index, row in self._dfchp.iterrows():
                if row["STATION"] == self._station:
                    print(row['STATION'], row["DATE"], row['SHIFT'])
                    idx = row["IDX"]
                    tsAdj[idx:] = tsAdj[idx:]+row["SHIFT"]
                    fig1.add_vline(x=row["DATE"], line_width=3, line_color="red", line_dash="dash")
                    # ax1.axvline(x=pd.Timestamp(row["DATE"]), color="r", label="aa")

            self._dfflt["ADJ"] = tsAdj

        else:
            print("KO")

        fig1.update_layout(
            title="Original time series and presentation of detected change-point(s)",
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

        self._fig1 = fig1  # chp.get_chp_fig()

        # adjusted series
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=self._dfflt["epochs"], y=self._dfflt["ADJ"], mode="lines"))
        fig2.update_layout(
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

        self._fig2 = fig2

        # Outliers replacing by median
        med1 = stat.median(self._dfflt.ADJ)
        self._dfflt["RED"] = abs(self._dfflt.ADJ-med1)
        MAD = stat.median(self._dfflt.RED)
        # Tukey's fence
        low = med1 - 4.45*MAD
        upp = med1 + 4.45*MAD

        # outlier indexes
        lowidx = self._dfflt.ADJ.lt(low)
        uppidx = self._dfflt.ADJ.gt(upp)

        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=self._dfflt.epochs, y=self._dfflt.ADJ, mode="lines"))
        fig3.add_trace(go.Scatter(x=self._dfflt.epochs[lowidx], y=self._dfflt.ADJ[lowidx], mode="lines"))
        fig3.add_trace(go.Scatter(x=self._dfflt.epochs[uppidx], y=self._dfflt.ADJ[uppidx], mode="markers"))
        fig3.update_layout(
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
        self._fig3 = fig3

        # replace the outlier values by the median ones
        self._dfflt["HOM"] = self._dfflt.ADJ
        self._dfflt.loc[lowidx, "HOM"] = med1
        self._dfflt.loc[uppidx, "HOM"] = med1

        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(x=self._dfflt.epochs, y=self._dfflt.HOM, mode="lines"))
        fig4.update_layout(
            title="Homogenized time series",
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
        self._fig4 = fig4

        # convert and save the container into the ascii file
        # elf._dfflt = self._dfflt.drop(columns=["index", "YM"])
        # self._dfflt.to_csv("Data/TXT/"+self._station+".txt", index=None, sep=" ",
        #                    header=False, date_format=("%Y-%m-%d\t%H:%M:%S").replace(' " ', '  '))

    def _create_median_year(self):
        """
        Function returns so called Median year usefull for missing data or outlier data replacement. Median 
        year dataframe is also useful for seasonality removing.

        Returns
        -------
        None.

        """

        # median year
        #  algorithm based on "contingency table"
        self._dfext = self._dfflt.copy()
        self._dfext["YM"] = [i.strftime("%m-%d-%H") for i in list(self._dfflt.epochs)]
        self._dfext = self._dfext.reset_index()

        self._dfmedian = self._dfext.groupby(["YM"]).median(numeric_only=True)
        self._dfmedian = self._dfmedian.reset_index()

        return 0

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

            self._dfflt = self._dffull[idxs].copy()
            self._dfflt = self._dfflt.reset_index()

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

            self._dfflt = self._dffull[idxs].copy()
            self._dfflt = self._dfflt.reset_index()

        return 0
