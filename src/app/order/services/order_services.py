# services/order_service.py
import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Union

from fastapi import HTTPException

from app.order.dtos.order_request import (
    CreateOrderRequest,
    OrderVerificationRequest,
    PaymentRequest,
    RefundRequest,
    UpdateShippingRequest,
)
from app.order.dtos.order_response import OrderProductResponse, OrderResponse, PaymentResponse, ShippingStatusResponse
from app.order.models.order import NonUserOrder, NonUserOrderProduct, NonUserPayment
from app.product.models.product import Product


class OrderService:
    @staticmethod
    async def create_order(request: CreateOrderRequest) -> OrderResponse:
        # 주문 번호 생성
        order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"

        # 상품 유효성 검사 및 총 금액 계산
        total_amount = Decimal("0")
        products_to_order = []

        for product_item in request.products:
            product = await Product.get_or_none(id=product_item.product_id)
            if not product:
                raise HTTPException(status_code=404, detail=f"Product {product_item.product_id} not found")

            # 가격 검증
            if product.price != product_item.price:
                raise HTTPException(status_code=400, detail="Product price mismatch")

            total_amount += product_item.price * product_item.quantity
            products_to_order.append((product, product_item))

        # 주문 생성
        order = await NonUserOrder.create(
            name=request.name,
            phone=request.phone,
            shipping_address=request.shipping_address,
            detail_address=request.detail_address,
            request=request.request,
        )

        # 주문 상품 생성
        for product, product_item in products_to_order:
            await NonUserOrderProduct.create(
                order=order,
                product=product,
                quantity=product_item.quantity,
                price=product_item.price,
                current_status="PENDING",
            )

        return await OrderService.get_order(order.pk)

    @staticmethod
    async def get_order(order_id: int) -> OrderResponse:
        order = await NonUserOrder.get_or_none(id=order_id).prefetch_related("order_product__product", "payment")
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # 결제 정보
        payment = await NonUserPayment.get_or_none(order_id=order.pk)
        payment_response = None
        if payment:
            payment_response = PaymentResponse(
                transaction_id=payment.transaction_id,
                order_id=order.pk,
                amount=payment.amount,
                payment_type=payment.payment_type,
                payment_status=payment.payment_status,
                paid_at=payment.created_at,
                receipt_url="",
            )

        # 배송 정보
        shipping_response = None
        order_product = await NonUserOrderProduct.get_or_none(order_id=order.pk)
        if order_product and order_product.courier:
            shipping_response = ShippingStatusResponse(
                status=order_product.current_status,
                courier=order_product.courier,
                tracking_number=order_product.shipping_id,
                tracking_url="",
                current_location="",
                updated_at=order_product.updated_at,
            )

        return OrderResponse(
            id=order.pk,
            order_number=f"ORD-{order.pk}",
            name=order.name,
            phone=order.phone,
            shipping_address=order.shipping_address,
            detail_address=order.detail_address,
            request=order.request,
            total_amount=sum(p.price * p.quantity for p in order.order_product),  # type: ignore
            order_status=order_product.current_status if order_product else "PENDING",
            created_at=order.created_at,
            updated_at=order.updated_at,
            products=[
                OrderProductResponse(
                    id=p.id,
                    product_id=p.product_id,
                    product_name=p.product.name,
                    quantity=p.quantity,
                    price=p.price,
                    courier=p.courier,
                    tracking_number=p.shipping_id,
                    shipping_status=p.current_status,
                    procurement_status=p.procurement_status,
                )
                for p in order.order_product  # type: ignore
            ],
            payment=payment_response,
            shipping=shipping_response,
        )

    @staticmethod
    async def verify_order_owner(order_id: int, verification: OrderVerificationRequest) -> bool:
        order = await NonUserOrder.get_or_none(id=order_id)
        if not order:
            return False
        return order.phone == verification.phone

    @staticmethod
    async def update_order_status(order_id: int, status: str) -> dict[str, Union[int, str]]:
        order_products = await NonUserOrderProduct.filter(order_id=order_id)
        if not order_products:
            raise HTTPException(status_code=404, detail="Order not found")

        for product in order_products:
            product.current_status = status
            await product.save()

        return {
            "order_id": order_id,
            "status": status,
            "updated_products_count": len(order_products),
            "message": "Order status updated successfully",
        }

    # bulk가 필요할 경우
    # @staticmethod
    # async def update_order_status(order_id: int, status: str) -> None:
    #     # 먼저 주문이 존재하는지 확인
    #     exists = await NonUserOrderProduct.filter(order_id=order_id).exists()
    #     if not exists:
    #         raise HTTPException(status_code=404, detail="Order not found")
    #
    #     # 한번에 모든 주문 상품의 상태 업데이트
    #     await NonUserOrderProduct.filter(order_id=order_id).update(current_status=status)
    @staticmethod
    async def get_shipping_status(order_id: int) -> ShippingStatusResponse:
        order_product = await NonUserOrderProduct.get_or_none(order_id=order_id)
        if not order_product or not order_product.courier:
            raise HTTPException(status_code=404, detail="Shipping information not found")

        return ShippingStatusResponse(
            status=order_product.current_status,
            courier=order_product.courier,
            tracking_number=order_product.shipping_id,
            tracking_url="",
            current_location="",
            updated_at=order_product.updated_at,
        )

    @staticmethod
    async def get_order_by_verification(order_id: int, phone: str) -> OrderResponse:
        order = await NonUserOrder.get_or_none(id=order_id, phone=phone).prefetch_related(
            "order_product__product", "payment"
        )

        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        return await OrderService.get_order(order.pk)

    @staticmethod
    async def update_shipping_info(order_id: int, shipping_info: UpdateShippingRequest) -> ShippingStatusResponse:
        order_product = await NonUserOrderProduct.get_or_none(order_id=order_id)
        if not order_product:
            raise HTTPException(status_code=404, detail="Order not found")

        order_product.courier = shipping_info.courier
        order_product.shipping_id = shipping_info.tracking_number
        order_product.current_status = shipping_info.shipping_status
        await order_product.save()

        return ShippingStatusResponse(
            status=order_product.current_status,
            courier=order_product.courier,
            tracking_number=order_product.shipping_id,
            tracking_url="",  # 빈 값이라도 제공
            current_location="",  # 빈 값이라도 제공
            updated_at=order_product.updated_at,
        )

    # @staticmethod
    # async def verify_admin(admin_key: str) -> bool:
    #     # 관리자 인증 로직
    #     return admin_key == "your_admin_key"  # 실제 구현 시 환경변수 등에서 가져오기
