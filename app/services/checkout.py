from decimal import Decimal
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.product import Product
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.payment import Payment
from app.models.receipt import Receipt


def checkout(
    db: Session,
    data,
    current_user=None
):
    try:
      

        customer = (
            db.query(Customer)
            .filter(
                Customer.customer_id ==
                data.customer_id
            )
            .first()
        )

        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found."
            )

      
        allowed_payment_methods = {
            "mobile_money",
            "cash",
            "card"
        }

        if data.payment_method not in allowed_payment_methods:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Invalid payment method. "
                    "Use mobile_money, cash or card."
                )
            )

      

        sale = Sale(
            customer_id=data.customer_id,
            user_id=(
                current_user.user_id
                if current_user
                else None
            ),
            total_amount=Decimal("0.00"),
            sale_status="pending"
        )

        db.add(sale)
        db.flush()

        total_amount = Decimal("0.00")

      

        for item in data.items:

            product = (
                db.query(Product)
                .filter(
                    Product.product_id ==
                    item.product_id
                )
                .with_for_update()
                .first()
            )

            if product is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=(
                        f"Product {item.product_id} "
                        "not found."
                    )
                )

       
            if product.stock_quantity < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Insufficient stock for "
                        f"{product.product_name}."
                    )
                )

          
            unit_price = product.unit_price

            subtotal = (
                unit_price *
                item.quantity
            )

            total_amount += subtotal

            # Create sale item
            sale_item = SaleItem(
                sale_id=sale.sale_id,
                product_id=product.product_id,
                quantity=item.quantity,
                unit_price=unit_price,
                sub_total=subtotal
            )

            db.add(sale_item)

     
            product.stock_quantity -= item.quantity


        sale.total_amount = total_amount

    

        payment = Payment(
            sale_id=sale.sale_id,
            payment_method=data.payment_method,
            amount_paid=total_amount
        )

        db.add(payment)

        db.flush()

  

        receipt = Receipt(
            sale_id=sale.sale_id,
            receipt_number=(
                f"REC-{uuid4().hex[:12].upper()}"
            )
        )

        db.add(receipt)

        db.flush()



        db.commit()

        db.refresh(sale)
        db.refresh(payment)
        db.refresh(receipt)

        return {
            "sale_id": sale.sale_id,
            "total_amount": sale.total_amount,
            "payment_id": payment.payment_id,
            "payment_status": "pending",
            "receipt_id": receipt.receipt_id
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Checkout failed."
        )