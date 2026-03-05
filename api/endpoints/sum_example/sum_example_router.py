from fastapi import APIRouter
from models.sum_example.sum_example_models import SumExampleRequest, SumExampleResponse
from services.sum_example.sum_example_services import add_numbers

router = APIRouter(prefix="/sum-example", tags=["sum_example"])


@router.post("/add", response_model=SumExampleResponse)
def sum_example_endpoint(request: SumExampleRequest) -> SumExampleResponse:
    return add_numbers(request)
