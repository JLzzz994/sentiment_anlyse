CREATE DATABASE IF NOT EXISTS ecommerce_insight DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ecommerce_insight;

CREATE TABLE IF NOT EXISTS customer_ticket (
    id BIGINT PRIMARY KEY,
    merchant_id VARCHAR(32) NOT NULL,
    platform VARCHAR(32) NOT NULL,
    merchant_tier VARCHAR(16) NOT NULL DEFAULT 'standard',
    business_area VARCHAR(32) NOT NULL,
    category VARCHAR(64) NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    priority_score DECIMAL(10,2) NOT NULL DEFAULT 0,
    KEY idx_ticket_created_at (created_at),
    KEY idx_ticket_platform_area (platform,business_area)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS merchant_feedback (
    id BIGINT PRIMARY KEY,
    merchant_id VARCHAR(32) NOT NULL,
    platform VARCHAR(32) NOT NULL,
    feedback_type VARCHAR(32) NOT NULL,
    business_area VARCHAR(32) NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    priority_score DECIMAL(10,2) NOT NULL DEFAULT 0,
    KEY idx_feedback_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS issue_case (
    id BIGINT PRIMARY KEY,
    issue_code VARCHAR(32) NOT NULL UNIQUE,
    platform VARCHAR(32) NOT NULL,
    business_area VARCHAR(32) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    resolution TEXT NULL,
    created_at DATETIME NOT NULL,
    severity_score DECIMAL(10,2) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS product_review (
    id BIGINT PRIMARY KEY,
    platform VARCHAR(32) NOT NULL,
    product_id VARCHAR(64) NOT NULL,
    sku_id VARCHAR(64) NULL,
    rating TINYINT NOT NULL,
    content TEXT NOT NULL,
    review_time DATETIME NOT NULL,
    like_count INT NOT NULL DEFAULT 0,
    reply_count INT NOT NULL DEFAULT 0,
    KEY idx_review_product_time (product_id,review_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
