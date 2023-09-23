#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 18:17:55 2023

@author: mel
"""

import os


def check_folder(folder_path):
    """
    Function checks the folder existece. If the folder does not exist, the the folder will be created.

    Parameters:
        folder_path: TYPE string
                    DESCRIPTION. The folder path.
    Returns
    -------
    None.

    """

    check_folder_existance = os.path.isdir(folder_path)

    if not check_folder_existance:

        os.makedirs(folder_path)
    else:
        pass
