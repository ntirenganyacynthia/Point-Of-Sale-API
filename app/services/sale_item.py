from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.sale import Sale
from app.repositories.sale_item import sale_item_repository


def get_all_sale_items(db: Session):
    return sale_item_repository.get_all(db)


def get_sale_item(
    db: Session,
    sale_item_id: int
):
    sale_item = sale_item_repository.get_by_id(
        db,
        sale_item_id
    )

    if sale_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale item not found."
        )

    return sale_item


def create_sale_item(
    db: Session,
    sale_item
):
    if sale_item.quantity <= Decimal("0"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be greater than zero."
        )

    sale = (
        db.query(Sale)
        .filter(
            Sale.sale_id == sale_item.sale_id
        )
        .first()
    )

    if sale is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found."
        )

    product = (
        db.query(Product)
        .filter(
            Product.product_id ==
            sale_item.product_id
        )
        .first()
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found."
        )

    if product.stock_quantity < sale_item.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient stock."
        )

    # Never trust the price sent by the client.
    unit_price = product.unit_price

    sub_total = (
        unit_price *
        sale_item.quantity
    )

    data = {
        "sale_id": sale_item.sale_id,
        "product_id": sale_item.product_id,
        "quantity": sale_item.quantity,
        "unit_price": unit_price,
        "sub_total": sub_total
    }

    # Deduct stock.
    product.stock_quantity -= sale_item.quantity

    db.add(product)

    sale_item_record = sale_item_repository.create(
        db,
        data
    )

    # Recalculate sale total from its items.
    db.flush()

    total = sum(
        item.sub_total
        for item in sale.sale_items
    )

    sale.total_amount = total

    db.commit()
    db.refresh(sale_item_record)

    return sale_item_record


def update_sale_item(
    db: Session,
    sale_item_id: int,
    sale_item
):
    existing = get_sale_item(
        db,
        sale_item_id
    )

    old_quantity = existing.quantity

    product_id = (
        sale_item.product_id
        if sale_item.product_id is not None
        else existing.product_id
    )

    quantity = (
        sale_item.quantity
        if sale_item.quantity is not None
        else existing.quantity
    )

    if quantity <= Decimal("0"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be greater than zero."
        )

    product = (
        db.query(Product)
        .filter(
            Product.product_id == product_id
        )
        .first()
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found."
        )

    # Return the old quantity to stock first.
    product.stock_quantity += old_quantity

    if product.stock_quantity < quantity:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient stock."
        )

    product.stock_quantity -= quantity

    existing.product_id = product.product_id
    existing.quantity = quantity
    existing.unit_price = product.unit_price
    existing.sub_total = (
        product.unit_price * quantity
    )

    if sale_item.sale_id is not None:
        sale = (
            db.query(Sale)
            .filter(
                Sale.sale_id == sale_item.sale_id
            )
            .first()
        )

        if sale is None:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sale not found."
            )

        existing.sale_id = sale.sale_id

    db.flush()

    sale = existing.sale

    sale.total_amount = sum(
        item.sub_total
        for item in sale.sale_items
    )

    db.commit()
    db.refresh(existing)

    return existing


def delete_sale_item(
    db: Session,
    sale_item_id: int
):
    sale_item = get_sale_item(
        db,
        sale_item_id
    )

    product = (
        db.query(Product)
        .filter(
            Product.product_id ==
            sale_item.product_id
        )
        .first()
    )

    if product:
        product.stock_quantity += sale_item.quantity

    sale = sale_item.sale

    db.delete(sale_item)

    db.flush()

    sale.total_amount = sum(
        item.sub_total
        for item in sale.sale_items
        if item.sale_item_id != sale_item_id
    )

    db.commit()