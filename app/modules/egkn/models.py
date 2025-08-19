from sqlalchemy import BigInteger, ForeignKey, Date, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry, WKBElement
from datetime import date, datetime

from app.modules.common.models import (
    BaseModel,
    BaseModelWithShapePoint,
    BasestModel,
    str_uniq,
)

class Lands(BasestModel):
    __tablename__ = 'lands'
    __table_args__ = dict(schema='egkn', comment='Земельный участок')

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    kad_number: Mapped[str] = mapped_column(name='kad_number', nullable=True)
    change_date: Mapped[date] = mapped_column(name='change_date', nullable=True)
    stop_date: Mapped[date] = mapped_column(name='stop_date', nullable=True)
    stop_reason_ru: Mapped[str] = mapped_column(name='stop_reason_ru', nullable=True)
    stop_reason_kk: Mapped[str] = mapped_column(name='stop_reason_kk', nullable=True)
    square: Mapped[float] = mapped_column(name='square', nullable=True)
    purpose_ru: Mapped[str] = mapped_column(name='purpose_ru', nullable=True)
    purpose_kk: Mapped[str] = mapped_column(name='purpose_kk', nullable=True)
    shape: Mapped[WKBElement] = mapped_column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326, spatial_index=True),
        comment="Геометрия",
        nullable=True,
    )
    address_code: Mapped[str] = mapped_column(name='address_code', nullable=True)
    adress_name_ru: Mapped[str] = mapped_column(name='address_name_ru', nullable=True)
    address_name_kk: Mapped[str] = mapped_column(name='address_name_kk', nullable=True)
    divisibility_id: Mapped[int] = mapped_column(ForeignKey('ref_divisibility.id'), nullable=False)
    functional_id: Mapped[int] = mapped_column(ForeignKey('ref_functional_purpose.id'), nullable=False)
    land_category_id: Mapped[int] = mapped_column(ForeignKey('ref_land_category.id'), nullable=False)
    part_type_id: Mapped[int] = mapped_column(ForeignKey('part_type_ref.id'), nullable=True)
    purpose_use_id: Mapped[int] = mapped_column(ForeignKey('ref_purpose.id'), nullable=False)
    start_date: Mapped[date] = mapped_column(name='start_date', nullable=True)
    uniq_identif_economic_charachter: Mapped[str] = mapped_column(name='uniq_identif_economic_charachter', nullable=True)
    ball_boniteta: Mapped[str] = mapped_column(name='ball_boniteta', nullable=True)
    data_reg_boniteta: Mapped[str] = mapped_column(name='data_reg_boniteta', nullable=True)
    uniq_identif_soil: Mapped[str] = mapped_column(name='uniq_identif_soil', nullable=True)
    uniq_identif_istorii_izm: Mapped[str] = mapped_column(name='uniq_identif_istorii_izm', nullable=True)
    uniq_identif_pravootnow: Mapped[str] = mapped_column(name='uniq_identif_pravootnow', nullable=True)
    uniq_identif_docs: Mapped[str] = mapped_column(name='uniq_identif_docs', nullable=True)
    uniq_identif_zapis_zareg_pravah: Mapped[str] = mapped_column(name='uniq_identif_zapis_zareg_pravah', nullable=True)
    uniq_identif_restrict: Mapped[str] = mapped_column(name='uniq_identif_restrict', nullable=True)
    status: Mapped[int] = mapped_column(name='status', nullable=True)
    law_status: Mapped[str] = mapped_column(name='law_status', nullable=True)
    right_status: Mapped[str] = mapped_column(name='right_status', nullable=True)
    restrict_status: Mapped[str] = mapped_column(name='restrict_status', nullable=True)
    economic_status: Mapped[str] = mapped_column(name='economic_status', nullable=True)
    object_id: Mapped[str] = mapped_column(name='object_id', nullable=True)
    close: Mapped[bool] = mapped_column(name='close', nullable=True)
    stop_reason: Mapped[str] = mapped_column(name='stop_reason', nullable=True)
    part_number: Mapped[str] = mapped_column(name='part_number', nullable=True)

