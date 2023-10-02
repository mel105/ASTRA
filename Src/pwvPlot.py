#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  2 18:55:16 2023

@author: mel
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots


def intakes(mergedSeries):

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

    return fig


def linePlot(data_X, data_Y, mtitle=" ", xlabel="TIME [#6 hours]", ylabel="PWV [mm]"):

    # MELTODO: take a control, that input dataframe contains required keys, such as epochs or/and HOM etc.

    fo = go.Figure()
    fo.add_trace(go.Scatter(x=data_X, y=data_Y, mode="lines"))
    fo.update_layout(
        title=mtitle,
        xaxis_title=xlabel,
        yaxis_title=ylabel,
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

    return fo
