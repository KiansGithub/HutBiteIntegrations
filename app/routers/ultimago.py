from fastapi import Router, HTTPException, status 
from app.schemas.ultimago import StoreProfileResponse 
from app.services.ultimago import ultimago_service 

router = Router(prefix="/ultimago", tags=["ultimago"])

@router.get("/store-profile", response_model=StoreProfileResponse)
async def store_profile():
    try:
        response = ultimago_service.get_store_profile()
        return response 
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to retrieve store profile: {str(e)}"
        )
