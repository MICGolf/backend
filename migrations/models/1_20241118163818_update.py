from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `banner` ADD `banner_type` VARCHAR(10) NOT NULL;
        ALTER TABLE `product` ADD `discount_option` VARCHAR(10) NOT NULL  COMMENT 'PERCENT: percent\nAMOUNT: amount' DEFAULT 'percent';

        -- Change ON DELETE action for category.parent_id to CASCADE
        ALTER TABLE `category` DROP FOREIGN KEY `fk_category_category_0e124d68`;
        ALTER TABLE `category`
        ADD CONSTRAINT `fk_category_category_0e124d68`
        FOREIGN KEY (`parent_id`) REFERENCES `category` (`id`) ON DELETE CASCADE;
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `banner` DROP COLUMN `banner_type`;
        ALTER TABLE `product` DROP COLUMN `discount_option`;

        -- Revert ON DELETE action for category.parent_id to SET NULL
        ALTER TABLE `category` DROP FOREIGN KEY `fk_category_category_0e124d68`;
        ALTER TABLE `category`
        ADD CONSTRAINT `fk_category_category_0e124d68`
        FOREIGN KEY (`parent_id`) REFERENCES `category` (`id`) ON DELETE SET NULL;
    """
