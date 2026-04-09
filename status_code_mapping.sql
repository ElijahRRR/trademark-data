-- USPTO Trademark Status Code Mapping
-- 用于将数字状态码分类为 LIVE / DEAD
-- 来源: USPTO Official Status Line Documentation (cons181.htm)
-- https://www.uspto.gov/news/og/con/files/cons181.htm

CREATE TABLE IF NOT EXISTS status_code_mapping (
    status_code TEXT PRIMARY KEY,
    live_dead   TEXT NOT NULL,        -- 'LIVE' or 'DEAD'
    category    TEXT NOT NULL,        -- 分类
    description TEXT                  -- 含义
);

TRUNCATE status_code_mapping;

INSERT INTO status_code_mapping (status_code, live_dead, category, description) VALUES
-- ========================================
-- DEAD: 已放弃 (Abandoned) 600-618
-- ========================================
('600', 'DEAD', 'abandoned', 'Abandoned - Incomplete'),
('601', 'DEAD', 'abandoned', 'Abandoned - Express'),
('602', 'DEAD', 'abandoned', 'Abandoned - Failure to Respond'),
('603', 'DEAD', 'abandoned', 'Abandoned - After ex parte Appeal'),
('604', 'DEAD', 'abandoned', 'Abandoned - After inter partes Decision'),
('605', 'DEAD', 'abandoned', 'Abandoned - After Publication'),
('606', 'DEAD', 'abandoned', 'Abandoned - No Statement of Use Filed (ITU)'),
('607', 'DEAD', 'abandoned', 'Abandoned - Defective Statement of Use (ITU)'),
('608', 'DEAD', 'abandoned', 'Abandoned - After Petition Decision'),
('609', 'DEAD', 'abandoned', 'Abandoned - Defective Divided Application'),
('610', 'DEAD', 'abandoned', 'Abandoned - Petition Dismissed'),
('612', 'LIVE', 'petition',  'Petition to Revive Received'),
('614', 'DEAD', 'abandoned', 'Abandoned - Petition to Revive Denied'),
('616', 'LIVE', 'petition',  'Revived - Awaiting Further Action'),
('618', 'DEAD', 'abandoned', 'Abandoned File - Backfile'),

-- ========================================
-- DEAD: 杂项 (Miscellaneous Dead)
-- ========================================
('0',   'DEAD', 'other',     'Unknown/Unassigned'),
('400', 'DEAD', 'other',     'Pre-examination - Abandoned'),
('401', 'DEAD', 'other',     'Pre-examination - Abandoned'),
('402', 'DEAD', 'other',     'Pre-examination - Abandoned'),
('403', 'DEAD', 'other',     'Pre-examination - Abandoned'),
('404', 'DEAD', 'other',     'Pre-examination - Abandoned'),
('405', 'DEAD', 'other',     'Pre-examination - Abandoned'),
('406', 'DEAD', 'other',     'Pre-examination - Abandoned'),
('411', 'DEAD', 'other',     'Pre-examination - Abandoned'),
('412', 'DEAD', 'other',     'Pre-examination - Abandoned'),
('414', 'DEAD', 'other',     'Pre-examination - Abandoned'),
('415', 'DEAD', 'other',     'Pre-examination - Abandoned'),
('417', 'DEAD', 'other',     'Pre-examination - Abandoned'),
('622', 'DEAD', 'other',     'Misassigned Serial Number'),
('626', 'DEAD', 'other',     'Registered - Backfile Cancelled or Expired'),

