def get_grade(payload):

    for day in payload:
        for order in day["schedule"]:
            order["grade"] = "A"
    return payload
