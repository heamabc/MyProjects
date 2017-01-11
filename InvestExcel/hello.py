# -*- coding: utf-8 -*-
"""
Created on Fri Nov 11 14:13:30 2016

@author: ywang
"""

# hello.py
import numpy as np
import xlwings as xw

def world():
    wb = xw.Book.caller()
    wb.sheets[0].range('A1').value = 'Hello World!'