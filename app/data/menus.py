# app/data/menus.py
from app.schemas.menu import MenuData

MENU_ELCURIOSO: MenuData = MenuData(
    categories=[
        {
            "id": "cat-1",
            "name": "Tapas",
            "items": [
                {
                    "id": "vid-2",
                    "title": "Fabada (Veg)",
                    "videoUrl": "https://tanexoecudctdtlmuqhr.supabase.co/storage/v1/object/public/videos/Hertfordshire/Cheshunt/El%20Curioso/Fabada%20con%20Veg.mp4",
                },
                {
                    "id": "vid-3",
                    "title": "Gambas al Ajillo",
                    "videoUrl": "https://tanexoecudctdtlmuqhr.supabase.co/storage/v1/object/public/videos/Hertfordshire/Cheshunt/El%20Curioso/Gambas%20al%20Ajilo.mp4",
                },
                {
                    "id": "vid-4",
                    "title": "Halloumi a la Diabla",
                    "videoUrl": "https://tanexoecudctdtlmuqhr.supabase.co/storage/v1/object/public/videos/Hertfordshire/Cheshunt/El%20Curioso/Halloumi%20A%20Diabla.mp4",
                },
                {
                    "id": "vid-5",
                    "title": "Steak Tapas",
                    "videoUrl": "https://tanexoecudctdtlmuqhr.supabase.co/storage/v1/object/public/videos/Hertfordshire/Cheshunt/El%20Curioso/Steak%20Tapas.mp4",
                },
            ],
        },
        {
            "id": "cat-2",
            "name": "Desserts",
            "items": [
                {
                    "id": "vid-6",
                    "title": "Churros",
                    "videoUrl": "https://tanexoecudctdtlmuqhr.supabase.co/storage/v1/object/public/videos/Hertfordshire/Cheshunt/El%20Curioso/Kurros.mp4",
                }
            ],
        },
    ],
)
