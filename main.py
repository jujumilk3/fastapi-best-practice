from datetime import datetime
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from pydantic.main import ModelMetaclass
from typing import Optional, List


app = FastAPI()


class AllOptional(ModelMetaclass):
    def __new__(self, name, bases, namespaces, **kwargs):
        annotations = namespaces.get('__annotations__', {})
        for base in bases:
            annotations.update(base.__annotations__)
        for field in annotations:
            if not field.startswith('__'):
                annotations[field] = Optional[annotations[field]]
        namespaces['__annotations__'] = annotations
        return super().__new__(self, name, bases, namespaces, **kwargs)


class Omit(ModelMetaclass):
    def __new__(self, name, bases, namespaces, **kwargs):
        omit_fields = getattr(namespaces.get("Config", {}), "omit_fields", {})
        fields = namespaces.get('__fields__', {})
        annotations = namespaces.get('__annotations__', {})
        for base in bases:
            fields.update(base.__fields__)
            annotations.update(base.__annotations__)
        merged_keys = fields.keys() & annotations.keys()
        [merged_keys.add(field) for field in fields]
        new_fields = {}
        new_annotations = {}
        for field in merged_keys:
            if not field.startswith('__') and field not in omit_fields:
                new_annotations[field] = annotations.get(field, fields[field].type_)
                new_fields[field] = fields[field]
        namespaces['__annotations__'] = new_annotations
        namespaces['__fields__'] = new_fields
        return super().__new__(self, name, bases, namespaces, **kwargs)


class BaseItem(BaseModel):
    name: str
    model: str
    manufacturer: str
    price: float
    tax: float


class UpsertItem(BaseItem, metaclass=AllOptional):
    pass


class Item(BaseItem, metaclass=AllOptional):
    id: int
    created_datetime: datetime
    updated_datetime: datetime


class OmittedTaxPrice(BaseItem, metaclass=Omit):
    class Config:
        omit_fields = {'tax', 'price'}


class FindBase(BaseModel):
    count: int
    page: int
    order: str


class FindItem(FindBase, BaseItem, metaclass=AllOptional):
    pass


@app.get("/")
async def root(
):
    return {"message": "Hello World"}


@app.get("/items/", response_model=List[Item])
async def find_items(
        find_query: FindItem = Depends()
):
    return {"hello": "world"}


@app.post("/items/", response_model=Item)
async def create_item(
        schema: UpsertItem
):
    return {"hello": "world"}


@app.patch("/items/{id}", response_model=Item)
async def update_item(
        id: int,
        schema: UpsertItem
):
    return {"hello": "world"}


@app.put("/items/{id}", response_model=Item)
async def put_item(
        id: int,
        schema: BaseItem
):
    return {"hello": "world"}


@app.get("/items/omitted", response_model=OmittedTaxPrice)
async def omitted_item(
        schema: OmittedTaxPrice
):
    return {"hello": "world"}
