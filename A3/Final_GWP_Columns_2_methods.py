#StreamID : 2a3df00e3e
# C:/Users/Lenovo/Documents/Studium/DTU/2_Semester/BIM/CES_BLD_24_06_STR.ifc
#Token: e84c64a17e9103569a55ccb97e2f00526982240229

# Importing color libraries
from matplotlib import cm
from matplotlib.colors import Normalize
#for Excel part
import ifcopenshell
import ifcopenshell.geom
import xlwings as xw
from collections import defaultdict
#for Speckle part
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_default_account
from specklepy.objects.geometry import Mesh
from specklepy.objects import Base
from specklepy.transports.server import ServerTransport
from specklepy.api.operations import send
import random

#OBS: Put your own file paths here!!!
Ifc_file_path = 'C:/Users/Lenovo/Documents/Studium/DTU/2_Semester/BIM/CES_BLD_24_06_STR.ifc'
Excel_file_path = 'C:/Users/Lenovo/Documents/Studium/DTU/2_Semester/BIM/A2/LCA_Advanced_BIM_to_Python_slabs.xlsx'

# Open the IFC file 
ifc_file = ifcopenshell.open(Ifc_file_path)

# Define concrete strength assumption for missing data
concrete_strength = " C25/30"

# Reinforcement densities
reinforcement_density_column = 170  # kg/m³ for columns
reinforcement_density_slab = 150     # kg/m³ for slabs

# 2. Extract all columns
columns = ifc_file.by_type("IfcColumn")
if len(columns) == 0:
    raise Exception("No columns found in the IFC file.")

# Function to calculate bounding box dimensions
def calculate_bounding_box(vertices):
    if not vertices:
        return None, None, None

    x_values = [v[0] for v in vertices]
    y_values = [v[1] for v in vertices]
    z_values = [v[2] for v in vertices]

    min_x, max_x = min(x_values), max(x_values)
    min_y, max_y = min(y_values), max(y_values)
    min_z, max_z = min(z_values), max(z_values)

    length = max_x - min_x
    width = max_y - min_y
    height = max_z - min_z

    return length, width, height

# Extract vertex coordinates from the geometry
def extract_vertex_coordinates(geometry):
    vertices = []
    for i in range(0, len(geometry), 3):
        x, y, z = geometry[i], geometry[i + 1], geometry[i + 2]
        if isinstance(x, (int, float)) and isinstance(y, (int, float)) and isinstance(z, (int, float)):
            vertices.append((x, y, z))
        else:
            print(f"Invalid vertex coordinates: {x}, {y}, {z}")
    return vertices

# Function to extract material from the type name
def extract_material_from_type_name(type_name):
    if 'Concrete' in type_name:
        return 'Concrete'
    if 'Timber' in type_name:
        return 'Timber'
    if 'Steel' in type_name:
        return 'Steel'
    return 'Unknown'



# Process columns and aggregate identical types/materials/dimensions
def process_columns(columns):
    column_info_dict = {}

    for column in columns:
        try:
            # Get type name and material
            type_name = column.ObjectType if hasattr(column, 'ObjectType') else 'N/A'
            material = extract_material_from_type_name(type_name) + concrete_strength  # Adding "C25/30"

            # Generate geometry and calculate dimensions
            shape = ifcopenshell.geom.create_shape(settings, column)
            geometry = shape.geometry.verts
            vertices = extract_vertex_coordinates(geometry)
            if not vertices:
                print(f"No valid vertices found for column: {type_name}.")
                continue
            length, width, height = calculate_bounding_box(vertices)
            if length is None or width is None or height is None:
                print(f"Failed to calculate bounding box dimensions for column: {type_name}.")
                continue

            # Round height to one decimal place
            height = round(height, 1)

            # Calculate volume and round it to 5 digits
            volume = round(length * width * height, 4)


            # Create a key based on type, material, volume, and height
            key = (type_name, material, volume, height)

            # Update the count and volume in the dictionary
            if key in column_info_dict:
                column_info_dict[key]['count'] += 1
            else:
                column_info_dict[key] = {
                    'count': 1,
                    'volume': volume,
                    'height': height,  # Store height for later use
                    'length': round(length, 4),  # Store length for later use
                    'width': round(width, 4),     # Store width for later use
                }

        except Exception as e:
            print(f"Error processing column {type_name}: {e}")

    return column_info_dict


