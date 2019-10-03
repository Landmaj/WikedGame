import re
from typing import Dict, Set

# https://www.mediawiki.org/wiki/Manual:Page_title
# [[lingua Graeca antiqua|Graece]]
# [[meteorologia]]
# [[clima]]tologia
pattern = re.compile(
    r"\[\["
    r"(?!\w+:)"
    r"(?P<link>([^[\]|{}]+((?!]])\|.*?)?))"
    r"\]\]"
    r"(?P<remainder>([^\s{}[\]|,.\'\"()\-;:<>]*))"
)

html_pattern = re.compile("<.*?>")


def clean_html(raw_html):
    return re.sub(html_pattern, "", raw_html)


def get_internal_links_from_article(body: str) -> Set[str]:
    links = set()
    for match in pattern.finditer(body):
        matched_string = match.group("link").split("|")
        internal_link = matched_string[0]
        # capitalize first letter to avoid duplicates
        internal_link = f"{internal_link[0].upper()}{internal_link[1:]}"

        # sanitize data
        internal_link = (
            internal_link.strip()
            .replace("\r", "")
            .replace("\t", " ")
            .replace("\n", " ")
        )
        links.add(internal_link)
    return links


def get_visible_links_from_article(body: str) -> Dict[str, str]:
    links = dict()
    for match in pattern.finditer(body):
        matched_string = match.group("link").split("|")
        internal_link = matched_string[0]
        try:
            visible_link = matched_string[1]
        except IndexError:
            visible_link = internal_link
            # there is no remainder if visible link is explicit
            visible_link = f"{visible_link}{match.group('remainder')}"
        # capitalize first letter to avoid duplicates
        internal_link = f"{internal_link[0].upper()}{internal_link[1:]}"

        # sanitize data
        internal_link = (
            internal_link.strip()
            .replace("\r", "")
            .replace("\t", " ")
            .replace("\n", " ")
        )
        visible_link = (
            visible_link.strip()
            .replace("\r", " ")
            .replace("\t", " ")
            .replace("\n", " ")
        )
        visible_link = clean_html(visible_link)

        if internal_link not in links:
            links[internal_link] = visible_link
    return links
