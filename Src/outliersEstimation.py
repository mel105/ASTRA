#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  2 19:53:36 2023

@author: mel
"""


import statistics as stat
import plotly.graph_objects as go


def outliers(data):

    # Outliers replacing by median
    med1 = stat.median(data)

    MAD = stat.median(abs(data-med1))

    # Tukey's fence
    low = med1 - 4.45*MAD
    upp = med1 + 4.45*MAD

    # outlier indexes
    uppidx = data >= upp
    lowidx = data <= low
    # lowidx = data.lt(low)
    # uppidx = data.gt(upp)

    return med1, MAD, lowidx, uppidx


def outliersPlot(data_X, data_Y, lowidx, uppidx):

    fig_out = go.Figure()
    fig_out.add_trace(go.Scatter(x=data_X, y=data_Y, mode="lines"))
    fig_out.add_trace(go.Scatter(x=data_X[lowidx], y=data_Y[lowidx], mode="markers"))
    fig_out.add_trace(go.Scatter(x=data_X[uppidx], y=data_Y[uppidx], mode="markers"))
    fig_out.update_layout(
        title="Presentation the Outliers in Analysed Time Series",
        xaxis_title="TIME [#6 hours]",
        yaxis_title="PWV [mm]",
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

    return fig_out


# def _outlierReplacement(self):

#     # replace the outlier values by the median ones
#     self._data.loc[self._lowidx, "HOM"] = self._med1
#     self._data.loc[self._uppidx, "HOM"] = self._med1

#     fig_repl = go.Figure()
#     fig_repl.add_trace(go.Scatter(x=self._data.epochs, y=self._data.HOM, mode="lines"))
#     fig_repl.update_layout(
#         title="Time series cleaned of outliers",
#         autosize=False,
#         width=800,
#         height=400,
#         yaxis=dict(
#             autorange=True,
#             showgrid=True,
#             zeroline=True,
#             dtick=250,
#             gridcolor="rgb(255, 255, 255)",
#             gridwidth=1,
#             zerolinecolor="rgb(255, 255, 255)",
#             zerolinewidth=2,
#         ),
#         margin=dict(l=40, r=30, b=80, t=100,),
#         paper_bgcolor="rgb(243, 243, 243)",
#         plot_bgcolor="rgb(243, 243, 243)",
#         showlegend=False,
#     )
#     fig_repl.show()
#     self._fig_repl = fig_repl
