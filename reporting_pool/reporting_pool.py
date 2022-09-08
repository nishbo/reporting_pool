#!python3
# -*- coding: utf-8 -*-
"""Main class.

Reporting Pool
Copyright 2022 Anton Sobinov
https://github.com/nishbo/reporting_pool
"""
import time
import datetime
# import sys
# import traceback
import multiprocessing


class ReportingPool(object):
    """A wrapper around multiprocessing.Pool that keeps track of the completion of the jobs.

    """
    def __init__(self, func, p_args, processes=None, report_rate=60, report_on_change=False,
                 track_failures=False):
        """A wrapper around multiprocessing.Pool that keeps track of the completion of the jobs.

        Start the pool with `start()` method. All arguments can be updated.

        Legend:
            Q -- queued
            R -- running
            S -- success
            F -- failed

        Arguments:
            func {callable} -- function to run parallel pool on.
            p_args {list or tuple} -- list of arguments to pass to pool.starmap(func, p_args).
            processes {int} -- number of processes to spawn. (default: {None} (uses default
                multiprocessing value -- the number returned by os.cpu_count()))
            report_rate {number} -- how many reports per second are generated. If report_on_change
                ==  True, maximum frequency of updates on the changes in the state. (default: {60})
            report_on_change {bool} -- if True, reports will be generated only when a process
                completes. Useful when func does not print much to std. (default: {False})
            track_failures {bool} -- if True, catches functions that raised exceptions and reports
                on them after all processes finished. (default: {False})
        """
        super(ReportingPool, self).__init__()
        self.processes = processes
        self.func = func
        self.p_args = p_args
        self.report_rate = report_rate
        self.report_on_change = report_on_change
        self.track_failures = track_failures

    @staticmethod
    def _print_report(done_list, shared_completion_list, start_time, processes):
        scl = [int(i) for i in done_list]
        n_completed = sum(scl)
        time_passed = time.time() - start_time
        if n_completed < processes:  # this would give a bad estimate
            est_time_left = 'NaN'
        else:
            est_time_left = time_passed / n_completed * (len(scl) - n_completed)
            est_time_left = str(datetime.timedelta(seconds=est_time_left))
        print(('Completed {:.2%} ({}/{}) of jobs. Time elapsed: {}, remaining: {}.'
               ' States: {}.').format(
            float(n_completed) / len(scl),
            n_completed,
            len(scl),
            datetime.timedelta(seconds=time_passed),
            est_time_left,
            ''.join(shared_completion_list)))

    @staticmethod
    def _periodic_reporting_process(report_rate, shared_completion_list, processes):
        sleep_period = 1./report_rate
        done_list = [False] * len(shared_completion_list)

        start_time = time.time()
        while not all(done_list):
            ReportingPool._print_report(done_list, shared_completion_list, start_time, processes)

            time.sleep(sleep_period)
            done_list = [v in ('S', 'F') for v in shared_completion_list]

        print('Reporting pool finished after {}.'.format(
            datetime.timedelta(seconds=time.time() - start_time)))

    @staticmethod
    def _on_change_reporting_process(report_rate, shared_completion_list, processes):
        sleep_period = 1./report_rate
        done_list = [False] * len(shared_completion_list)
        done_list_prev = [False] * len(shared_completion_list)

        start_time = time.time()

        # print all not done, first message
        ReportingPool._print_report(done_list, shared_completion_list, start_time, processes)
        while not all(done_list):
            if not all(v == vprev for v, vprev in zip(done_list, done_list_prev)):
                ReportingPool._print_report(
                    done_list, shared_completion_list, start_time, processes)
                done_list_prev = done_list

            time.sleep(sleep_period)
            done_list = [v in ('S', 'F') for v in shared_completion_list]

        print('Reporting pool finished after {}.'.format(
            datetime.timedelta(seconds=time.time() - start_time)))

    @staticmethod
    def _function_wrapper(func, shared_completion_list, i_job, *args):
        shared_completion_list[i_job] = 'R'
        res = func(*args)
        shared_completion_list[i_job] = 'S'
        return res

    @staticmethod
    def _function_wrapper_track_failure(func, shared_completion_list, i_job, error_reports, *args):
        shared_completion_list[i_job] = 'R'
        try:
            res = func(*args)
            shared_completion_list[i_job] = 'S'
        except Exception as e:
            res = None
            shared_completion_list[i_job] = 'F'
            print('Job #{} failed with error:\n{}\n'.format(i_job, str(e)))
            error_reports[i_job] = str(e)
        # For some reason, on my python3.7 it leads to sporadic failures of multiprocessing.pool
        # but these messages are much more informative
        # except Exception:
        #     res = None
        #     shared_completion_list[i_job] = 'F'
        #     _, exc_value, exc_traceback = sys.exc_info()
        #     error_str = ''.join(traceback.format_exception(None, exc_value, exc_traceback))
        #     print('Job #{} failed with error:\n{}\n'.format(i_job, error_str))
        #     error_reports[i_job] = error_str

        return res

    def start(self):
        """Starts the pool and reporter. Returns result obtained from starmap. For control
        variables see help on __init__ method.
        """
        manager = multiprocessing.Manager()
        shared_completion_list = manager.list()
        if self.track_failures:
            self.error_reports = manager.list()

        i_jobs = list(range(len(self.p_args)))
        expanded_p_args = []
        for i_job, p_arg in enumerate(self.p_args):
            shared_completion_list.append('Q')
            if self.track_failures:
                self.error_reports.append('')
                expanded_p_args.append([
                    self.func, shared_completion_list, i_job, self.error_reports] + list(p_arg))
            else:
                expanded_p_args.append([self.func, shared_completion_list, i_job] + list(p_arg))

        # reporting process
        if self.report_on_change:
            rpf = ReportingPool._on_change_reporting_process
        else:
            rpf = ReportingPool._periodic_reporting_process
        report_process = multiprocessing.Process(
            target=rpf, args=[self.report_rate, shared_completion_list, self.processes])
        report_process.start()

        # pool
        if self.track_failures:
            fwf = ReportingPool._function_wrapper_track_failure
        else:
            fwf = ReportingPool._function_wrapper
        if self.processes > 1:
            with multiprocessing.Pool(processes=self.processes) as pool:
                res = pool.starmap(fwf, expanded_p_args)
        else:
            # no reason to spawn a pool
            res = []
            for epa in expanded_p_args:
                res.append(fwf(*epa))

        # close the report
        report_process.join()

        # check failures
        if self.track_failures:
            self.failed_i_jobs = []
            for i_job in i_jobs:
                if shared_completion_list[i_job] == 'F':
                    self.failed_i_jobs.append(i_job)
            if len(self.failed_i_jobs) > 0:
                print('{} job{} {} not finished correctly:'.format(
                    len(self.failed_i_jobs),
                    's' if len(self.failed_i_jobs) > 1 else '',
                    'were' if len(self.failed_i_jobs) > 1 else 'was'))
                for i_job in self.failed_i_jobs:
                    print('\t{}: {}'.format(i_job, self.error_reports[i_job]))

        return res


def _reporting_pool_test_func_wof(v):
    time.sleep(0.25)
    return v**2


def _reporting_pool_test_func_wf(v):
    time.sleep(0.25)
    if v % 6 == 0:
        raise ValueError()
    return v**2


if __name__ == '__main__':
    # example without failures
    p_args = [[v] for v in range(40)]

    pool = ReportingPool(_reporting_pool_test_func_wof, p_args, processes=8,
                         report_on_change=True)
    res = pool.start()

    print(res)

    # example with failures
    pool = ReportingPool(_reporting_pool_test_func_wf, p_args,
                         report_rate=20, track_failures=True)
    res = pool.start()

    print(res)
