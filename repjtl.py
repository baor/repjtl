'''

example:
python repjtl.py example2.jtl example3.jtl


Attribute	Content
by	Bytes
de	Data encoding
dt	Data type
ec	Error count (0 or 1, unless multiple samples are aggregated)
hn	Hostname where the sample was generated
it	Idle Time = time not spent sampling (milliseconds) (generally 0)
lb	Label
lt	Latency = time to initial response (milliseconds) - not all samplers support this
ct	Connect Time = time to establish the connection (milliseconds) - not all samplers support this
na	Number of active threads for all thread groups
ng	Number of active threads in this group
rc	Response Code (e.g. 200)
rm	Response Message (e.g. OK)
s	Success flag (true/false)
sc	Sample count (1, unless multiple samples are aggregated)
t	Elapsed time (milliseconds)
tn	Thread Name
ts	timeStamp (milliseconds since midnight Jan 1, 1970 UTC)
varname	Value of the named variable (versions of JMeter after 2.3.1)

Setup:

pip install lxml argparse numpy fpdf math

ubuntu: sudo apt-get install libpng-dev libfreetype6-dev
rhel: yum install freetype libpng-devel freetype-devel

then -->>

pip install matplotlib
'''

from lxml import etree
import datetime
import argparse
import parse_jtl
import calc_statistics
import time
import print_to_pdf
import print_to_xls
import plotgraphs

REPORTNAME = "rep_" + str(datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))

def compate_tables_to_table(table_new, table_base):

    print("Compare tables")
    table = {}
    for label, values_base in sorted(table_base.items()):
        print("Compare for label %s" % str(label).encode("UTF-8"))

        line = [[0], [0], [0], [0], [0],
                [0], [0], [0], [0], [0],
                [0]]

        if label in table_new:
            line = list(map(calc_statistics.percent_diff_time, table_new[label], values_base))
            line[0][0] = -line[0][0] #samples count diff
            if line[0][1] != "nan":
                line[0][1] = -line[0][1] #samples count percent diff

            line[8][0] = -line[8][0] #hps diff
            if line[8][1] != "nan":
                line[8][1] = -line[8][1] #hps percent diff

            line = list(map(print_to_pdf.map_color_for_cell, line))
        table[label] = line
    return table

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process jtl files.')
    parser.add_argument('files', nargs='+', help='an list of files(1 or 2)')
    parser.add_argument('--trc_only', help='report only transactions', action='store_true')
    parser.add_argument('--no_graphs', help='disable graphs', action='store_true')
    args = parser.parse_args()

    if len(args.files) == 1:
        etree_from_file = etree.iterparse(args.files[0], tag=('testResults'), encoding='utf-8')
        labels, thread_groups = parse_jtl.parse_tree_into_labels_and_threads_dict(etree_from_file, args.trc_only)
        table_new = calc_statistics.calculate_values_to_table_and_errors(labels)

        if args.no_graphs:
            count_of_png = 0
        else:
            count_of_png = plotgraphs.generate_graphs_for_threads(thread_groups)
            count_of_png = plotgraphs.generate_graphs_for_labels_and_threads(labels, thread_groups, count_of_png)


        print_to_pdf.print_result_to_pdf_1_file(table_new, parse_jtl.get_errors_from_labels(labels), args.files[0], count_of_png)
        print_to_xls.print_result_to_xlsx_1_file(table_new, parse_jtl.get_errors_from_labels(labels), args.files[0], count_of_png)

    elif len(args.files) == 2:
        labels_new, thread_groups = parse_jtl.parse_tree_into_labels_and_threads_dict(etree.iterparse(args.files[0], tag=('testResults')))
        table_new = calc_statistics.calculate_values_to_table_and_errors(labels_new)

        labels_base, thread_groups = parse_jtl.parse_tree_into_labels_and_threads_dict(etree.iterparse(args.files[1], tag=('testResults')))
        table_base = calc_statistics.calculate_values_to_table_and_errors(labels_base)

        table_compare = compate_tables_to_table(table_new, table_base)
        table_compare_xls = print_to_xls.compate_tables_to_table(table_new, table_base)

        print_to_pdf.print_result_to_pdf_2_files(table_new, parse_jtl.get_errors_from_labels(labels_new), args.files[0],
                                                 table_base, parse_jtl.get_errors_from_labels(labels_base), args.files[1],
                                                 table_compare)
        print_to_xls.print_result_to_xlsx_2_file(table_new, parse_jtl.get_errors_from_labels(labels_new), args.files[0],
                                                 table_base, parse_jtl.get_errors_from_labels(labels_base), args.files[1],
                                                 table_compare_xls, parse_jtl.get_errors_from_labels(labels_new))
    else:
        print("Args error!")
