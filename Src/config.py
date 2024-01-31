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
