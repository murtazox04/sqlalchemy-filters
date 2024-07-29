from starlette.exceptions import HTTPException


class FilterValidationError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail)


class InvalidFilterOperatorError(HTTPException):
    def __init__(self, operator: str):
        super().__init__(
            status_code=400,
            detail=f"Invalid filter operator: {operator}"
        )


class InvalidOrderFieldError(HTTPException):
    def __init__(self, field: str):
        super().__init__(
            status_code=400,
            detail=f"Invalid order field: {field}"
        )
