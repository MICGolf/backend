import json

OPTION_CREATE_SCHEMA = {
    "example": {
        "color": "Red",
        "color_code": "#FF0000",
        "sizes": [
            {"size": "M", "stock": 50},
            {"size": "L", "stock": 30},
        ],
    }
}

PRODUCT_CREATE_SCHEMA = {
    "example": {
        "name": "믹골프 파우치 2세대",
        "price": 199.99,
        "discount": 0.1,
        "origin_price": 249.99,
        "description": "믹골프의 최신 프리미엄 파우치입니다.",
        "detail": "2세대 디자인으로, 내구성과 실용성을 모두 갖춘 고급 파우치입니다.",
        "product_code": "MGP-2NDGEN",
    }
}

PRODUCT_CREATE_REQUEST_SCHEMA = {
    "example": {
        "product": {
            "name": "Sample Product",
            "price": 100.0,
            "discount": 0.1,
            "origin_price": 110.0,
            "description": "A sample product",
            "detail": "Detailed product description.",
            "product_code": "SP001",
        },
        "options": [
            {
                "color": "Red",
                "color_code": "#FF0000",
                "sizes": [
                    {"size": "M", "stock": 50},
                    {"size": "L", "stock": 30},
                ],
            },
            {
                "color": "Blue",
                "color_code": "#0000FF",
                "sizes": [
                    {"size": "M", "stock": 40},
                    {"size": "L", "stock": 20},
                ],
            },
        ],
        "image_mapping": {
            "#FF0000": ["image1.jpg", "image2.jpg"],
            "#0000FF": ["image3.jpg"],
        },
    }
}

PRODUCT_CREATE_REQUEST_EXAMPLE_SCHEMA = {
    "category_id": 1,
    "product": {
        "name": "믹골프 샘플 데이터",
        "price": 90000,
        "discount": 10,
        "discount_option": "percent",
        "origin_price": 100000,
        "description": "믹골프 샘플데이터",
        "detail": "믹골프 샘플 데이터 상세 설명",
        "product_code": "MG-0001-RD",
    },
    "options": [
        {
            "color": "믹골프 레드",
            "color_code": "#FF0000",
            "sizes": [{"size": "M", "stock": 50}, {"size": "L", "stock": 30}],
        },
        {
            "color": "믹골프 스카이블루",
            "color_code": "#0000FF",
            "sizes": [{"size": "M", "stock": 40}, {"size": "L", "stock": 20}],
        },
    ],
    "image_mapping": {
        "#FF0000": ["로고1.jpg", "로고2.jpg"],
        "#0000FF": ["로고3.jpg"],
    },
}

PRODUCT_CREATE_DESCRIPTION = (
    "### Request Structure\n\n"
    "- **request**: JSON data 예시입니다. product, options, image mapping.\n\n"
    "  {\n\n"
    '      "category_id": 1,\n\n'
    '      "product": {\n\n'
    '          "name": "믹골프 파우치 2세대",\n\n'
    '          "price": 199.99,\n\n'
    '          "discount": 10,\n\n'
    '          "discount_option": "percent or amount",\n\n'
    '          "origin_price": 249.99,\n\n'
    '          "description": "믹골프의 최신 프리미엄 파우치입니다.",\n\n'
    '          "detail": "2세대 디자인으로, 내구성과 실용성을 모두 갖춘 고급 파우치입니다.",\n\n'
    '          "product_code": "MGP-2NDGEN"\n\n'
    "      },\n\n"
    '      "options": [\n\n'
    "          {\n\n"
    "              'color': 'Black',\n\n"
    "              'color_code': '#000000',\n\n"
    "              'sizes': [\n\n"
    "                  {'size': 'M', 'stock': 50},\n\n"
    "                  {'size': 'L', 'stock': 30}\n\n"
    "              ]\n\n"
    "          },\n\n"
    "          {\n\n"
    "              'color': 'White',\n\n"
    "              'color_code': '#FFFFFF',\n\n"
    "              'sizes': [\n\n"
    "                  {'size': 'M', 'stock': 40},\n\n"
    "                  {'size': 'L', 'stock': 20}\n\n"
    "              ]\n\n"
    "          }\n\n"
    "      ],\n\n"
    '      "image_mapping": {\n\n'
    "          '#000000': ['image1.jpg', 'image2.jpg'],\n\n"
    "          '#FFFFFF': ['image3.jpg']\n\n"
    "      }\n\n"
    "  }\n\n"
    "- **files**: image_mapping 안에 있는 color_code로 매핑된 이미지 파일 목록.\n\n"
    "  Example:\n\n"
    "  - files=@image1.jpg\n\n"
    "  - files=@image2.jpg\n\n"
    "  - files=@image3.jpg\n\n"
)

PRODUCT_UPDATE_REQUEST_EXAMPLE_SCHEMA = {
    "category_id": 2,  # 수정된 카테고리 ID
    "product": {
        "name": "믹골프 수정된 샘플 데이터",  # 수정된 이름
        "price": 85000,  # 수정된 가격
        "discount": 15,  # 수정된 할인율
        "discount_option": "percent",
        "origin_price": 100000,
        "description": "믹골프 수정된 샘플 데이터 설명",
        "detail": "믹골프 수정된 샘플 데이터 상세 설명",
        "product_code": "MG-0002-RD",
    },
    "options": [
        {
            "id": 1,  # 기존 옵션의 ID (필수)
            "color": "믹골프 레드",  # 수정 없음
            "color_code": "#FF0000",  # 수정 없음
            "sizes": [
                {"id": 1, "size": "M", "stock": 60},  # 기존 사이즈, 재고만 수정
                {"size": "XL", "stock": 20},  # 새로운 사이즈 추가 (id 없음)
            ],
        },
        {
            "id": 2,  # 기존 옵션의 ID
            "color": "믹골프 스카이블루",  # 수정 없음
            "color_code": "#0000FF",  # 수정 없음
            "sizes": [
                {"id": 3, "size": "M", "stock": 50},  # 기존 사이즈, 재고 수정
                {"id": 4, "size": "L", "stock": 25},  # 기존 사이즈, 재고 수정
            ],
        },
        {
            "color": "믹골프 그린",  # 새로운 옵션 추가
            "color_code": "#00FF00",
            "sizes": [
                {"size": "M", "stock": 30},  # 새로운 사이즈 추가
                {"size": "L", "stock": 20},  # 새로운 사이즈 추가
            ],
        },
    ],
    "image_mapping": {
        "#FF0000": ["로고1.jpg", "로고2.jpg"],  # 기존 매핑 유지
        "#0000FF": ["로고3.jpg", "로고4.jpg"],  # 새로운 이미지 추가
        "#00FF00": ["로고5.jpg"],  # 새로운 옵션 이미지 추가
    },
}
