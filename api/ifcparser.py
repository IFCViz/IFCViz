"""
This module implements the core parsing logic for the IFCViz project.
"""


import ifcopenshell
import ifcopenshell.file
import ifcopenshell.util.element
import json
import gzip


class Parser:
    def __init__(self, ifc_file_content, surface_type="all", file_name="hash_for_the_file"):
        model = ifcopenshell.file().from_string(gzip.decompress(ifc_file_content).decode())
        self.surface_type = surface_type
        # Todo: Make a solution for multiple files, with hashes instead of names
        self.file_name = file_name
        self.json_dict = {self.file_name: dict()}

        self.ifc_objects = {
            "floors": Floor(model),
            "windows": Window(model),
            "walls": Wall(model),
            "doors": Door(model),
            "roofs": Roof(model),
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
    more_properties = {}

    def __init__(self, model, name="Some model name"):
        self.model = model
        self.name = name

        self.data = dict()
        self.data["amount"] = 0
        self.data["total_area"] = 0
        self.data[self.surface_type[:-1] + "_list"] = []

        self.base_properties = [
            "BaseQuantities",
            "Dimensions"
        ]
        self.area_keywords = [
            "Area",
            "GrossArea",
            "GrossSideArea"
        ]

    def parse(self):
        self.get_by_area_type(self.surface_type)

        # Todo: Add more fields (such as objects with min/max area, etc.)? Move from here?
        self.data["total_area"] = self.total_area
        # self.data["amount"] = len(self.surfaces)

    def get_by_area_type(self, area_type):
        # Put the analysis of surfaces into a json string and return it
        for surface in self.surfaces:
            # Get the right properties
            properties = ifcopenshell.util.element.get_psets(surface)
            for base_property in self.base_properties:
                if base_property in properties:
                    base_properties = properties[base_property]
                    for keyword in self.area_keywords:
                        if keyword in base_properties:
                            self.data[self.surface_type[:-1] + "_list"].append({
                                "name": surface.Name,
                                "area": base_properties[keyword],
                            })
                            self.total_area += base_properties[keyword]
                            self.data["amount"] += 1
                            self.add_more_properties(base_properties)

    def add_more_properties(self, base_properties):
        for prop, keywords in self.more_properties.items():
            for keyword in keywords:
                if keyword in base_properties:
                    self.data[self.surface_type[:-1] + "_list"][-1][prop] = base_properties[keyword]


class Floor(IFCObject):
    def __init__(self, model, name="Some floor name"):
        self.surface_type = "floors"
        self.more_properties = {
            "thickness": [
                "Width",
                "Thickness"
            ]
        }

        super().__init__(model, name)

    def parse(self):
        self.surfaces = [floor for floor in self.model.by_type('IfcSlab') if
                         ifcopenshell.util.element.get_predefined_type(floor) == "FLOOR"]
        self.get_by_area_type("GrossArea")

        # Todo: Add more fields (such as objects with min/max area, etc.)? Move from here?
        self.data["total_area"] = self.total_area
        # self.data["amount"] = len(self.surfaces)


class Window(IFCObject):
    def __init__(self, model, name="Some floor name"):
        # Todo: Correct?
        self.surface_type = "windows"
        self.more_properties = {
            "perimeter": [
                "Perimeter"
            ]
        }

        super().__init__(model, name)

    def parse(self):
        self.surfaces = self.model.by_type('IfcWindow')
        self.get_by_area_type("GrossArea")

        # Todo: Add more fields (such as objects with min/max area, etc.)? Move from here?
        self.data["total_area"] = self.total_area
        # self.data["amount"] = len(self.surfaces)


class Door(IFCObject):
    def __init__(self, model, name="Some floor name"):
        # Todo: Correct?
        self.surface_type = "doors"
        self.more_properties = {
            "height": [
                "Height"
            ]
        }

        super().__init__(model, name)

    def parse(self):
        self.surfaces = self.model.by_type('IfcDoor')
        self.get_by_area_type("Area")

        # Todo: Add more fields (such as objects with min/max area, etc.)? Move from here?
        self.data["total_area"] = self.total_area
        # self.data["amount"] = len(self.surfaces)


class Roof(IFCObject):
    def __init__(self, model, name="Some floor name"):
        # Todo: Correct?
        self.surface_type = "roofs"
        self.more_properties = {
            "thickness": [
                "Width"
            ]
        }

        super().__init__(model, name)

    def parse(self):
        self.surfaces = [floor for floor in self.model.by_type('IfcSlab') if
                         ifcopenshell.util.element.get_predefined_type(floor) == "ROOF"]
        self.get_by_area_type("GrossArea")

        # Todo: Add more fields (such as objects with min/max area, etc.)? Move from here?
        self.data["total_area"] = self.total_area
        # self.data["amount"] = len(self.surfaces)


class Wall(IFCObject):
    def __init__(self, model, name="Some floor name"):
        self.surface_type = "walls"
        self.more_properties = {
            "thickness": [
                "Width"
            ]
        }

        super().__init__(model, name)

    def parse(self):
        self.surfaces = self.model.by_type('IfcWall')
        self.get_by_area_type("GrossSideArea")

        # Todo: Add more fields (such as objects with min/max area, etc.)? Move from here?
        self.data["total_area"] = self.total_area
        # self.data["amount"] = len(self.surfaces)


def parse(ifc_file_content, surface_type="all", hash="no_hash_given"):
    # ERROR_NO_FLOORS = json.dumps({"error": "no floors found!"})
    # ERROR_BAD_SURFACE_TYPE = json.dumps({"error": f"bad surface type: {surface_type}"})
    # ERROR_NYI = json.dumps({"error"})

    parser = Parser(ifc_file_content, surface_type, hash)
    parser.parse()
    
    return parser.get_json()
