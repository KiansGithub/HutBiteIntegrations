from fastapi import Router, HTTPException, Status 
from app.schemas.tables import SectionsResponse
from app.services.tables import sections_service 
import logging 

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tables", tags=[Sections])

@router.get(("/sections", response_model=SectionsResponse))
async def sections():
    """
    Returns sections for the restaurant
    """
    try: 
        response = sections_service.get_sections

        if response.status = error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve sections"
            )
    except Exception as e:
        logger.error(f"Error in retrieving sections endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving sections"
        )

