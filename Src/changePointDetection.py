#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 24 13:22:00 2023

@author: mel
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from statsmodels.graphics.tsaplots import plot_acf
import statsmodels.api as sm
import pandas as pd
import numpy as np

import math

# from Src.medianYear import medianYear


class changePointDetection:

    """
    The class contains the algorithm for change point detection
    """

    # constructor
    def __init__(self, conf, data):
        """
        Construction of changePointDetection class.

        """

        # setting
        self._conf = conf
        self._data = data

        # Time series for analysis preparation (Difference of analysed vs. referenced series)
        self._preparation()

        # The dependency investigation
        self._dependency()

        # Estimate T_K statistics
        self._tkfunc()

        # Ciritical values estimation (based on asymptotic distribution)
        self._criticalValue()

        # Average values of time series before and after the detected change point
        self._avgFunc()

        # Shift estimation
        self._shiftEstimation()

        # Sigma* estimation
        self._sigmaStar()

        # p-value estimation
        self._pValueEstimation()

        # Test hypothesis
        self._hypoTest()

        # Confidence interval Estimation
        self._confidenceInterval()

        # Print results on screen
        # MELTODO: If requested and requestion should be configured in configure file
        self._printResults()

        # Plot the results
        # MELTODO: If requested and requestion should be configured in configure file
        self._plotResults()

        return None

    # PUBLIC FUNCTIONS
    def get_chp_result(self):
        return self._result_of_stationarity

    def get_chp(self):
        """
        Function returns index of detected change point, its time stamp and shift

        Returns
        -------
        TYPE
            DESCRIPTION.
        TYPE
            DESCRIPTION.

        """
        return self._tdata.epochs.iloc[self._idxMaxTk], self._idxMaxTk, self._shift

    def get_chp_plot(self):
        return self._fig

    # PRIVATE FUNCTIONS

    def _plotResults(self):
        """
        If requested, function plots the results of change point detection
        """

        if self._result_of_stationarity:
            fig = make_subplots(specs=[[{"secondary_y": True}]])

            #
            fig.add_trace(go.Scatter(x=self._tdata.epochs, y=self._data.vals,
                          name="PWV [mm]"), secondary_y=False)
            fig.add_trace(go.Scatter(x=self._tdata.epochs, y=self._TK, fill="tozeroy",
                          name=" TK [-]"), secondary_y=True)

            fig.update_layout(
                title_text="<b>Result of change point detection</b>",
                yaxis2=dict(range=[min(self._TK), 1.5*max(self._TK)+max(self._TK)]),
                autosize=False,
                width=800,
                height=400,
                yaxis=dict(
                    autorange=True,
                    showgrid=True,
                    zeroline=True,
                    dtick=5,
                    gridcolor="rgb(255, 255, 255)",
                    gridwidth=1,
                    zerolinecolor="rgb(255, 255, 255)",
                    zerolinewidth=2,
                ),
                margin=dict(l=40, r=30, b=80, t=100,),
                paper_bgcolor="rgb(243, 243, 243)",
                plot_bgcolor="rgb(243, 243, 243)",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )

            fig.add_vrect(x0=self._tdata.epochs.iloc[self._idxMaxTk],
                          x1=self._tdata.epochs.iloc[self._idxMaxTk],
                          line=dict(
                              color="green",
                              dash="dash"
            ),
            )

            fig.add_vrect(x0=self._tdata.epochs.iloc[self._lowConfIntervalIdx],
                          x1=self._tdata.epochs.iloc[self._uppConfIntervalIdx],
                          annotation_text="95% Interval Confidence", annotation_position="top left",
                          fillcolor="green", opacity=0.2, line_width=0
                          )

            fig.add_shape(type="line",
                          xref="paper", yref="y2",
                          x0=0, y0=self._criticalValue, x1=1, y1=self._criticalValue,
                          line=dict(
                              color="red",
                              dash="dash"
                          ),
                          )

            # Set x-axis title
            fig.update_xaxes(title_text="TIME [#6 Hours]")

            # Set y-axes titles
            fig.update_yaxes(title_text="<b>PWV [mm]</b>", secondary_y=False)
            fig.update_yaxes(title_text="<b>TK Statistics [-]</b>", secondary_y=True)

            self._fig = fig

        else:
            print("No plot will be created!\n\n")

            return go.Figure()

    def _printResults(self):
        """
        Functions print the results on screen

        Returns
        -------
        None.

        """

        print("\n======================= CHANGE POINT DETECTION ========================== \n")
        bg = self._tdata.epochs.iloc[0]
        en = self._tdata.epochs.iloc[-1]
        print("Time series interval: From {0} to {1}".format(bg, en))
        print("Size: ", len(self._data))
        print("Detected change point: ", self._result_of_stationarity)

        if self._result_of_stationarity:
            print("\n   Change point detected at: {0} [index {1}]".format(
                self._tdata.epochs.iloc[self._idxMaxTk], self._idxMaxTk))
            print(
                "   95% - Confidence interval: {0} - {1}".format(
                    self._tdata.epochs.iloc[self._lowConfIntervalIdx],
                    self._tdata.epochs.iloc[self._uppConfIntervalIdx]))
            print("   Shift: ", self._shift)

        return 0

    def _confidenceInterval(self):
        """

        MELTODO: NEED TO BE CHECKED!!!!!!!!
        Functions returns the indexes of confidence interval of detected change point

        Returns
        -------
        None.

        """

        critAlpha = 999
        prob = 0.95  # MELTODO: parameter should be given from configure file

        # if we want 95% cinfidence interval than we have to select 0.975 quantile
        if (prob == 0.9):
            quantile = 0.95
        elif (prob == 0.95):
            quantile = 0.975
        elif (prob == 0.975):
            quantile = 0.9875
        elif (prob == 0.99):
            quantile = 0.995
        elif (prob == 0.995):
            quantile = 0.9975

        if (quantile == 0.9):
            critAlpha = 4.696
        elif (quantile == 0.95):
            critAlpha = 7.687
        elif (quantile == 0.975):
            critAlpha = 11.033
        elif (quantile == 0.99):
            critAlpha = 15.868
        elif (quantile == 0.995):
            critAlpha = 19.767
        else:
            critAlpha = 4

        mVal = (critAlpha * self._SK[self._idxMaxTk] ** 2) / (self._shift ** 2)

        if np.isnan(mVal):
            self._uppConfIntervalIdx = self._idxMaxTk
            self._lowConfIntervalIdx = self._idxMaxTk
        else:
            self._uppConfIntervalIdx = self._idxMaxTk + math.floor(mVal)
            self._lowConfIntervalIdx = self._idxMaxTk - math.floor(mVal)

    def _hypoTest(self):
        """
        Function return result of hypothesis testing. The results is True meaning, that the time series is
        non-stationary and False, maxTK < critcal value, meaning that the time series is stationary.
        """

        if self._maxTk > self._criticalValue:
            self._result_of_stationarity = True
        else:
            self._result_of_stationarity = False

        return 0

    def _pValueEstimation(self):
        """
        Function returns estimated value of P-value

        Returns
        -------
        None.

        """

        N = len(self._data)
        tNorm = self._maxTk / self._sigStar

        an = math.sqrt(2.0 * math.log(math.log(N)))
        bn = 2.0 * math.log(math.log(N)) + 0.5 * \
            math.log(math.log(math.log(N))) - 0.5 * math.log(math.pi)

        y = an * tNorm - bn

        self._pVal = 1.0 - math.exp(-2.0 * math.exp(-y))

    def _sigmaStar(self):
        """
        Function returns the Sigma Star parameter as is define in Antoch at al.

        Returns
        -------
        int
            DESCRIPTION.

        """

        data = self._data.vals.to_numpy()

        # norm series
        dataBefore = data[:self._idxMaxTk] - self._meanBefore
        dataAfter = data[self._idxMaxTk:] - self._meanAfter

        dataNew = np.concatenate((dataBefore, dataAfter), axis=0)

        N = len(data)

        L = math.ceil(math.pow(N, 1/3))
        norm_acorr = sm.tsa.acf(dataNew, nlags=L)

        # self._acf = acorr[1]
        f0est = norm_acorr[0]

        for i in range(L):
            k = i + 1
            w = 1.0 - k / L
            f0est += 2.0 * w * norm_acorr[k]

        self._sigStar = math.sqrt(abs(f0est))

        # update critical value
        if norm_acorr[0] > 0.4:
            self._criticalValue = self._criticalValue * self._sigStar * self._rho

        return 0

    def _shiftEstimation(self):
        """
        FUnction returns etimated shift value

        Returns
        -------
        int
            DESCRIPTION.

        """

        self._shift = self._meanAfter - self._meanBefore

        return 0

    def _avgFunc(self):
        """
        Functions returns the averages befor and after the potential change point

        Returns
        -------
        int
            DESCRIPTION.

        """

        data = self._data.vals.to_numpy()

        self._meanBefore = data[:self._idxMaxTk].mean()
        self._meanAfter = data[self._idxMaxTk+1:].mean()

        return 0

    def _criticalValue(self):
        """
        Function returns the critical value
        """

        prob = 0.95  # MELTODO: add to configure
        N = len(self._data)

        an = 1.0 / math.sqrt(2.0 * math.log(math.log(N)))
        bn = (1.0/an) + (an/2) * math.log(math.log(math.log(N)))
        cr = -math.log(-math.sqrt(math.pi)/2.0 * math.log(prob))

        self._criticalValue = (cr * an) + bn

        return 0

    def _tkfunc(self):
        """
        The method returns the TK series. Max value of TK vector that cross the thrashold, this values is
        suspicious as change point.

        Returns
        -------
        int
            DESCRIPTION.

        """
        N = len(self._data)

        # actualMean = self._data.mean()
        k = 2
        self._TK = pd.DataFrame()
        TK = []
        SK = []
        data = self._data.vals.to_numpy()
        while (k <= N-1):

            x_k = data[:k].mean()
            x_n = data[k:N].mean()

            sumk = np.sum((data[:k] - x_k) ** 2)
            sumn = np.sum((data[k:N] - x_n) ** 2)

            sk = math.sqrt((sumk + sumn) / (N - 2))
            SK.append(sk)

            tk = math.sqrt((N - k) * k / N) * abs(x_k - x_n) / sk

            TK.append(tk)

            k += 1

        maxTk = max(TK)
        idxMaxTk = TK.index(maxTk)

        self._maxTk = maxTk
        self._idxMaxTk = idxMaxTk
        self._TK = TK
        self._SK = SK

        return 0

    def _dependency(self):
        """
        The method returns the autocorrelation index

        Returns
        -------
        int
            DESCRIPTION.

        """

        acorr = sm.tsa.acf(self._data.vals, nlags=3)

        # if plot is required, then
        plot_acf(self._data.vals)

        self._acf = acorr[1]
        self._rho = math.sqrt((1.0 + self._acf)/(1.0 - self._acf))

        return 0

    def _preparation(self):
        """
        The method prepare the differenced time series.

        Returns
        -------
        int
            DESCRIPTION.

        """

        self._data.rename(columns={"dpwv": "vals"}, inplace=True)

        # # NEED TO create and use medain series even on ERA-GNSS difference series, because of
        # # bad distributon or periodicity respectively
        # toMedian = pd.DataFrame()
        # toMedian["epochs"] = self._data[["epochs"]].copy()
        # toMedian["values"] = self._data[["vals"]].copy()
        # my = medianYear(self._conf, toMedian)
        # med = my.get_median_year()
        # # my.get_plot()

        # med = med.set_index("epochs")
        # self._data = self._data.set_index("epochs")

        # mergedSeries = pd.merge(self._data, med, how='inner', left_index=True, right_index=True)
        # mergedSeries = mergedSeries.reset_index()
        # self._data = self._data.reset_index()

        # a = pd.DataFrame()
        # a = mergedSeries[["epochs", "vals", "values"]].copy()
        # a["diff"] = a.vals - a.values[:, 2]

        # # replacement of original differences by correction of median year
        # self._data.vals = a[["diff"]].copy()

        self._tdata = pd.DataFrame()
        self._tdata["epochs"] = self._data[["epochs"]].copy()