-- ========================================
-- LIVE: 审查中 (Under Examination) 630-699
-- ========================================
('630', 'LIVE', 'examination', 'New Application - Record Initialized, Not Assigned to Examiner'),
('631', 'LIVE', 'examination', 'New Application - Divided - Initial Processing'),
('632', 'LIVE', 'examination', 'Informal Application - Incomplete'),
('638', 'LIVE', 'examination', 'New Application - Assigned to Examiner'),
('640', 'LIVE', 'examination', 'Non-final Action Counted - Not Mailed'),
('641', 'LIVE', 'examination', 'Non-final Action - Mailed'),
('642', 'LIVE', 'examination', 'Non-final Action'),
('643', 'LIVE', 'examination', 'Previous Action/Approval Count Withdrawn'),
('644', 'LIVE', 'examination', 'Final Refusal Counted - Not Mailed'),
('645', 'LIVE', 'examination', 'Final Refusal - Mailed'),
('646', 'LIVE', 'examination', 'Examiners Amendment Counted - Not Mailed'),
('647', 'LIVE', 'examination', 'Final Refusal - After Response'),
('648', 'LIVE', 'examination', 'Final Refusal'),
('649', 'LIVE', 'examination', 'Action Continuing Final - Mailed'),
('650', 'LIVE', 'examination', 'Suspension Inquiry Counted - Not Mailed'),
('651', 'LIVE', 'examination', 'Suspension Inquiry - Mailed'),
('652', 'LIVE', 'examination', 'Suspension Inquiry'),
('653', 'LIVE', 'examination', 'Suspension Letter - Mailed'),
('654', 'LIVE', 'examination', 'Report Completed Suspension Check - Case Still Suspended'),
('655', 'LIVE', 'examination', 'Suspension'),
('656', 'LIVE', 'examination', 'Examiners Amendment/Priority Action Mailed'),
('657', 'LIVE', 'examination', 'Priority Action'),
('658', 'LIVE', 'examination', 'Priority Action Mailed'),
('659', 'LIVE', 'examination', 'Priority Action'),
('660', 'LIVE', 'examination', 'Subsequent Final Mailed'),
('661', 'LIVE', 'examination', 'Response After Non-Final Action - Entered'),
('663', 'LIVE', 'examination', 'Response After Final Action'),
('665', 'LIVE', 'examination', 'Response'),
('666', 'LIVE', 'examination', 'Response After Action'),
('672', 'LIVE', 'examination', 'Awaiting Action'),
('680', 'LIVE', 'examination', 'Approved for Publication'),
('681', 'LIVE', 'examination', 'Publication/Issue Review Complete'),
('686', 'LIVE', 'examination', 'Published for Opposition'),
('688', 'LIVE', 'examination', 'Notice of Allowance - Issued (ITU)'),
('689', 'LIVE', 'examination', 'Notice of Allowance - Withdrawn'),
('690', 'LIVE', 'examination', 'Notice of Allowance'),
('692', 'LIVE', 'examination', 'Withdrawn Before Publication'),
('694', 'LIVE', 'examination', 'Withdrawn Before Issue'),

-- ========================================
-- LIVE: 已注册 (Registered) 700-708
-- ========================================
('700', 'LIVE', 'registered', 'Registered'),
('701', 'LIVE', 'registered', 'Section 8 - Accepted'),
('702', 'LIVE', 'registered', 'Section 8 & 15 - Accepted and Acknowledged'),
('703', 'LIVE', 'registered', 'Section 15 - Acknowledged'),
('704', 'LIVE', 'registered', 'Partial Section 8 - Accepted'),
('705', 'LIVE', 'registered', 'Partial Section 8 & 15 - Accepted and Acknowledged'),
('706', 'LIVE', 'registered', 'Section 71 - Accepted'),
('707', 'LIVE', 'registered', 'Partial Section 71 - Accepted'),
('708', 'LIVE', 'registered', 'Partial Section 71 & 15 - Accepted and Acknowledged'),

-- ========================================
-- DEAD: 已取消 (Cancelled) 709-716
-- ========================================
('709', 'DEAD', 'cancelled', 'Cancelled - Section 71'),
('710', 'DEAD', 'cancelled', 'Cancelled - Section 8'),
('711', 'DEAD', 'cancelled', 'Cancelled - Section 7(d)'),
('712', 'DEAD', 'cancelled', 'Cancelled by Court Order under Section 37'),
('713', 'DEAD', 'cancelled', 'Cancelled - Section 18'),
('714', 'DEAD', 'cancelled', 'Cancelled - Section 24'),
('715', 'LIVE', 'examination', 'Cancelled - Restored to Pendency'),
('717', 'DEAD', 'cancelled', 'Cancelled'),
('718', 'DEAD', 'cancelled', 'Cancelled'),
('719', 'DEAD', 'cancelled', 'Cancelled'),
('720', 'DEAD', 'cancelled', 'Cancelled'),
('721', 'DEAD', 'cancelled', 'Cancelled'),
('722', 'DEAD', 'cancelled', 'Cancelled'),
('725', 'DEAD', 'cancelled', 'Cancelled'),