class Document(BasestModel):
    __tablename__ = 'document'
    __table_args__ = dict(schema='egkn', comment='Документы используемые в земельных отношениях ЕГКН')

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    doc_number: Mapped[str] = mapped_column(name='doc_number', comment='Номер документа', nullable=True)
    name_ru: Mapped[str] = mapped_column(name='name_ru', comment='Наименование документа на русском', nullable=True)
    name_kz: Mapped[str] = mapped_column(name='name_kz', comment='Наименование документа на казахском', nullable=True)
    issue_date: Mapped[date] = mapped_column(name='issue_date', comment='Дата выдачи документа', nullable=True)
    authority_ru1: Mapped[str] = mapped_column(name='authority_ru1', comment='Кем выдан документ на русском', nullable=True)
    authority_kz: Mapped[str] = mapped_column(name='authority_kz', comment='Кем выдан документ на казахском', nullable=True)
    series: Mapped[str] = mapped_column(name='series', comment='Серийный номер документа', nullable=True)
    type_id: Mapped[int] = mapped_column(ForeignKey('ref_document_type.id'), nullable=False)
    identif_doc: Mapped[str] = mapped_column(name='identif_doc', comment='Идентификатор документа', nullable=True)
    status: Mapped[str] = mapped_column(name='status', comment='Статус документа', nullable=True)

class LandIdentityDocs(BasestModel):
    __tablename__ = 'land_identity_docs'
    __table_args__ = dict(schema='egkn', comment='Документы по ЗУ')

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    land_id: Mapped[int] = mapped_column(ForeignKey('lands.id'), nullable=False)
    document_id: Mapped[int] = mapped_column(ForeignKey('document.id'), nullable=False)

class LandRights(BasestModel):
    __tablename__ = 'land_rights'
    __table_args__ = dict(schema='egkn', comment='Право на ЗУ')

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    start_date: Mapped[date] = mapped_column(name='start_date', nullable=True)
    stop_date: Mapped[date] = mapped_column(name='stop_date', nullable=True)
    expiration_date: Mapped[date] = mapped_column(name='expiration_date', nullable=True)

    land_id: Mapped[int] = mapped_column(ForeignKey('lands.id'), nullable=False)
    legal_id: Mapped[int] = mapped_column(ForeignKey('ref_legal.id'), nullable=False)
    validity_ru: Mapped[str] = mapped_column(name='validity_ru', nullable=True)
    validity_kk: Mapped[str] = mapped_column(name='validity_kk', nullable=True)
    owner_subject_id: Mapped[int] = mapped_column(ForeignKey('subjects.id'), nullable=False)

class LandEconomicChars(BasestModel):
    __tablename__ = 'land_economic_chars'
    __table_args__ = dict(schema='egkn', comment='Сведения об экономических характеристиках')

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    value: Mapped[float] = mapped_column(name='value', comment='Значение экономической характеристики', nullable=True)
    start_date: Mapped[date] = mapped_column(name='start_date', comment='Дата изменения характеристик', nullable=True)
    land_id: Mapped[int] = mapped_column(ForeignKey('lands.id'), nullable=False)
    economic_char_id: Mapped[int] = mapped_column(ForeignKey('ref_economical'), nullable=False)
    economic_identif: Mapped[str] = mapped_column(name='economic_identif', comment='Идентификатор экономической характеристики', nullable=True)

class RefRestriciton(BasestModel):
    __tablename__ = 'ref_restriction'
    __table_args__ = dict(schema='egkn', comment = 'Справочник Вид ограничения на ЗУ')

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    code: Mapped[str] = mapped_column(name='code', nullable=True)
    name_ru: Mapped[str] = mapped_column(name='name_ru', nullable=True)
    name_kz: Mapped[str] = mapped_column(name='name_kz', nullable=True)

    modification_date: Mapped[date] = mapped_column(name='modification_date', nullable=True)

class Infrastructures(BasestModel):
    __tablename__ = 'infrastructures'
    __table_args__ = dict(schema='egkn')
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    land_id: Mapped[int] = mapped_column(ForeignKey('lands.id'), nullable=False)
    electricity: Mapped[bool] = mapped_column(name='electricity', comment='Электричество', nullable=False)
    water: Mapped[bool] = mapped_column(name='water', comment='Вода', nullable=False)
    gas: Mapped[bool] = mapped_column(name='gas', comment='Газ', nullable=False)
    sewage: Mapped[bool] = mapped_column(name='sewage', comment='Канализация', nullable=False)
    internet: Mapped[bool] = mapped_column(name='internet', comment='Интернет', nullable=False)
    road_type: Mapped[bool] = mapped_column(name='road_type', comment='Подъезд', nullable=False)

    distance_to_city_km: Mapped[int] = mapped_column(name='distance_to_city_km', comment='Дистанция от города', nullable=True)

