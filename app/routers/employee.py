from fastapi import APIRouter, HTTPException, status
from app.services import employee
from app import schemas
from app.dependencies import dbDep, pagination_params, currentEmployee

router = APIRouter(prefix="/employee", tags=["Employee"])


@router.get("/", response_model=schemas.EmployeesOut)
def get_employees(db: dbDep, pg_params: pagination_params, cur_emp: currentEmployee):
    try:
        data = employee.get_all(db=db, pg_params=pg_params)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        )
    return schemas.EmployeesOut(
        employees=[
            employee.convert_employee_to_schema(emp) for emp in data["employees"]
        ],
        total_records=data["total_records"],
        total_pages=data["total_pages"],
        page_number=pg_params.page,
        page_size=pg_params.limit,
    )


@router.get("/{id}", response_model=schemas.EmployeeOut)
def get_by_id(id: int, db: dbDep, cur_emp: currentEmployee):
    try:
        emp = employee.get_employee_by_id(id=id, db=db)
        if emp is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
            )
    except HTTPException as http_error:
        raise http_error
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        )
    return employee.convert_employee_to_schema(emp)


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.EmployeeOut
)
async def create_employee(emp: schemas.EmployeeCreate, db: dbDep):
    try:
        new_emp = await employee.create_employee(emp.model_dump(), db)
    except HTTPException as http_error:
        raise http_error
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        )
    return employee.convert_employee_to_schema(new_emp)


@router.put("/{id}", response_model=schemas.EmployeeOut)
async def update_employee(
    update_data: schemas.EmployeeUpdate, id: int, db: dbDep, cur_emp: currentEmployee
):
    try:
        if update_data.password != update_data.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be match"
            )
        employee_updated = await employee.edit_employee(
            id, update_data.model_dump(), db
        )
    except HTTPException as http_error:
        raise http_error
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        )
    return employee.convert_employee_to_schema(employee_updated)


@router.patch("/")
def confirm_account(
    password_data: schemas.CreatePassword,
    code: str,
    db: dbDep,
):
    try:
        if password_data.password != password_data.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be match"
            )
        return employee.confirmation_account(
            code=code, password=password_data.password, db=db
        )
    except HTTPException as http_error:
        raise http_error
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        )


@router.patch("/confirmEmail")
def confirm_email(entry: schemas.confirmationCode, db: dbDep):
    try:
        return employee.confirmation_email(entry.code, db)
    except HTTPException as http_error:
        raise http_error
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        )
