# Modified the files of YouTube Search to make it Async Compatible

import json
import urllib.parse

import aiohttp


class YoutubeSearch:
    @classmethod
    async def search(cls, search_terms, max_results=1):
        encoded_search = urllib.parse.quote_plus(search_terms)
        BASE_URL = "https://youtube.com"
        url = f"{BASE_URL}/results?search_query={encoded_search}"
        session = aiohttp.ClientSession()
        async with session.get(url) as resp:
            response = await resp.text()
        await session.close()
        results = cls._parse_html(response)
        if max_results is not None and len(results) > max_results:
            return results[:max_results]
        return results

    @classmethod
    def _parse_html(cls, response):
        results = []
        start = response.index("ytInitialData") + len("ytInitialData") + 3
        end = response.index("};", start) + 1
        json_str = response[start:end]
        data = json.loads(json_str)

        videos = data["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"][
            "sectionListRenderer"
        ]["contents"][0]["itemSectionRenderer"]["contents"]

        for video in videos:
            res = {}
            if "videoRenderer" in video.keys():
                video_data = video.get("videoRenderer", {})
                res["id"] = video_data.get("videoId", None)
                res["thumbnails"] = [
                    thumb.get("url", None)
                    for thumb in video_data.get("thumbnail", {}).get("thumbnails", [{}])
                ]
                res["title"] = (
                    video_data.get("title", {}).get("runs", [[{}]])[0].get("text", None)
                )
                res["long_desc"] = (
                    video_data.get("descriptionSnippet", {})
                    .get("runs", [{}])[0]
                    .get("text", None)
                )
                res["channel"] = (
                    video_data.get("longBylineText", {})
                    .get("runs", [[{}]])[0]
                    .get("text", None)
                )
                res["duration"] = video_data.get("lengthText", {}).get("simpleText", 0)
                res["views"] = video_data.get("viewCountText", {}).get("simpleText", 0)
                res["publish_time"] = video_data.get("publishedTimeText", {}).get(
                    "simpleText", 0
                )
                res["url_suffix"] = (
                    video_data.get("navigationEndpoint", {})
                    .get("commandMetadata", {})
                    .get("webCommandMetadata", {})
                    .get("url", None)
                )
                results.append(res)
        return results