class LandCharges(BasestModel):
    __tablename__ = 'land_charges'
    __table_args__ = dict(schema='egkn', comment='Сведения о зарегистрированных обременениях (арестах)')

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    charge_type_id: Mapped[int] = mapped_column(ForeignKey('ref_charge_type.id'), nullable=False)
    land_id: Mapped[int] = mapped_column(ForeignKey('lands.id'), nullable=False)

    start_date: Mapped[date] = mapped_column(name='start_date', comment='', nullable=True)
    start_date: Mapped[date] = mapped_column(name='start_date', comment='Дата изменения характеристик', nullable=True)
    
    expiration_date: Mapped[date] = mapped_column(name='expiration_date', nullable=True)
    validity_ru: Mapped[str] = mapped_column(name='validity_ru', nullable=True)
    validity_kk: Mapped[str] = mapped_column(name='validity_kk', nullable=True)

    imposed_subject_id: Mapped[int] = mapped_column(ForeignKey('subjects.id'), nullable=False)

class Subjects(BasestModel):
    __tablename__ = 'subjects'
    __table_args__ = dict(schema='egkn')

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    iin: Mapped[str] = mapped_column(name='iin', nullable=True)
    bin: Mapped[str] = mapped_column(name='bin', nullable=True)
    org_name: Mapped[str] = mapped_column(name='org_name', nullable=True)
    first_name: Mapped[str] = mapped_column(name='first_name', nullable=True)
    last_name: Mapped[str] = mapped_column(name='last_name', nullable=True)
    patronym: Mapped[str] = mapped_column(name='patronym', nullable=True)
    birth_date: Mapped[date] = mapped_column(name='birth_date', nullable=True)

class LandRestriction(BasestModel):
    __tablename__ = 'land_restrictions'
    __table_args__ = dict(schema='egkn')

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name_ru: Mapped[str] = mapped_column(name='name_ru', nullable=True)
    name_kk: Mapped[str] = mapped_column(name='name_kk', nullable=True)

    validity_ru: Mapped[str] = mapped_column(name='validity_ru', nullable=True)
    validity_kk: Mapped[str] = mapped_column(name='validity_kk', nullable=True)

    start_date: Mapped[date] = mapped_column(name='start_date', nullable=True)
    stop_date: Mapped[date] = mapped_column(name='stop_date', nullable=True)
    expiration_date: Mapped[date] = mapped_column(name='expiration_date', nullable=True)

    land_id: Mapped[int] = mapped_column(ForeignKey('lands.id'), nullable=False)
    imposed_subject_id: Mapped[int] = mapped_column(ForeignKey('subjects.id'), nullable=False)
    type_id: Mapped[int] = mapped_column(ForeignKey('ref_restriction.id'), nullable=False)

class RefChargeTypes(BasestModel):
    __tablename__ = "ref_charge_type"
    __table_args__ = dict(schema='egkn')

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    code: Mapped[str] = mapped_column(name='code', nullable=True)
    name_ru: Mapped[str] = mapped_column(name='name_ru', nullable=True)
    name_kk: Mapped[str] = mapped_column(name='name_kk', nullable=True)

    modification_date: Mapped[date] = mapped_column(name='modification_date', nullable=True)

class LandChargeDocs(BasestModel):
    __tablename__ = 'land_charge_docs'
    __table_args__ = dict(schema='egkn')

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    land_charge_id: Mapped[int] = mapped_column(ForeignKey('land_charges.id'), nullable=False)
    document_id: Mapped[int] = mapped_column(ForeignKey('document.id'), nullable=False)

    reason_type: Mapped[str] = mapped_column(name='reason_type', nullable=True)

class RefLandCategory(BasestModel):
    __tablename__ = 'ref_land_category'
    __table_args__ = dict(schema='egkn')

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    code: Mapped[str] = mapped_column(name='code', nullable=True)
    name_ru: Mapped[str] = mapped_column(name='name_ru', nullable=True)
    name_kz: Mapped[str] = mapped_column(name='name_kz', nullable=True)
    modification_date: Mapped[date] = mapped_column(name='modification_date', nullable=True)