import numpy as np

def calculate_values_to_table_and_errors(labels):

    table = {}
    for label, touple_arr in labels.items():
        t_arr = []
        ts_arr = []
        errors = {}
        for ts, s, value in touple_arr:
            ts_arr.append(int(ts))
            if s == "true":
                t_arr.append(int(value))
            else:
                if label not in errors:
                    errors[label] = []
                errors[label].append(value)

        ok_count = 0
        min_val = 0
        avg_val = 0
        perc50 = 0
        perc80 = 0
        perc90 = 0
        perc95 = 0
        perc99 = 0
        hps_avg = 0.0
        if len(t_arr) != 0:
            ok_count = len(t_arr)
            min_val = np.min(t_arr)
            avg_val = np.average(t_arr)
            perc50 = np.percentile(t_arr, 50)
            perc80 = np.percentile(t_arr, 80)
            perc90 = np.percentile(t_arr, 90)
            perc95 = np.percentile(t_arr, 95)
            perc99 = np.percentile(t_arr, 99)


        if len(ts_arr) != 0:
            ts_diff = float(np.max(ts_arr) - np.min(ts_arr))/1000
            if ts_diff >= 0.1:
                hps_avg = float(len(ts_arr))/ts_diff
            else:
                hps_avg = 0.0

        err_count = 0.0
        err_percent = 0.0
        if label in errors:
            err_count = len(errors[label])
            err_percent = (float(err_count)/float(ok_count + err_count))*100

        table[label] = [ok_count, min_val, avg_val, perc50, perc80, perc90, perc95, perc99, hps_avg, err_count, err_percent]
    return table



def percent_diff_time(value_new, value_base):
    if isinstance(value_base, str):
        if value_base == "nan":
            return "nan"
        return str(value_new) + value_base

    if float(value_base) < 0.1:
        diff_percent = "nan"
    else:
        diff_percent = (1 - float(value_new)/float(value_base))*100

    return [value_base - value_new, diff_percent]


