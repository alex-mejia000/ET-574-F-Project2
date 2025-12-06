#Alexander Mejia ID:24588520
#Bassel O  ID:
import os
import sys
import traceback
import wx
import wx.lib.mixins.listctrl as listmix
import pandas as pd
import numpy as np  
import matplotlib
matplotlib.use('WXAgg')
import matplotlib.pyplot as plt

APP_TITLE = "Project II - Data Analysis Tool"
PANEL_MIN_SIZE = (800, 600)

def is_numeric_series(s: pd.Series) -> bool:
    return pd.api.types.is_numeric_dtype(s)

class StatusListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        self.InsertColumn(0, "Time")
        self.InsertColumn(1, "Event")
        self.SetColumnWidth(0, 150)
        self.SetColumnWidth(1, 1000)
    
    def log(self, msg: str):
        import datatime
        t = datatime.datatime.now().strftime("%Y-%m-%d %H:%M:%S")
        index = self.InsertItem(self.GetItemCount(), t)
        self.SetItem(index, 1, msg)
        self.EnsureVisible(index)

    class Plotter:
        @staticmethod
        def popup_hist(series: pd.Series, title: "Histogram"):
            if series is None or series.empty:
                raise ValueError("Series is empty")
            fig, ax = plt. subplots(figsize=(8, 6))
            ax.hist(series.dropna(), bins='auto', edgecolor='black')
            ax.set_title(title)
            ax.set_xlabel(series.name)
            ax.set_ylabel("Count")
            fig.tight_layout()
            fig.show()

        @staticmethod
        def popup_scatter(x: pd.Series, y: pd.Series, title: str = "Scatter Plot"):
            if x is None or y is None:
                raise ValueError("One or both series are empty")
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.scatter(x, y, s=20, alpha=0.7)
            ax.set_xlabel(x.name)
            ax.set_ylabel(y.name)
            ax.set_title(title)
            fig.tight_layout()
            fig.show()

    class MainFrame(wx.Frame):
        def __init__(self):
            super().__init__(None, title=APP_TITLE, size=(920, 600))
            self.panel = wx.Panel(self)
            self.panel.SetMinSize(PANEL_MIN_SIZE)
            sizer.Add(self.status_list, 1, wx.EXPAND | wx.ALL, 5)
            self.panel.SetSizer(sizer)
            self.Centre()
            self.Show()

        def log_event(self, msg: str):
            self.status_list.log(msg)

        def _make_menu(self):
            menubar = wx.MenuBar()
            file_menu = wx.Menu()
            load_item = file_menu.Append(wx.ID_OPEN, "&Load dataset...\tCtrl+O", "Load a CSV or TSV file")
            file_menu.AppendSeparator()
            exit_item = file_menu.Append(wx.ID_EXIT, "E&xit\tCtrl+Q", "Exit the application")
            menubar.Append(file_menu, "&File")

            plotMenu = wx.Menu()
            hist_item = plotMenu.Append(wx.ID_ANY, "&Histogram\tCtrl+H")
            scatter_item = plotMenu.Append(wx.ID_ANY, "&Scatter Plot\tCtrl+S")
            menubar.Append(plotMenu, "&Plot")
            self.SetMenuBar(menubar)

            helpMenu = wx.Menu()
            about_item = helpMenu.Append(wx.ID_ABOUT, "&About", "About this app")
            menubar.Append(helpMenu, "&Help")

            self.SetMenuBar(menubar)

            self.Bind(wx.EVT_MENU, self.on_load, load_item)
            self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
            self.Bind(wx.EVT_MENU, self.on_histogram, hist_item)
            self.Bind(wx.EVT_MENU, self.on_scatter, scatter_item)
            self.Bind(wx.EVT_MENU, self.on_boxplot, box_item)
            self.Bind(wx.EVT_MENU, self.on_about, about_item)

        