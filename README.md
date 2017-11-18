ScrapyGithub v1.0

基于Scrapy爬虫对Github网站的抓取

模拟github和zhihu登录，并对github网页 https://github.com/user 中overview、repository、star、followers、following的tab页中的内容进行抓取，并将抓取内容分别保存到json、txt、mysql数据中。<br /> 

使用说明：
1、创建github的数据库（使用utf8mb4的编码，否则无法插入emoji表情），运行github.sql;
2、创建user.txt文件，格式为：	userName \r password
