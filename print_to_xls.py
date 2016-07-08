# _*_ coding: utf-8
import os
import datetime
import xlsxwriter
from PIL import Image

import calc_statistics

# INSTALL INFO #########################################################################################################
# this dependencies required to use Pillow on rhel
# yum install libjpeg-turbo-devel
# then use
# chmod -R 777 /usr/local/lib/python2.7/site-packages
# INSTALL INFO #########################################################################################################

COLUMN_NAMES = ["Name", "OK cnt", "Min", "Avg", "p50%",
                "p80%", "p90%", "p95%", "p99%", "HPS",
                "Err cnt", "Err %", "(Error count) Error text"]


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

        table[label] = line
    return table


def generate_list_of_errors(errors):
    set_val_arr = set(errors)
    line_errors = [[]]
    for err in set_val_arr:
        line_errors[0] += ["(%d) %s" % (errors.count(err), err)]
    return line_errors


def insert_img_to_sheet(sheet, count_of_png):
    row = 0
    for i in range(0, count_of_png):
        size = Image.open('%s.png' % i).size
        sheet.insert_image(row, 0, "%s.png" % i, {'positioning': 3})
        row += int(size[1])/20


def print_result_to_xlsx_1_file(table, errors, filename, count_of_png=0):
    dt = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    wb = xlsxwriter.Workbook(os.path.basename(filename).replace(".", "_") + '_' + dt + '.xlsx')
    stat_sheet = wb.add_worksheet('Statistics')
    row, col = 0, 0
    style_for_header = make_document_header_style(wb, stat_sheet)
    for name in COLUMN_NAMES:
        stat_sheet.write(row, col, str(name), style_for_header)
        col += 1
    row += 1
    col = 0

    for part in table.items():
        sample_name = eval('part[0]')
        error_count = part[1][-1]
        stat_sheet.write(row, col, sample_name)
        for el_in_list in part[1]:
            col += 1
            stat_sheet.write(row, col, el_in_list)
        if error_count != 0.0:
            col += 1
            for label, error_list in errors.items():
                if sample_name == eval('label'):
                    generated_err_list = generate_list_of_errors(error_list)
                    #print 'generated for label: ' + eval(u'sample_name') + ' ' + str(generate_list_of_errors(error_list))
                    for err in generated_err_list:
                        stat_sheet.write(row, col, str(err))
        row += 1
        col = 0
    graphs_sheet = wb.add_worksheet('Graphs')
    make_graphs_style(graphs_sheet)
    insert_img_to_sheet(graphs_sheet, count_of_png)
    print('output xlsx file: ' + os.path.basename(filename).replace(".", "_") + '_' + dt + '.xlsx')
    wb.close()


def print_result_to_xlsx_2_file(table, errors, filename, table_new, errors_new, filename_new, table_compare, errors_compare):
    dt = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    wb = xlsxwriter.Workbook(os.path.basename(filename).replace(".", "_") + '_VS_' + os.path.basename(filename_new).replace(".", "_") + '_' + dt + '.xlsx')
    stat_sheet = wb.add_worksheet('Statistics new')
    row, col = 0, 0
    style_for_header = make_document_header_style(wb, stat_sheet)
    for name in COLUMN_NAMES:
        stat_sheet.write(row, col, str(name), style_for_header)
        col += 1
    row += 1
    col = 0

    for part in table.items():
        sample_name = eval('part[0]')
        error_count = part[1][-1]
        stat_sheet.write(row, col, sample_name)
        for el_in_list in part[1]:
            col += 1
            stat_sheet.write(row, col, el_in_list)
        if error_count != 0.0:
            col += 1
            for label, error_list in errors.items():
                if sample_name == eval('label'):
                    generated_err_list = generate_list_of_errors(error_list)
                    #print 'generated for label: ' + eval(u'sample_name') + ' ' + str(generate_list_of_errors(error_list))
                    for err in generated_err_list:
                        stat_sheet.write(row, col, str(err))
        row += 1
        col = 0

    #Second File     ###################################################################################################
    stat_sheet2 = wb.add_worksheet('Statistics old')
    style_for_header2 = make_document_header_style(wb, stat_sheet2)
    row, col = 0, 0
    for name in COLUMN_NAMES:
        stat_sheet2.write(row, col, str(name), style_for_header2)
        col += 1
    row += 1
    col = 0

    for part in table_new.items():
        sample_name = eval('part[0]')
        error_count = part[1][-1]
        stat_sheet2.write(row, col, sample_name)
        for el_in_list in part[1]:
            col += 1
            stat_sheet2.write(row, col, el_in_list)
        if error_count != 0.0:
            col += 1
            for label, error_list in errors_new.items():
                if sample_name == eval('label'):
                    generated_err_list = generate_list_of_errors(error_list)
                    #print 'generated for label: ' + eval(u'sample_name') + ' ' + str(generate_list_of_errors(error_list))
                    for err in generated_err_list:
                        stat_sheet2.write(row, col, str(err))
        row += 1
        col = 0

    #Comparative          ###################################################################################################
    stat_sheet3 = wb.add_worksheet('Comparative new -> old')
    style_for_header3 = make_document_header_style(wb, stat_sheet3)
    row, col = 0, 0
    for name in COLUMN_NAMES:
        stat_sheet3.write(row, col, str(name), style_for_header3)
        col += 1
    row += 1
    col = 0

    for part in table_compare.items():
        # print 'Compare -->> ' + str(part)
        sample_name = eval('part[0]')
        error_count = part[1][-1]
        stat_sheet3.write(row, col, sample_name)
        for el_in_list in part[1]:
            col += 1
            # print 'EL in LIST -->> ' + str(el_in_list)
            float_format = "%0.0f"
            diff = float_format % float(el_in_list[0])
            if len(el_in_list) > 1:
                diff_percents = float_format % float(el_in_list[1])
            else:
                diff_percents = "NaN"
            stat_sheet3.write(row, col, '(' + diff + ') ' + diff_percents + '%')
        if error_count != 0.0:
            col += 1
            for label, error_list in errors_compare.items():
                if sample_name == eval('label'):
                    generated_err_list = generate_list_of_errors(error_list)
                    #print 'generated for label: ' + eval(u'sample_name') + ' ' + str(generate_list_of_errors(error_list))
                    for err in generated_err_list:
                        stat_sheet3.write(row, col, str(err))
        row += 1
        col = 0
    print('output xlsx file: ' + os.path.basename(filename).replace(".", "_") + '_VS_' + os.path.basename(filename_new).replace(".", "_") + '_' + dt + '.xlsx')
    wb.close()


