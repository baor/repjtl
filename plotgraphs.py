import numpy as np
import matplotlib
matplotlib.use('Agg')



import matplotlib.pyplot as pyplot
import matplotlib.colors as colors
import collections
import datetime
from matplotlib.dates import DateFormatter
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA

font = {'family': 'Droid Sans',
        'weight': 'normal',
        'size': 14}

RGB_COLORS = ["#FF0000", "#FF8000", "#FFFF00", "#80FF00", "#00FF00", "#00FF80", "#00FFFF",
              "#0080FF", "#0000FF", "#8000FF", "#FF00FF", "#FF0080", "#909090", "#FFFFFF"]


def get_unique_ts_and_count(ts_not_unique):
    ts_not_unique = [int(x)/1000 for x in ts_not_unique]
    return np.unique(ts_not_unique, return_index=True, return_counts=True)


def get_average_values_from_notunique(ts_unique_arr, not_unique_arr, counts_arr, index_arr):
    avg_values = []
    for indx, indx_in_arr_value in enumerate(index_arr):
        total_value = 0.0
        if counts_arr[indx] > 0:
            for i in range(indx_in_arr_value, indx_in_arr_value+counts_arr[indx]):
                total_value += not_unique_arr[i]
            avg_values += [total_value/counts_arr[indx]]
    return avg_values


def parse_labels_for_plot(group_names):
    dict_groups = {}
    for tn, touple_arr in group_names.items():
        print("Parse thread groups %s for plot" % tn)
        ts_ng_np = np.asarray(touple_arr)

        ts_not_unique = sorted(ts_ng_np[:, 0])
        ts_unique_arr, index_arr, counts_arr = get_unique_ts_and_count(ts_not_unique)

        ng_count_not_unique = ts_ng_np[:, 1]
        ng_count_not_unique = list(map(int, ng_count_not_unique))

        arr_with_avg_ng_count = get_average_values_from_notunique(ts_unique_arr, ng_count_not_unique, counts_arr, index_arr)

        # zip arrays
        dict_groups[tn] = list(zip(ts_unique_arr, arr_with_avg_ng_count))
    return dict_groups


def scale_to_count_of_points(ts_arr, values_arr, count_of_points=100):
    all_count = len(ts_arr)
    step_size = all_count/count_of_points

    if step_size < 2:
        return ts_arr, values_arr

    ts_arr_new = []
    values_arr_new = []
    accumulate_value = 0
    i = 0
    last_avg_index = 0
    while i < all_count:
        accumulate_value += values_arr[i]
        if i % step_size == 0 and i > 0:
            ts_arr_new.append(ts_arr[i])
            values_arr_new.append(float(accumulate_value/step_size))
            accumulate_value = 0
            last_avg_index = i
        i += 1

    if last_avg_index != all_count:
        ts_arr_new.append(ts_arr[all_count-1])
        values_arr_new.append(float(accumulate_value/(all_count-last_avg_index)))

    return ts_arr_new, values_arr_new


