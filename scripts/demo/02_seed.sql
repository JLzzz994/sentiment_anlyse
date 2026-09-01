USE ecommerce_insight;

INSERT INTO customer_ticket VALUES
(1001,'M-DEMO-001','taobao','key','售后','退款规则咨询','近期售后规则说明更新后，客服反馈商家对退款处理时点理解不一致，希望系统能在售后单详情直接展示规则来源和生效时间。','2026-08-18 09:20:00',92),
(1002,'M-DEMO-002','taobao','standard','售后','仅退款流程','服饰商家集中咨询仅退款场景下 ERP 状态和平台状态不同步时应该以哪个状态为准，人工核对次数明显增加。','2026-08-19 10:15:00',88),
(1003,'M-DEMO-003','taobao','key','客服','规则解释','一线客服需要频繁跳转平台规则中心确认售后规则，建议知识库能按平台和规则版本返回可追溯说明。','2026-08-20 13:30:00',84),
(1004,'M-DEMO-004','jd','standard','履约','超时发货','大促期间缺货订单触发超时发货风险，商家希望系统提前识别库存不足与待发订单冲突并给出处理优先级。','2026-08-21 11:00:00',81)
ON DUPLICATE KEY UPDATE content=VALUES(content),priority_score=VALUES(priority_score);

INSERT INTO merchant_feedback VALUES
(2001,'M-DEMO-011','taobao','product_request','售后','希望新增平台规则变更提醒，最好能说明受影响的订单类型、售后节点和需要人工确认的动作。','2026-08-18 14:00:00',95),
(2002,'M-DEMO-012','taobao','pain_point','客服','规则更新后培训材料跟不上，一线客服答复口径不一致，容易反复确认。','2026-08-19 09:45:00',90),
(2003,'M-DEMO-013','jd','pain_point','库存','多平台共库存时，活动订单突增会放大缺货和超时发货问题，希望风险能提前到订单分配阶段暴露。','2026-08-21 09:10:00',82),
(2004,'M-DEMO-015','internal','competitor','产品','客户交流中多次提到友商的智能审单和异常单解释能力，希望对比我们现有规则配置、证据追溯和人工审核能力。','2026-08-24 10:05:00',77)
ON DUPLICATE KEY UPDATE content=VALUES(content),priority_score=VALUES(priority_score);

INSERT INTO issue_case VALUES
(3001,'CASE-DEMO-001','taobao','售后','规则版本理解偏差导致重复核单','多个客服班组使用不同版本的售后说明，出现同类退款单处理口径不一致。','统一规则版本号和来源链接；高风险动作仍由人工确认。','2026-07-28 12:00:00',85),
(3002,'CASE-DEMO-002','multi_platform','履约','共享库存导致缺货与超时发货叠加','活动期间多个平台同时占用共享库存，部分订单进入待发后才发现库存不足。','在订单分配前增加可售库存校验并对高风险订单预警。','2026-08-02 11:30:00',80),
(3003,'CASE-DEMO-003','internal','产品','竞品能力被客户高频提及','客户在续费沟通中询问智能审单、异常解释和规则自动更新能力，但现有记录分散，无法形成统一竞品证据。','建立竞品公开信息与客户反馈的统一主题归档。','2026-08-10 10:00:00',72)
ON DUPLICATE KEY UPDATE content=VALUES(content),resolution=VALUES(resolution);

INSERT INTO product_review VALUES
(4001,'taobao','DEMO-OUTDOOR-JACKET','BLACK-M',2,'衣服整体可以，但尺码偏小，按平时尺码买有点紧，换货流程花了几天。','2026-08-15 18:30:00',12,3),
(4002,'taobao','DEMO-OUTDOOR-JACKET','BLACK-L',1,'拉链偶尔卡顿，第一次收到后又申请售后，客服回复还算及时。','2026-08-16 20:10:00',18,4),
(4003,'jd','DEMO-OUTDOOR-JACKET','BLUE-L',2,'活动期间发货比预计慢，商品本身没有大问题，但物流等待时间影响体验。','2026-08-18 08:50:00',9,2),
(4004,'douyin_ec','DEMO-OUTDOOR-JACKET','BLACK-M',2,'直播间说的尺码和实际感觉有差异，建议详情页把身高体重参考写清楚。','2026-08-20 21:15:00',24,6),
(4005,'taobao','DEMO-OUTDOOR-JACKET','BLUE-M',1,'尺码偏小和拉链不顺两个问题都遇到了，申请换货后希望状态更新再快一点。','2026-08-23 20:20:00',20,5)
ON DUPLICATE KEY UPDATE content=VALUES(content),rating=VALUES(rating);
