# -*- coding: utf-8 -*-

from fpdf import *
import numpy as np
import math


class WFPDF(FPDF):

    def __init__(self, orientation="P", unit="mm", format="A4", path_to_font_dir="."):
        self.font_family = "DejaVu"
        self.font_size = 8
        self.float_format = "%.2f"

        self.wrapped_fpdf = FPDF(orientation, unit, format)
        self.wrapped_fpdf.add_font(self.font_family, "", path_to_font_dir + "/font/DejaVuSansCondensed.ttf", uni=True)
        self.wrapped_fpdf.add_font(self.font_family, "B", path_to_font_dir + "/font/DejaVuSansCondensed-Bold.ttf", uni=True)
        self.wrapped_fpdf.set_font(self.font_family, '', self.font_size)
        self.wrapped_fpdf.set_margins(20, 0)

    def text_formatter(self, text):
        if isinstance(text, list):
            return [self.text_formatter(text[0])] + text[1:]

        if isinstance(text, float) or isinstance(text, np.float64):
            return self.float_format % text
        if isinstance(text, str):
            return text.encode("UTF-8")
        return str(text)

    def count_of_lines_in_text(self, text, column_width):
        if isinstance(text, list):
            text = text[0]
        if isinstance(text, (bytes, bytearray)):
            text = str(text, 'utf-8')
        print(text)
        return int(math.ceil(self.wrapped_fpdf.get_string_width(text)/(column_width*0.9))) + text.count("\n")

    def _draw_rect(self, x, y, w, h, draw_top=True):
        # only left and right lines
        self.wrapped_fpdf.rect(x, y, 0, h)
        self.wrapped_fpdf.rect(x+w, y, 0, h)
        if draw_top:
            self.wrapped_fpdf.rect(x, y, w, 0)

    def add_cell(self, data_cell, default_row_height, column_width):
        old_x = self.wrapped_fpdf.get_x()
        old_y = self.wrapped_fpdf.get_y()

        rect_height = data_cell[1]*default_row_height
        is_fill = False
        text = ""
        if isinstance(data_cell[0], str):
            text = data_cell[0]
        elif isinstance(data_cell[0], list):
            is_fill = True
            text = data_cell[0][0]
            r, g, b = data_cell[0][1]
            self.wrapped_fpdf.set_fill_color(r, g, b)


        self._draw_rect(old_x, old_y, column_width, rect_height, text != "")
        if isinstance(text, (bytes, bytearray)):
            text = str(text, 'utf-8')
        self.wrapped_fpdf.multi_cell(column_width, default_row_height, text, border="0", align="L", fill=is_fill)

        new_y = self.wrapped_fpdf.get_y()

        self.wrapped_fpdf.set_xy(old_x + column_width, old_y)
        return new_y

    def list_of_subrows_for_row(self, row_cells, list_of_column_widths):
        """
        :param row_cells: list of columns
                        format [[["00"]],[["10"], ["11"]], [["20"], ["21"], ["22"]]]

        :param list_of_column_widths:
                        format ["10", "20", "30"]

        :return: list of subrows, appended with empty cells
                        format [[["00"], ["10"], ["20"]], [[""], ["11"], ["21"]], [[""], [""], ["22"]]]

        """
        col_count = len(row_cells)
        row_count = 0
        for cell_1_level in row_cells:
            if len(cell_1_level) > row_count:
                row_count = len(cell_1_level)

        list_subrows = [[["", 0] for row_indx in range(0, row_count)] for col_indx in range(0, col_count)]
        # append matrix with Nones
        for row_indx in range(0, row_count):
            max_lines_count_in_row = 0
            for col_indx in range(0, col_count):
                if row_indx >= len(row_cells[col_indx]):
                    continue
                lines_count = self.count_of_lines_in_text(self.text_formatter(row_cells[col_indx][row_indx]), list_of_column_widths[col_indx])
                if lines_count > max_lines_count_in_row:
                    max_lines_count_in_row = lines_count

            for col_indx in range(0, col_count):
                if row_indx < len(row_cells[col_indx]):
                    list_subrows[col_indx][row_indx] = [self.text_formatter(row_cells[col_indx][row_indx]), max_lines_count_in_row]
                else:
                    list_subrows[col_indx][row_indx] = ["", max_lines_count_in_row]
        return list_subrows

    def add_cells_row(self, list_of_subrows, column_indx, default_row_height, list_of_column_widths):
        max_y = 0
        for row_indx in range(0, len(list_of_subrows)):
            curr_y = self.add_cell(list_of_subrows[row_indx][column_indx], default_row_height, list_of_column_widths[row_indx])
            if curr_y > max_y:
                max_y = curr_y
        return max_y

    def write_line(self, row_cells, default_row_height, list_of_column_widths):
        list_of_subrows = self.list_of_subrows_for_row(row_cells, list_of_column_widths)

        start_x = self.wrapped_fpdf.get_x()
        new_y = 0

        columns_count = len(list_of_subrows[0])
        for column_indx in range(0, columns_count):
            self.wrapped_fpdf.set_auto_page_break(False, self.wrapped_fpdf.t_margin)

            new_y = self.add_cells_row(list_of_subrows, column_indx, default_row_height, list_of_column_widths)

            if new_y > self.wrapped_fpdf.h:
                self.add_page()
                new_y = self.add_cells_row(list_of_subrows, column_indx, default_row_height, list_of_column_widths)

            self.wrapped_fpdf.set_xy(start_x, new_y)

        # draw last bottom line
        total_width = 0
        for w in list_of_column_widths:
            total_width += w
        self.wrapped_fpdf.rect(start_x, new_y, total_width, 0)

    @staticmethod
    def convert_list_of_rows_to_list_of_columns(list):
        """

        :param list: [[["00"], ["01"], ["02"]],
                      [["10"], ["11"], ["12"]],
                      [["20"], ["21"], ["22"]]]

        :return:     [[["00"], ["10"], ["20"]],
                      [["01"], ["11"], ["21"]],
                      [["02"], ["12"], ["22"]]]
        """
        row_count = len(list)
        col_count = len(list[0])
        list_col = [[[""] for i in range(0, row_count)] for j in range(0, col_count)]
        for i in range(0, row_count):
            for j in range(0, col_count):
                list_col[j][i] = list[i][j]
        return list_col

    def set_font(self, style="", size=0):
        if size == 0:
            size = self.font_size
        self.wrapped_fpdf.set_font(self.font_family, style, size)

    def add_page(self):
        self.wrapped_fpdf.add_page()

    def output(self, name="", dest=""):
        print("output file %s" % name)
        self.wrapped_fpdf.output(name, dest)

    def multi_cell(self, w, h, txt="", border=0, align="J", fill=0, split_only=False):
        self.wrapped_fpdf.multi_cell(w, h, txt, border, align, fill, split_only)

    def image(self, *args, **kwargs):
        self.wrapped_fpdf.set_auto_page_break(True)
        self.wrapped_fpdf.image(*args, **kwargs)
