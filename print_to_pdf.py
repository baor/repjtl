import datetime
import os

from wfpdf import WFPDF

PATH_TO_WFPDF = "."
REPORTNAME = "rep_%s_%s.%s"

PDF_PAGE_WIDTH = 1500
PDF_PAGE_HEIGHT = 2000
wfpdf = WFPDF("P", "pt", (PDF_PAGE_WIDTH, PDF_PAGE_HEIGHT), PATH_TO_WFPDF)

DEFAULT_HEIGHT = 20
DEFAULT_WIDTH_TEXT = 300
DEFAULT_WIDTH_TEXT_ERROR = 500
DEFAULT_WIDTH_NUMBER = 55

COLUMN_WIDTHS = [DEFAULT_WIDTH_TEXT, DEFAULT_WIDTH_NUMBER, DEFAULT_WIDTH_NUMBER, DEFAULT_WIDTH_NUMBER, DEFAULT_WIDTH_NUMBER,
                 DEFAULT_WIDTH_NUMBER, DEFAULT_WIDTH_NUMBER, DEFAULT_WIDTH_NUMBER, DEFAULT_WIDTH_NUMBER, DEFAULT_WIDTH_NUMBER,
                 DEFAULT_WIDTH_NUMBER, DEFAULT_WIDTH_NUMBER, DEFAULT_WIDTH_TEXT_ERROR]
COLUMN_NAMES = [[u"Name"], ["OK cnt"], ["Min"], ["Avg"], ["p50%"],
                ["p80%"], ["p90%"], ["p95%"], ["p99%"], ["HPS"],
                ["Err cnt"], ["Err %"], ["(Error count) Error text"]]

#table[label] = [ok_count, min_val, avg_val, perc50,
# perc80, perc90, perc95, perc99,
# hps_avg, err_count, err_percent]
ITEM_KEYS_POSTFIX_UNITS = [("ok_count", ""), ("min_val", "ms"), ("avg_val", "ms"), ("perc50", "ms"),
                          ("perc80", "ms"), ("perc90", "ms"), ("perc95", "ms"), ("perc99", "ms"),
                          ("hps_avg", ""), ("err_count", "")]

RGB_GOOD = [(204, 255, 204), (102, 255, 102), (0, 255, 0)]
RGB_BAD = [(255, 255, 204), (255, 204, 204), (255, 0, 0)]


def generate_list_of_errors(errors):
    set_val_arr = set(errors)
    line_errors = [[]]
    for err in set_val_arr:
        line_errors[0] += ["(%d) %s" % (errors.count(err), err)]
    return line_errors

def surround_notlist_with_brakets(value):
    if not isinstance(value, list):
        return [value]
    return value

def print_result_to_pdf(table, errors):

    for label, values in sorted(table.items()):
        values = list(map(surround_notlist_with_brakets, values))
        line = [[label]] + values
        if label in errors:
            line += generate_list_of_errors(errors[label])
        else:
            line += [[" "]]
        wfpdf.write_line(line, DEFAULT_HEIGHT, COLUMN_WIDTHS)

    for label, values in errors.items():
        if label in table:
            continue
        line = [[label], [0], [0], [0], [0],
                [0], [0], [0], [0], [0],
                [len(values)], [[100, RGB_BAD[2]]]] + generate_list_of_errors(label)
        wfpdf.write_line(line, DEFAULT_HEIGHT, COLUMN_WIDTHS)


def map_color_for_cell(cell):
    if not isinstance(cell, list):
        return cell

    if len(cell) < 2:
        return cell

    float_format = "%0.0f"

    if cell[1] == "nan":
        if cell[0] < 0:
            cell[0] = [float_format % cell[0], RGB_BAD[0]]
        elif cell[0] > 0:
            cell[0] = [float_format % cell[0], RGB_GOOD[0]]
        return cell

    cell[0] = float_format % cell[0]
    diff_percent = cell[1]

    border1 = 10
    border2 = 50
    border3 = 100

    sign_value = 1
    if diff_percent < 0:
        sign_value = -1
        rgb_list = RGB_BAD
        diff_percent = -diff_percent
    else:
        rgb_list = RGB_GOOD

    if border1 <= diff_percent < border2:
        cell[1] = [diff_percent, rgb_list[0]]
    elif border2 <= diff_percent < border3:
        cell[1] = [diff_percent, rgb_list[1]]
    elif border3 <= diff_percent:
        cell[1] = [diff_percent, rgb_list[2]]
    else:
        cell[1] = (float_format + " %%") % (sign_value*diff_percent)
        return cell

    cell[1][0] = (float_format + " %%") % (sign_value*cell[1][0])
    return cell


