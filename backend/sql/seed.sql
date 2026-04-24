INSERT INTO roles(name) VALUES ('admin'), ('operator');
INSERT INTO dictionary_items(dict_type,label,value,sort_order,enabled) VALUES
('department','浆洗所','浆洗所',1,1),
('department','红牌楼所','红牌楼所',2,1),
('department','玉林所','玉林所',3,1),
('decision_content','撤销重新作出','撤销重新作出',1,1),
('decision_content','维持','维持',2,1),
('case_type','食品','食品',1,1),
('case_type','广告','广告',2,1),
('current_status','待处理','待处理',1,1),
('current_status','处理中','处理中',2,1),
('current_status','已答复','已答复',3,1);
INSERT INTO responsible_mappings(rule_name,handling_department,primary_name,primary_wechat_remark,backup_name,backup_wechat_remark,warning_days,enabled)
VALUES ('浆洗所默认规则','浆洗所','张三','张三','李四','李四',3,1);
INSERT INTO system_params(param_key,param_value,remark) VALUES
('near_threshold','3','临期提醒阈值'),
('urgent_threshold','1','紧急提醒阈值'),
('deadline_workdays','10','签收日期后多少个工作日为最晚答复日'),
('auto_notify_enabled','true','是否启用自动微信通知'),
('preview_only_mode','true','是否预览不发送'),
('max_retry','3','失败重试次数'),
('throttle_seconds','4','发送节流秒数');
