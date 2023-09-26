#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 10 16:09:45 2023

@author: mel
"""

import time
import pandas as pd
from Src.config import config
from Src.process_ts import process_ts
from jinja2 import Environment, FileSystemLoader
from Src.support import check_folder
from xhtml2pdf import pisa


def get_version_table():
    """
    Function returns the verion of program and descritption of last updates
    Returns
    -------
    None.

    """

    # data, ktore by sa mali nejak editovat. Sluzi mi to hlavne pre nacvicenie vyrobi html reportu.
    edit_data = {
        "Version": ["0.0.1", "0.0.2"],
        "Author": ["MEL", "MEL"],
        "DATE": ["2023-09-18", "2023-09-26"],
        "Main contribution": [
            "Basic variant of html report that includes the PWV Time Series homogenization results",
            "Basic version of change point algorithm is implemented",
        ],
    }

    df_vt = pd.DataFrame(edit_data)

    return df_vt


def second_level_report(tsObj, input_file_name, input_file_add):
    """
    Function creates the second level of html report. This page includes the graphics and statistical results
    of time series homogenization
    """

    env = Environment(loader=FileSystemLoader("pwvHtmlTemplates"))
    sec_lev = env.get_template("second_level.html")

    # adresar, kam budeme html level2 reporty ukladat
    level2_folder_path = "Report" + "/" + input_file_name

    # kontrola, ze ci takato adresa existuje, ak nie, tak ju vytvor
    check_folder(level2_folder_path)

    data_level2 = {
        "fig_orig": tsObj.get_orig_fig().to_html(),
        "fig_chp":  tsObj.get_chp_fig().to_html(),
        "fig_out":  tsObj.get_out_fig().to_html(),
        "fig_homo": tsObj.get_homo_fig().to_html(),
    }

    # Naplnenie sablony pozadovanymi udajmi
    html = sec_lev.render(data_level2)

    # kontrola, ze ci takato adresa existuje, ak nie, tak ju vytvor
    check_folder(level2_folder_path)

    level2_file = level2_folder_path + "/" + "index.html"
    with open(level2_file, "w", encoding="utf8") as f:
        f.write(html)

    return level2_file


# Report generator


def report():

    # Program version table
    version_table = get_version_table()

    # Configure file reading
    configObj = config()

    # loop over the processed stations
    for iFile in configObj.get_inp_file_name():

        idx = 0
        list_of_file_names = []
        list_of_links = []

        while idx < len(configObj.get_inp_file_name()):

            print(idx, configObj.get_inp_file_name()[idx])

            # Process the data
            tsObj = process_ts(configObj, idx)

            actual_input = (
                configObj.get_inp_local_path()
                + "/"
                + configObj.get_inp_file_name()[idx]
                + ".csv"
            )

            second_lev = second_level_report(
                tsObj, configObj.get_inp_file_name()[idx], actual_input,
            )

            # Data collection
            list_of_file_names.append(configObj.get_inp_file_name()[idx])
            list_of_links.append(f"<a href={second_lev}>Link</a>")

            idx += 1
    #
    info_summary = {"Files": list_of_file_names, "Link": list_of_links}
    info_table = pd.DataFrame(info_summary)

    #         HTML REPORT
    env = Environment(loader=FileSystemLoader("pwvHtmlTemplates"))

    # First level report generator
    first_lev = env.get_template("report_main.html")

    # data
    data = {
        "version_table": version_table,
        "docu_gen_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "info_table": info_table,
    }

    #  Naplnenie sablony pozadovanymi udajmi
    html = first_lev.render(data)
    with open("pwv_report.html", "w") as f:
        f.write(html)

    # Convert HTML to PDF
    with open('pwv_report.pdf', "w+b") as out_pdf_file_handle:
        pisa.CreatePDF(
            src=html,  # HTML to convert
            dest=out_pdf_file_handle)  # File handle to receive result

    return configObj, tsObj


# spustenie reportu
if __name__ == "__main__":
    cfg, ts = report()
