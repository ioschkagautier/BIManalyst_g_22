#StreamID : 2a3df00e3e
# C:/Users/Lenovo/Documents/Studium/DTU/2_Semester/BIM/CES_BLD_24_06_STR.ifc
#Token: e84c64a17e9103569a55ccb97e2f00526982240229

#for Excel part
import ifcopenshell
import ifcopenshell.geom
import xlwings as xw
#for Speckle part
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_default_account
from specklepy.objects.geometry import Mesh
from specklepy.objects import Base
from specklepy.transports.server import ServerTransport
from specklepy.api.operations import send
import random

#put file path
Ifc_file_path = 'C:/Users/Lenovo/Documents/Studium/DTU/2_Semester/BIM/CES_BLD_24_06_STR.ifc'
Excel_file_path = 'C:/Users/Lenovo/Documents/Studium/DTU/2_Semester/BIM/A2/LCA_Advanced_BIM_to_Python_slabs.xlsx'

# Open the IFC file 
ifc_file = ifcopenshell.open(Ifc_file_path)

# Define concrete strength assumption for missing data
concrete_strength = " C25/30"

# Reinforcement densities
reinforcement_density_column = 170  # kg/m³ for columns
reinforcement_density_slab = 150     # kg/m³ for slabs

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

# First, ensure that the GWP includes the reinforcement GWP (this is already being done)

# Find the maximum GWP value for normalization (including reinforcement)
max_gwp = 0
for (type_name, material, volume, height), data in column_info_dict.items():
    if 'Reinforcement' not in type_name and data.get('GWP') != 'N/A':
        max_gwp = max(max_gwp, data['GWP'])  # Track the maximum GWP value

# List to store the type_name, height, and normalized GWP
gwp_data_list = []

# Iterate over the columns and calculate GWP
for (type_name, material, volume, height), data in column_info_dict.items():
    if 'Reinforcement' not in type_name:  # Exclude reinforcement types
        real_gwp = data.get('GWP', 'N/A')
        
        # Normalize only if GWP is available and max_gwp is non-zero
        if real_gwp != 'N/A' and max_gwp != 0:
            normalized_gwp = round(real_gwp / max_gwp, 4)  # Normalized GWP
        else:
            normalized_gwp = 'N/A'  # Handle cases where normalization isn't possible
        
        # Append the type_name, height, and normalized GWP to the list
        gwp_data_list.append({
            'type_name': type_name,
            'height': height,
            'normalized_gwp': normalized_gwp,
            'real_gwp': real_gwp
        })

# Print the list (if needed)
for entry in gwp_data_list:
    print(f"Type: {entry['type_name']}, Height: {entry['height']}m, Normalized GWP: {entry['normalized_gwp']}, Real GWP: {entry['real_gwp']}")



# Helper function to ensure the GWP value is a float
def ensure_float(value):
    # Check for common invalid values like 'N/A', None, or empty string
    if value in [None, 'N/A', '']:
        print(f"Warning: Invalid GWP value found: {value}")
        return None  # Return None for invalid values

    try:
        return float(value)  # Try to convert the value to a float
    except ValueError:
        print(f"Warning: Could not convert {value} to float.")  # Debugging message
        return None  # Return None if conversion fails

# Interpolate color function: from green (low GWP) to yellow (medium GWP) to red (high GWP)
def interpolate_color(normalized_gwp):
    # Check if normalized_gwp is a valid number
    if isinstance(normalized_gwp, (int, float)):
        # Color values for the gradient points:
        # Green (0, 255, 0), Yellow (255, 255, 0), Red (255, 0, 0)

        if normalized_gwp <= 0.5:
            # Interpolate between green and yellow
            green = 255
            red = int(255 * (normalized_gwp / 0.5))  # Gradually increase red as GWP approaches 0.5
            blue = 0
        else:
            # Interpolate between yellow and red
            red = 255
            green = int(255 * (1 - (normalized_gwp - 0.5) / 0.5))  # Gradually decrease green as GWP approaches 1
            blue = 0

        return (red, green, blue)  # Return the interpolated RGB color
    else:
        # Return a default color (e.g., white) if normalized_gwp is not a valid number
        return (255, 255, 255)

