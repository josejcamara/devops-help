""" Manage Spreadsheets """

# pylint: disable=import-error
# pyright: reportMissingImports=false, reportMissingModuleSource=false

import openpyxl


class Spreadsheet:
    """ Excel Spreadsheet Management """

    def __init__(self):
        # Creats empty workbook
        wb = openpyxl.Workbook()

        self.wb = wb
        self.sheets = {}
        self.data = {}

    def add_sheet(self, sheet_id, data=None):
        """ Add Sheet with optional data """
        if data is None:
            data = []
        sheet = self.wb.create_sheet(sheet_id)

        self.sheets[sheet_id] = sheet
        self.data[sheet_id] = data

        return sheet

    def set_sheet_data(self, sheet_id, data):
        """ Set the spreadsheet data """
        self.data[sheet_id] = data

    def add_sheet_data(self, sheet_id, data):
        """ Add data to the spreadsheet """
        self.data[sheet_id].extend(data)

    def save(self, filename):
        """ Save to a file """
        for sid, sheet in self.sheets.items():
            for row in self.data[sid]:
                sheet.append(row)

        self.wb.save(filename)


if __name__ == "__main__":
    xls1 = Spreadsheet()

    print('Enter the demo filename to create:')
    namefile = input()

    XID1 = "sheet1"
    xls1.add_sheet(XID1)

    data1 = [["Title1", "Title2"], ["row1_col1", "row1_col2"]]
    xls1.set_sheet_data(XID1, data1)

    if not namefile.endswith('xlsx'):
        namefile = namefile + '.xlsx'

    xls1.save(namefile)
