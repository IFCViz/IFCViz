import ifcopenshell
import ifcopenshell.file
import ifcopenshell.util.element
import json
import gzip


def parse(file_name):
    ERROR_NO_FLOORS = json.dumps({"error": "no floors found!"})

    model = None
    with gzip.open(file_name) as gz:
        model = ifcopenshell.file().from_string(gz.read().decode())

    # Get model name
    model_name = "Some model name"
    # Make the name cleaner
    # model_name = model_name.split(".")[0].replace("_", " ").replace("-", " ").title()
    # print(model_name)
    json_dict = {model_name: {"floors": []}}

    floors = [floor for floor in model.by_type('IfcSlab') if ifcopenshell.util.element.get_predefined_type(floor) == "FLOOR"]
    if len(floors) == 0:
        return ERROR_NO_FLOORS

    # result = f"Amount of floor type objects: {len(floors)}<br><br>"

    for floor in floors:
        # Get the right properties
        properties = ifcopenshell.util.element.get_psets(floor)
        base_properties = properties["BaseQuantities"]

        json_dict[model_name]["floors"].append({floor.Name: base_properties['GrossArea']})
        # result += f"Object name: {floor.Name}<br>"
        # result += f"&emsp;&emsp;Area: {base_properties['GrossArea']} m^2<br>"
    
    return json.dumps(json_dict)