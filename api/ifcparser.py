"""
This module implements the core parsing logic for the IFCViz project.
"""


import ifcopenshell
import ifcopenshell.file
import ifcopenshell.util.element
import json
import gzip

def surface_type_to_string(st):
    match st.upper():
        case "FLOOR":
            return "floors"
        case "WINDOW":
            return "windows"
        case _:
            return f"bad surface type: {st}"

def parse(ifc_file_content, surface_type = "FLOOR"):
    ERROR_NO_FLOORS = json.dumps({"error": "no floors found!"})
    ERROR_BAD_SURFACE_TYPE = json.dumps({"error": f"bad surface type: {surface_type}"})
    ERROR_NYI = json.dumps({"error"})

    model = None
    
    model = ifcopenshell.file().from_string(gzip.decompress(ifc_file_content).decode())

    # Get model name
    model_name = "Some model name"
    # Make the name cleaner
    # model_name = model_name.split(".")[0].replace("_", " ").replace("-", " ").title()
    # print(model_name)
    json_dict = {model_name: {surface_type_to_string(surface_type): []}}

    # Define a list of the surfaces we're trying to analyze
    surfaces = []
    match (surface_type.upper()):
        case "FLOOR":
            surfaces = [floor for floor in model.by_type('IfcSlab') if ifcopenshell.util.element.get_predefined_type(floor) == "FLOOR"]
        case "WINDOW":
            return ERROR_NYI # what to put here??
        case _:
            return ERROR_BAD_SURFACE_TYPE

    if len(surfaces) == 0:
        return ERROR_NO_FLOORS

    # Put the analysis of surfaces into a json string and return it
    for surface in surfaces:
        # Get the right properties
        properties = ifcopenshell.util.element.get_psets(surface)
        base_properties = properties["BaseQuantities"]

        json_dict[model_name][surface_type_to_string(surface_type)].append({surface.Name: base_properties['GrossArea']})
        # result += f"Object name: {floor.Name}<br>"
        # result += f"&emsp;&emsp;Area: {base_properties['GrossArea']} m^2<br>"
    
    return json.dumps(json_dict)