def print_result_to_xlsx_1_file_and_zabbix(table_file, errors_file, filename,
                                        table_base_zabbix, datetime_from, datetime_to,
                                        table_compare, count_of_png=0):
    dt = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    wb = xlsxwriter.Workbook(os.path.basename(filename).replace(".", "_") + '_zabbix_7days' + '_' + dt + '.xlsx')
    stat_sheet = wb.add_worksheet('Statistics new')
    row, col = 0, 0
    style_for_header = make_document_header_style(wb, stat_sheet)
    for name in COLUMN_NAMES:
        stat_sheet.write(row, col, str(name), style_for_header)
        col += 1
    row += 1
    col = 0

    for part in table_file.items():
        # print part
        sample_name = eval('part[0]')
        error_count = part[1][-1]
        stat_sheet.write(row, col, sample_name)
        for el_in_list in part[1]:
            col += 1
            stat_sheet.write(row, col, el_in_list)
        if error_count != 0.0:
            col += 1
            for label, error_list in errors_file.items():
                if sample_name == eval('label'):
                    generated_err_list = generate_list_of_errors(error_list)
                    #print 'generated for label: ' + eval(u'sample_name') + ' ' + str(generate_list_of_errors(error_list))
                    for err in generated_err_list:
                        stat_sheet.write(row, col, str(err))
        row += 1
        col = 0

    #Second File     ###################################################################################################
    stat_sheet2 = wb.add_worksheet('Statistics from zabbix 7 days')
    style_for_header2 = make_document_header_style(wb, stat_sheet2)
    row, col = 0, 0
    for name in COLUMN_NAMES:
        stat_sheet2.write(row, col, str(name), style_for_header2)
        col += 1
    row += 1
    col = 0

    for part in table_base_zabbix.items():
        sample_name = eval('part[0]')
        error_count = part[1][-1]
        stat_sheet2.write(row, col, sample_name)
        for el_in_list in part[1]:
            col += 1
            stat_sheet2.write(row, col, el_in_list)
        if error_count != 0.0:
            col += 1
            for label, error_list in errors_file.items():
                if sample_name == eval('label'):
                    generated_err_list = generate_list_of_errors(error_list)
                    #print 'generated for label: ' + eval(u'sample_name') + ' ' + str(generate_list_of_errors(error_list))
                    for err in generated_err_list:
                        stat_sheet2.write(row, col, str(err))
        row += 1
        col = 0

    #Comparative          ###################################################################################################
    stat_sheet3 = wb.add_worksheet('Comparative new -> zabbix')
    style_for_header3 = make_document_header_style(wb, stat_sheet3)
    row, col = 0, 0
    for name in COLUMN_NAMES:
        stat_sheet3.write(row, col, str(name), style_for_header3)
        col += 1
    row += 1
    col = 0

    for part in table_compare.items():
        # print 'Compare -->> ' + str(part)
        sample_name = eval('part[0]')
        error_count = part[1][-1]
        stat_sheet3.write(row, col, sample_name)
        for el_in_list in part[1]:
            col += 1
            #print 'EL in LIST -->> ' + str(el_in_list)
            float_format = "%0.0f"
            diff = float_format % float(el_in_list[0]) if len(el_in_list) == 2 else '0' # somewhere in zabbix we have to chance to gen 'nan' instead of [0.0, 'nan']
            diff_percents = float_format % float(el_in_list[1]) if len(el_in_list) == 2 else '0' # same here
            stat_sheet3.write(row, col, '(' + diff + ') ' + diff_percents + '%')
        if error_count != 0.0:
            col += 1
            for label, error_list in errors_file.items():
                if sample_name == eval('label'):
                    generated_err_list = generate_list_of_errors(error_list)
                    print('generated for label: ' + eval('sample_name') + ' ' + str(generate_list_of_errors(error_list)))
                    for err in generated_err_list:
                        stat_sheet3.write(row, col, str(err))
        row += 1
        col = 0
    graphs_sheet = wb.add_worksheet('Graphs new')
    make_graphs_style(graphs_sheet)
    insert_img_to_sheet(graphs_sheet, count_of_png)
    print('output xlsx file: ' + os.path.basename(filename).replace(".", "_") + '_zabbix_7days' + '_' + dt + '.xlsx')
    wb.close()


def make_document_header_style(workbook, worksheet):
    bold = workbook.add_format()
    bold.set_bold()
    bold.set_color('white')
    bold.set_border()
    bold.set_bg_color('black')
    for col in range(0, len(COLUMN_NAMES)):
        worksheet.set_column(col, col, 12)
    worksheet.set_column(0, 0, 50)
    return bold


def make_graphs_style(worksheet):
    worksheet.set_column(0, 0, 200) # make col bigger so graphs are in 100% scale





