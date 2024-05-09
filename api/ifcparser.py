"""
This module implements the core parsing logic for the IFCViz project.
"""


import ifcopenshell
import ifcopenshell.file
import ifcopenshell.util.element
import json
import gzip


class IFCObject:
    json_dict = dict()
    surfaces = []

    def __init__(self, model, surface_type, name="Some model name"):
        self.model = model
        self.name = name
        self.surface_type = surface_type
        self.json_dict = {self.name: {self.surface_type: []}}

    def parse(self):
        pass

    def get_by_area_type(self, area_type):
        # Put the analysis of surfaces into a json string and return it
        for surface in self.surfaces:
            # Get the right properties
            properties = ifcopenshell.util.element.get_psets(surface)
            base_properties = properties["BaseQuantities"]

            self.json_dict[self.name][self.surface_type].append(
                {surface.Name: base_properties[area_type]})
            # result += f"Object name: {floor.Name}<br>"
            # result += f"&emsp;&emsp;Area: {base_properties['GrossArea']} m^2<br>"


class Floor(IFCObject):
    def parse(self):
        self.surfaces = [floor for floor in self.model.by_type('IfcSlab') if
                         ifcopenshell.util.element.get_predefined_type(floor) == "FLOOR"]

        self.get_by_area_type("GrossArea")


class Window(IFCObject):

    def parse(self):
        self.surfaces = [floor for floor in self.model.by_type('IfcSlab') if
                         ifcopenshell.util.element.get_predefined_type(floor) == "FLOOR"]

        self.get_by_area_type("GrossArea")


class Wall(IFCObject):

    def parse(self):
        self.surfaces = [floor for floor in self.model.by_type('IfcSlab') if
                         ifcopenshell.util.element.get_predefined_type(floor) == "FLOOR"]

        self.get_by_area_type("GrossSideArea")


def parse(ifc_file_content, surface_type="floors"):
    ERROR_NO_FLOORS = json.dumps({"error": "no floors found!"})
    ERROR_BAD_SURFACE_TYPE = json.dumps({"error": f"bad surface type: {surface_type}"})
    # ERROR_NYI = json.dumps({"error"})

    model = ifcopenshell.file().from_string(gzip.decompress(ifc_file_content).decode())

    types = {
        "floors": Floor(model, surface_type),
        "windows": Window(model, surface_type),
        "walls": Wall(model, surface_type),
    }

    obj = types[surface_type]
    obj.parse()
    
    return json.dumps(obj.json_dict)