-- ========================================
-- LIVE: ITU 延期 (Intent-to-Use Extensions) 730-734
-- ========================================
('730', 'LIVE', 'itu_extension', '1st Extension - Granted'),
('731', 'LIVE', 'itu_extension', '2nd Extension - Granted'),
('732', 'LIVE', 'itu_extension', '3rd Extension - Granted'),
('733', 'LIVE', 'itu_extension', '4th Extension - Granted'),
('734', 'LIVE', 'itu_extension', '5th Extension - Granted'),
('739', 'LIVE', 'itu_extension', 'Extension Request Filed'),
('744', 'LIVE', 'itu_extension', 'Extension'),
('745', 'LIVE', 'itu_extension', 'Extension'),
('746', 'LIVE', 'itu_extension', 'Extension'),
('748', 'LIVE', 'itu_extension', 'Statement of Use - To Examiner for Examination'),
('753', 'LIVE', 'itu_extension', 'Statement of Use'),
('757', 'LIVE', 'itu_extension', 'Statement of Use'),

-- ========================================
-- LIVE: TTAB 程序 (Trial & Appeal Board) 760-794
-- ========================================
('760', 'LIVE', 'ttab', 'Ex Parte Appeal Pending'),
('762', 'LIVE', 'ttab', 'Appeal'),
('765', 'LIVE', 'ttab', 'Appeal'),
('766', 'LIVE', 'ttab', 'Appeal'),
('771', 'LIVE', 'ttab', 'TTAB Proceeding'),
('773', 'LIVE', 'ttab', 'TTAB Proceeding'),
('774', 'LIVE', 'ttab', 'Opposition Pending'),
('775', 'LIVE', 'ttab', 'Opposition'),
('777', 'LIVE', 'ttab', 'Opposition'),
('780', 'LIVE', 'ttab', 'Cancellation Terminated - See TTAB Records'),
('781', 'LIVE', 'ttab', 'Cancellation'),
('782', 'LIVE', 'ttab', 'SU - Opposition Decided - Entry of Judgment Deferred'),
('783', 'LIVE', 'ttab', 'SU - Cancellation Decided - Entry of Judgment Deferred'),
('790', 'LIVE', 'ttab', 'Cancellation Pending'),
('794', 'LIVE', 'ttab', 'Jurisdiction Restored to Examining Attorney'),

-- ========================================
-- LIVE: 已续展 (Renewed) 800-819
-- 注意: 800 在 XML 数据中可能包含已过期但曾续展的商标
-- 但 USPTO 官方将其归类为 LIVE
-- ========================================
('800', 'LIVE', 'renewed',   'Registered and Renewed'),
('801', 'LIVE', 'renewed',   'Opposition Papers Filed (Post-Reg)'),
('802', 'LIVE', 'renewed',   'Request for Extension of Time to File Opposition'),
('803', 'LIVE', 'renewed',   'Amendment After Publication'),
('804', 'LIVE', 'renewed',   'Post-Registration'),
('806', 'LIVE', 'renewed',   'Post-Registration'),
('807', 'LIVE', 'renewed',   'SU - Non-final Action - Mailed'),
('809', 'LIVE', 'renewed',   'SU - Final Refusal - Mailed'),
('810', 'LIVE', 'renewed',   'Post-Registration'),
('811', 'LIVE', 'renewed',   'Post-Registration'),
('812', 'LIVE', 'renewed',   'Post-Registration'),
('813', 'LIVE', 'renewed',   'Post-Registration'),
('814', 'LIVE', 'renewed',   'Post-Registration'),
('815', 'LIVE', 'renewed',   'Post-Registration'),
('816', 'LIVE', 'renewed',   'Post-Registration'),
('817', 'LIVE', 'renewed',   'Post-Registration'),
('818', 'LIVE', 'renewed',   'Post-Registration'),
('819', 'LIVE', 'renewed',   'SU - Registration Review Complete'),
('821', 'LIVE', 'renewed',   'Post-Registration'),
('823', 'LIVE', 'renewed',   'Post-Registration'),
('825', 'LIVE', 'renewed',   'Post-Registration'),

-- ========================================
-- DEAD: 已过期 (Expired) 900
-- ========================================
('900', 'DEAD', 'expired',   'Expired'),
('901', 'DEAD', 'expired',   'Expired'),

-- ========================================
-- LIVE: 待决 (Pending Decision) 968-973
-- ========================================
('968', 'LIVE', 'pending',   'Pending - Pre-examination'),
('969', 'LIVE', 'pending',   'Non-Registration Data'),
('973', 'LIVE', 'pending',   'Pending Petition / Court Decision');

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_status_mapping_live_dead ON status_code_mapping(live_dead);

-- 验证
SELECT live_dead, COUNT(*) FROM status_code_mapping GROUP BY live_dead;
