# court
裁判文书网

**FAQ**
1,首次访问会出现网站访问频繁，出现输入验证码页面(这不是针对个人，而是所有访问这个网站的机器)
2,频繁的访问或下载（比如下载5条之后，就会出现下载列表错误，出现验证码）
3,文书网，每天只能爬一次，爬多了，会封ip
4,写文件的日志，必须调一下缓存大小，不是实时写入
5,文书网服务器压力大时，会出现【下载列表失败】错误，建议闲时下载

**Windows环境下**
1,安装pip install pytesseract
2,安装pip install pillow
3,安装Tesseract-OCR程序
4,运行程序出现win Error2错误,解决办法：打开文件 pytesseract.py，找到如下代码，将tesseract_cmd的值修改为全路径，在此使用就不会报错了
    # CHANGE THIS IF TESSERACT IS NOT IN YOUR PATH, OR IS NAMED DIFFERENTLY
    # tesseract_cmd = 'tesseract'
    tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract.exe'
