from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `banner` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `title` VARCHAR(255) NOT NULL,
    `image_url` VARCHAR(255) NOT NULL,
    `redirect_url` VARCHAR(255),
    `is_active` BOOL NOT NULL  DEFAULT 1
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `user` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `name` VARCHAR(255) NOT NULL,
    `email` VARCHAR(255) NOT NULL UNIQUE,
    `phone` VARCHAR(20),
    `login_id` VARCHAR(255) NOT NULL UNIQUE,
    `user_type` VARCHAR(10) NOT NULL  DEFAULT 'guest',
    `password` VARCHAR(255) NOT NULL,
    `social_login_type` VARCHAR(50),
    `social_id` VARCHAR(255),
    `refresh_token_id` VARCHAR(255),
    `withdraw_period` DATETIME(6),
    `status` BOOL NOT NULL  DEFAULT 1
) CHARACTER SET utf8mb4 COMMENT='User table';
CREATE TABLE IF NOT EXISTS `category` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `name` VARCHAR(255) NOT NULL,
    `depth` INT NOT NULL  DEFAULT 0,
    `parent_id` INT,
    CONSTRAINT `fk_category_category_0e124d68` FOREIGN KEY (`parent_id`) REFERENCES `category` (`id`) ON DELETE SET NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `non_user_order` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `name` VARCHAR(255) NOT NULL,
    `phone` VARCHAR(20) NOT NULL,
    `shipping_address` VARCHAR(255) NOT NULL,
    `detail_address` VARCHAR(255),
    `request` LONGTEXT
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `non_user_payment` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `transaction_id` VARCHAR(255) NOT NULL UNIQUE,
    `amount` DECIMAL(10,2) NOT NULL,
    `payment_type` VARCHAR(50) NOT NULL,
    `payment_status` VARCHAR(50) NOT NULL,
    `order_id` INT NOT NULL,
    CONSTRAINT `fk_non_user_non_user_5a81d056` FOREIGN KEY (`order_id`) REFERENCES `non_user_order` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `product` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `name` VARCHAR(255) NOT NULL,
    `price` DECIMAL(10,2) NOT NULL,
    `discount` DECIMAL(5,2) NOT NULL  DEFAULT 0,
    `origin_price` DECIMAL(10,2) NOT NULL,
    `description` LONGTEXT,
    `detail` LONGTEXT,
    `brand` VARCHAR(255) NOT NULL  DEFAULT 'micgolf',
    `status` VARCHAR(1) NOT NULL  DEFAULT 'Y',
    `product_code` VARCHAR(255) NOT NULL UNIQUE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `cart` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `product_count` INT NOT NULL  DEFAULT 1,
    `product_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    CONSTRAINT `fk_cart_product_92186a63` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_cart_user_a79aa2ff` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `category_product` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `category_id` INT NOT NULL,
    `product_id` INT NOT NULL,
    CONSTRAINT `fk_category_category_cd472b35` FOREIGN KEY (`category_id`) REFERENCES `category` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_category_product_689579a6` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `non_user_order_product` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `quantity` INT NOT NULL  DEFAULT 1,
    `price` DECIMAL(10,2) NOT NULL,
    `courier` VARCHAR(255),
    `shipping_id` VARCHAR(255),
    `current_status` VARCHAR(255),
    `procurement_status` VARCHAR(255),
    `order_id` INT NOT NULL,
    `product_id` INT NOT NULL,
    CONSTRAINT `fk_non_user_non_user_36abf39a` FOREIGN KEY (`order_id`) REFERENCES `non_user_order` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_non_user_product_d00e4c17` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `option` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `size` VARCHAR(255) NOT NULL,
    `color` VARCHAR(255) NOT NULL,
    `color_code` VARCHAR(255),
    `product_id` INT NOT NULL,
    CONSTRAINT `fk_option_product_ccfbb3fe` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `count_product` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `count` INT NOT NULL  DEFAULT 0,
    `option_id` INT NOT NULL,
    `product_id` INT NOT NULL,
    CONSTRAINT `fk_count_pr_option_20e4c507` FOREIGN KEY (`option_id`) REFERENCES `option` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_count_pr_product_a33d2f44` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `option_image` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `image_url` VARCHAR(255) NOT NULL,
    `option_id` INT NOT NULL,
    CONSTRAINT `fk_option_i_option_ed4344e0` FOREIGN KEY (`option_id`) REFERENCES `option` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `promotion_product` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `promotion_type` VARCHAR(10) NOT NULL,
    `is_active` BOOL NOT NULL  DEFAULT 1,
    `product_id` INT NOT NULL,
    CONSTRAINT `fk_promotio_product_f620f170` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`) ON DELETE CASCADE
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
