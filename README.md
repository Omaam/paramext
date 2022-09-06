# paramext
paramext is prameter extractor from log file in [Xspec](https://heasarc.gsfc.nasa.gov/docs/xanadu/xspec/).

## Usage

1. Save estimation log using save command in xspec.
```bash
$ xspec
> ...
> # After completing parameter estimation process
> save all filename
> show para
> show fit
> save none
```

2. Give xcm file to `Estimator` object and extract information.
```python
from paramext import Extractor

ext = Extractor(filename)
ext.param  # Return dataframe of paramter output.
ext.chi2   # Return chi-square value.
```
