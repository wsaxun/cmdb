/*
Navicat MySQL Data Transfer

Date: 2017-11-27 15:22:30
*/
USE auto_operation;

SET FOREIGN_KEY_CHECKS=0;
-- ----------------------------
-- Records of t_classification_sub
-- ----------------------------
INSERT INTO `t_classification_sub` VALUES ('1', '未记录应用集', '0', '未记录应用集', '1');
-- ----------------------------
-- Records of t_classification_sup
-- ----------------------------
INSERT INTO `t_classification_sup` VALUES ('1', '未记录应用集', '未记录应用集');
-- ----------------------------
-- Records of t_cront
-- ----------------------------
INSERT INTO `t_cront` VALUES ('1', '8', '32');
-- ----------------------------
-- Records of t_interval
-- ----------------------------
INSERT INTO `t_interval` VALUES ('1', '46400');
-- ----------------------------
-- Records of t_rule
-- ----------------------------
INSERT INTO `t_rule` VALUES ('1', '#level >= High#', '1', '2', '红色级别之上告警');
-- ----------------------------
-- Records of t_stragety
-- ----------------------------
INSERT INTO `t_stragety` VALUES ('1', 'StragetyOrigin', '{\'interval\': 0}', '0', '原始聚合');
INSERT INTO `t_stragety` VALUES ('2', 'StragetyEasy', '{\'interval\': 30, \'classify\': \'sub_id\'}', '1', '应用集聚合');
-- ----------------------------
-- Records of t_user
-- ----------------------------
-- ----------------------------
-- Records of t_user_group
