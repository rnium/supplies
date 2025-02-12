from odoo.api import Environment
import xlsxwriter
import base64
import tempfile
from io import BytesIO
from base64 import encodebytes


def generate_excel_report(env: Environment, supplier) -> bytes:
    """
    Generate the excel report
    """
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()
    logo_data = base64.b64decode(env.company.logo)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_logo_file:
        temp_logo_file.write(logo_data)
        file_path = temp_logo_file.name
        worksheet.insert_image('A1', file_path, {
            'x_scale': 0.5,
            'y_scale': 0.5,
        })
    common_style_config = {
        'align': 'center',
        'valign': 'vcenter',
        'font_name': 'Arial',
    }
    def insert_vendor_info():
        col_offset = 4
        row_offset = 1
        bank_ac = supplier.bank_ids[0] if supplier.bank_ids else None
        header_style_config = {
            **common_style_config,
            'bold': True,
            'border': 0,
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
        vendor_info = {
            'Email': supplier.email or '<N/A>',
            'Phone': supplier.phone or '<N/A>',
            'Address': supplier.street or '<N/A>',
            'TIN': supplier.vat or '<N/A>',
            'Bank': bank_ac.bank_name if bank_ac else '<N/A>',
            'Account name': (bank_ac.acc_holder_name or '<N/A>') if bank_ac else '<N/A>',
            'Account number': (bank_ac.acc_number or '<N/A>') if bank_ac else '<N/A>',
        }
        worksheet.merge_range(row_offset, col_offset, row_offset, col_offset + 1, supplier.name, workbook.add_format(header_style_config))
        row_offset += 2
        for i, (key, value) in enumerate(vendor_info.items()):
            worksheet.write(row_offset + i, col_offset, key, workbook.add_format(key_cell_style_config))
            worksheet.write(row_offset + i, col_offset + 1, value, workbook.add_format(value_cell_style_config))
        worksheet.set_column(col_offset, col_offset, 20)
        worksheet.set_column(col_offset + 1, col_offset + 1, 35)

    insert_vendor_info()
    workbook.close()
    output.seek(0)
    data = encodebytes(output.read())
    return data