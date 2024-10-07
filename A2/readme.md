### A2a: About Your Group 22

I am confident coding in Python  
    1 - Disagree


### A2b: Identify Claim  
Review the reports from last year’s Advanced Building Design Course. We currently have 3 to choose from:  
    - Building #2406  

Select which building(s) to focus on for your focus area:  
    - Focus area: Structure  

Identify a ‘claim’ / issue / fact to check from one of those reports:  
    - Claim: Evaluate the LCA from the Building.

Write a short description of the claim you wish to check:  
    - We want to perform an LCA of the building by extracting the needed information and object types and supplementing them with an LCA evaluation. Then input that into the IFC to include it in the model. The final goal is to use the updated IFC Model to export the added data visually through a color gradient in Speckle.

### A2c: Use Case  
How would you check this claim?  
    - Extract important data/attributes – type/dimensions.

When would this claim need to be checked?  
    - LCA verification or evaluation of the presented structural idea.

What information does this claim rely on?  
    - Included dimensions from each object material and calculation of LCA values.

What phase? Planning, design, build, or operation?  
    - Early structural planning (efficiency and LCA/cost-effectiveness).

What BIM purpose is required? Gather, generate, analyze, communicate, or realize?  
    - Communication and analysis between BIM model and planning service to improve LCA, leading to better decision-making.

Review use case examples – do any of these help? What BIM use case is this closest to? If you cannot find one from the examples, you can create a new one.  
    - Communicate/Visualize (Excel/Speckle).

Produce a BPMN drawing for your chosen use case. Link to this so we can see it in your markdown file. To do this, you will have to save it as an SVG. Please also save the BPMN with it. You can use this online tool to create a BPMN file.  
    - Link to BPMN Diagram https://github.com/ioschkagautier/BIManalyst_g_22/blob/main/A2/Proccess%20Diagram%20Group%2022%20(Overview)%20Coloured.bpmn
    - Link to SVG Diagram https://github.com/ioschkagautier/BIManalyst_g_22/blob/main/A2/diagram%20Overview.svg

### A2d: Scope the Use Case  
    - Link to BPMN Diagram https://github.com/ioschkagautier/BIManalyst_g_22/blob/main/A2/Proccess%20Diagram%20Group%2022%20(Detailed)%20Coloured.bpmn
    - Link to SVG https://github.com/ioschkagautier/BIManalyst_g_22/blob/main/A2/diagram%20Detailed.svg

### A2e: Tool Idea  
Describe in words your idea for your own OpenBIM ifcOpenShell Tool in Python.  
    - Creating LCA information from an existing BIM model.

What is the business and societal value of your tool?  
    - Sustainability through visualizing and communicating LCA data from structural design data.

### A2f: Information Requirements  
Identify what information you need to extract from the model.  
Where is this in IFC?  
    - The data is available for all types of objects defined by dimensions and can be found in typological outputs from IFC.

Is it in the model?  
    - Not always directly in the object attributes but in the object typologies and geometry.

Do you know how to get it in ifcOpenShell?  
    - Through the typologic library and by using assumptions/rules and standardized information.

What will you need to learn to do this?  
    - How to use ifcOpenShell and typologic Python libraries to extract the dimensions from objects of interest.

### A2g: Identify Appropriate Software License  
What software license will you choose for your project?  
    - VS Code  
    - Blender