# Add reinforcement data based on concrete elements
def add_reinforcement_info(info_dict):
    reinforcement_info = {}

    for (type_name, material, volume, height), data in info_dict.items():
        if 'Concrete' in material:
            # Calculate reinforcement volume (in kg) based on element type
            if 'Column' in type_name:
                reinforcement_volume = data['volume'] * reinforcement_density_column
            else:
                # Assuming all non-column concrete elements are slabs
                reinforcement_volume = data['volume'] * reinforcement_density_slab

            # Round height to one decimal place
            rounded_height = round(height, 1)

            # Create a new entry for reinforcement with height included in the key
            reinforcement_key = (type_name + '_Reinforcement', 'Reinforcement', reinforcement_volume, rounded_height)
            
            # Check if the reinforcement type is already in the dictionary
            if reinforcement_key not in reinforcement_info:
                reinforcement_info[reinforcement_key] = {
                    'count': 1,  # Count is always 1 for reinforcement
                    'volume': reinforcement_volume
                }

    # Merge reinforcement info into the original dictionary
    info_dict.update(reinforcement_info)
    return info_dict

# Write data to Excel Input sheet and update the sheet
def write_data_to_excel(info_dict, sheet):
    start_row = 14  # Start writing at row 14
    for row_index, ((type_name, material, volume, height), data) in enumerate(info_dict.items(), start=start_row):
        # Include height in the type name for the Excel sheet
        sheet.range(f'A{row_index}').value = f"{type_name} - {material} (Height: {height}m)"  # Column A
        sheet.range(f'B{row_index}').value = material  # Column B
        sheet.range(f'D{row_index}').value = data['volume']  # Column D
        
        # Set count to 1 for reinforcement, otherwise use the original count
        count_value = 1 if 'Reinforcement' in type_name else data['count']
        sheet.range(f'E{row_index}').value = count_value  # Column E

# Retrieve GWP data from Excel for each type and print individually
def retrieve_gwp_from_excel(sheet, start_row, end_row):
    gwp_dict = {}

    # Read GWP values from column J, starting at row 14
    gwp_values = sheet.range(f'J{start_row}:J{end_row}').value  # Adjust range as necessary
    element_names = sheet.range(f'A{start_row}:A{end_row}').value  # Corresponding element names (types)

    # Store GWP in a dictionary
    for element_name, gwp in zip(element_names, gwp_values):
        if element_name:
            gwp_dict[element_name] = gwp

    return gwp_dict

# Example usage
settings = ifcopenshell.geom.settings()
settings.set(settings.USE_WORLD_COORDS, True)

# Retrieve all IfcColumn elements
columns = ifc_file.by_type('IfcColumn')

# Process columns and aggregate the results
column_info_dict = process_columns(columns)

# Add reinforcement information for concrete columns and slabs
column_info_dict = add_reinforcement_info(column_info_dict)

# Open the workbook with xlwings
wb = xw.Book(Excel_file_path)

# Select the 'Input' sheet to write the data
input_sheet = wb.sheets['Input']

# Write data to the Input sheet
write_data_to_excel(column_info_dict, input_sheet)

# Refresh and calculate the Excel file
wb.app.calculate()

# Save the Excel file
wb.save()

# Select the 'RESULTS' sheet to read GWP data
results_sheet = wb.sheets['RESULTS']

# Retrieve GWP data from Excel and match it with the element data
gwp_dict = retrieve_gwp_from_excel(results_sheet, start_row=14, end_row=100)

# Create a temporary dictionary to store GWP data for reinforcement types
reinforcement_gwp_dict = {}

