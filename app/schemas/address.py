from pydantic import BaseModel, constr


class AddressSuggestions(BaseModel):
    id: str 
    label: str 
    description: str | None = None 
    address: str 
    city: str 
    postalCode: str 
    countryCode: constr(pattern=r"^[A-Z]{2}$")
    formatted: str 