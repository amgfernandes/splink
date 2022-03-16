import json
import os
import pkgutil

from .waterfall_chart import records_to_waterfall_data

altair_installed = True
try:

    from altair.vegalite.v4.display import vegalite
except ImportError:
    altair_installed = False


def load_chart_definition(filename):
    path = f"files/chart_defs/{filename}"
    data = pkgutil.get_data(__name__, path)
    schema = json.loads(data)
    return schema


def _load_external_libs():

    to_load = {
        "vega-embed": "files/external_js/vega-embed@6.20.2",
        "vega-lite": "files/external_js/vega-lite@5.2.0",
        "vega": "files/external_js/vega@5.21.0",
    }

    loaded = {}
    for k, v in to_load.items():
        script = pkgutil.get_data(__name__, v).decode("utf-8")
        loaded[k] = script

    return loaded


def vegalite_or_json(chart_dict, as_dict=False):

    if altair_installed:
        if not as_dict:
            try:
                return vegalite(chart_dict)
            except ModuleNotFoundError:
                return chart_dict

    return chart_dict


iframe_message = """
To view in Jupyter you can use the following command:

from IPython.display import IFrame
IFrame(src="./{filename}", width=1000, height=500)
"""


def save_offline_chart(
    chart_dict, filename="my_chart.html", overwrite=False, print_msg=True
):

    if os.path.isfile(filename) and not overwrite:
        raise ValueError(
            f"The path {filename} already exists. Please provide a different path."
        )

    # get altair chart as json
    path = "files/templates/single_chart_template.txt"
    template = pkgutil.get_data(__name__, path).decode("utf-8")

    fmt_dict = _load_external_libs()

    fmt_dict["mychart"] = json.dumps(chart_dict)

    with open(filename, "w") as f:
        f.write(template.format(**fmt_dict))

    if print_msg:
        print(f"Chart saved to {filename}")
        print(iframe_message.format(filename=filename))


def match_weights_chart(records, as_dict=False):
    chart_path = "match_weights_interactive_history.json"
    chart = load_chart_definition(chart_path)

    # Remove iteration history since this is a static chart
    del chart["params"]
    del chart["transform"]

    records = [r for r in records if r["comparison_vector_value"] != -1]
    chart["data"]["values"] = records
    return vegalite_or_json(chart, as_dict=as_dict)


def m_u_values_chart(records, as_dict=False):
    chart_path = "m_u_values_interactive_history.json"
    chart = load_chart_definition(chart_path)

    # Remove iteration history since this is a static chart
    del chart["params"]
    del chart["transform"]

    records = [r for r in records if r["comparison_vector_value"] != -1]
    chart["data"]["values"] = records
    return vegalite_or_json(chart, as_dict=as_dict)


def proportion_of_matches_iteration_chart(records, as_dict=False):
    chart_path = "proportion_of_matches_iteration.json"
    chart = load_chart_definition(chart_path)

    chart["data"]["values"] = records
    return vegalite_or_json(chart, as_dict=as_dict)


def match_weights_interactive_history_chart(records, as_dict=False):
    chart_path = "match_weights_interactive_history.json"
    chart = load_chart_definition(chart_path)
    records = [r for r in records if r["comparison_vector_value"] != -1]
    chart["data"]["values"] = records

    max_iteration = 0
    for r in records:
        max_iteration = max(r["iteration"], max_iteration)

    chart["params"][0]["bind"]["max"] = max_iteration
    return vegalite_or_json(chart, as_dict=as_dict)


def m_u_values_interactive_history_chart(records, as_dict=False):
    chart_path = "m_u_values_interactive_history.json"
    chart = load_chart_definition(chart_path)
    records = [r for r in records if r["comparison_vector_value"] != -1]
    chart["data"]["values"] = records

    max_iteration = 0
    for r in records:
        max_iteration = max(r["iteration"], max_iteration)

    chart["params"][0]["bind"]["max"] = max_iteration
    return vegalite_or_json(chart, as_dict=as_dict)


def waterfall_chart(
    records,
    settings_obj,
    filter_nulls=True,
    as_dict=False,
):
    data = records_to_waterfall_data(records, settings_obj)
    chart_path = "match_weights_waterfall.json"
    chart = load_chart_definition(chart_path)
    chart["data"]["values"] = data
    chart["params"][0]["bind"]["max"] = len(records) - 1
    if filter_nulls:
        chart["transform"].insert(1, {"filter": "(datum.bayes_factor !== 1.0)"})

    return vegalite_or_json(chart, as_dict=as_dict)


def roc_chart(records, height=400, width=400, as_dict=False):
    chart_path = "roc.json"
    chart = load_chart_definition(chart_path)

    chart["data"]["values"] = records

    # If 'curve_label' not in records, remove colour coding
    # This is for if you want to compare roc curves
    r = records[0]
    if "curve_label" not in r.keys():
        del chart["encoding"]["color"]

    chart["height"] = height
    chart["width"] = width

    return vegalite_or_json(chart, as_dict=as_dict)


def precision_recall_chart(records, height=400, width=400, as_dict=False):
    chart_path = "precision_recall.json"
    chart = load_chart_definition(chart_path)

    chart["data"]["values"] = records

    # If 'curve_label' not in records, remove colour coding
    # This is for if you want to compare roc curves
    r = records[0]
    if "curve_label" not in r.keys():
        del chart["encoding"]["color"]

    chart["height"] = height
    chart["width"] = width

    return vegalite_or_json(chart, as_dict=as_dict)


def match_weight_histogram(records, height=250, width=500, as_dict=False):
    chart_path = "match_weight_histogram.json"
    chart = load_chart_definition(chart_path)

    chart["data"]["values"] = records

    chart["height"] = height
    chart["width"] = width

    return vegalite_or_json(chart, as_dict=as_dict)
