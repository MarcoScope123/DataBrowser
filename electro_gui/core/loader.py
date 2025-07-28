import pandas as pd
from pathlib import Path
from yadg import extractors

# ── Registry of loaders ────────────────────────────────────────────────
def _load_txt(path: Path, dtype: str | None = None):
    if(dtype=="cv"):
        df = pd.read_table(path, sep=" ", header=None,
                       names=["cycle", "time", "Ewe", "I"])
    return df

def _load_mpt(path: Path, dtype: str):

    dataframe = extractors.extract(filetype="eclab.mpt",path=path).to_dataset().to_dataframe().reset_index()

    if(dtype=="cv"):
        df = dataframe[['cycle number', 'time', 'Ewe', '<I>']].rename(columns={'cycle number': "cycle", '<I>': "I"})
    elif(dtype=="eis"):
        df = dataframe[['freq', 'Z_real', 'Z_imag', 'alpha']]
    return df

LOADERS = {
    (".txt", "cv"):  _load_txt,          # default CV
    (".mpt", "cv"): _load_mpt,
    (".mpt", None):  _load_mpt,
}

# ── Public API ─────────────────────────────────────────────────────────
def load(path: str | Path, ftype: str, dtype: str | None = None):
    key = (ftype.lower(), dtype.lower())
    if key not in LOADERS:
        raise ValueError(f"No loader registered for {ftype}/{dtype}")
    return LOADERS[key](Path(path), dtype)