def print_png_to_pdf(count_of_png):
    for i in range(0, count_of_png):
        wfpdf.image("%s.png" % i)


def print_result_to_pdf_1_file(table, errors, filename, count_of_png=0):
    wfpdf.add_page()
    wfpdf.multi_cell(0, DEFAULT_HEIGHT, str("File %s" % filename), 0, "L")
    wfpdf.set_font(style="B")
    wfpdf.write_line(COLUMN_NAMES, DEFAULT_HEIGHT, COLUMN_WIDTHS)
    wfpdf.set_font(style="")
    print_result_to_pdf(table, errors)
    print_png_to_pdf(count_of_png)

    wfpdf.output(REPORTNAME % (os.path.basename(filename).replace(".", "_"), datetime.datetime.now().strftime('%Y%m%d_%H%M%S'), "pdf"), "F")


def print_result_to_pdf_file_and_zabbix(table_file, errors_file, filename,
                                        table_base_zabbix, datetime_from, datetime_to,
                                        table_compare, count_of_png=0):

    wfpdf.add_page()
    wfpdf.multi_cell(0, DEFAULT_HEIGHT, str("File %s" % filename), 0, "L")
    wfpdf.set_font(style="B")
    wfpdf.write_line(COLUMN_NAMES, DEFAULT_HEIGHT, COLUMN_WIDTHS)
    wfpdf.set_font(style="")
    print_result_to_pdf(table_file, errors_file)

    wfpdf.add_page()
    wfpdf.multi_cell(0, DEFAULT_HEIGHT, "Data from zabbix from %s to %s" % (datetime_from.strftime('%Y-%m-%d %H:%M:%S'), datetime_to.strftime('%Y-%m-%d %H:%M:%S')), 0, "L")
    wfpdf.set_font(style="B")
    wfpdf.write_line(COLUMN_NAMES, DEFAULT_HEIGHT, COLUMN_WIDTHS)
    wfpdf.set_font(style="")

    print_result_to_pdf(table_base_zabbix, errors_file)

    wfpdf.add_page()
    wfpdf.multi_cell(0, DEFAULT_HEIGHT, "Difference. Minus means worse - bigger time or lower HPS or count", 0, "L")
    wfpdf.multi_cell(0, DEFAULT_HEIGHT, "2 values: New - Old and perecent", 0, "L")
    wfpdf.set_font(style="B")
    wfpdf.write_line(COLUMN_NAMES, DEFAULT_HEIGHT, COLUMN_WIDTHS)
    wfpdf.set_font(style="")

    print_result_to_pdf(table_compare, errors_file)

    print_png_to_pdf(count_of_png)

    wfpdf.output(REPORTNAME % (os.path.basename(filename).replace(".", "_"), datetime.datetime.now().strftime('%Y%m%d_%H%M%S'), "pdf"), "F")

def print_result_to_pdf_2_files(table_new, errors_new, filename_new,
                                table_base, errors_base, filename_base,
                                table_compare):
    wfpdf.add_page()
    wfpdf.multi_cell(0, DEFAULT_HEIGHT, str("File %s" % filename_new), 0, "L")
    wfpdf.set_font(style="B")
    wfpdf.write_line(COLUMN_NAMES, DEFAULT_HEIGHT, COLUMN_WIDTHS)
    wfpdf.set_font(style="")
    print_result_to_pdf(table_new, errors_new)

    wfpdf.add_page()
    wfpdf.multi_cell(0, DEFAULT_HEIGHT, "File %s" % filename_base, 0, "L")
    wfpdf.set_font(style="B")
    wfpdf.write_line(COLUMN_NAMES, DEFAULT_HEIGHT, COLUMN_WIDTHS)
    wfpdf.set_font(style="")
    print_result_to_pdf(table_base, errors_base)

    wfpdf.add_page()
    wfpdf.multi_cell(0, DEFAULT_HEIGHT, "Difference. Minus means worse - bigger time or lower HPS or count", 0, "L")
    wfpdf.multi_cell(0, DEFAULT_HEIGHT, "2 values: New - Old and perecent", 0, "L")
    wfpdf.set_font(style="B")
    wfpdf.write_line(COLUMN_NAMES, DEFAULT_HEIGHT, COLUMN_WIDTHS)
    wfpdf.set_font(style="")
    print_result_to_pdf(table_compare, errors_new)

    wfpdf.output(REPORTNAME % (os.path.basename(filename_new).replace(".", "_"), datetime.datetime.now().strftime('%Y%m%d_%H%M%S'), "pdf"), "F")