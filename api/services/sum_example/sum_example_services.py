from models.sum_example.sum_example_models import SumExampleRequest, SumExampleResponse


def add_numbers(request: SumExampleRequest) -> SumExampleResponse:
    return SumExampleResponse(sum=request.a + request.b)
