from pydantic import (
    BaseModel, Field, field_validator,
    model_validator, EmailStr, conbytes
)
from typing import List
from collections import defaultdict
import re

DOC_MAX_SIZE = 1 * 1024 * 1024 # 1 MB

class ContactSchema(BaseModel):
    name: str
    email: EmailStr
    phone: str
    address: str
    
class ClientContactSchema(BaseModel):
    name: str = None
    email: EmailStr = None
    phone: str = None
    address: str = None
    
    @model_validator(mode='before')
    @classmethod
    def check_name_required(cls, values):
        name = values.get('name')
        email = values.get('email')
        phone = values.get('phone')
        address = values.get('address')

        if (email or phone or address) and not name:
            raise ValueError("If email, phone, or address is provided, name must also be provided.")
        return values


class SupplierRegistrationSchema(BaseModel):
    company_name: str
    company_category_type: str
    email: EmailStr
    address_line_1: str
    address_line_2: str = None
    trade_license_number: str = None
    tax_identification_number: str = None
    commencement_date: str = None
    primary_contact_id: ContactSchema
    finance_contact_id: ContactSchema
    authorized_contact_id: ContactSchema
    expiry_date: str = None
    # Bank info
    bank_name: str
    swift_code: str = None
    iban: str = None
    branch_address: str
    acc_holder_name: str = None
    acc_number: str
    # certification
    certification_name: str = None
    certificate_number: str = None
    certifying_body: str = None
    certification_award_date: str = None
    certification_expiry_date: str = None
    # client references
    client_ref_ids: List[ClientContactSchema] = []
    # docs
    trade_license_doc: conbytes(max_length=DOC_MAX_SIZE) = None # type: ignore
    certificate_of_incorporation_doc: conbytes(max_length=DOC_MAX_SIZE) = None # type: ignore
    certificate_of_good_standing_doc: conbytes(max_length=DOC_MAX_SIZE) = None # type: ignore
    establishment_card_doc: conbytes(max_length=DOC_MAX_SIZE) = None # type: ignore
    vat_tax_certificate_doc: conbytes(max_length=DOC_MAX_SIZE) = None # type: ignore
    memorandum_of_association_doc: conbytes(max_length=DOC_MAX_SIZE) = None # type: ignore
    identification_of_authorised_person_doc: conbytes(max_length=DOC_MAX_SIZE) = None # type: ignore
    bank_letter_doc: conbytes(max_length=DOC_MAX_SIZE) = None # type: ignore
    past_2_years_financial_statement_doc: conbytes(max_length=DOC_MAX_SIZE) = None # type: ignore
    other_certification_doc: conbytes(max_length=DOC_MAX_SIZE) = None # type: ignore
    
    @model_validator(mode='before')
    @classmethod
    def preprocess_data(cls, values):
        groups_types = {'contact', 'client'}
        group_collections = defaultdict(dict)
        for key in values.keys():
            match = re.match(r"([a-zA-Z]+)_(\d+)_(.+)", key)
            if match:
                group, index, field = match.groups()
                if group in groups_types:
                    group_collections[f"{group}_{index}"][field] = values[key]
        grouped_data = dict(group_collections)
        contact_mapping = {
            'contact_1': 'primary_contact_id', 
            'contact_2': 'finance_contact_id', 
            'contact_3': 'authorized_contact_id'
        }
        for key in contact_mapping.keys():
            if key in grouped_data:
                values[contact_mapping[key]] = grouped_data[key]
        client_ref_ids = []
        for key in grouped_data.keys():
            if 'client' in key:
                client_ref_ids.append(grouped_data[key])
        values['client_ref_ids'] = client_ref_ids
        return values


    @field_validator(
        'trade_license_doc',
        'certificate_of_incorporation_doc',
        'certificate_of_good_standing_doc',
        'establishment_card_doc',
        'vat_tax_certificate_doc',
        'memorandum_of_association_doc',
        'identification_of_authorised_person_doc',
        'bank_letter_doc',
        'past_2_years_financial_statement_doc',
        'other_certification_doc',
        mode='before'
    )
    @classmethod
    def transform_binary_fields(cls, value):
        if value and hasattr(value, 'read'):
            return value.read()
    