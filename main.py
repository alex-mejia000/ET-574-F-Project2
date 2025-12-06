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
            # =========================
# STATUS DISPLAY + PAGE LAYOUT
# This section builds the log area at the bottom of the app where
# messages appear (like "File loaded" or "Histogram displayed").
# _layout_widgets organizes the entire window layout.
# =========================
    def _make_status_area(self):
        self.status = StatusListCtrl(self.panel)

    def _layout_widgets(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.toolbar_sizer, 0, wx.EXPAND | wx.ALL, 4)
        main_sizer.Add(self.status, 1, wx.EXPAND | wx.ALL, 8)
        self.panel.SetSizer(main_sizer)


# =========================
# FILE LOADING FUNCTIONS
# on_load opens a file-choose window so the user can select a CSV.
# _load_dataset actually reads the CSV into pandas, cleans columns,
# sets up dropdown choices, and logs that the file was loaded.
# =========================
    def on_load(self, event=None):
        try:
            wildcard = "CSV files (*.csv)|*.csv|TSV files (*.tsv;*.txt)|*.tsv;*.txt|All files (*.*)|*.*"
            dlg = wx.FileDialog(
                self, message="Choose a dataset file", wildcard=wildcard,
                style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
            )

            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                self._load_dataset(path)

            dlg.Destroy()

        except Exception as e:
            self._show_error("Error loading file", e)

    def _load_dataset(self, path: str):
        try:
            ext = os.path.splitext(path)[1].lower()
            sep = "\t" if ext in (".tsv", ".txt") else ","

            df = pd.read_csv(path, sep=sep, engine="python", low_memory=False)
            df.columns = [str(c).strip() for c in df.columns]

            self.dataframe = df
            self.current_file = path
            self.file_label.SetLabel(
                f"Loaded: {os.path.basename(path)} ({len(df)} rows, {len(df.columns)} columns)"
            )

            numeric_cols = [c for c in df.columns if is_numeric_series(df[c])]
            other_cols = [c for c in df.columns if c not in numeric_cols]
            choices = numeric_cols + other_cols

            self.col_x_choice.Clear()
            self.col_y_choice.Clear()

            if choices:
                self.col_x_choice.AppendItems(choices)
                self.col_y_choice.AppendItems(choices)

                if numeric_cols:
                    self.col_x_choice.SetSelection(0)
                    if len(numeric_cols) > 1:
                        self.col_y_choice.SetSelection(1)
                    else:
                        self.col_y_choice.SetSelection(0)

            self.status.log(f"Loaded dataset: {path}")

        except Exception as e:
            self._show_error("Failed to load dataset", e)


# =========================
# BASIC MENU ACTIONS
# on_exit closes the program.
# on_about shows a simple popup with information about the project.
# =========================
    def on_exit(self, _):
        self.Close(True)

    def on_about(self, _):
        wx.MessageBox(
            "ET-574 Project II\n\nData Visualization Application\nBuilt with wxPython & Matplotlib",
            "About",
            wx.OK | wx.ICON_INFORMATION
        )


# =========================
# HISTOGRAM PLOT
# Creates a histogram of one selected column.
# Converts data to numbers if needed, then displays the plot.
# =========================
    def on_histogram(self, event=None):
        try:
            if self.dataframe is None:
                wx.MessageBox(
                    "No dataset loaded. Load a CSV first.",
                    "Missing Data",
                    wx.OK | wx.ICON_WARNING
                )
                return

            sel = self.col_x_choice.GetSelection()
            if sel == wx.NOT_FOUND:
                wx.MessageBox(
                    "Select a column for the histogram.",
                    "Missing Column",
                    wx.OK | wx.ICON_INFORMATION
                )
                return

            col = self.col_x_choice.GetString(sel)
            series = pd.to_numeric(self.dataframe[col], errors="coerce")

            Plotter.popup_hist(series, title=f"Histogram — {col}")
            self.status.log(f"Histogram displayed for column: {col}")

        except Exception as e:
            self._show_error("Failed to create histogram", e)


# =========================
# SCATTER PLOT
# Uses two selected columns (X and Y) and plots them against each other.
# Good for seeing relationships between two variables.
# =========================
    def on_scatter(self, event=None):
        try:
            if self.dataframe is None:
                wx.MessageBox(
                    "No dataset loaded. Load a CSV first.",
                    "Missing Data",
                    wx.OK | wx.ICON_WARNING
                )
                return

            sx = self.col_x_choice.GetSelection()
            sy = self.col_y_choice.GetSelection()

            if sx == wx.NOT_FOUND or sy == wx.NOT_FOUND:
                wx.MessageBox(
                    "Select both X and Y columns for scatter plot.",
                    "Missing Columns",
                    wx.OK | wx.ICON_INFORMATION
                )
                return

            colx = self.col_x_choice.GetString(sx)
            coly = self.col_y_choice.GetString(sy)

            x = pd.to_numeric(self.dataframe[colx], errors="coerce")
            y = pd.to_numeric(self.dataframe[coly], errors="coerce")

            mask = x.notna() & y.notna()

            if mask.sum() == 0:
                raise ValueError("No valid numeric data for scatter plot.")

            Plotter.popup_scatter(x[mask], y[mask], title=f"Scatter — {colx} vs {coly}")
            self.status.log(f"Scatter plot displayed: {colx} vs {coly}")

        except Exception as e:
            self._show_error("Failed to create scatter plot", e)


# =========================
# BOXPLOT
# Shows the distribution of one selected column.
# Helps identify medians, quartiles, and outliers.
# =========================
    def on_boxplot(self, event=None):
        try:
            if self.dataframe is None:
                wx.MessageBox(
                    "No dataset loaded. Load a CSV first.",
                    "Missing Data",
                    wx.OK | wx.ICON_WARNING
                )
                return

            sel = self.col_x_choice.GetSelection()
            if sel == wx.NOT_FOUND:
                wx.MessageBox(
                    "Select a column for the boxplot.",
                    "Missing Column",
                    wx.OK | wx.ICON_INFORMATION
                )
                return

            col = self.col_x_choice.GetString(sel)
            series = pd.to_numeric(self.dataframe[col], errors="coerce")

            Plotter.popup_box(series, title=f"Boxplot — {col}")
            self.status.log(f"Boxplot displayed for column: {col}")

        except Exception as e:
            self._show_error("Failed to create boxplot", e)


# =========================
# ERROR HANDLING
# If something goes wrong (bad file, wrong column, etc),
# this shows a popup and logs the error for the user.
# =========================
    def _show_error(self, title: str, exc: Exception):
        tb = "".join(traceback.format_exception_only(type(exc), exc)).strip()
        self.status.log(f"{title}: {tb}")
        wx.MessageBox(f"{title}:\n\n{str(exc)}", "Error", wx.OK | wx.ICON_ERROR)


# =========================
# PROGRAM ENTRY POINT
# main() starts the app by creating the window and running the event loop.
# =========================
def main():
    app = wx.App(False)
    frame = MainFrame(None)
    frame.Show(True)
    app.MainLoop()


if __name__ == "__main__":
    main()


        