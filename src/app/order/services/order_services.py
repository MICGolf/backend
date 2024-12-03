import uuid
from decimal import Decimal
from typing import List

from fastapi import HTTPException

from app.order.dtos.order_request import (
    BatchOrderStatusRequest,
    CreateOrderRequest,
    OrderClaimRequest,
    OrderSearchRequest,
    OrderVerificationRequest,
    PurchaseOrderRequest,
    UpdatePurchaseStatusRequest,
    UpdateShippingRequest,
)
from app.order.dtos.order_response import (
    BatchUpdateStatusResponse,
    OrderProductResponse,
    OrderResponse,
    OrderSearchResponse,
    OrderStatisticsResponse,
    ProductOptionResponse,
    ShippingStatusResponse,
    StockCheckResponse,
    UpdateOrderStatusResponse,
    VerifyOrderOwnerResponse,
)
from app.order.models.order import NonUserOrder, NonUserOrderProduct
from app.product.models.product import CountProduct, Option, Product


class OrderService:
    @staticmethod
    async def create_order(request: CreateOrderRequest) -> OrderResponse:
        # 주문 번호 생성
        order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"

        # 상품 유효성 검사 및 총 금액 계산
        total_amount = Decimal("0")
        products_to_order = []

        # 한번에 모든 상품의 옵션과 상품 정보를 가져옴
        product_ids = [item.product_id for item in request.products]
        products = await Product.filter(id__in=product_ids)

        if len(products) != len(product_ids):
            found_ids = {p.id for p in products}
            missing_ids = set(product_ids) - found_ids
            raise HTTPException(status_code=404, detail=f"Products not found: {missing_ids}")

        # 상품 정보를 ID로 빠르게 조회하기 위한 딕셔너리
        product_map = {p.id: p for p in products}

        # 옵션 정보 가져오기
        options = await Option.get_by_product_ids(product_ids)
        option_map = {(opt.product_id, opt.id): opt for opt in options}  # type: ignore

        for product_item in request.products:
            # 상품 정보 가져오기 (이미 검증됨)
            product = product_map[product_item.product_id]

            # 가격 검증
            if product.price != product_item.price:
                raise HTTPException(status_code=400, detail="Product price mismatch")

            # 옵션 존재 및 재고 확인
            option = option_map.get((product_item.product_id, product_item.option_id))
            if not option:
                raise HTTPException(
                    status_code=404,
                    detail=f"Option {product_item.option_id} not found for product {product_item.product_id}",
                )

            # 재고 확인
            if option.stock < product_item.quantity:  # type: ignore
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for product {product_item.product_id} "
                    f"option {product_item.option_id}: available {option.stock}, "  # type: ignore
                    f"requested {product_item.quantity}",
                )

            # 재고 차감
            stock_check = await OrderService.check_and_update_stock(
                product_id=product_item.product_id, option_id=product_item.option_id, quantity=product_item.quantity
            )

            total_amount += product_item.price * product_item.quantity
            products_to_order.append((product, option, product_item))

        # 주문 생성
        order = await NonUserOrder.create(
            name=request.name,
            phone=request.phone,
            shipping_address=request.shipping_address,
            detail_address=request.detail_address,
            request=request.request,
        )

        # 주문 상품 생성
        for product, option, product_item in products_to_order:
            await NonUserOrderProduct.create(
                order=order,
                product=product,
                option_id=option.id,
                quantity=product_item.quantity,
                price=product_item.price,
                current_status="PENDING",
            )

        return await OrderService.get_order(order.pk)

    @staticmethod
    async def get_order(order_id: int) -> OrderResponse:
        order = await NonUserOrder.get_or_none(id=order_id).prefetch_related(
            "order_product__product", "order_product__product__options", "payment"  # 상품의 옵션 정보도 함께 로드
        )
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        products = []
        for p in order.order_product:  # type: ignore
            # p.option_id를 사용하여 해당 옵션을 직접 찾기
            option = await Option.get(id=p.option_id)
            products.append(
                OrderProductResponse(
                    id=p.id,
                    product_id=p.product_id,
                    product_name=p.product.name,
                    quantity=p.quantity,
                    price=p.price,
                    option=(
                        ProductOptionResponse(
                            size=option.size, color=option.color, color_code=option.color_code, price=p.product.price
                        )
                        if option
                        else None
                    ),
                    courier=p.courier,
                    tracking_number=p.shipping_id,
                    shipping_status=p.current_status,
                    procurement_status=p.procurement_status,
                )
            )
        shipping_status = ShippingStatusResponse(
            status="PENDING", courier="", tracking_number="", updated_at=order.updated_at
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
            order_status=products[0].shipping_status if products else "PENDING",
            created_at=order.created_at,
            updated_at=order.updated_at,
            products=products,
            payment=None,
            shipping=shipping_status,
        )

    @staticmethod
    async def verify_order_owner(order_id: int, verification: OrderVerificationRequest) -> VerifyOrderOwnerResponse:
        order = await NonUserOrder.get_or_none(id=order_id)
        if not order:
            return VerifyOrderOwnerResponse(is_owner=False, message="Order not found")

        is_owner = order.phone == verification.phone
        message = "Verification successful" if is_owner else "Phone number does not match"

        return VerifyOrderOwnerResponse(is_owner=is_owner, message=message)

    @staticmethod
    async def update_order_status(order_id: int, status: str) -> UpdateOrderStatusResponse:
        order_products = await NonUserOrderProduct.filter(order_id=order_id)
        if not order_products:
            raise HTTPException(status_code=404, detail="Order not found")

        for product in order_products:
            product.current_status = status
            await product.save()

        return UpdateOrderStatusResponse(
            order_id=order_id,
            status=status,
            updated_products_count=len(order_products),
            message="Order status updated successfully",
        )

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
    async def update_shipping_info(request: UpdateShippingRequest) -> ShippingStatusResponse:
        order_product = await NonUserOrderProduct.get_or_none(order_id=request.order_id)
        if not order_product:
            raise HTTPException(status_code=404, detail="Order not found")

        order_product.courier = request.courier
        order_product.shipping_id = request.tracking_number
        order_product.current_status = request.shipping_status
        await order_product.save()

        return ShippingStatusResponse(
            status=order_product.current_status,
            courier=order_product.courier,
            tracking_number=order_product.shipping_id,
            tracking_url="",
            current_location="",
            updated_at=order_product.updated_at,
        )

    @staticmethod
    async def search_orders(search_params: OrderSearchRequest, page: int = 1, limit: int = 10) -> list[OrderResponse]:
        query = NonUserOrder.all()

        if search_params.start_date and search_params.end_date:
            query = query.filter(created_at__gte=search_params.start_date, created_at__lte=search_params.end_date)

        if search_params.order_number:
            query = query.filter(id=int(search_params.order_number.replace("ORD-", "")))

        if search_params.order_status:
            query = query.filter(order_product__current_status=search_params.order_status)

        if search_params.payment_status:  # type: ignore
            query = query.filter(payment__payment_status=search_params.payment_status)  # type: ignore

        skip = (page - 1) * limit
        orders = await query.offset(skip).limit(limit).prefetch_related("order_product__product", "payment")

        return [OrderResponse.model_validate(order, from_attributes=True) for order in orders]

    @staticmethod
    async def batch_update_status(request: BatchOrderStatusRequest) -> BatchUpdateStatusResponse:  # 반환 타입 수정
        await NonUserOrderProduct.filter(order_id__in=request.order_ids).update(current_status=request.status)
        return BatchUpdateStatusResponse(  # 직접 객체 생성하여 반환
            updated_count=len(request.order_ids), status=request.status
        )

    @staticmethod
    async def check_and_update_stock(product_id: int, option_id: int, quantity: int) -> StockCheckResponse:
        """
        재고 확인 및 업데이트
        """
        # 해당 상품/옵션의 재고들을 생성일순으로 조회
        stocks = await CountProduct.filter(product_id=product_id, option_id=option_id).order_by("created_at")

        available_quantity = sum(stock.count for stock in stocks)
        has_sufficient_stock = available_quantity >= quantity

        message = None
        if has_sufficient_stock:
            # FIFO로 재고 차감
            remaining = quantity
            for stock in stocks:
                if stock.count >= remaining:
                    stock.count -= remaining
                    await stock.save()
                    break
                else:
                    remaining -= stock.count
                    stock.count = 0
                    await stock.save()
            message = "재고 차감 완료"
        else:
            message = f"재고 부족 (필요: {quantity}, 현재: {available_quantity})"

        return StockCheckResponse(
            has_sufficient_stock=has_sufficient_stock,
            available_quantity=available_quantity,
            product_id=product_id,
            option_id=option_id,
            requested_quantity=quantity,
            message=message,
        )

    @staticmethod
    async def update_purchase_order(request: PurchaseOrderRequest) -> tuple[OrderResponse, StockCheckResponse]:
        order_product = await NonUserOrderProduct.get_or_none(order_id=request.order_id).prefetch_related(
            "product", "product__options"
        )

        if not order_product:
            raise HTTPException(status_code=404, detail="Order not found")

        # 재고 확인
        stock_check = await OrderService.check_and_update_stock(
            order_product.product_id, order_product.option_id, order_product.quantity  # type: ignore
        )

        # 재고 상태에 따른 발주 상태 설정
        status = "CONFIRMED" if stock_check.has_sufficient_stock else "PENDING"

        # 발주 정보 업데이트
        order_product.procurement_status = status
        await order_product.save()

        order_response = await OrderService.get_order(request.order_id)
        return order_response, stock_check

    @staticmethod
    async def get_order_statistics() -> OrderStatisticsResponse:
        total = await NonUserOrder.all().count()

        # 상태별 주문 수 집계
        pending = await NonUserOrderProduct.filter(current_status="PENDING").count()
        shipping = await NonUserOrderProduct.filter(current_status="SHIPPING").count()
        completed = await NonUserOrderProduct.filter(current_status="COMPLETED").count()
        cancelled = await NonUserOrderProduct.filter(current_status="CANCELLED").count()

        return OrderStatisticsResponse(
            total_orders=total,
            pending_orders=pending,
            shipping_orders=shipping,
            completed_orders=completed,
            cancelled_orders=cancelled,
        )

    @staticmethod
    async def handle_order_claim(request: OrderClaimRequest) -> OrderResponse:
        order = await NonUserOrder.get_or_none(id=request.order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        order_product = await NonUserOrderProduct.get_or_none(order_id=request.order_id)
        if not order_product:
            raise HTTPException(status_code=404, detail="Order product not found")

        # 클레임 상태 업데이트
        order_product.current_status = request.claim_status
        await order_product.save()

        return await OrderService.get_order(request.order_id)

    @staticmethod
    async def update_purchase_status(request: UpdatePurchaseStatusRequest) -> OrderResponse:
        order_product = await NonUserOrderProduct.get_or_none(order_id=request.order_id)
        if not order_product:
            raise HTTPException(status_code=404, detail="Order not found")

        order_product.procurement_status = request.purchase_status
        await order_product.save()

        return await OrderService.get_order(request.order_id)

    @staticmethod
    async def advanced_search(request: OrderSearchRequest) -> OrderSearchResponse:
        query = NonUserOrder.all()

        # 기존 필터링 로직 유지
        if request.start_date and request.end_date:
            query = query.filter(created_at__gte=request.start_date, created_at__lte=request.end_date)

        if request.order_number:
            query = query.filter(id=int(request.order_number.replace("ORD-", "")))

        if request.order_status:
            query = query.filter(order_product__current_status=request.order_status)

        if request.purchase_status:
            query = query.filter(order_product__procurement_status=request.purchase_status)

        if request.shipping_status:
            query = query.filter(order_product__current_status=request.shipping_status)

        if request.claim_status:
            query = query.filter(order_product__current_status=request.claim_status)

        # 정렬
        if request.sort_by:
            direction = "" if request.sort_direction == "asc" else "-"
            query = query.order_by(f"{direction}{request.sort_by}")

        # 페이징 처리
        total = await query.count()
        skip = (request.page - 1) * request.limit
        orders = await query.offset(skip).limit(request.limit)

        # 각 주문에 대해 OrderResponse 생성
        order_responses = []
        for order in orders:
            # get_order 메서드 재사용
            order_response = await OrderService.get_order(order.pk)
            order_responses.append(order_response)

        return OrderSearchResponse(
            orders=order_responses,
            search_params=request,
            total=total,
            page=request.page,
            limit=request.limit,
            total_pages=(total + request.limit - 1) // request.limit,
        )

    # @staticmethod
    # async def verify_admin(admin_key: str) -> bool:
    #     # 관리자 인증 로직
    #     return admin_key == "your_admin_key"  # 실제 구현 시 환경변수 등에서 가져오기
