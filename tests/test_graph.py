from datetime import date

from wiked.app.graph import find_shortest_path
from wiked.app.models import WikiPage


def test_directly_connected_pages(db_session):
    start = WikiPage(page_id=1, title="start", dump_date=date(2019, 6, 7))
    destination = WikiPage(page_id=2, title="destination", dump_date=date(2019, 6, 7))
    start.links.append(destination)
    db_session.add_all([start, destination])
    db_session.flush()

    result = find_shortest_path(start, destination)
    assert result == (start, destination)

    db_session.rollback()


def test_pages_connected_through_another_page(db_session):
    start = WikiPage(page_id=1, title="start", dump_date=date(2019, 6, 7))
    intermediate = WikiPage(page_id=2, title="intermediate", dump_date=date(2019, 6, 7))
    destination = WikiPage(page_id=3, title="destination", dump_date=date(2019, 6, 7))
    start.links.append(intermediate)
    intermediate.links.append(destination)
    db_session.add_all([start, intermediate, destination])
    db_session.flush()

    result = find_shortest_path(start, destination)
    assert result == (start, intermediate, destination)

    db_session.rollback()


def test_disconnected_pages(db_session):
    start = WikiPage(page_id=1, title="start", dump_date=date(2019, 6, 7))
    destination = WikiPage(page_id=3, title="destination", dump_date=date(2019, 6, 7))
    db_session.add_all([start, destination])
    db_session.flush()

    result = find_shortest_path(start, destination)
    assert result == ()

    db_session.rollback()