# Add GWP to the reinforcement info
for (type_name, material, volume, height), data in column_info_dict.items():
    if 'Reinforcement' in type_name:
        input_key = f"{type_name} - {material} (Height: {height}m)"
        if input_key in gwp_dict:
            reinforcement_gwp_dict[input_key] = gwp_dict[input_key]

# Add GWP to the corresponding parent types
for (type_name, material, volume, height), data in column_info_dict.items():
    input_key = f"{type_name} - {material} (Height: {height}m)"
    if input_key in gwp_dict:
        data['GWP'] = gwp_dict[input_key]  # Match GWP based on the input key
    else:
        data['GWP'] = 'N/A'  # In case GWP is not found

    # If reinforcement GWP exists, add it to the parent GWP
    reinforcement_key = f"{type_name}_Reinforcement - Reinforcement (Height: {height}m)"
    if reinforcement_key in reinforcement_gwp_dict:
        data['GWP'] += reinforcement_gwp_dict[reinforcement_key]  # Add reinforcement GWP

# Close the workbook without saving
wb.close()



# List to store the type_name, height
gwp_data_list = []

# Iterate over the columns and calculate GWP
for (type_name, material, volume, height), data in column_info_dict.items():
    if 'Reinforcement' not in type_name:  # Exclude reinforcement types
        real_gwp = data.get('GWP', 'N/A')
        
        
        # Append the type_name, height to the list
        gwp_data_list.append({
            'type_name': type_name,
            'height': height,
            'real_gwp': real_gwp
        })

# Print the list (if needed)
for entry in gwp_data_list:
    print(f"Type: {entry['type_name']}, Height: {entry['height']}m, Real GWP: {entry['real_gwp']}")

print(gwp_data_list)



#Mode 2


def get_column_levels_by_exact_z(columns):
    # Dictionary to store column levels
    level_dict = {}
    z_coordinates = []

    # Retrieve the exact z-coordinate for each column and store it
    for column in columns:
        if hasattr(column, 'ObjectPlacement') and column.ObjectPlacement:
            placement = column.ObjectPlacement
            if placement.is_a("IfcLocalPlacement") and placement.RelativePlacement:
                if placement.RelativePlacement.Location:
                    z = placement.RelativePlacement.Location.Coordinates[2]  # z-coordinate
                    z_coordinates.append((z, column))  # Store z-coordinate with the column itself
                else:
                    print(f"Column {column.id()} lacks placement location data.")
            else:
                print(f"Column {column.id()} lacks local placement data.")
        else:
            print(f"Column {column.id()} has no ObjectPlacement.")

    # Sort columns by their z-coordinate in descending order (highest z-coordinate first)
    z_coordinates.sort(key=lambda x: x[0], reverse=True)

    # Map each unique z-coordinate to a sequential level number (starting from 0 for highest level)
    current_level = 0
    last_z = z_coordinates[0][0] if z_coordinates else None

    for z, column in z_coordinates:
        # Assign a new level if the z-coordinate has changed
        if z != last_z:
            current_level += 1
            last_z = z
        # Assign the level to the column
        level_dict[column] = f"Level {current_level}"

    # Display summary
    print(f"Total columns: {len(columns)}")
    print(f"Columns with assigned levels: {len(level_dict)}")
    
    return level_dict

# Call the refined function to get exact levels with reversed ordering based on sorted z-coordinates
column_levels_by_z = get_column_levels_by_exact_z(columns)





# Function to calculate bounding box dimensions
def calculate_bounding_box(vertices):
    if not vertices:
        return None, None, None

    x_values = [v[0] for v in vertices]
    y_values = [v[1] for v in vertices]
    z_values = [v[2] for v in vertices]

    length = max(x_values) - min(x_values)
    width = max(y_values) - min(y_values)
    height = max(z_values) - min(z_values)

    return length, width, height

# Dictionary to hold columns by level with unique keys
columns_by_level = defaultdict(list)

