USE ecommerce_insight;
SELECT source_table,COUNT(*) document_count,ROUND(AVG(hotness_score),2) avg_hotness
FROM ecommerce_insight_document GROUP BY source_table ORDER BY document_count DESC;

SELECT platform,source_table,source_id,LEFT(content,120) content_preview,
FROM_UNIXTIME(published_at) published_at,hotness_score
FROM ecommerce_insight_document
ORDER BY hotness_score DESC,published_at DESC LIMIT 10;
