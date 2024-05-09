"""
This module implements the core parsing logic for the IFCViz project.
"""


import ifcopenshell
import ifcopenshell.file
import ifcopenshell.util.element
import json
import gzip


class Parser:
    def __init__(self, ifc_file_content, surface_type="all", file_name="hash_for_the_file", ):
        model = ifcopenshell.file().from_string(gzip.decompress(ifc_file_content).decode())
        self.surface_type = surface_type
        # Todo: Make a solution for multiple files, with hashes instead of names
        self.file_name = file_name
        self.json_dict = {self.file_name: dict()}

        self.ifc_objects = {
            "floors": Floor(model),
            "windows": Window(model),
            "walls": Wall(model),
        }

    def parse(self):
        if self.surface_type == "all":
            for key, obj in self.ifc_objects.items():
                obj.parse()
                self.json_dict[self.file_name][key] = obj.data
        else:
            obj = self.ifc_objects[self.surface_type]
            obj.parse()
            self.json_dict[self.file_name][self.surface_type] = obj.data

    def get_json(self):
        return json.dumps(self.json_dict)


class IFCObject:
    json_dict = dict()
    surfaces = []
    amount = 0
    total_area = 0
    surface_type = ""

    def __init__(self, model, name="Some model name"):
        self.model = model
        self.name = name

        self.data = dict()
        self.data["amount"] = 0
        self.data["total_area"] = 0
        self.data[self.surface_type[:-1] + "_list"] = []

    def parse(self):
        pass

    def get_by_area_type(self, area_type):
        # Put the analysis of surfaces into a json string and return it
        for surface in self.surfaces:
            # Get the right properties
            properties = ifcopenshell.util.element.get_psets(surface)
            base_properties = properties["BaseQuantities"]

            self.data[self.surface_type[:-1] + "_list"].append(
                {surface.Name: base_properties[area_type]})
            # result += f"Object name: {floor.Name}<br>"
            # result += f"&emsp;&emsp;Area: {base_properties['GrossArea']} m^2<br>"
            self.total_area += base_properties[area_type]

        self.data["total_area"] = self.total_area
        self.data["amount"] = len(self.surfaces)


class Floor(IFCObject):
    def __init__(self, model, name="Some floor name"):
        self.surface_type = "floors"
        super().__init__(model, name)

    def parse(self):
        self.surfaces = [floor for floor in self.model.by_type('IfcSlab') if
                         ifcopenshell.util.element.get_predefined_type(floor) == "FLOOR"]
        self.get_by_area_type("GrossArea")


class Window(IFCObject):
    def __init__(self, model, name="Some floor name"):
        # Todo: Correct?
        self.surface_type = "windows"
        super().__init__(model, name)

    def parse(self):
        self.surfaces = self.model.by_type('IfcWindow')
        self.get_by_area_type("GrossArea")


class Wall(IFCObject):
    def __init__(self, model, name="Some floor name"):
        self.surface_type = "walls"
        super().__init__(model, name)

    def parse(self):
        self.surfaces = self.model.by_type('IfcWall')
        self.get_by_area_type("GrossSideArea")


def parse(ifc_file_content, surface_type="all"):
    # ERROR_NO_FLOORS = json.dumps({"error": "no floors found!"})
    # ERROR_BAD_SURFACE_TYPE = json.dumps({"error": f"bad surface type: {surface_type}"})
    # ERROR_NYI = json.dumps({"error"})

    parser = Parser(ifc_file_content, surface_type)
    parser.parse()
    
    return parser.get_json()
