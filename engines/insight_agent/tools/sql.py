"""电商私域统一证据视图的 MySQL 检索 SQL。

上游将客服工单、商家反馈、历史问题案例、商品评价/追评映射到
ecommerce_insight_document，Agent 层不直接绑定 ERP/CRM 原始业务表。
"""

from sqlalchemy import text


def db_sql_statement():
    return text("""
        SELECT
            platform,
            source_table,
            source_id AS mysql_primary_key,
            content AS title_or_content,
            published_at,
            COALESCE(likes, 0) AS eng_likes,
            COALESCE(comments, 0) AS eng_comments,
            COALESCE(shares, 0) AS eng_shares,
            COALESCE(collects, 0) AS eng_collects,
            COALESCE(replies, 0) AS eng_replies,
            COALESCE(hotness_score, 0) AS hotness_score
        FROM ecommerce_insight_document
        WHERE content LIKE :search_term
        ORDER BY hotness_score DESC, published_at DESC
        LIMIT :limit
    """)


def vector_sql_statement():
    return text("""
        SELECT
            platform,
            source_table,
            source_id AS mysql_primary_key,
            content,
            published_at,
            COALESCE(likes, 0) AS eng_likes,
            COALESCE(comments, 0) AS eng_comments,
            COALESCE(shares, 0) AS eng_shares,
            COALESCE(collects, 0) AS eng_collects,
            COALESCE(replies, 0) AS eng_replies,
            COALESCE(hotness_score, 0) AS hotness_score
        FROM ecommerce_insight_document
        WHERE content IS NOT NULL
          AND content <> ''
    """)
