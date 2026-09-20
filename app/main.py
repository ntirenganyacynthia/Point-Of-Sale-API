from fastapi import FastAPI

from app.database import Base, engine

from app.routers.auth import router as auth_router
from app.routers.product import router as product_router
from app.routers.user import router as user_router
from app.routers.customer import router as customer_router
from app.routers.category import router as category_router
from app.routers.supplier import router as supplier_router
from app.routers.sale import router as sale_router
from app.routers.sale_item import router as sale_item_router
from app.routers.payment import router as payment_router
from app.routers.receipt import router as receipt_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="POS API"
)


app.include_router(auth_router)
app.include_router(product_router)
app.include_router(user_router)
app.include_router(customer_router)
app.include_router(category_router)
app.include_router(supplier_router)
app.include_router(sale_router)
app.include_router(sale_item_router)
app.include_router(payment_router)
app.include_router(receipt_router)


@app.get("/")
def read_root():
    return {
        "status": "success",
        "message": "POS System Backend API is active"
    }