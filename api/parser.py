import ifcopenshell
import ifcopenshell.util.element
import json


def parse(file_name):
    model = ifcopenshell.open(file_name)

    # Get model name
    model_name = file_name.split("/")[-1]
    # Make the name cleaner
    # model_name = model_name.split(".")[0].replace("_", " ").replace("-", " ").title()
    print(model_name)
    json_dict = {model_name: {"floors": []}}

    floors = [floor for floor in model.by_type('IfcSlab') if ifcopenshell.util.element.get_predefined_type(floor) == "FLOOR"]
    if len(floors) == 0:
        return "No floors found!<br>"

    # result = f"Amount of floor type objects: {len(floors)}<br><br>"

    for floor in floors:
        # Get the right properties
        properties = ifcopenshell.util.element.get_psets(floor)
        base_properties = properties["BaseQuantities"]

        json_dict[model_name]["floors"].append({floor.Name: base_properties['GrossArea']})
        # result += f"Object name: {floor.Name}<br>"
        # result += f"&emsp;&emsp;Area: {base_properties['GrossArea']} m^2<br>"
    final_json = json.dumps(json_dict)
    return final_json

if __name__ == "__main__":
    parse('../test_files/simple_house.ifc')