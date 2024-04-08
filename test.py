import requests
from parsel import Selector
import pdfkit
from urllib.parse import urljoin

# 示例网址
url = "https://docs.cocos.com/creator/manual/zh/getting-started/support.html"

# 用于存储页面内容的字符串
all_content = "<style>body { font-family: 'Microsoft YaHei'; }</style>"

response = requests.get(url)
response.encoding = 'utf-8'
selector = Selector(response.text)

# 提取页面的特定部分，这里假设内容位于<section class="normal markdown-section">中
content = selector.css('section.normal.markdown-section').get()

# 修复相对路径的图片URLs
base_url = "https://docs.cocos.com/creator/manual/zh/getting-started/"
content = selector.css('section.normal.markdown-section').get()
# 确保我们有内容来处理
if content:
    selector = Selector(text=content)
    # 遍历所有<img>标签
    for img in selector.css('img'):
        # 获取图片的原始src属性
        src = img.attrib['src']
        # 将相对路径转换为绝对路径
        absolute_src = urljoin(base_url, src)
        # 替换内容中的src属性为绝对路径
        content = content.replace(src, absolute_src)

# 将处理后的HTML内容累加
all_content += content + "<hr>"  # 使用<hr>作为页面分隔符

options = {
    'no-outline': None,
    'encoding': "UTF-8",
    'enable-local-file-access': None,
    # 这里添加更多的wkhtmltopdf选项
}

# 将所有内容保存到PDF文件中
pdfkit.from_string(all_content, 'output.pdf', options=options)

print("PDF文件已生成")
