#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  2 18:55:16 2023

@author: mel
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots


def detections(data, listOfChp):

    fo = go.Figure()
    fo.add_trace(go.Scatter(x=data.DATE, y=data.vals, mode="lines"))

    fo.update_layout(
        title_text="<b>Presentation of all detected change point</b>",
        autosize=False,
        width=800,
        height=400,
        yaxis=dict(
            # autorange=True,
            showgrid=True,
            zeroline=True,
            # dtick=5,
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

    mbeg = 0
    counter = 0
    listOfChp.sort()

    for idx in listOfChp:

        # plot means
        if counter == len(listOfChp):
            mend = -1
        else:
            mend = idx

        fo.add_shape(type='line',
                     x0=data.DATE.iloc[mbeg],
                     y0=data.vals[mbeg:mend].mean(),
                     x1=data.DATE.iloc[mend],
                     y1=data.vals[mbeg:mend].mean(),
                     line=dict(color='Red',),
                     xref='x',
                     yref='y'
                     )

        # plot change point index
        fo.add_vrect(x0=data.DATE.iloc[idx],
                     x1=data.DATE.iloc[idx],
                     line=dict(
            color="green",
            dash="dash"
        ),
        )

        mbeg = mend
        counter += 1

    fo.add_shape(type='line',
                 x0=data.DATE.iloc[listOfChp[-1]],
                 y0=data.vals[listOfChp[-1]:].mean(),
                 x1=data.DATE.iloc[-1],
                 y1=data.vals[listOfChp[-1]:].mean(),
                 line=dict(color='Red',),
                 xref='x',
                 yref='y'
                 )

    # fo.show()

    return fo


def intakes(mergedSeries):

    fig = make_subplots(rows=2, cols=1)
    fig.add_trace(go.Scatter(x=mergedSeries.DATE,
                  y=mergedSeries["Analysed"], mode="lines"), row=1, col=1)
    fig.add_trace(go.Scatter(x=mergedSeries.DATE,
                  y=mergedSeries["Reference"], mode="lines"), row=1, col=1)
    fig.add_trace(go.Scatter(x=mergedSeries.DATE, y=mergedSeries.vals, mode="lines"), row=2, col=1)
    fig.update_layout(
        title="Analysed and Reference time series presentation",
        autosize=False,
        width=800,
        height=400,
        yaxis=dict(
            # autorange=True,
            showgrid=True,
            zeroline=True,
            # dtick=5,
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
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Time series", row=1, col=1)
    fig.update_yaxes(title_text="Difference", row=2, col=1)

    # fig.show()

    return fig


def linePlot(data_X, data_Y, mtitle=" ", xlabel="Date", ylabel="Analysed time series"):

    # MELTODO: take a control, that input dataframe contains required keys, such as DATE or/and HOM etc.

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
            # autorange=True,
            showgrid=True,
            zeroline=True,
            # dtick=5,
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

    # fo.show()
    return fo
