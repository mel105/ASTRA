#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 18:24:26 2023

@author: mel
"""
import pandas as pd
import plotly.graph_objects as go


class medianYear:
    # the class returns the median time series addapted to whole time span. First of all, the median year is
    # created and than the "year" is distributed over defined spam.

    def __init__(self, conf, inpTimeSeries):

        # MELTODO: How to secure, that input data must be in dataframe.series format?
        # MELTODO: Check the time span. To have median year robust at least, the time span should consist min.
        #          5> years of data

        # setting
        self._beg = conf.get_beg()
        self._end = conf.get_end()
        self._df = inpTimeSeries.copy()

        # create the median year time series
        self._create_median_year()

        # distribute the median year time series over the time span
        self._distribute_median_year()

    # public function
    def get_plot(self):
        """
        If required, then plot the situation with median series

        Returns
        -------
        None.

        """

        fo = go.Figure()
        fo.add_trace(go.Scatter(x=self._df.DATE, y=self._df.values[:, 1], mode="lines"))
        fo.add_trace(go.Scatter(x=self._med.DATE, y=self._med.values[:, 1], mode="lines"))
        fo.update_layout(
            title="Applied Median year time series on Original time series",
            autosize=False,
            width=800,
            height=400,
            yaxis=dict(
                # autorange=True,
                showgrid=True,
                zeroline=True,
                # dtick=250,
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

        return fo

    def get_median_year(self):
        """
        MEthod returns the median year time series.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """

        return self._med

    # protected functions

    def _distribute_median_year(self):
        """
        Method process the distribution of the median year over the time span defined by original time span.

        Returns
        -------
        None.

        """

        dis = pd.DataFrame()
        dis["DATE"] = pd.date_range(start="1/1/"+str(self._beg),
                                    end="1/1/"+str(self._end+1), freq="6h")
        dis["YM"] = dis.DATE.dt.strftime("%m-%d-%H")

        med = pd.merge(dis, self._dfmedian, on="YM")
        med = med.sort_values("DATE")
        med = med.reset_index()
        med = med.drop(columns=["YM", "index"])

        self._med = pd.DataFrame()
        self._med = med.copy()
        # self._med["DATE"] = med.DATE
        # self._med["vals"] = med.values

        return 0

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
        self._dfext = self._df.copy()
        self._dfext["YM"] = [i.strftime("%m-%d-%H") for i in list(self._df.DATE)]
        # self._dfext = self._dfext.reset_index()

        self._dfmedian = self._dfext.groupby(["YM"]).median(numeric_only=True)
        self._dfmedian = self._dfmedian.reset_index()
        # self._dfmedian = self._dfmedian.drop(columns=["index"])

        return 0
