import requests
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os

def main():

    print("スクリプト開始！")  # デバッグ用
    
    # 初期設定
    url = "https://b.hatena.ne.jp/entrylist/it/AI%E3%83%BB%E6%A9%9F%E6%A2%B0%E5%AD%A6%E7%BF%92"
    output_file = "makeRSS_HatenaBookmark.xml"

    print(f"初期URL: {url}")  # デバッグ用

    # 既存のRSSフィードを読む
    existing_links = set()
    if os.path.exists(output_file):
        tree = ET.parse(output_file)
        root = tree.getroot()
        for item in root.findall(".//item/link"):
            existing_links.add(item.text)
    else:
        root = ET.Element("rss", version="2.0")
        channel = ET.SubElement(root, "channel")
        title = "はてなブックマーク AI・機械学習からの情報"
        description = "はてなブックマーク AI・機械学習からの情報を提供します。"
        ET.SubElement(channel, "title").text = title
        ET.SubElement(channel, "description").text = description
        ET.SubElement(channel, "link").text = "https://example.com"

        # 初期ページ番号と最終ページ番号
        start_page = 1
        end_page = 100
        current_page = start_page

        # スクレイピング処理
        while url and current_page <= end_page:

            print(f"現在のページ：{current_page}")
            
            response = requests.get(url)
            html_content = response.text

            article_pattern = re.compile(r'<h3 class="entrylist-contents-title">[\s\S]*?<a href="([^"]+)"[\s\S]*?title="([^"]+)"[\s\S]*?<\/a>[\s\S]*?<li class="entrylist-contents-date">([^<]+)<\/li>[\s\S]*?<p class="entrylist-contents-description" data-gtm-click-label="entry-info-description-href">([\s\S]+?)<\/p>')
        
            channel = root.find("channel")
        
            for match in article_pattern.findall(html_content):
                link, title, date, description = match

                if link in existing_links:
                    continue

                new_item = ET.SubElement(channel, "item")
                ET.SubElement(new_item, "title").text = title
                ET.SubElement(new_item, "link").text = link
                ET.SubElement(new_item, "pubDate").text = date
                ET.SubElement(new_item, "description").text = description

            # 次のページへ
            #next_page_match = re.search(r'<a href="([^"]+)" class="js-keyboard-openable">[\s\S]*?次のページ[\s\S]*?<\/a>', html_content)
            next_page_match = re.search(r'<a href="(/entrylist/it/AI%E3%83%BB%E6%A9%9F%E6%A2%B0%E5%AD%A6%E7%BF%92\?page=\d+)" class="js-keyboard-openable">', html_content)

            if next_page_match:
                url = 'https://b.hatena.ne.jp' + next_page_match.group(1)
            else:
                url = None

            current_page += 1  # ページ番号を更新

    # XMLを出力
    xml_str = ET.tostring(root)
    xml_pretty_str = minidom.parseString(xml_str).toprettyxml(indent="  ")
    xml_pretty_str = os.linesep.join([s for s in xml_pretty_str.splitlines() if s.strip()])  # 空白行を削除
    
    with open(output_file, "w") as f:
        f.write(xml_pretty_str)

    print("スクリプト終了！")  # デバッグ用

if __name__ == "__main__":
    main()
