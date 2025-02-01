from pydantic import BaseModel, Field, field_validator, model_validator, EmailStr
from typing import List

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
    bank_name: str
    swift_code: str = None
    iban: str = None
    branch_address: str
    acc_holder_name: str = None
    acc_number: str
    certification_name: str = None
    certificate_number: str = None
    certifying_body: str = None
    certification_award_date: str = None
    certification_expiry_date: str = None
    trade_license_doc: bytes = None
    certificate_of_incorporation_doc: bytes = None
    certificate_of_good_standing_doc: bytes = None
    establishment_card_doc: bytes = None
    vat_tax_certificate_doc: bytes = None
    memorandum_of_association_doc: bytes = None
    identification_of_authorised_person_doc: bytes = None
    bank_letter_doc: bytes = None
    past_2_years_financial_statement_doc: bytes = None
    other_certification_doc: bytes = None