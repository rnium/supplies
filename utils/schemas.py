from pydantic import (
    BaseModel, Field, field_validator,
    model_validator, EmailStr, conbytes
)
from typing import List, Optional
from collections import defaultdict
from datetime import date
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
    name: str
    company_category_type: str
    email: EmailStr
    street: str
    street2: str = None
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


class BankSchema(BaseModel):
    bank_name: str
    swift_code: str = None
    iban: str = None

    class Config:
        from_attributes = True


class BankAccountSchema(BaseModel):
    branch_address: str
    acc_holder_name: str = None
    acc_number: str
    bank_id: int
    partner_id: int


class CompanySchema(BaseModel):
    name: str
    company_category_type: str
    email: EmailStr
    street: str
    street2: Optional[str] | bool
    trade_license_number: Optional[str] | bool
    tax_identification_number: Optional[str] | bool
    commencement_date: Optional[date] | bool
    primary_contact_id: int
    finance_contact_id: int
    authorized_contact_id: int
    expiry_date: Optional[date] | bool
    certification_name: Optional[str] | bool
    certificate_number: Optional[str] | bool
    certifying_body: Optional[str] | bool
    certification_award_date: Optional[date] | bool
    certification_expiry_date: Optional[date] | bool
    client_ref_ids: List[int] = []
    trade_license_doc: Optional[bytes] | bool
    certificate_of_incorporation_doc: Optional[bytes] | bool
    certificate_of_good_standing_doc: Optional[bytes] | bool
    establishment_card_doc: Optional[bytes] | bool
    vat_tax_certificate_doc: Optional[bytes] | bool
    memorandum_of_association_doc: Optional[bytes] | bool
    identification_of_authorised_person_doc: Optional[bytes] | bool
    bank_letter_doc: Optional[bytes] | bool
    past_2_years_financial_statement_doc: Optional[bytes] | bool
    other_certification_doc: Optional[bytes] | bool
    bank_ids: List[int] = []
    supplier_rank: int = 1
    company_type: str = 'company'

    class Config:
        from_attributes = True

    @field_validator(
        'primary_contact_id',
        'finance_contact_id',
        'authorized_contact_id',
        mode='before'
    )
    @classmethod
    def validate_contact_ids(cls, value):
        if not isinstance(value, int):
            return value.id
        return value

    @field_validator('client_ref_ids', mode='before')
    @classmethod
    def validate_client_ref_ids(cls, value):
        if not isinstance(value, list):
            return value.ids
        return value
