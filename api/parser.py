import ifcopenshell
import ifcopenshell.util.element

def parse(file_name):
    model = ifcopenshell.open(file_name)

    # Gets the units used in the model

    # global_unit_assignments = model.by_type("IfcUnitAssignment")
    # print(global_unit_assignments)
    # # The global context defines 0 or more unit sets, each containing IFC unit definitions (using list comprehension):
    # global_length_unit_definition = [u for ua in global_unit_assignments for u in ua.Units if u.is_a() in ('IfcSIUnit', 'IfcConversionBasedUnit') and u.UnitType=='LENGTHUNIT'][-1]
    # print(global_length_unit_definition)

    # print(model.schema) # May return IFC2X3, IFC4, or IFC4X3.
    # print(model.by_id(1))

    # print(model.by_guid('0EI0MSHbX9gg8Fxwar7lL8'))

    floors = [floor for floor in model.by_type('IfcSlab') if ifcopenshell.util.element.get_predefined_type(floor) == "FLOOR"]
    if len(floors) == 0:
        return "No floors found!<br>"

    result = f"Amount of floor type objects: {len(floors)}<br><br>"

    for floor in floors:
        # Get the right properties
        properties = ifcopenshell.util.element.get_psets(floor)
        base_properties = properties["BaseQuantities"]

        result += f"Object name: {floor.Name}<br>"
        result += f"&emsp;&emsp;Area: {base_properties['GrossArea']} m^2<br>"

    return result