def generate_graphs_for_labels_and_threads(labels, group_names, fig_count_start=0):

    if len(group_names) == 0:
        return fig_count_start
    matplotlib.rc('font', family='DejaVu Sans')

    fig_count = fig_count_start
    color_converter = colors.ColorConverter()

    dict_groups = parse_labels_for_plot(group_names)

    for label, touple_arr in labels.items():
        print("Parse label %s for plot" % label)
        array_of_values = []
        array_of_errors = []
        for ts, s, value in touple_arr:
            if s == "true":
                array_of_values += [[ts, float(value)]]
            else:
                array_of_errors += [ts]
        if len(array_of_values) == 0:
            continue

        array_of_values = np.asarray(sorted(array_of_values, key=lambda x: x[0]))
        ts_not_unique = array_of_values[:, 0]
        values_not_unique = list(map(float, array_of_values[:, 1]))

        ts_unique_arr, index_arr, counts_arr = get_unique_ts_and_count(ts_not_unique)

        response_time_array = get_average_values_from_notunique(ts_unique_arr, values_not_unique, counts_arr, index_arr)

        array_of_errors = sorted(array_of_errors)
        ts_err_unique_arr, index_err_arr, tps_err_array = get_unique_ts_and_count(array_of_errors)

        #########
        i_color = 0
        new_fixed_axis_offset = 50
        subplot1 = host_subplot(111, axes_class=AA.Axes)
        subplot2 = subplot1.twinx()
        subplot3 = subplot1.twinx()
        if len(ts_err_unique_arr) != 0:
            subplot4 = subplot1.twinx()

        subplot1.set_xlabel("time")
        subplot1.set_ylabel("Thread count")
        subplot2.set_ylabel('TPS', color='g')
        subplot3.set_ylabel('Response (ms)', color='b')
        if len(ts_err_unique_arr) != 0:
            subplot4.set_ylabel('Error count')

        subplot2.axis["left"].toggle(all=False)
        subplot3.axis["left"].toggle(all=False)
        if len(ts_err_unique_arr) != 0:
            subplot4.axis["right"].toggle(all=False)

        new_fixed_axis = subplot3.get_grid_helper().new_fixed_axis
        subplot3.axis["right"] = new_fixed_axis(loc="right",
                                                axes=subplot3,
                                                offset=(new_fixed_axis_offset, 0))
        if len(ts_err_unique_arr) != 0:
            new_fixed_axis = subplot4.get_grid_helper().new_fixed_axis
            subplot4.axis["left"] = new_fixed_axis(loc="left",
                                                   axes=subplot4,
                                                   offset=(-new_fixed_axis_offset, 0))

        for tn in group_names.keys():
            ts_arr, threads_arr = list(zip(*dict_groups[tn]))
            ts_arr, threads_arr = scale_to_count_of_points(ts_arr, threads_arr)

            ts_arr = [(datetime.datetime.fromtimestamp(x)) for x in ts_arr]

            subplot1.plot(ts_arr, threads_arr, '--', label=tn, color=color_converter.to_rgb(RGB_COLORS[i_color]))
            i_color = (i_color + 1) % len(RGB_COLORS)

        ts_counts_arr, counts_arr = scale_to_count_of_points(ts_unique_arr, counts_arr)
        ts_response_arr, response_time_array = scale_to_count_of_points(ts_unique_arr, response_time_array)

        ts_counts_arr = [(datetime.datetime.fromtimestamp(x)) for x in ts_counts_arr]
        ts_response_arr = [(datetime.datetime.fromtimestamp(x)) for x in ts_response_arr]

        subplot2.plot(ts_counts_arr, counts_arr, 'g.-', label='tps')
        subplot3.plot(ts_response_arr, response_time_array, 'b.-', label='Response')

        if len(ts_err_unique_arr) != 0:
            ts_err_unique_arr, tps_err_array = scale_to_count_of_points(ts_err_unique_arr, tps_err_array)

            ts_err_unique_arr = [(datetime.datetime.fromtimestamp(x)) for x in ts_err_unique_arr]
            subplot4.plot(ts_err_unique_arr, tps_err_array, 'r.-', label='Errors')

        subplot1.xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
        subplot1.set_ylim(0, subplot1.get_ylim()[1])

        subplot2.xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
        subplot2.set_ylim(0, subplot2.get_ylim()[1])

        subplot3.xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
        subplot3.set_ylim(0, subplot3.get_ylim()[1])

        if len(ts_err_unique_arr) != 0:
            subplot4.xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
            subplot4.set_ylim(0, subplot4.get_ylim()[1])

        figure = pyplot.gcf()
        figure.autofmt_xdate()
        figure.suptitle('Label %s' % label)

        figure.set_size_inches(14, 5)
        pyplot.subplots_adjust(right=0.75)
        pyplot.tight_layout()

        print("Save fig %s.png" % fig_count)
        figure.savefig("%s.png" % fig_count, format="png")

        pyplot.close(figure)

        fig_count += 1
    print("plot graphs for labels end")
    return fig_count


