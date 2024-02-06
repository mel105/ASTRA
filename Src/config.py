#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 19:13:02 2023

@author: mel
"""

import json


class config:
    """
    The class process the configure json file.
    """

    def __init__(self):
        """
        Konstruktor

        Returns
        -------
        None.

        """

        self._load_config()

    # get funkcie
    def get_inp_file_name(self):
        """

        Returns
        -------
        TYPE string
            DESCRIPTION.

        """
        return self._inp_file_name

    def get_inp_local_path(self):
        """
        Returns
        -------
        TYPE string
            DESCRIPTION.
        """
        return self._inp_local_path

    def get_out_file_name(self):
        """
         Function return station name or vector of station names.

         Returns
         -------
         TYPE string
             DESCRIPTION.

         """
        return self._out_file_name

    def get_out_local_path(self):
        """
         Functions retunr local path to output folder

         Returns
         -------
         TYPE string
             DESCRIPTION. Local path for outputs
         """
        return self._out_local_path

    def get_beg(self):
        """
        Function returns parameter BEG

        Returns
        -------
        None.

        """

        return self._BEG

    def get_end(self):
        """
        Function returns parameter END

        Returns
        -------
        None.

        """

        return self._END

    def get_preprocess(self):
        """
        The function returns the 0, 1 or 2 decision. If:
            0 - then the analysed series is investigated withut the seasonal signal removing,
            1 - then from the analysed series, the seasonal signal is removed using the median year and
            2 - then from the analysed series, the seasonal signal is removed using the reference series.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        return self._preprocess

    def get_cnd_actual_data(self):
        """
        Function returns minimal length of time series that is accepted to change point detection. NOTE that
        this costant depends on time span. For instat, assume that we process daily data, then one may set 365
        that means thet we want process data that contains more than 365 days.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        return self._actual_data

    def get_cnd_orig_idx(self):
        """
        Function returns the condition that evaulates the actually detected change point index. Assess if the
        detected change point already exists in the container, where the detected change points are sorted.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        return self._orig_idx

    def get_cnd_ci_prob(self):

        return self._ci_prob

    def get_cnd_norm_acorr(self):

        return self._norm_acorr

    def get_cnd_cv_prob(self):

        return self._cv

    # protected functions

    def _load_config(self):
        """
        funkcia nacita konfiguracny subor.

        Returns
        -------
        None.

        """
        with open("config.json") as j:
            cf = json.load(j)

        # General setting of input
        self._inp_file_name = cf["set_inp"]["inp_file_name"]
        self._inp_local_path = cf["set_inp"]["inp_local_path"]

        # General setting of output
        self._out_file_name = cf["set_out"]["out_file_name"]
        self._out_local_path = cf["set_out"]["out_local_path"]

        # General setting
        self._preprocess = cf["set_general"]["preprocess"]
        self._BEG = cf["set_general"]["BEG"]
        self._END = cf["set_general"]["END"]

        # conditions
        self._actual_data = cf["set_conditions"]["cnd_actual_data"]
        self._orig_idx = cf["set_conditions"]["cnd_orig_idx"]
        self._ci_prob = cf["set_conditions"]["cnd_ci_prob"]
        self._norm_acorr = cf["set_conditions"]["cnd_norm_acorr"]
        self._cv = cf["set_conditions"]["cnd_cv"]
