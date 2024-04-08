import requests
from parsel import Selector
from urllib.parse import urljoin
import pdfkit

def fetch_page(url):
    """尝试获取页面内容，失败时返回None"""
    try:
        response = requests.get(url)
        response.raise_for_status()  # 确保响应状态码为200
        response.encoding = 'utf-8'
        return response.text
    except requests.RequestException as e:
        print(f"请求错误: {e}")
        return None

def fix_image_paths(base_url, content):
    """修正HTML内容中图片的路径"""
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
    return content

def get_chapters(base_url):
    """获取所有章节的标题和链接"""
    page_content = fetch_page(base_url)
    if page_content is None:
        return []
    
    selector = Selector(page_content)
    chapters = selector.css('.summary .chapter a')
    return chapters

def generate_pdf_from_chapters(base_url, chapters):
    """根据章节内容生成PDF"""
    all_content = "<style>body { font-family: 'Microsoft YaHei'; }</style>"
    
    for chapter in chapters:
        title = chapter.css('::text').get().strip()
        href = chapter.css('::attr(href)').get()
        full_url = urljoin(base_url, href)

        chapter_content = fetch_page(full_url)
        if chapter_content:
            # 修正图片路径
            fixed_content = fix_image_paths(full_url, chapter_content)
            chapter_selector = Selector(text=fixed_content)
            content = chapter_selector.css('section.normal.markdown-section').get()
            all_content += f"<h1>{title}</h1>{content}<hr>"
        else:
            print(f"跳过无法获取的章节: {title}")

    # PDF生成选项
    options = {
        'no-outline': None,
        'encoding': "UTF-8",
        'enable-local-file-access': None
    }

    # 将所有内容保存到PDF文件中
    pdfkit.from_string(all_content, 'output.pdf', options=options)

def main():
    base_url = "https://docs.cocos.com/creator/manual/zh/"
    chapters = get_chapters(base_url)
    if chapters:
        generate_pdf_from_chapters(base_url, chapters)
        print("PDF文件已生成")
    else:
        print("无法获取章节信息")

main()