def generate_graphs_for_labels(labels, fig_count_start=0):
    matplotlib.rc('font', family='DejaVu Sans')
    fig_count = fig_count_start

    for label, touple_arr in labels.items():
        fig, (subplot01, subplot02) = pyplot.subplots(nrows=2, ncols=1)
        #label = re.sub(re.compile("[\"\'\r\n\t]+", re.UNICODE | re.MULTILINE), "", label)
        print("Parse label %s for plot" % label)
        array_of_values = []
        array_of_errors = []
        for ts, s, value in touple_arr:
            ts = int(ts)/1000
            if s == "true":
                array_of_values += [[ts, s, value]]
            else:
                array_of_errors += [ts]
        if len(array_of_values) == 0:
            continue

        array_of_values = np.array(array_of_values)

        ts_not_unique = array_of_values[:, 0]
        ts_not_unique = list(map(int, ts_not_unique))

        values_not_unique = array_of_values[:, 2]
        values_not_unique = list(map(float, values_not_unique))

        ts_unique_counter = collections.Counter(ts_not_unique)
        tps_array = []
        response_time_array = []

        for ts, count in ts_unique_counter.items():
            tps_array += [[datetime.datetime.fromtimestamp(ts), count]]

            values_for_avg = [values_not_unique[i] for i, x in enumerate(ts_not_unique) if x == ts]
            response_time_array += [[datetime.datetime.fromtimestamp(ts), np.mean(values_for_avg)]]

        tps_array = np.array(sorted(tps_array, key=lambda x: x[0]))
        response_time_array = np.array(sorted(response_time_array, key=lambda x: x[0]))

        ts_errors_unique_counter = collections.Counter(array_of_errors)
        tps_errors = []
        for ts, count in ts_errors_unique_counter.items():
            tps_errors += [[datetime.datetime.fromtimestamp(ts), count]]

        tps_errors = np.array(sorted(tps_errors, key=lambda x: x[0]))

        subplot01.xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
        subplot02.xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
        fig.autofmt_xdate()

        fig.suptitle('Label %s' % label)

        subplot01.plot(tps_array[:, 0], tps_array[:, 1], 'g.-')
        if len(tps_errors) != 0:
            subplot01.plot(tps_errors[:, 0], tps_errors[:, 1], 'r.-')
        subplot01.set_ylabel('TPS OK and ERR')

        subplot02.plot(response_time_array[:, 0], response_time_array[:, 1], 'b.-')
        subplot02.set_ylabel('Response')

        fig.set_size_inches(14, 5)
        pyplot.tight_layout()

        print("Save fig %s.png" % fig_count)
        fig.savefig("%s.png" % fig_count, format="png")

        pyplot.close(fig)

        fig_count += 1
    print("plot graphs for labels end")
    return fig_count


def generate_graphs_for_threads(group_names, fig_count_start=0):

    if len(group_names) == 0:
        return fig_count_start
    matplotlib.rc('font', family='DejaVu Sans')

    fig_count = fig_count_start
    labels_for_legend = []
    fig = pyplot.figure(1)
    ax = fig.add_subplot(111)

    color_converter = colors.ColorConverter()
    i_color = 0

    dict_groups = parse_labels_for_plot(group_names)
    for tn in group_names.keys():
        ts_arr, threads_arr = list(zip(*dict_groups[tn]))
        ts_arr, threads_arr = scale_to_count_of_points(ts_arr, threads_arr)

        ts_arr = [(datetime.datetime.fromtimestamp(x)) for x in ts_arr]

        ax.xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
        ax.plot(ts_arr, threads_arr, '.-', label=tn, color=color_converter.to_rgb(RGB_COLORS[i_color]))
        i_color = (i_color + 1) % len(RGB_COLORS)

        fig.autofmt_xdate()

        labels_for_legend += [tn]
        ax.set_xlabel("time (sec)")
        ax.set_ylabel("Thread count")


    lgd = ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=4,
          mode="expand", borderaxespad=0.)

    fig.set_size_inches(14, 10)
    pyplot.tight_layout()

    print("Save fig %s.png" % fig_count)
    fig.savefig("%s.png" % fig_count, format="png", bbox_extra_artists=(lgd,), bbox_inches='tight')
    pyplot.close(fig)

    fig_count += 1
    print("plot graphs for threads end")
    return fig_count