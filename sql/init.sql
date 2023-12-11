-- SQlite stuff
PRAGMA encoding = "UTF-8";

DROP TABLE IF EXISTS `transaction`;

CREATE TABLE `transaction` (
    `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    `symbol_id` INTEGER DEFAULT NULL,
    `price` FLOAT(24) NOT NULL,
    `count` FLOAT(24) NOT NULL,
    `type` VARCHAR(50) NOT NULL,
    `datetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `commission` FLOAT(24) NOT NULL,
    `currency_id` INTEGER,
    `platform_id` INTEGER NOT NULL,
    `user_id` INTEGER NOT NULL,
    `description` TEXT NOT NULL,
    `notes` TEXT DEFAULT NULL,
    `pattern` VARCHAR(255) NOT NULL,
    `timeframe` VARCHAR(24) NOT NULL
);

CREATE INDEX `ix_transaction_symbol` ON `transaction` (`symbol_id`);

CREATE INDEX `ix_transaction_platform` ON `transaction` (`platform_id`);

CREATE INDEX `ix_transaction_type` ON `transaction` (`type`);

DROP TABLE IF EXISTS `symbol`;

CREATE TABLE `symbol` (
    `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    `title` VARCHAR(255) NOT NULL,
    `code` VARCHAR(50) NOT NULL,
    `currency_id` INTEGER DEFAULT NULL,
    `market` VARCHAR(255) NOT NULL
);

CREATE INDEX `ix_transaction_code` ON `symbol` (`code`);

DROP TABLE IF EXISTS `symbol_cumulative`;

CREATE TABLE `symbol_cumulative` (
    `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    `symbol_id` INTEGER NOT NULL,
    `aggregate_count` FLOAT(24) NOT NULL DEFAULT 0,
    `avg_cost` FLOAT(24) DEFAULT NULL,
    `number_of_transactions` INTEGER DEFAULT NULL
);

CREATE INDEX `ix_symbol_cumulative_symbol_id` ON `symbol_cumulative` (`symbol_id`);

DROP TABLE IF EXISTS `platform`;

CREATE TABLE `platform` (
    `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    `title` VARCHAR(255) NOT NULL,
    `url` VARCHAR(255) NOT NULL,
    `logo_url` TEXT DEFAULT NULL,
    `description` TEXT DEFAULT NULL
);

DROP TABLE IF EXISTS `currency`;

CREATE TABLE `currency` (
    `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    `title` VARCHAR(255) NOT NULL,
    `code` VARCHAR(255) NOT NULL
);

DROP TABLE IF EXISTS `user`;

CREATE TABLE `user` (
    `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    `email` VARCHAR(255) NOT NULL,
    `password` VARCHAR(255) NOT NULL,
    `salt` VARCHAR(255) NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `modified_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `last_login_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX `ix_user_email` ON `user` (`email`);