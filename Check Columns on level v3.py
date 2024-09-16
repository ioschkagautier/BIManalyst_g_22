from collections import defaultdict
import ifcopenshell
import re

# Load the IFC model (update with your file path)
model = ifcopenshell.open('C:/Users/bruno/Desktop/DTU/BIM/CES_BLD_24_06_STR.ifc')

# Retrieve all levels of type IfcBuildingStorey
levels = model.by_type('IfcBuildingStorey')

# Dictionary to map levels by their number (positive, negative, or zero)
level_map = {}

# Function to extract the number from a level name
def extract_level_number(level_name):
    match = re.search(r'-?\d+', level_name)  # Find any integer (positive or negative)
    if match:
        return int(match.group())  # Return the number as an integer
    return None

# Populate the level_map with levels
for level in levels:
    level_number = extract_level_number(level.Name)
    if level_number is not None:
        level_map[level_number] = level

# Function to get the length/height of a column, if available
def get_column_length(column):
    if column.Representation is not None:
        # Traverse through the column's representations to find geometric data
        for representation in column.Representation.Representations:
            if representation.RepresentationType == 'SweptSolid':
                for item in representation.Items:
                    if hasattr(item, 'ExtrudedDirection'):
                        return item.Depth  # Depth is often the extrusion length (e.g., height in columns)
    return "Unknown length"  # Return this if length can't be determined

# Ask the user for a number input instead of the full name
print('Please enter the number corresponding to the desired Level (e.g., -2, 0, 2, ...):')

try:
    desired_level_number = int(input())  # Input level number (positive, negative, or zero)

    # Find the level corresponding to the entered number
    selected_level = level_map.get(desired_level_number)

    if selected_level is None:
        print(f"No level found for number {desired_level_number}.")
    else:
        # Retrieve all elements on the specific level
        elements_on_level = [rel.RelatedElements for rel in selected_level.ContainsElements]
        
        # Flatten the list of elements
        elements_on_level = [item for sublist in elements_on_level for item in sublist]
        
        # Filter only IfcColumn elements
        columns_on_level = [element for element in elements_on_level if element.is_a("IfcColumn")]
        
        # Dictionary to store counts of columns by their ObjectType
        column_type_counts = defaultdict(int)

        # Extract ObjectType for each column and count types
        print("\nColumn Information:")
        for column in columns_on_level:
            object_type = column.ObjectType if column.ObjectType else "Undefined"  # Handle None or undefined ObjectType
            column_type_counts[object_type] += 1
            column_length = get_column_length(column)  # Get the length of the column
            print(f"Column of type '{object_type}' has length: {column_length}")

        # Print the summary of column ObjectTypes and their counts
        print("\nSummary of Columns by ObjectType on Level:")
        for object_type, count in column_type_counts.items():
            print(f"{count} columns of type '{object_type}'")

        # Check if there are multiple types of columns or just a single one
        if len(column_type_counts) > 1:
            print("\nThere are multiple column types on this level.")
        elif len(column_type_counts) == 1:
            print("\nThere is a single column type on this level.")
        else:
            print("\nThere are no columns on this level.")

except ValueError:
    print("Invalid input. Please enter a valid number.")
