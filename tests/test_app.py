import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from dash import dcc, html

from app import app


def walk(component):
    """Recursively yield all Dash components in the layout tree."""
    if component is None:
        return
    yield component

    children = getattr(component, "children", None)
    if children is None:
        return

    if isinstance(children, (list, tuple)):
        for child in children:
            yield from walk(child)
    else:
        yield from walk(children)


def find_first(root, predicate):
    for c in walk(root):
        if predicate(c):
            return c
    return None


def find_by_id(root, component_id):
    return find_first(root, lambda c: getattr(c, "id", None) == component_id)


def test_header_is_present():
    h1 = find_first(app.layout, lambda c: isinstance(c, html.H1))
    assert h1 is not None, "No H1 header found in layout"
    assert h1.children == "Pink Morsel Sales Visualiser"


def test_visualisation_is_present():
    graph = find_by_id(app.layout, "sales_line_chart")
    assert graph is not None, "Graph with id='sales_line_chart' not found"
    assert isinstance(graph, dcc.Graph)


def test_region_picker_is_present():
    radio = find_by_id(app.layout, "region_radio")
    assert radio is not None, "RadioItems with id='region_radio' not found"
    assert isinstance(radio, dcc.RadioItems)

    # Validate the expected options exist
    option_values = []
    for opt in (radio.options or []):
        if isinstance(opt, dict) and "value" in opt:
            option_values.append(opt["value"])
        else:
            option_values.append(opt)

    expected = {"all", "north", "east", "south", "west"}
    assert expected.issubset(set(option_values)), f"Missing options. Found: {option_values}"
