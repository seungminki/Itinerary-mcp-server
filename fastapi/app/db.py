import json


def get_output_db(query_input):
    json_file = "/workspace/data.json"
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data["items"]:
        for hi in item["human_inputs"]:
            if all(token in hi for token in query_input.split()[:2]):
                return item["ai_output"]

    return None
