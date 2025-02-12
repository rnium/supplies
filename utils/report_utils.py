from odoo.api import Environment
import xlsxwriter
import base64
import tempfile
from io import BytesIO
from base64 import encodebytes
from typing import Iterable
from datetime import datetime


def generate_excel_report(env: Environment, supplier, accepted_rfps: Iterable) -> bytes:
    """
    Generate the Excel report
    """
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()
    ROW_OFFSET = 1
    COL_OFFSET = 1
    common_style_config = {
        'align': 'center',
        'valign': 'vcenter',
        'font_name': 'Arial',
    }
    key_cell_style_config = {
        **common_style_config,
        'bold': True,
        'border': 1,
    }
    value_cell_style_config = {
        **common_style_config,
        'border': 1,
    }
    header_style_config = {
        **common_style_config,
        'bold': True,
        'border': 0,
        'font_size': 12,
    }

    def insert_vendor_info():
        nonlocal ROW_OFFSET
        nonlocal COL_OFFSET
        COL_OFFSET = 4
        bank_ac = supplier.bank_ids[0] if supplier.bank_ids else None
        bank = bank_ac.bank_id if bank_ac else None
        nonlocal value_cell_style_config
        nonlocal key_cell_style_config
        vendor_info = {
            'Email': supplier.email or 'N/A',
            'Phone': supplier.phone or 'N/A',
            'Address': supplier.street or 'N/A',
            'TIN': supplier.vat or 'N/A',
            'Bank': bank_ac.bank_name if bank_ac else 'N/A',
            'IBAN No.': (bank.iban or 'N/A') if bank else 'N/A',
            'Swift Code': (bank.swift_code or 'N/A') if bank else 'N/A',
            'Account name': (bank_ac.acc_holder_name or 'N/A') if bank_ac else 'N/A',
            'Account number': (bank_ac.acc_number or 'N/A') if bank_ac else 'N/A',
        }

        worksheet.merge_range(ROW_OFFSET, COL_OFFSET, ROW_OFFSET, COL_OFFSET + 1, supplier.name, workbook.add_format(header_style_config))
        ROW_OFFSET += 1
        for i, (key, value) in enumerate(vendor_info.items()):
            ROW_OFFSET += 1
            worksheet.write(ROW_OFFSET, COL_OFFSET, key, workbook.add_format(key_cell_style_config))
            worksheet.write(ROW_OFFSET, COL_OFFSET + 1, value, workbook.add_format(value_cell_style_config))
        worksheet.set_column(COL_OFFSET, COL_OFFSET, 20)
        worksheet.set_column(COL_OFFSET + 1, COL_OFFSET + 1, 35)
        COL_OFFSET = 1 # reset back to 1

    def insert_rfps():
        nonlocal ROW_OFFSET
        nonlocal COL_OFFSET
        ROW_OFFSET += 3
        header = ['RFP Number', 'Date', 'Required Date', 'Total Amount']
        rfp_data = [
            [
                rfp.rfp_number,
                datetime.strftime(rfp.submitted_date, '%d-%m-%Y'),
                datetime.strftime(rfp.required_date, '%d-%m-%Y'),
                rfp.total_amount
            ] for rfp in accepted_rfps
        ]
        worksheet.merge_range(ROW_OFFSET, COL_OFFSET, ROW_OFFSET, COL_OFFSET + len(header) - 1, 'Accepted RFPs', workbook.add_format(header_style_config))
        ROW_OFFSET += 1
        for i, cell in enumerate(header):
            worksheet.write(ROW_OFFSET, COL_OFFSET + i, cell, workbook.add_format(key_cell_style_config))
        for i, row in enumerate(rfp_data):
            ROW_OFFSET += 1
            for j, cell in enumerate(row):
                worksheet.write(ROW_OFFSET, COL_OFFSET + j, cell, workbook.add_format(value_cell_style_config))
        worksheet.set_column(COL_OFFSET, COL_OFFSET + len(rfp_data[0]) - 1, 20)

    # insert elements
    logo_data = base64.b64decode(env.company.logo)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_logo_file:
        temp_logo_file.write(logo_data)
        file_path = temp_logo_file.name
        worksheet.insert_image('A1', file_path, {
            'x_scale': 0.5,
            'y_scale': 0.5,
        })
    insert_vendor_info()
    insert_rfps()
    # close workbook and return the data
    workbook.close()
    output.seek(0)
    data = encodebytes(output.read())
    return data