# Process each column to calculate height and assign to levels
for column in columns:
    try:
        # Get type name
        type_name = column.ObjectType if hasattr(column, 'ObjectType') else 'N/A'

        # Generate geometry and calculate dimensions
        shape = ifcopenshell.geom.create_shape(settings, column)
        geometry = shape.geometry.verts
        vertices = extract_vertex_coordinates(geometry)
        
        if not vertices:
            print(f"No valid vertices found for column: {type_name}.")
            continue
            
        # Calculate height
        length, width, height = calculate_bounding_box(vertices)
        height = round(height, 1) if height is not None else "Unknown Height"

        # Determine level from the previously computed column_levels_by_z
        level = column_levels_by_z.get(column, "Unknown Level")

        # Create unique key and store by level
        unique_key = (type_name, height)
        columns_by_level[level].append(unique_key)
        
    except Exception as e:
        print(f"Error processing column {type_name}: {e}")

# Identify the lowest and highest levels
sorted_levels = sorted(columns_by_level.keys(), key=lambda lvl: int(lvl.split()[1]))
level_0 = sorted_levels[0]
top_level = sorted_levels[-1]

# Get columns on Level 0 and Top Level
level_0_columns = columns_by_level[level_0]
top_level_columns = columns_by_level[top_level]


# Display results
print("Columns on Level 0:")
for column in level_0_columns:
    print(column)

print("\nColumns on Top Level:")
for column in top_level_columns:
    print(column)





#...................................................GWP allocation.....................................


# Function to find the average GWP for a given list of columns and the GWP data
def calculate_average_gwp(columns, gwp_data_list):
    gwp_values = []

    # Loop through each unique column type on the specified level
    for type_name, height in columns:
        # Find matching GWP data for the given type_name and height
        matching_gwps = [
            entry['real_gwp'] for entry in gwp_data_list
            if entry['type_name'] == type_name and entry['height'] == height
        ]
        
        # Add all matching GWP values to our list
        gwp_values.extend(matching_gwps)

    # Calculate and return the average GWP for the level
    if gwp_values:
        average_gwp = sum(gwp_values) / len(gwp_values)
    else:
        average_gwp = 0  # Default if no matching GWP data found

    return average_gwp

# Calculate average GWP for Level 0 and Top Level
average_gwp_level_0 = calculate_average_gwp(level_0_columns, gwp_data_list)
average_gwp_top_level = calculate_average_gwp(top_level_columns, gwp_data_list)

# Display the results
print(f"Average GWP for Level 0: {average_gwp_level_0}")
print(f"Average GWP for Top Level: {average_gwp_top_level}")


# Calculate the level allocation factor
if average_gwp_level_0 != 0:  # Prevent division by zero
    level_allocation_factor = 1 - (round(average_gwp_top_level / average_gwp_level_0,3))
else:
    level_allocation_factor = None  # Handle case where level 0 average GWP is zero

# Display the factor
if level_allocation_factor is not None:
    print(f"Level Allocation Factor: {level_allocation_factor}")
else:
    print("Level Allocation Factor could not be calculated due to zero average GWP on Level 0.")


#........................................................................Apply GWP_allocation factor to each individual coloumn by level.....................


# Step 1: Define `level_numbers` based on `column_levels_by_z`
level_numbers = {level: int(level.split()[1]) for level in sorted(column_levels_by_z.values(), key=lambda lvl: int(lvl.split()[1]))}

# Print `level_numbers` to verify levels
print("Level numbers mapping:", level_numbers)

# Step 2: Initialize list to store each column's individual adjusted GWP data
individual_adjusted_gwp_list = []

# Get the top level number, n
n = max(level_numbers.values()) 

level_allocation_factor_pr_level = level_allocation_factor/n

