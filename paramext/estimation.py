"""Library for handling xspec results.
"""
import re

import numpy as np
import pandas as pd


def extract_param_from_log(log_file):
    with open(log_file) as f:
        a = [text for text in f if re.findall("#  ..   ..", text)]
    a = [aa.replace("10^22", "xxxxx") for aa in a]

    rr_for_num = r"[+-]?\d+(?:\.\d+)?(?:(?:[eE][+-]?\d+)|"\
                 r"(?:\*10\^[+-]?\d+))?"

    b = [re.findall(rr_for_num, aa) for aa in a]

    c = [bb for bb in b if len(bb) == 4]

    d = []
    for li in c:
        li_out = [float(a) for a in li]
        d.append(li_out)

    d = np.array(d)
    df = pd.DataFrame(d)
    df.columns = ["par", "comp", "param_med", "param_error"]

    return df


def get_qdp_columns():
    col_names = [
        "ENERGY", "ENERGY_ERR",
        "OBS", "OBS_ERR",
        "MODEL_TOTAL",
        "COMP_SOFTEX", "COMP_FE1", "COMP_FE2",  # Gaussian comp.
        "COMP_DISK", "COMP_POWL",
        "RESI", "RESI_ERR"
    ]
    return col_names


def get_model_param_name():
    model_param_list = [
        "TBabs.nH",
        "gaussian.LineE",
        "gaussian.Sigma",
        "gaussian.norm",
        "gaussian.LineE",
        "gaussian.Sigma",
        "gaussian.norm",
        "gaussian.LineE",
        "gaussian.Sigma",
        "gaussian.norm",
        "diskbb.Tin",
        "diskbb.norm",
        "powerlaw.PhoIndex",
        "powerlaw.norm"
    ]
    return model_param_list


class FitExtractor():
    """Prameter Extoractor from Xspec

    Input file is lof file created in XSPEC by
    ```bash
    log hogehoge.log
    err 0
    err 1
    ```
    """

    def __init__(self, logfile):
        self.logfile = logfile
        self.df_err = self._extract_error(logfile)

    @property
    def median(self):
        return self.df_err["median"].values

    @property
    def lower(self):
        return self.df_err["lower"].values

    @property
    def upper(self):
        return self.df_err["upper"].values

    @property
    def error(self):
        return self.df_err[["err_lower", "err_upper"]].values.T

    def _extract_error(self, logfile):
        with open(logfile) as f:
            a = [text for text in f if "#   " in text]

        rr_for_num = r"[+-]?\d+(?:\.\d+)?(?:(?:[eE][+-]?\d+)|"\
                     r"(?:\*10\^[+-]?\d+))?"
        b = [re.findall(rr_for_num, aa) for aa in a]
        c = [bb for bb in b if len(bb) == 5]
        d = []
        for li in c:
            li_out = [float(a) for a in li]
            d.append(li_out)
        d = np.array(d)
        df = pd.DataFrame(d)
        df.columns = ["para", "lower", "upper", "err_lower", "err_upper"]
        df["err_lower"] *= -1
        df["median"] = df["lower"] + df["err_lower"]

        return df


class ErrorExtractor:

    def __init__(self, logfile):
        self.logfile = logfile
        self.df_params = self._extract_params()
        self.chi2, self.dof = self._extract_fit_info()

    @property
    def params(self):
        return self.df_params

    @property
    def reduced_chi2(self):
        return self.chi2 / self.dof

    def _extract_fit_info(self):

        with open(self.logfile) as f:
            texts_original = [t for t in f]

        texts_filter_00 = [re.findall(r"[^ ]+", t)
                           for t in texts_original]
        texts_filter_01 = [t for t in texts_filter_00 if len(t) == 8]
        texts_filter_02 = [t for t in texts_filter_01 if t[0] == "#Fit"]

        chi2 = float(texts_filter_02[0][4])
        dof = float(texts_filter_02[0][6])

        return chi2, dof

    def _extract_params(self):
        """Extract parameters from xspec log file.

        Returns:
            df_params
        """
        with open(self.logfile) as f:
            texts_original = [t for t in f]

        texts_filter_00 = [re.findall(r"[^ ]+", t)
                           for t in texts_original]
        texts_filter_01 = [t for t in texts_filter_00 if 8 < len(t) <= 10]
        texts_filter_02 = [t for t in texts_filter_01 if t[0] != "#Model"]
        texts_filter_03 = []
        for t in texts_filter_02:
            if len(t) == 9:
                t.insert(5, "")
            t.pop(0)
            t.pop(6)
            t.pop(7)
            texts_filter_03.append(t)

        col_names = ["par_id", "comp_id", "model_name", "param_name",
                     "unit", "value", "error"]
        df_params = pd.DataFrame(texts_filter_03, columns=col_names)

        df_params["value"] = df_params["value"].astype(float)
        df_params["error"] = df_params["error"].astype(float)

        return df_params.convert_dtypes()
