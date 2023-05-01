-- SQlite stuff
PRAGMA encoding = "UTF-8";

DROP TABLE `journal_transaction`;

DROP TABLE `ticker`;

DROP TABLE `broker`;

DROP TABLE `currency`;

CREATE TABLE `journal_transaction` (
    `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    `ticker_id` INTEGER DEFAULT NULL,
    `type` VARCHAR(50) NOT NULL,
    `lot` FLOAT(24) NOT NULL,
    `price` FLOAT(24) NOT NULL,
    `fee` FLOAT(24) NOT NULL,
    `currency_id` INT(10),
    `description` TEXT,
    `broker_id` INT(10),
    `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `modified` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX `ix_ticker` ON `journal_transaction` (`ticker_id`);

CREATE INDEX `ix_broker` ON `journal_transaction` (`broker_id`);

CREATE INDEX `ix_type` ON `journal_transaction` (`type`);

CREATE TABLE `ticker` (
    `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    `title` VARCHAR(255) NOT NULL,
    `code` VARCHAR(50) NOT NULL,
    `market` VARCHAR(255) NOT NULL
);

CREATE TABLE `broker` (
    `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    `title` VARCHAR(255) NOT NULL,
    `url` VARCHAR(255) NOT NULL,
    `description` TEXT
);

CREATE TABLE `currency` (
    `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    `title` VARCHAR(255) NOT NULL,
    `code` VARCHAR(255) NOT NULL
);