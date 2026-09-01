USE ecommerce_insight;
DROP VIEW IF EXISTS ecommerce_insight_document;
CREATE VIEW ecommerce_insight_document AS
SELECT 'internal_crm' platform,'customer_ticket' source_table,id source_id,
CONCAT('平台:',platform,'；商家等级:',merchant_tier,'；业务环节:',business_area,'；问题分类:',category,'；工单内容:',content) content,
UNIX_TIMESTAMP(created_at) published_at,0 likes,0 comments,0 shares,0 collects,0 replies,priority_score hotness_score
FROM customer_ticket
UNION ALL
SELECT 'internal_feedback','merchant_feedback',id,
CONCAT('原平台:',platform,'；反馈类型:',feedback_type,'；业务环节:',business_area,'；反馈内容:',content),
UNIX_TIMESTAMP(created_at),0,0,0,0,0,priority_score FROM merchant_feedback
UNION ALL
SELECT 'internal_case','issue_case',id,
CONCAT('平台:',platform,'；业务环节:',business_area,'；案例标题:',title,'；问题:',content,'；历史处理:',COALESCE(resolution,'')),
UNIX_TIMESTAMP(created_at),0,0,0,0,0,severity_score FROM issue_case
UNION ALL
SELECT platform,'product_review',id,
CONCAT('商品:',product_id,'；SKU:',COALESCE(sku_id,''),'；评分:',rating,'；评价:',content),
UNIX_TIMESTAMP(review_time),like_count,0,0,0,reply_count,((6-rating)*10+like_count+reply_count*3) FROM product_review;