# Step 3: Iterate over all columns to calculate and apply the adjustment factor individually
for column in columns:
    # Retrieve column properties
    type_name = column.ObjectType if hasattr(column, 'ObjectType') else 'N/A'
    
    # Retrieve geometry and calculate height for the individual column
    shape = ifcopenshell.geom.create_shape(settings, column)
    geometry = shape.geometry.verts
    vertices = extract_vertex_coordinates(geometry)
    
    if not vertices:
        print(f"No valid vertices found for column: {type_name}.")
        continue
        
    length, width, height = calculate_bounding_box(vertices)
    height = round(height, 1) if height is not None else "Unknown Height"
    
    # Retrieve the level for this column from column_levels_by_z
    level_name = column_levels_by_z.get(column, "Unknown Level")
    if level_name == "Unknown Level":
        continue  # Skip if level is unknown
    
    # Convert `level_name` to its integer value for calculation
    L = level_numbers[level_name]
    
    # Find matching GWP data for this specific column type and height
    matching_gwp_entry = next((entry for entry in gwp_data_list 
                               if entry['type_name'] == type_name and entry['height'] == height), None)
    
    if matching_gwp_entry and matching_gwp_entry['real_gwp'] != 'N/A':
        # Real GWP value for the column
        real_gwp = matching_gwp_entry['real_gwp']
        
        # Calculate adjustment factor using the level-specific formula
        adjustment_factor = (-(n - L) + L) * level_allocation_factor_pr_level #.............................................Adjust formualr!!!
        adjusted_gwp = real_gwp + (real_gwp * adjustment_factor)
        
        # Store individual column data with adjusted GWP
        individual_adjusted_gwp_list.append({
            'column_id': column.id(),
            'type_name': type_name,
            'height': height,
            'level': L,
            'real_gwp': real_gwp,
            'adjusted_gwp': adjusted_gwp
        })

# Display individual adjusted GWP values
print("Individual Adjusted GWP values by column:")
for entry in individual_adjusted_gwp_list:
    print(f"Column ID: {entry['column_id']}, Type: {entry['type_name']}, Height: {entry['height']}m, "
          f"Level: {entry['level']}, Real GWP: {entry['real_gwp']}, Adjusted GWP: {entry['adjusted_gwp']}")




#......................................................colour by method..................................................................


# Function to normalize and create a color gradient
def create_color_gradient(gwp_values):
    max_value = max(gwp_values)
    min_value = min(gwp_values)
    normalized_values = [(value - min_value) / (max_value - min_value) for value in gwp_values]

    # Create color map (green -> yellow -> red)
    color_map = cm.get_cmap("RdYlGn_r")  # Reverse for red high, green low

    # Generate colors for each normalized value
    colors = [color_map(norm_value) for norm_value in normalized_values]
    return colors

# Step 1: User selection of Method 1 (Real GWP) or Method 2 (Adjusted GWP)
method = input("Choose GWP calculation method (1 for Real GWP, 2 for Adjusted GWP): ")

# Step 2: Collect GWP values for normalization based on type, height, and level as unique keys
gwp_values = []
unique_column_keys = []

for entry in individual_adjusted_gwp_list:
    unique_key = (entry['type_name'], entry['height'], entry['level'])
    unique_column_keys.append(unique_key)
    
    if method == "1":
        gwp_values.append(entry['real_gwp'])
    elif method == "2":
        gwp_values.append(entry['adjusted_gwp'])
    else:
        print("Invalid method chosen. Defaulting to Real GWP.")
        gwp_values.append(entry['real_gwp'])

# Step 3: Generate color gradient based on normalized GWP values
colors = create_color_gradient(gwp_values)

# Step 4: Assign colors to each column entry based on the unique key (type, height, level)
color_mapping = dict(zip(unique_column_keys, colors))

for entry in individual_adjusted_gwp_list:
    unique_key = (entry['type_name'], entry['height'], entry['level'])
    entry['color'] = color_mapping.get(unique_key, (1, 1, 1, 0))  # Transparent if no color found

# Display individual adjusted GWP values with colors
print("Individual GWP values with color gradient:")
for entry in individual_adjusted_gwp_list:
    print(f"Column ID: {entry['column_id']}, Type: {entry['type_name']}, Height: {entry['height']}m, "
          f"Level: {entry['level']}, GWP: {entry['real_gwp'] if method == '1' else entry['adjusted_gwp']}, "
          f"Color: {entry['color']}")


