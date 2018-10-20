import re
from typing import Dict

# https://www.mediawiki.org/wiki/Manual:Page_title
# [[lingua Graeca antiqua|Graece]]
# [[meteorologia]]
# [[clima]]tologia
pattern = re.compile(
    r"\[\["
    r"(?!\w+:)"
    r"(?P<link>([^{}\]].*?))"
    r"\]\]"
    r"(?P<remainder>([^\s,.\'\"(){}]*))"
)


def get_links_from_article(body: str) -> Dict[str, str]:
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
        if internal_link not in links:
            links[internal_link] = visible_link
    return links
