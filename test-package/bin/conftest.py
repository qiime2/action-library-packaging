from collections import defaultdict
import pytest
import statistics

_durations = defaultdict(dict)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    outcome = yield
    report = outcome.get_result()
    _durations[item.nodeid][report.when] = report.duration

# sort the output with longest runtime first
def _total_test_duration(item):
    nodeid, phases = item
    return sum(phases.get(p, 0) for p in ('setup', 'call', 'teardown'))

# compute mean & stdev
def _compute_duration_stats(durations):
    test_duration_times = []
    test_stats = {}
    for nodeid, phases in durations:
        item = (nodeid, phases)
        test_duration_times.append(_total_test_duration(item))

    test_stats['mean'] = statistics.mean(test_duration_times)
    test_stats['stdev'] = statistics.stdev(test_duration_times)

    return test_stats

# determine the terminal color (determinalor) to highlight for each test
# green is test time < 1σ
# yellow is test time within +/- 1σ
# red is test time > 1σ
def _compute_terminal_color(stats, duration):
    mean = stats['mean']
    stdev = stats['stdev']

    total_runtime = _total_test_duration(duration)

    if (total_runtime < (mean - stdev)):
        terminal_color = 'green'
    elif ((mean - stdev) <= total_runtime <= (mean + stdev)):
        terminal_color = 'yellow'
    elif (total_runtime > (mean + stdev)):
        terminal_color = 'red'

    return terminal_color

# test runtime summary grouped by test with per-phase runtime
def pytest_terminal_summary(terminalreporter):
    terminalreporter.write_sep('=', 'Runtime Duration per Test')

    stats = _compute_duration_stats(_durations.items())
    mean = stats['mean']
    stdev = stats['stdev']

    reds = 0
    for nodeid, phases in sorted(_durations.items(),
                                 key=_total_test_duration,
                                 reverse=True):
        item = (nodeid, phases)
        color = _compute_terminal_color(stats, item)

        if color == 'green':
            terminalreporter._tw.line(nodeid, green=True)
        elif color == 'yellow':
            terminalreporter._tw.line(nodeid, yellow=True)
        elif color == 'red':
            terminalreporter._tw.line(nodeid, red=True)
            reds += 1
        else:
            terminalreporter._tw.line(nodeid)

        for phase in ('setup', 'call', 'teardown'):
            duration = phases.get(phase)

            if duration is not None:
                terminalreporter.write_line(f'  {phase:<10} {duration:.5f}s')

    terminalreporter.write_sep('=', 'Test Suite Runtime Statistical Summary')
    terminalreporter.write_line(f' -1σ:   {(mean - stdev):.5f}')
    terminalreporter.write_line(f' Mean:  {mean:.5f}')
    terminalreporter.write_line(f' +1σ:   {(mean + stdev):.5f}')
    terminalreporter.write_line(f' Number of tests with > +1σ runtime: {reds}')
