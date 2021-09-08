import asyncio

import aiohttp
from bs4 import BeautifulSoup

baseurl = "https://www.discudemy.com/search/"


async def req(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            varr = await response.text()
            return varr


class Courses:
    async def get_course(self, topic):
        content = await req((baseurl + topic))
        html_content = BeautifulSoup(content, "html.parser")
        content_in_div = html_content.find("div", "content")
        link_to_course = (content_in_div.find("a", "card-header"))["href"]
        course_title = (content_in_div.find("a", "card-header")).text
        course_description = (content_in_div.find("div", "description")).text
        image_link = (content_in_div.find("amp-img"))["src"]

        p1 = await req(link_to_course)
        p1_html = (BeautifulSoup(p1, "html.parser")).find(
            "div", "ui center aligned basic segment"
        )
        downloadpagelink = (p1_html.find("a"))["href"]
        lastpage = await req(downloadpagelink)
        link = (
            ((BeautifulSoup(lastpage, "html.parser")).find("div", "ui segment")).find(
                "a"
            )
        )["href"]

        result = {
            "title": course_title,
            "description": course_description,
            "img_link": image_link,
            "link": link_to_course,
            "direct_link": link,
        }
        return result


if __name__ == "__main__":
    obj = Courses()
    asyncio.run(obj.get_course("python"))