#......................................................................Speckle.................................................

# 1. Open the IFC file

ifc_file = ifcopenshell.open(Ifc_file_path)

# 2. Extract all columns
columns = ifc_file.by_type("IfcColumn")
if len(columns) == 0:
    raise Exception("No columns found in the IFC file.")

# 3. Dictionary to hold unique colors for each combination of ObjectType and rounded height
type_colors = {}

# 4. Create a main Base object to hold all columns
speckle_columns = Base()




# Function to generate a random color
def generate_random_color():
    return int(f'{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}', 16)

# Function to calculate bounding box dimensions
def calculate_bounding_box(vertices):
    if not vertices or not isinstance(vertices, (tuple, list)):
        return None, None, None

    # Convert vertices from tuple to a list of (x, y, z) tuples
    vertices_list = [(vertices[i], vertices[i + 1], vertices[i + 2]) for i in range(0, len(vertices), 3)]

    # Extract x, y, z values from the vertices
    x_values = [v[0] for v in vertices_list]
    y_values = [v[1] for v in vertices_list]
    z_values = [v[2] for v in vertices_list]

    min_x, max_x = min(x_values), max(x_values)
    min_y, max_y = min(y_values), max(y_values)
    min_z, max_z = min(z_values), max(z_values)

    length = max_x - min_x
    width = max_y - min_y
    height = max_z - min_z

    return length, width, height

# Define the method to assign levels based on exact z-coordinates
def get_column_levels_by_exact_z(columns):
    level_dict = {}
    z_coordinates = []

    # Retrieve the exact z-coordinate for each column and store it
    for column in columns:
        if hasattr(column, 'ObjectPlacement') and column.ObjectPlacement:
            placement = column.ObjectPlacement
            if placement.is_a("IfcLocalPlacement") and placement.RelativePlacement:
                if placement.RelativePlacement.Location:
                    z = placement.RelativePlacement.Location.Coordinates[2]  # z-coordinate
                    z_coordinates.append((z, column))  # Store z-coordinate with the column itself
                else:
                    print(f"Column {column.id()} lacks placement location data.")
            else:
                print(f"Column {column.id()} lacks local placement data.")
        else:
            print(f"Column {column.id()} has no ObjectPlacement.")

    # Sort columns by their z-coordinate in descending order (highest z-coordinate first)
    z_coordinates.sort(key=lambda x: x[0], reverse=True)

    # Map each unique z-coordinate to a sequential level number (starting from 0 for highest level)
    current_level = 0
    last_z = z_coordinates[0][0] if z_coordinates else None

    for z, column in z_coordinates:
        # Assign a new level if the z-coordinate has changed
        if z != last_z:
            current_level += 1
            last_z = z
        # Assign the level to the column
        level_dict[column] = f"Level {current_level}"

    # Display summary
    print(f"Total columns: {len(columns)}")
    print(f"Columns with assigned levels: {len(level_dict)}")
    
    return level_dict

# Step 1: Get column levels based on z-coordinate ordering
column_levels_by_z = get_column_levels_by_exact_z(columns)

# 3. Dictionary to hold unique colors for each combination of ObjectType, height, and level
predefined_colors = {
    (item['type_name'], item['height'], item['level']): item['color'] for item in individual_adjusted_gwp_list
}

# Helper function to convert RGB to Hexadecimal
def rgb_to_hex(rgb):
    return (int(rgb[0] * 255) << 16) + (int(rgb[1] * 255) << 8) + int(rgb[2] * 255)

