#!/anaconda3/bin/python
# -*- coding: utf-8 -*-
# Date: 2017.12.15
# Author: Zhu Mengyan
# Email: zhumengyan1994@gmail.com
# purpose: douban 豆瓣阅读 免费
# requests + re + BeautifulSoup + selenium

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import re
import csv
import random
import time


headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8"
}
url = "https://read.douban.com/"


def get_free_url(raw_url):
    """
    获得免费书籍的url
    :param raw_url: url
    :return: url for free e-books
    """
    response = requests.get(raw_url, headers, timeout = 10)
    soup = BeautifulSoup(response.text, "lxml")
    suffix = soup.select(".inner ul li a")[6]["href"]
    new_url = raw_url[:-1] + suffix
    print("Got url for free e-books...")
    return new_url


def get_page_url(new_url):
    """

    :param new_url: 免费书籍的url(home)
    :return: 免费书籍各页的url
    """
    url_list = []
    browser = webdriver.PhantomJS()
    browser.get(new_url)
    pagination = browser.find_element_by_class_name("pagination")
    a = pagination.find_elements_by_tag_name("a")
    tmp_url = a[2].get_attribute("href")
    for i in range(1, 560):
        num = (i - 1) * 20
        tmp_url1 = re.sub("start=(\d+)&", "start=" + str(num) + "&", tmp_url)
        url_list.append(tmp_url1)
    browser.close()
    print("Got urls for all pages...")
    return url_list



def isElementExist(alt, element):
    """
    判断是否存在某个标签属性
    :param alt: info_list
    :param element: 标签属性
    :return: True or False
    """
    flag = True
    try:
        alt.find_element_by_css_selector(element)
        return flag
    except:
        flag = False
        return  flag


def get_info(url):
    """
    获得详细信息
    :param url: 免费书籍的各页的url
    :return: 详细信息的列表
    """
    browser = webdriver.PhantomJS()
    browser.get(url)
    browser.set_page_load_timeout(20)
    time.sleep(5)
    ## info
    info_lists = browser.find_elements_by_class_name("info")
    detailed_info = []
    for info_list in info_lists:
        if (isElementExist(info_list, ".subscribe")):  ## 判断是连载还是书籍
            author = info_list.find_element_by_css_selector(".author").text
            category = info_list.find_element_by_css_selector(".category").text
            name = info_list.find_element_by_css_selector(".title a").text
            description = info_list.find_element_by_css_selector(".intro").text
            rating_average = -1
            rating_number = -1
        else:
            author = info_list.find_element_by_css_selector(".labeled-text .author-item").text
            category = info_list.find_element_by_css_selector(".category .labeled-text").text
            name = info_list.find_element_by_css_selector(".title a").text
            description = info_list.find_element_by_css_selector(".article-desc-brief").text
            #rating_number = info_list.find_element_by_css_selector(".rating-amount .ratings-link").text[1:-1]
            if (isElementExist(info_list, ".rating-amount .ratings-link")):
                rating_number = info_list.find_element_by_css_selector(".rating-amount .ratings-link").text[1:-1]
            else:
                rating_number = 0

            if (isElementExist(info_list, ".rating-average")):  ## 判断是否有评分均值
                rating_average = info_list.find_element_by_css_selector(".rating-average").text
            else:
                rating_average = 0
        detailed_info.append((name, author, category, rating_average, rating_number, description))
    browser.close()
    return detailed_info


def write_to_file(info):
    """
    将数据写入文件
    :param info: 详细信息列表
    :return: csv文件
    """
    with open("douban_dushu.csv", "a") as csvfile:
        writer = csv.writer(csvfile)

        ##  写入列名
        writer.writerow(["name", "author", "category", "rating_number", "description"])
        ##  写入信息
        for i in info:
            writer.writerow(i)


def write_to_sql(info):
    """
    将数据写入数据库， 待完成
    :param info: 详细信息列表
    :return:
    """
    pass


def main(url):
    info = []  ## store detailed info
    new_url = get_free_url(url)  ##  获取免费书籍的主页url
    urls = get_page_url(new_url)  ##  获取免费书籍各页的url列表
    num = 0
    for url in urls:
        tmp_info = get_info(url)
        info.extend(tmp_info)
        time.sleep(random.randint(2, 8))
        num += 1
        print("Page",num, "is done...")
    write_to_file(info)

if __name__ == "__main__":
    main(url)





