#pip install ifcopenshell specklepy

import ifcopenshell
import ifcopenshell.geom
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_default_account
from specklepy.objects.geometry import Mesh
from specklepy.objects import Base
from specklepy.transports.server import ServerTransport
from specklepy.api.operations import send
import random

# Function to generate a random color in hexadecimal format
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

# 1. Open the IFC file
ifc_file_path = 'C:/Users/Lenovo/Documents/Studium/DTU/2_Semester/BIM/CES_BLD_24_06_STR.ifc'
ifc_file = ifcopenshell.open(ifc_file_path)

# 2. Extract all columns
columns = ifc_file.by_type("IfcColumn")
if len(columns) == 0:
    raise Exception("No columns found in the IFC file.")

# 3. Dictionary to hold unique colors for each combination of ObjectType and rounded height
type_colors = {}

# 4. Create a main Base object to hold all columns
speckle_columns = Base()

# 5. Loop over all columns and extract geometry, applying color based on ObjectType and height
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

    # Assign a unique color for each key if it doesn't already exist
    if key not in type_colors:
        type_colors[key] = generate_random_color()  # Assign a random color for each unique key

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
    speckle_mesh.colors = [type_colors[key]] * (len(scaled_vertices) // 3)  # Same color for all vertices

    # Assign other attributes (like height) if needed
    speckle_mesh['height'] = height  # Add height as a direct attribute

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

from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_default_account
from specklepy.objects.geometry import Mesh
from specklepy.objects import Base
from specklepy.transports.server import ServerTransport
from specklepy.api.operations import send
import random



# 6. Authenticate with your Speckle account using a Personal Access Token (PAT)
client = SpeckleClient(host="app.speckle.systems")  # Make sure to specify the correct server host (e.g., app.speckle.systems)

# Replace this with your actual personal access token (PAT)
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