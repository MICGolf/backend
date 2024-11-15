from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `banner` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `best_production` (
    `product_id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `is_active` BOOL NOT NULL,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `category` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `mdschoice` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `product` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
