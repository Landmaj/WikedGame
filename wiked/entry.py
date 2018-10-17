from wiked.game.page_parser import parse_page_sql

page_path = "/home/landmaj/Downloads/plwiki-20181001-page.sql"
link_path = "/home/landmaj/Downloads/plwiki-20181001-pagelinks.sql"
parse_page_sql(page_path, link_path)
