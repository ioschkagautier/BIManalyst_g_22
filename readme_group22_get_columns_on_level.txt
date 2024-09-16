1. Group 22
2. Structure
3. Amount and Type of Column on Chosen Floor
4. Our script checks the claim made on chapter 7.3 Columns, table 15 & 16 of the structural report. We want to check if they assign the correct columns to the different floors.

5. The script allows the user to check for columns on each level, including the quantity and their type based on measurements. 

Before calling the function 'get_columns_on_level' be sure to have done these two imports.
-from collections import defaultdict
-import ifcopenshell

By inputting your model's file path as first argument of the function, you can load it into the script. 
Enter the level of interest by inputting the corresponding "number" (e.g., Level 2 = 2) as the second argument of the function.
The script will then check the specified level and output the number of columns found, their measurements, and whether there are multiple types of columns.

Arguments of the Function:
1- Input your model's file path (e.g., model = `C:/path/to/model.ifc`).
2- Input the number of the level you're interested in (e.g., desired_level_num = 2)

The script will export the number and type of columns found on the selected level.

There is no need to add a code line at the end where you print the results of the function, you just have to call the function because the print are added inside.


Usage example (to get the columns data about the 5th level):

model_path = ifcopenshell.open('C:/Users/Lenovo/Desktop/CES_BLD_24_06_STR.ifc')
get_columns_on_level(model = model_path, desired_level_num = 5)