# Apply the color gradient to each entry in gwp_data_list based on the normalized GWP value
gwp_data_with_colors = []

# Check and print entries in the list before processing
print("Initial Data Inspection:")
for entry in gwp_data_list:
    print(entry)

for entry in gwp_data_list:
    type_name = entry.get('type_name', 'Unknown')  # Get the type name or use 'Unknown' if missing
    height = entry.get('height', 'Unknown')  # Get the height or use 'Unknown' if missing
    normalized_gwp = ensure_float(entry.get('normalized_gwp'))  # Ensure the normalized GWP value is converted to float
    real_gwp = ensure_float(entry.get('real_gwp')) # Ensure the real GWP value is converted to float
    
    # Only assign colors if GWP is a valid number
    if normalized_gwp is not None:
        color = interpolate_color(normalized_gwp)
    else:
        color = (255, 255, 255)  # Default to white if GWP is not available or invalid

    # Append the data along with the color to the new list
    gwp_data_with_colors.append((type_name, height, normalized_gwp, real_gwp, color))

# Now gwp_data_with_colors contains the Type_name, Height, Normalized GWP, and corresponding Color

# Example: Print the data with colors
for type_name, height, normalized_gwp, real_gwp, color in gwp_data_with_colors:
    print(f"Type: {type_name}, Height: {height}m, Normalized GWP: {normalized_gwp}, Real GWP: {real_gwp}, Color: {color}")

print(gwp_data_with_colors)


#-----------------------------Speckle--------------------------------------------------------------------------------------------------------------------

def generate_random_color():
    return int(f'{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}', 16)


# Convert the list to a dictionary for quick look-up
predefined_colors = {
    (item[0], item[1]): item[4] for item in gwp_data_with_colors
}

# Helper function to convert RGB to Hexadecimal
def rgb_to_hex(rgb):
    return (rgb[0] << 16) + (rgb[1] << 8) + rgb[2]



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

# 5. Loop over all columns and extract geometry, applying color based on ObjectType and height
# Loop over all columns and extract geometry, applying color based on ObjectType and height
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
    object_type = getattr(column, 'ObjectType', None)
    if not object_type:
        object_type = column.Name if column.Name else "Unnamed"

    # Create a unique key based on ObjectType and rounded height
    key = (object_type, height)

    # Assign a color from predefined_colors if available, else use a default color
    if key in predefined_colors:
        column_color_rgb = predefined_colors[key]
        column_color_hex = rgb_to_hex(column_color_rgb)
    else:
        column_color_hex = generate_random_color()  # Fallback to random color if not defined

    # Now find the matching GWP value for this column
    matching_gwp = None  # Default in case no match is found
    for entry in gwp_data_list:
        if entry['type_name'] == object_type and entry['height'] == height:
            matching_gwp = entry['real_gwp']
            break  # Stop searching once we've found the match

    if matching_gwp is None:
        print(f"No matching GWP found for column: {object_type} with height: {height}")
        matching_gwp = 'N/A'  # Or set a default value

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
    speckle_mesh['height'] = height  # Add height as a direct attribute
    speckle_mesh['GWP'] = f'{round(matching_gwp, 2)} [kg CO2-eq / Object]'  # Add GWP as a direct attribute for each individual column

    # Create a Speckle Base object for the column, which includes the mesh and GUID
    column_object = Base()
    column_object['mesh'] = speckle_mesh
    column_object['guid'] = column.GlobalId if column.GlobalId else "No GUID"
    column_object['name'] = column.Name if column.Name else "Unnamed Column"
    column_object['ifc_type'] = column.is_a()  # e.g., IfcColumn
    column_object['height'] = height  # Add height to the column object
    column_object['object_type'] = object_type  # Add ObjectType to the column object

    # Add this column object to the main collection of columns
    speckle_columns[f'column_{column.GlobalId}'] = column_object


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
