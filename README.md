# 说明：本项目是一个处理邮件清洗的daemon
# 架构：某个告警平台调用web api把数据存入kafka
       --->守护进程从kafka读取消息
       --->守护进程把消息分类
       --->守护进程把分类后的消息做聚合
       --->守护进程发送告警邮件或者告警短信
 
       守护进程重启是刷新应用集
       守护进程定时执行计划任务（刷新应用集，刷新告警列表，定时发送未解决故障邮件，定时发送邮件汇总）
 
# 其它：告警平台调用的web api使用openresty + lua 编写，接受到消息之后，异步存入kafka
 
# 操作步骤
 1. 把整个项目文件copy到/r2/maintain_scripts/ops/目录
 2. 修改平config目录下配置文件
 3. 修改sbin/collectAlertsd 中py_pth变量，此变量为python绝对路径
 4. 把sbin/collectAlertsd copy 到/etc/rc.d/init.d/ 下
 5. chkconfig --add collectAlertsd
 6. service collectAlertsd start 
 7. chkconfig collectAlertsd on  
