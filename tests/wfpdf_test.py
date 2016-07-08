# -*- coding: utf-8 -*-

import unittest
from wfpdf import WFPDF
import sys
import matplotlib.pyplot as plt
import numpy as np


class Testwfpdf(unittest.TestCase):

    def test_1_emptypage(self):
        this_function_name = sys._getframe().f_code.co_name
        print("Start test %s" % this_function_name)

        pdf = WFPDF(orientation="P", unit="pt", format="A4")
        pdf.add_page()

        pdf.output(this_function_name+".pdf", "F")

    def test_2_multi_cell(self):
        this_function_name = sys._getframe().f_code.co_name
        print("Start test %s" % this_function_name)

        pdf = WFPDF(orientation="P", unit="pt", format="A4")
        pdf.add_page()

        pdf.multi_cell(w=0, h=20, txt="Отчет за период ")

        pdf.output(this_function_name+".pdf", "F")

    def test_3_write_line(self):
        this_function_name = sys._getframe().f_code.co_name
        print("Start test %s" % this_function_name)

        default_width_text_groups = 150
        default_width_text = 230
        default_width_number = 75

        column_widths = [default_width_text_groups,
                         default_width_text,
                         default_width_number,
                         default_width_number,
                         default_width_number,
                         default_width_number,
                         default_width_number,
                         default_width_number,
                         default_width_number,
                         default_width_number,
                         default_width_number,
                         default_width_number,
                         default_width_number,
                         default_width_number]

        column_names = [["Группа параметров"],
                        ["Параметр"],
                        ["Среднее (сек)"],
                        ["Среднее 90% (сек)"],
                        ["50% percentile"],
                        ["80% percentile"],
                        ["90% percentile"],
                        ["95% percentile"],
                        ["99% percentile"],
                        ["Доступность (%)"],
                        ["Кол-во сбоев (шт)"],
                        ["Кол-во проверок (шт)"],
                        ["Средняя нагрузка (Mbps)"],
                        ["Максимальная нагрузка (Mbps)"]]
        pdf_page_width = 1500
        pdf_page_height = 2000
        pdf = WFPDF(orientation="P", unit="pt", format=(pdf_page_width, pdf_page_height))
        pdf.add_page()

        pdf.set_font(style="B")
        pdf.write_line(column_names, default_row_height=20, list_of_column_widths=column_widths)

        pdf.output(this_function_name+".pdf", "F")

    def test_4_write_multiline(self):
        this_function_name = sys._getframe().f_code.co_name
        print("Start test %s" % this_function_name)

        default_width_text = 230

        column_widths = [2*default_width_text/3, default_width_text, default_width_text*1.4]
        column_names = [["Группа параметров"], ["Параметр"], ["URL"]]

        pdf_page_width = 1500
        pdf_page_height = 2000
        pdf = WFPDF(orientation="P", unit="pt", format=(pdf_page_width, pdf_page_height))
        pdf.add_page()

        pdf.set_font(style="B")
        pdf.write_line(column_names, default_row_height=20, list_of_column_widths=column_widths)
        pdf.set_font(style="")

        group_count = 10
        for i in range(0, group_count):
            names = [[]]
            urls = [[]]
            for j in range(0, 5):
                names[0] += ["name"+str(j)]
                urls[0] += ["url"+str(j)]
            line = [["group"+str(i)]] + names + urls
            pdf.write_line(line, default_row_height=20, list_of_column_widths=column_widths)

        for i in range(0, group_count):
            groups = [[]]
            urls = [[]]
            for j in range(0, 5):
                groups[0] += ["group"+str(j)]
                urls[0] += ["url"+str(j)]
            line = groups + [["name"+str(i)]] + urls
            pdf.write_line(line, default_row_height=20, list_of_column_widths=column_widths)

        for i in range(0, group_count):
            groups = [[]]
            names = [[]]
            for j in range(0, 5):
                groups[0] += ["group"+str(j)]
                names[0] += ["url"+str(j)]
            line = groups + names + [["url"+str(i)]]
            pdf.write_line(line, default_row_height=20, list_of_column_widths=column_widths)

        pdf.output(this_function_name+".pdf", "F")

    def test_5_write_multiline_page_split(self):
        this_function_name = sys._getframe().f_code.co_name
        print("Start test %s" % this_function_name)

        default_width_text = 230

        column_widths = [2*default_width_text/3, default_width_text, default_width_text*1.4]
        column_names = [["Группа параметров"], ["Параметр"], ["URL"]]

        pdf_page_width = 1500
        pdf_page_height = 200
        pdf = WFPDF(orientation="P", unit="pt", format=(pdf_page_width, pdf_page_height))
        pdf.add_page()

        pdf.set_font(style="B")
        pdf.write_line(column_names, default_row_height=20, list_of_column_widths=column_widths)
        pdf.set_font(style="")

        group_count = 10
        for i in range(0, group_count):
            names = [[]]
            urls = [[]]
            for j in range(0, 5):
                names[0] += ["namenamenamenamenamenamenamenamenamenamenamenamenamenamenamenamenamename"+str(j)]
                urls[0] += ["ururlurlurlurlurlurlurlurlurlurlurlurlurlurlurlurlurlurlurlurlurlurll"+str(j)]
            line = [["grougroupgroupgroupgroupgroupgroupgroupgroupgroupgroupgroupgroupgroupgroupp"+str(i)]] + names + urls
            pdf.write_line(line, default_row_height=20, list_of_column_widths=column_widths)

        pdf.output(this_function_name+".pdf", "F")

    def test_6_write_image(self):
        this_function_name = sys._getframe().f_code.co_name
        print("Start test %s" % this_function_name)

        pdf_page_width = 1500
        pdf_page_height = 2000
        pdf = WFPDF(orientation="P", unit="pt", format=(pdf_page_width, pdf_page_height))
        pdf.add_page()

        # Make a quick sin plot
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        plt.plot(x, y)
        plt.xlabel("Time")
        plt.ylabel("Amplitude")

        plt.savefig("signal.png")

        pdf.image("signal.png", x=None, y=None, w=0, h=0)

        pdf.output(this_function_name+".pdf", "F")


    def test_7_color_line(self):
        this_function_name = sys._getframe().f_code.co_name
        print("Start test %s" % this_function_name)

        default_width_text = 230

        column_widths = [2*default_width_text/3, default_width_text, default_width_text*1.4]
        column_names = [["Группа параметров"], ["Параметр"], ["URL"]]

        pdf_page_width = 1500
        pdf_page_height = 2000
        pdf = WFPDF(orientation="P", unit="pt", format=(pdf_page_width, pdf_page_height))
        pdf.add_page()

        pdf.set_font(style="B")
        pdf.write_line(column_names, default_row_height=20, list_of_column_widths=column_widths)
        pdf.set_font(style="")

        group_count = 10
        for i in range(0, group_count):
            names = [[]]
            urls = [[]]
            for j in range(0, 5):
                names[0] += [["namenamenamenamenamenamenamenamenamenamenamenamenamenamenamenamenamename"+str(j), (102, 255, 102)]]
                urls[0] += ["ururlurlurlurlurlurlurlurlurlurlurlurlurlurlurlurlurlurlurlurlurlurll"+str(j)]
            line = [[["grougroupgroupgroupgroupgroupgroupgroupgroupgroupgroupgroupgroupgroupgroupp"+str(i), (102, 102, 255)]]] + names + urls
            pdf.write_line(line, default_row_height=20, list_of_column_widths=column_widths)

        pdf.output(this_function_name+".pdf", "F")



if __name__ == '__main__':
    unittest.main()