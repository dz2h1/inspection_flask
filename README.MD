简介  
====
这是一个基于flask框架和mongodb数据库的小型巡检工具。  
工具通过web形式展示以下内容：  
1、巡检端到被检测设备的网络延迟和延迟历史数据的折线图表；  
2、页面http头部状态码；  
3、页面的大小；  
4、被检测服务器的CPU负载、内存使用率、根目录使用率的信息；  
5、巡检时故障的日志记录。  
可配置定时对网络延迟、状态码和页面数据长度进行巡检，遇到网络、应用异常时可以进行邮件或企业微信报警。  
数据长度检测主要用于页面被改动的提示。  

V0.2.2 版本更新  
定时巡检新增flask_apscheduler插件方式。  

V0.2.1 版本更新  
增加对Win系统的支持，服务器巡检改为使用paramiko模块，log页面添加分页。优化定时巡检功能代码。  

V0.1.7 版本更新  
大部分函数添加说明，删除留存的无用函数。

V0.1.6 版本更新  
charts图表数据直接采取聚合方式取值。将前端状态颜色判断工作由主文件改至模板渲染。定时检测发送的默认配置从只检测页面大小改为全部启动。优化一些邮件显示和数据插入。

V0.1.5 版本更新  
优化报警巡检初始化时，check表中无值报错导致无法发送邮件的问题。  
  
V0.1.4 版本更新  
dev页面增加网络延迟报警阈值设定，默认报警阈值为100ms，可在dev页面中修改。  
优化告警信息格式，内容展示更清晰。
### 部署环境  
在CentOS6、7和Ubuntu18.04、mint19、Raspbian中运行正常，其余linux发行版未测试。中文windows系统下展示和手动巡检部分正常。  
数据库使用mongodb，版本3.6、4.0、4.2正常工作，其余版本未测试。巡检工具默认需要用户名密码访问名为inspection的数据库，请新建该数据库并设定用户名密码。  
python3.6、3.7版本正常。不支持python2，其余未测试。  
  
### 依赖  
#### 静态文件  
css样式文件采用bootstrap，图表使用Chart.js，所需文件都已经放置于static文件夹中。  
  
#### python  
pip安装flask、pymongo、requests、gevent、paramiko包，flask版本 >= 1.0.0，低版本未测试。  
```sh
$ pip install flask pymongo requests gevent paramiko flask_apscheduler
```
  
### 使用
完成上述工作并部署完成工具后，需要进行如下配置（linux）：  
#### 修改配置
部署正式配置文件。  
```sh
$ cp config/settings_example.py config/settings.py
$ cp crontab_mail/mail_settings_example.py crontab_mail/mail_settings.py
$ cp crontab_mail/wechat_settings_example.py crontab_mail/wechat_settings.py
```
settings中修改数据库服务器地址、用户名、密码等信息。  
mail_settings中进行报警邮件相关配置，wechat_settings.py进行企业微信推送配置（邮件、微信报警选一个）。  
```sh
$ vim config/settings.py
$ vim crontab_mail/mail_settings.py
$ vim crontab_mail/wechat_settings.py
```
  
#### 启动巡检工具
```sh
$ python3 inspection_main.py
```
直接用浏览器访问项目服务器地址，测试巡检工具是否正常启动。
#### 数据库初始化
浏览器访问后台管理页面 /console/  
在后台管理页面插入数据到inspection数据库相关集合中：  
dev集合为ping检测使用，支持ip和域名；  
svr集合为http状态码检测使用，需要输入完整的网页访问地址；  
size集合为网站页面数据长度检测使用，需要输入完整的网页访问地址；  
info集合为服务器巡检使用，仅支持linux服务器。  
  
info集合中存储的服务器密码只进行了简单的加密，可在check_info目录下的disweb和sshcheck文件中修改加密和解密函数规则。  

同一集合内名称请勿重复，且不可使用汉字。如集合内条目错误可在下方输入该条目名称进行删除。  
  
#### 巡检监控配置
访问 /crontab/ 触发巡检，具体巡检顺序由主程序中inspection_crontab控制。设置settings内reportSetTime参数可控制报告时间，如reportSetTime = '0830'为上午8:30发送巡检报告。  
访问 /crondev/ 触发dev设备巡检。表格数据数量由settings中charts_dis_num_limit控制，默认为12。  
以上巡检有两种方式。1、可通过settings内schedulerEnabled参数改为True启动，crontabTime和crondevTime设置巡检间隔时间。2、可以通过访问页面/crontab/和/crondev/触发巡检。  
    
例如通过访问页面巡检方法可通过curl命令和crontab定时控制完成：  
```sh
$ crontab -e
```
crontab配置例子：  
```
#每2分钟触发巡检
*/2 * * * * /usr/bin/curl -I -s http://服务器IP/crontab/ -o /dev/null

#每10分钟触发dev设备巡检
*/10 * * * * /usr/bin/curl -I -s http://服务器IP/crondev/ -o /dev/null
```
一般建议使用settings内schedulerEnabled等参数开启巡检。  
有些服务器可能登录耗时较长，所以服务器巡检需要进入 /info/ 页面手动点击按钮完成。  
后台管理界面也可以通过点击日志页面中的版本号进入。    

----------------------------------------------------------------------------
### Mongodb安装和配置
CentOS系统安装Mongodb教程：
https://docs.mongodb.com/manual/tutorial/install-mongodb-on-red-hat/  

登录mongo：  
```sh
$ mongo --port 27017 
```

#### admin数据库验证配置
```sh
> use admin; 
> db.createUser({user: "用户名",pwd: "密码",roles: [ { role: "userAdminAnyDatabase", db: "admin" } ]}); 
```

#### inspection数据库验证配置
```sh
> use inspection; 
> db.createUser({user: "用户名",pwd: "密码",roles: [ { role: "dbOwner", db: "inspection" } ]}); 
```

#### 开启验证配置
修改配置文件  
```sh
$ vim /etc/mongod.conf 
```
添加如下配置（注意空格）  
```
security: 
  authorization: enabled 
```

重启MongoDB服务  
CentOS6：  
```sh
$ /etc/init.d/mongod restart 
```
CentOS7：  
```sh
$ systemctl restart mongod 
```
