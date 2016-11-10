# court
裁判文书网

**问题**
1,首次访问会出现网站访问频繁，出现输入验证码页面(这不是针对个人，而是所有访问这个网站的机器)

**Windows环境下**
1,安装pip install pytesseract
2,安装pip install pillow
3,安装Tesseract-OCR程序
4,运行程序出现win Error2错误,解决办法：打开文件 pytesseract.py，找到如下代码，将tesseract_cmd的值修改为全路径，在此使用就不会报错了
    # CHANGE THIS IF TESSERACT IS NOT IN YOUR PATH, OR IS NAMED DIFFERENTLY
    # tesseract_cmd = 'tesseract'
    tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract.exe'
