from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.utils.success_response import success_response
from api.v1.services.terms_and_conditions import terms_and_conditions_service
from api.v1.schemas.terms_and_conditions import UpdateTermsAndConditions
from api.v1.services.user import user_service
from api.v1.models import *

terms_and_conditions = APIRouter(
    prefix="/terms-and-conditions", tags=["Terms and Conditions"]
)


@terms_and_conditions.patch("/{id}", response_model=success_response, status_code=200)
async def update_terms_and_conditions(
    id: str,
    schema: UpdateTermsAndConditions,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin),
):
    """Endpoint to update terms and conditions. Only accessible to superadmins"""

    tc = terms_and_conditions_service.update(db, id=id, data=schema)
    if not tc:
        return success_response(
            message="Terms and conditions not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return success_response(
        data=tc.to_dict(),
        message="Successfully updated terms and conditions",
        status_code=status.HTTP_200_OK,
    )


@terms_and_conditions.post("/", response_model=success_response, status_code=201)
async def create_terms_and_conditions(
    schema: UpdateTermsAndConditions,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin),
):
    """Endpoint to create terms and conditions. Only accessible to superadmins"""

    # Check if terms and conditions already exist
    existing_tc = db.query(TermsAndConditions).first()
    if existing_tc:
        return success_response(
            message="Terms and conditions already exist. Use PATCH to update.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # Create new terms and conditions
    new_tc = TermsAndConditions(title=schema.title, content=schema.content)
    db.add(new_tc)
    db.commit()
    db.refresh(new_tc)

    return success_response(
        data=new_tc.to_dict(),
        message="Successfully created terms and conditions",
        status_code=status.HTTP_201_CREATED,
    )