from app.schemas.ultimago import TableBill 

BILL_ELCURIOSO: TableBill = TableBill(
    order_id=1009, 
    items=[
        {
            "name": "Fabada (Veg)", 
            "quantity": 1, 
            "price": 10.99
        }, 
        {
            "name": "Gambas al Ajillo", 
            "quantity": 2, 
            "price": 12.99
        }, 
        {
            "name": "Halloumi a la Diabla", 
            "quantity": 1, 
            "price": 14.99
        }, 
        {
            "name": "Steak Tapas", 
            "quantity": 1, 
            "price": 16.99
        }, 
        {
            "name": "Churros", 
            "quantity": 1, 
            "price": 18.99
        }
    ], 
    total_amount=82.97
)