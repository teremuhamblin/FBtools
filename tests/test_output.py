import json

from fbtools.output import flatten, render, to_csv, to_json, to_table


def test_flatten_nested_and_lists():
    row = {"id": "1", "from": {"id": "9", "name": "Ana"}, "tags": ["a", "b"]}
    assert flatten(row) == {"id": "1", "from.id": "9", "from.name": "Ana", "tags": '["a", "b"]'}


def test_to_json_keeps_unicode():
    assert "é" in to_json({"m": "été"})


def test_to_csv_infers_columns():
    out = to_csv([{"b": 2, "a": 1}])
    assert out.splitlines()[0] == "a,b"


def test_to_table_empty():
    assert to_table([], ["id"]) == "(aucun résultat)"


def test_to_table_truncates_long_cells():
    out = to_table([{"m": "x" * 100}], ["m"], max_width=10)
    assert out.splitlines()[2] == "x" * 9 + "…"


def test_to_table_replaces_newlines():
    out = to_table([{"m": "a\nb"}], ["m"])
    assert out.splitlines()[2].strip() == "a b"


def test_render_dispatch():
    rows = [{"id": "1"}]
    assert json.loads(render(rows, "json", ["id"])) == rows
    assert render(rows, "csv", ["id"]).splitlines() == ["id", "1"]
    assert render(rows, "table", ["id"]).splitlines()[0].strip() == "id"
