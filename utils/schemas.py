from pydantic import (
    BaseModel, Field, field_validator,
    model_validator, EmailStr, conbytes, ConfigDict, Base64Str,
    Base64Bytes, StringConstraints
)
from typing import List, Optional, Annotated
from collections import defaultdict
from datetime import date
import re
import base64

DOC_MAX_SIZE = 1 * 1024 * 1024 # 1 MB
TRADE_LIC_TYPE = Annotated[str, StringConstraints(pattern=r"^[a-zA-Z0-9]{8,20}$")]
TINType = Annotated[str, StringConstraints(pattern=r"^\d{16}$")]

class ContactSchema(BaseModel):
    name: str
    email: EmailStr
    phone: str
    address: str

class ContactOutSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
    name: str
    email: EmailStr
    phone: str
    street: str = Field(alias='address')
    company_type: str = 'person'
    type: str = 'contact'

    def model_dump(self, **kwargs):
        data = super().model_dump()
        data['function'] = kwargs.get('function')
        return data

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

class ClientContactOutSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
    name: str
    email: EmailStr | bool
    phone: str | bool
    street: str | bool = Field(alias='address')


class SupplierRegistrationSchema(BaseModel):
    name: str
    company_category_type: str
    email: EmailStr
    image_1920: Base64Bytes | None = None
    street: str
    street2: str = None
    trade_license_number: Optional[TRADE_LIC_TYPE] = None
    tax_identification_number: Optional[TINType] = None
    commencement_date: Optional[date] = None
    primary_contact_id: ContactSchema
    finance_contact_id: ContactSchema
    authorized_contact_id: ContactSchema
    expiry_date: Optional[date] = None
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
    certification_award_date: Optional[date] = None
    certification_expiry_date: Optional[date] = None
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
        # Binary fields
        binary_file_fields = [
            'image_1920',
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
        ]
        for field in binary_file_fields:
            if field in values:
                file_value = values[field]
                values[field] = cls.transform_binary_fields(file_value)
        return values

    @classmethod
    def transform_binary_fields(cls, value):
        if value and hasattr(value, 'read'):
            return base64.b64encode(value.read())
        return value

    @field_validator('commencement_date')
    @classmethod
    def validate_commencement_date(cls, value):
        if value and value >= date.today():
            raise ValueError("Commencement date must be in the past.")
        return value

    @field_validator('expiry_date')
    @classmethod
    def validate_expiry_date(cls, value):
        if value and value <= date.today():
            raise ValueError("Expiry date must be in the future.")
        return value


class BankSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
    name: str = Field(alias='bank_name')
    swift_code: str = None
    iban: str = None


class BankAccountSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
    branch_address: str | bool
    acc_holder_name: str | bool
    acc_number: str

    def model_dump(self, **kwargs):
        data = super().model_dump()
        bank_id = kwargs.get('bank_id')
        if bank_id:
            data['bank_id'] = bank_id
        return data


class UserSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
    login: EmailStr = Field(alias='email')
    password: str = Field(alias='email')

    def model_dump(self, **kwargs):
        data = super().model_dump()
        data['partner_id'] = kwargs.get('partner_id')
        data['company_id'] = kwargs.get('company_id')
        data['groups_id'] = kwargs.get('groups_id')
        return data

class CompanySchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
    name: str
    company_category_type: str
    email: EmailStr
    street: str
    street2: Optional[str] | bool
    image_1920: Optional[Base64Bytes] | bool
    trade_license_number: Optional[str] | bool
    tax_identification_number: Optional[str] | bool
    commencement_date: Optional[date] | bool
    expiry_date: Optional[date] | bool
    certification_name: Optional[str] | bool
    certificate_number: Optional[str] | bool
    certifying_body: Optional[str] | bool
    certification_award_date: Optional[date] | bool
    certification_expiry_date: Optional[date] | bool
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
    supplier_rank: int = 1
    company_type: str = 'company'

class PurchaseOrderLineSchema(BaseModel):
    product_id: int
    product_qty: int
    product_uom: Optional[int] | None = None
    price_unit: float
    delivery_charge: float
    date_planned: date
    name: str # description

class PurchaseOrderSchema(BaseModel):
    rfp_id: int
    partner_id: int
    warrenty_period: int
    date_planned: date
    notes: str
    user_id: int
    order_line: List[PurchaseOrderLineSchema]

    @model_validator(mode='before')
    @classmethod
    def preprocess_data(cls, values):
        groups_types = {'line'}
        group_collections = defaultdict(dict)
        for key in values.keys():
            match = re.match(r"([a-zA-Z]+)-(\d+)-(.+)", key)
            if match:
                group, index, field = match.groups()
                if group in groups_types:
                    group_collections[f"{group}_{index}"][field] = values[key]
        grouped_data = dict(group_collections)
        date_planned = values.get('date_planned')
        order_line = [{'date_planned': date_planned, **vals} for vals in grouped_data.values()]
        values['order_line'] = order_line
        return values

    def get_new_purchase_order_data(self):
        data = self.model_dump()
        order_line = data.pop('order_line')
        data['order_line'] = []
        for line in order_line:
            data['order_line'].append(
                (0, 0, line)
            )
        return data

