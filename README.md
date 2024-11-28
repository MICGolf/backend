## Micgolf 쇼핑몰 서비스 - Backend
### < 프로젝트 구조 >

backend/
├── src/
│   ├── app/
│   │   ├── banner/
│   │   │   ├── dtos/
│   │   │   ├── models/
│   │   │   ├── services/
│   │   │   ├── __init__.py 
│   │   │   └── router.py
│   │   ├── cart/
│   │   ├── category/
│   │   ├── order/
│   │   ├── product/
│   │   ├── promotion_product/
│   │   └── ...     # 도메인
│   ├── common/
│   │   ├── exceptions/
│   │   ├── handlers/
│   │   ├── middlewares/
│   │   ├── models/
│   │   │   └── base_model.py
│   │   ├── utils/
│   │   ├── __init__.py
│   │   └── post_construct.py
│   ├── core/
│   │   ├── configs/         
│   │   │   ├── __init__.py
│   │   │   └── settings.py
│   │   ├── database/
│   │   │   ├── db_settings.py 
│   │   │   └── models.py      
│   │   └── __init__.py
│   ├── tests/
│   ├── .env                # 환경 변수 파일
│   ├── conftest.py
│   ├── main.py
│   ├── poetry.lock
│   ├── pyproject.toml
│   └── test.sh
├── .gitignore
├── docker-compose.yml
├── docker-compose-mysql.yml
├── Dockerfile
└── README.md