# Loop over all columns and extract geometry, applying color based on ObjectType, height, and level
for column in columns:
    settings = ifcopenshell.geom.settings()  # Default settings for geometry extraction
    shape = ifcopenshell.geom.create_shape(settings, column)  # Extract geometry

    # Get the geometry vertices and faces
    vertices = shape.geometry.verts
    faces = shape.geometry.faces

    if not vertices or not faces:
        print(f"No valid geometry found for column: {column.Name}")
        continue  # Skip if no valid geometry found

    # Calculate bounding box dimensions to determine height
    dimensions = calculate_bounding_box(vertices)
    if dimensions is None:
        print(f"Could not calculate dimensions for column: {column.Name}")
        continue

    length, width, height = dimensions
    height = round(height, 1)  # Round height to 1 decimal place

    # Get ObjectType (or a fallback if not available)
    object_type = getattr(column, 'ObjectType', None) or column.Name or "Unnamed"

    # Determine the level from `column_levels_by_z`
    level_name = column_levels_by_z.get(column, "Unknown Level")
    if level_name == "Unknown Level":
        print(f"No level information for column: {column.Name}")
        continue  # Skip if level information is missing

    # Convert level_name to an integer for comparison
    level = int(level_name.split()[1])

    # Create a unique key based on ObjectType, rounded height, and level
    key = (object_type, height, level)

    # Assign a color from predefined_colors if available, else use a random color
    if key in predefined_colors:
        column_color_rgb = predefined_colors[key]
        column_color_hex = rgb_to_hex(column_color_rgb)
    else:
        column_color_hex = generate_random_color()  # Fallback to random color if not defined

    # Find the matching GWP value for this column based on type, height, and level
    matching_gwp = next(
        (entry['real_gwp'] if method == '1' else entry['adjusted_gwp'] 
         for entry in individual_adjusted_gwp_list
         if entry['type_name'] == object_type and entry['height'] == height and entry['level'] == level),
        'N/A'
    )

    # Scale the vertices (if needed)
    scaled_vertices = [v * 1 for v in vertices]  # Scale to millimeters for Speckle

    # Format the faces for Speckle
    formatted_faces = []
    for i in range(0, len(faces), 3):
        formatted_faces.extend([3, faces[i], faces[i + 1], faces[i + 2]])

    # Create a Mesh for this column
    speckle_mesh = Mesh(
        name=f"IFC Column - {column.Name}",
        vertices=scaled_vertices,
        faces=formatted_faces
    )

    # Apply the color to the mesh
    speckle_mesh.colors = [column_color_hex] * (len(scaled_vertices) // 3)  # Same color for all vertices

    # Assign other attributes (like height) and GWP value
    speckle_mesh['height'] = height
    speckle_mesh['GWP'] = f'{round(matching_gwp, 2)} [kg CO2-eq / Object]' if method == '1' else f'{round(matching_gwp, 2)} [Allocated kg CO2-eq]'

    # Create a Speckle Base object for the column, which includes the mesh and GUID
    column_object = Base()
    column_object['mesh'] = speckle_mesh
    column_object['guid'] = column.GlobalId or "No GUID"
    column_object['name'] = column.Name or "Unnamed Column"
    column_object['ifc_type'] = column.is_a()  # e.g., IfcColumn
    column_object['height'] = height
    column_object['object_type'] = object_type
    column_object['level'] = level  # Include level in the column object

    # Add this column object to the main collection of columns
    speckle_columns[f'column_{column.GlobalId}'] = column_object

# Speckle client setup and sending code follows as in your original script


# 6. Authenticate with your Speckle account using a Personal Access Token (PAT)
client = SpeckleClient(host="app.speckle.systems")  # Make sure to specify the correct server host (e.g., app.speckle.systems)

# Replace this with your actual personal access token (PAT) #could also use default account method
personal_access_token = "e84c64a17e9103569a55ccb97e2f00526982240229"  

# Authenticate with the token
client.authenticate_with_token(personal_access_token)

# 7. Set up transport to the stream
stream_id = "2a3df00e3e"  # Your specified stream ID
transport = ServerTransport(client=client, stream_id=stream_id)

# 8. Send all columns as one object to Speckle
object_id = send(base=speckle_columns, transports=[transport])
print(f"All columns with colors sent to Speckle with object ID: {object_id}")

# 9. Print the Speckle viewer URL to view the object
print(f"View it at: https://app.speckle.systems/streams/{stream_id}/objects/{object_id}")
