# Reporting Pool

A simple wrapper around Python multiprocessing Pool that allows tracking of progress. 

While starmap runs, a report is printed that shows % of jobs completed, time elapsed, estimated remaining time and a list of jobs statuses. Status can be: 
    Q -- queued,
    R -- running,
    S -- success,
    F -- failed (in case track_failures is enabled).

The wrapper runs [multiprocessing.pool.starmap](https://docs.python.org/3/library/multiprocessing.html#multiprocessing.pool.Pool.starmap) on the `func` and `p_args` (see [Examples](#Examples)). 

Enabling `track_failures` allows native tracking of failed function runs. For other arguments, see help(ReportingPool).

## Getting Started

This project's code is available on [GitHub](https://github.com/nishbo/reporting_pool).

### Prerequisites

Software:
- Python 3+ (tested on 3.7 and 3.8)

### Installation

1. Download the [repository](https://github.com/nishbo/reporting_pool) or clone it using git: `git clone https://github.com/nishbo/reporting_pool.git`.
2. Open Terminal, Command Line, or the desired Anaconda environment in the project folder.
3. Run `python setup.py install`.

## Examples

Example of a normal use:

```
from reporting_pool import ReportingPool

def _reporting_pool_test_func_wof(v):
    time.sleep(0.25)
    return v**2

p_args = [[v] for v in range(40)]

pool = ReportingPool(_reporting_pool_test_func_wof, p_args, processes=8,
                     report_on_change=True)
res = pool.start()

print(res)
```

Output:
```
Completed 0.00% of jobs. Time elapsed: 0.00 s, remaining: NaN s. List: QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ.
Completed 20.00% of jobs. Time elapsed: 0.28 s, remaining: 1.13 s. List: SRSRSRSRSRSRSRSRQQQQQQQQQQQQQQQQQQQQQQQQ.
Completed 25.00% of jobs. Time elapsed: 0.53 s, remaining: 1.59 s. List: SSSSSRSRSRSRSRSRRQRQQQQQQQQQQQQQQQQQQQQQ.
Completed 40.00% of jobs. Time elapsed: 0.56 s, remaining: 0.84 s. List: SSSSSSSSSSSSSSSSRQRQRQRQRQRQRQRQQQQQQQQQ.
Completed 42.50% of jobs. Time elapsed: 0.78 s, remaining: 1.06 s. List: SSSSSSSSSSSSSSSSSRRQRQRQRQRQRQRQQQQQQQQQ.
Completed 60.00% of jobs. Time elapsed: 0.81 s, remaining: 0.54 s. List: SSSSSSSSSSSSSSSSSRSRSRSRSRSRSRSRQQQQQQQQ.
Completed 65.00% of jobs. Time elapsed: 1.06 s, remaining: 0.57 s. List: SSSSSSSSSSSSSSSSSSSSSRSRSRSRSRSRRQRQQQQQ.
Completed 80.00% of jobs. Time elapsed: 1.09 s, remaining: 0.27 s. List: SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSRQRQRQRQ.
Completed 82.50% of jobs. Time elapsed: 1.31 s, remaining: 0.28 s. List: SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSRRQRQRQ.
Completed 90.00% of jobs. Time elapsed: 1.34 s, remaining: 0.15 s. List: SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSRSRSRSR.
Completed 95.00% of jobs. Time elapsed: 1.59 s, remaining: 0.08 s. List: SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSRSR.
Reporting pool finished after 1.6205 s.
[0, 1, 4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144, 169, 196, 225, 256, 289, 324, 361, 400, 441, 484, 529, 576, 625, 676, 729, 784, 841, 900, 961, 1024, 1089, 1156, 1225, 1296, 1369, 1444, 1521]
```

Example where the function can throw exceptions:

```
from reporting_pool import ReportingPool

# a function that throws an error
def _reporting_pool_test_func_wf(v):
    time.sleep(0.25)
    if v % 6 == 0:
        raise ValueError()
    return v**2

p_args = [[v] for v in range(40)]

pool = ReportingPool(_reporting_pool_test_func_wf, p_args,
                     report_rate=20, track_failures=True)
res = pool.start()

print(res)
```

Output:
```
[0, 1, 4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144, 169, 196, 225, 256, 289, 324, 361, 400, 441, 484, 529, 576, 625, 676, 729, 784, 841, 900, 961, 1024, 1089, 1156, 1225, 1296, 1369, 1444, 1521]
Completed 0.00% of jobs. Time elapsed: 0.00 s, remaining: NaN s. List: QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ.
Completed 0.00% of jobs. Time elapsed: 0.07 s, remaining: NaN s. List: RRRRRRRRRRRRQQQQQQQQQQQQQQQQQQQQQQQQQQQQ.
Completed 0.00% of jobs. Time elapsed: 0.13 s, remaining: NaN s. List: RRRRRRRRRRRRQQQQQQQQQQQQQQQQQQQQQQQQQQQQ.
Completed 0.00% of jobs. Time elapsed: 0.19 s, remaining: NaN s. List: RRRRRRRRRRRRQQQQQQQQQQQQQQQQQQQQQQQQQQQQ.
Completed 0.00% of jobs. Time elapsed: 0.26 s, remaining: NaN s. List: RRRRRRRRRRRRQQQQQQQQQQQQQQQQQQQQQQQQQQQQ.
Completed 30.00% of jobs. Time elapsed: 0.32 s, remaining: 0.75 s. List: FSSSSSFSSSSSRRRRRRRRRRRRQQQQQQQQQQQQQQQQ.
Completed 30.00% of jobs. Time elapsed: 0.38 s, remaining: 0.89 s. List: FSSSSSFSSSSSRRRRRRRRRRRRQQQQQQQQQQQQQQQQ.
Completed 30.00% of jobs. Time elapsed: 0.44 s, remaining: 1.04 s. List: FSSSSSFSSSSSRRRRRRRRRRRRQQQQQQQQQQQQQQQQ.
Completed 30.00% of jobs. Time elapsed: 0.51 s, remaining: 1.19 s. List: FSSSSSFSSSSSRRRRRRRRRRRRQQQQQQQQQQQQQQQQ.
Completed 60.00% of jobs. Time elapsed: 0.57 s, remaining: 0.38 s. List: FSSSSSFSSSSSFSSSSSFSSSSSRRRRRRRRRRRRQQQQ.
Completed 60.00% of jobs. Time elapsed: 0.63 s, remaining: 0.42 s. List: FSSSSSFSSSSSFSSSSSFSSSSSRRRRRRRRRRRRQQQQ.
Completed 60.00% of jobs. Time elapsed: 0.70 s, remaining: 0.47 s. List: FSSSSSFSSSSSFSSSSSFSSSSSRRRRRRRRRRRRQQQQ.
Completed 60.00% of jobs. Time elapsed: 0.76 s, remaining: 0.51 s. List: FSSSSSFSSSSSFSSSSSFSSSSSRRRRRRRRRRRRQQQQ.
Completed 77.50% of jobs. Time elapsed: 0.83 s, remaining: 0.24 s. List: FSSSSSFSSSSSFSSSSSFSSSSSFSSSSSFRRRRRRRRR.
Completed 90.00% of jobs. Time elapsed: 0.89 s, remaining: 0.10 s. List: FSSSSSFSSSSSFSSSSSFSSSSSFSSSSSFSSSSSRRRR.
Completed 90.00% of jobs. Time elapsed: 0.95 s, remaining: 0.11 s. List: FSSSSSFSSSSSFSSSSSFSSSSSFSSSSSFSSSSSRRRR.
Completed 90.00% of jobs. Time elapsed: 1.01 s, remaining: 0.11 s. List: FSSSSSFSSSSSFSSSSSFSSSSSFSSSSSFSSSSSRRRR.
Completed 95.00% of jobs. Time elapsed: 1.08 s, remaining: 0.06 s. List: FSSSSSFSSSSSFSSSSSFSSSSSFSSSSSFSSSSSFSRR.
Reporting pool finished after 1.1385 s.
Jobs 0, 6, 12, 18, 24, 30, 36 were not finished correctly.
[None, 1, 4, 9, 16, 25, None, 49, 64, 81, 100, 121, None, 169, 196, 225, 256, 289, None, 361, 400, 441, 484, 529, None, 625, 676, 729, 784, 841, None, 961, 1024, 1089, 1156, 1225, None, 1369, 1444, 1521]
```

## Authors

- [**Anton Sobinov**](https://github.com/nishbo)


##### Keywords
python, multiprocessing, pool, starmap
