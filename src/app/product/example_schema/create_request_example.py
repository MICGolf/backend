import json

OPTION_CREATE_SCHEMA = {
    "example": {
        "size": "Large",
        "color": "Black",
        "color_code": "#000000",
        "stock": 20,
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
            "name": "믹골프 파우치 2세대",
            "price": 199.99,
            "discount": 0.1,
            "origin_price": 249.99,
            "description": "믹골프의 최신 프리미엄 파우치입니다.",
            "detail": "2세대 디자인으로, 내구성과 실용성을 모두 갖춘 고급 파우치입니다.",
            "product_code": "MGP-2NDGEN",
        },
        "option": [
            {"size": "Large", "color": "Black", "color_code": "#000000", "stock": 20},
            {"size": "Medium", "color": "White", "color_code": "#FFFFFF", "stock": 15},
        ],
        "image_mapping": {
            "#000000": ["image1.jpg", "image2.jpg"],
            "#FFFFFF": ["image3.jpg"],
        },
    }
}

PRODUCT_CREATE_REQUEST_EXAMPLE_SCHEMA = {
    "product": {
        "name": "믹골프 파우치 2세대",
        "price": 199.99,
        "discount": 0.1,
        "origin_price": 249.99,
        "description": "믹골프의 최신 프리미엄 파우치입니다.",
        "detail": "2세대 디자인으로, 내구성과 실용성을 모두 갖춘 고급 파우치입니다.",
        "product_code": "MGP-2NDGEN",
    },
    "option": [
        {"size": "Large", "color": "Black", "color_code": "#000000", "stock": 20},
        {"size": "Medium", "color": "White", "color_code": "#FFFFFF", "stock": 15},
    ],
    "image_mapping": {
        "#000000": ["image1.jpg", "image2.jpg"],
        "#FFFFFF": ["image3.jpg"],
    },
}

PRODUCT_CREATE_DESCRIPTION = (
    "### Request Structure\n\n"
    "- **request**: JSON data 예시입니다. product, options, image mapping.\n\n"
    "  {\n\n"
    '      "product": {\n\n'
    '          "name": "믹골프 파우치 2세대",\n\n'
    '          "price": 199.99,\n\n'
    '          "discount": 0.1,\n\n'
    '          "origin_price": 249.99,\n\n'
    '          "description": "믹골프의 최신 프리미엄 파우치입니다.",\n\n'
    '          "detail": "2세대 디자인으로, 내구성과 실용성을 모두 갖춘 고급 파우치입니다.",\n\n'
    '          "product_code": "MGP-2NDGEN"\n\n'
    "      },\n\n"
    '      "option": [\n\n'
    "          {\n\n"
    "              'size': 'Large',\n\n"
    "              'color': 'Black',\n\n"
    "              'color_code': '#000000',\n\n"
    "              'stock': 20\n\n"
    "          },\n\n"
    "          {\n\n"
    "              'size': 'Medium',\n\n"
    "              'color': 'White',\n\n"
    "              'color_code': '#FFFFFF',\n\n"
    "              'stock': 15\n\n"
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
