from pydantic import BaseModel


class SumExampleRequest(BaseModel):
    a: int
    b: int


class SumExampleResponse(BaseModel):
    sum: int
