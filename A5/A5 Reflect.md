# **Project Reflection: OpenBIM and LCA Tool Development**


## **Your learning experience for the concept you focused on?**
 
The concept we focused on was conducting **Life Cycle Assessment (LCA)** using OpenBIM workflows to analyze and visualize CO₂-eq emissions for building lifecycle phases (A1-A3, C3, C4). Our learning journey was transformative, moving from a basic understanding of OpenBIM tools to developing a script capable of extracting, processing, and visualizing LCA data.  
Key learning milestones included:
1. Understanding IFC data structures and extracting relevant attributes using **ifcOpenShell**.
2. Leanring to access stored data from the IFC through **scripting in Phython**.
3. Integrating material-specific CO₂ data from **EPD databases** with BIM models and our script.
4. Creating a user-friendly visualization in **Speckle** to present environmental impacts.

This experience deepened our technical skills and highlighted how OpenBIM can make sustainability data actionable in real-world projects.

## **Identify your own level at the beginning of this course and where you ended?**

- **Beginning Level:**  
  - Limited knowledge of IFC data structures and scripting for BIM workflows.  
  - No experience with tools like ifcOpenShell, Specklepy, or using Python for LCA purposes.  

- **Ending Level:**  
  - Proficient in extracting and processing IFC data with **ifcOpenShell**.  
  - Developed a full pipeline for LCA data integration within a python script combining information from IFC and external **Excel** sheet to visualize output in **Speckle**.  
  - Enhanced ability to automate sustainability assessments in BIM workflows, a skill applicable to thesis work and professional practice.

## **What else do you still need to learn?**
 
- How to handle more complex IFC models with greater variability in data completeness (e.g., missing reinforcement details, undefined material attributes).  
- Optimizing scripts for larger datasets to improve runtime and scalability.  
- Exploring other sustainability metrics to expand the tool’s functionality and usefullness.  


## **How you might use OpenBIM in the future?**

- **For My Thesis:**  
	Bruno - OpenBIM will be used to evaluate modular designs' environmental impact, with tools like ifcOpenShell and Speckle playing a central role in analyzing LCA and CO₂ emissions.  
	Janin - Enhancement of system thinking and its modelling. Remodelling and linking of data structures.
  Ioshka -
- **In Professional Life:**  
	Bruno - OpenBIM will become an essential part of my workflow, enabling better collaboration, data integration, and in architectural design and project development.
	Janin - Probably to enable better informed decisions to be made based on evidence and analysis, rather than on best practice.
	Ioshka -
---

## **Your process of developing the tutorial?**

The development process included the following steps:
1. **Research:** Identifying gaps in current OpenBIM workflows for LCA analysis, especially in the context of transporting data in an accessable manner to different diciplines.  
2. **Scripting:** Writing a Python script to extract data from IFC files, integrate EPD values, and visualize results in Speckle.  
3. **Testing and Refinement:** Iteratively improving the script based on peer feedback and improvement ideas. (Speckle real time results as guide)  
4. **Documentation:** Creating a clear instructions for setting up and running the tool, ensuring usability for future users.  
5. **Finding Applicable Solutions:** Highlight the Value for future users and making it addaptive to multiple situations with the same goal. 


## **Did the process of the course enable you to answer or define questions that you might need later for thesis?**

Yes, the course helped define key questions for my thesis, such as:
- How can OpenBIM workflows be optimized for modular design and sustainability evaluations and how much you can make use of it. 
- What are the limitations of current IFC data standards for capturing environmental metrics and how important a good modeled BIM model is for futher workflows. 
- How can visualization tools like Speckle improve stakeholder communication in sustainable building design.

## **Would you have preferred to have been given less choice in the use cases?**

No, the flexibility to choose our use case allowed us to focus on a topic aligned with our interests (LCA and CO₂ analysis). However, additional predefined examples could have provided clearer expectations and guidance, especially at the beginning. Still the open approached makes you think more about why and for what you choose a specific use case and if a tool would benifit enough for it to be created. This makes us studnets think more about the "why use BIM" and the possibilities behind it. 

## **Was the number of tools for the course OK?** 

The number of tools was appropriate.  
- **Tools to Keep:** ifcOpenShell, (Speckle), Python, Blender.  
- **Tools to Consider Removing:** We think is good to get a simple introduction to many programs to know what is out there. Since this course was open in what area we wanted to expand its usefull to have many tools as options.

## **(As a Group) Summary of the Feedback You Received on Your Tutorial**

They very much liked the tool, but we could improve it by marking up more instructions and discriptions within the main file to remove potential barriers of getting started on using the script. 

- **Positive Feedback:**  
  - The visualization in Speckle effectively communicated CO₂ impacts and made LCA data more actionable.  

- **Suggestions for Improvement:**  
  Write an intoduction in the main file aswell since the tool can be a little complex


## **(As a Group) Did the Tool Address the Use Case?**

Did the tool address the use case you identified?  

Yes, the tool successfully addressed the identified use case by:
- Extracting and processing IFC data for material and dimension attributes.  
- Integrating EPD values to provide CO₂-eq metrics for LCA.  
- Visualizing the environmental impact in Speckle for easier decision-making.

However direct comparison with the report is rather complicated since the report does not give detailed information on where their CO2 avlues come from or what assumptions they made.


## **(Individual) Your Future for Advanced Use of OpenBIM**

Are you likely to use OpenBIM tools in your thesis?  
 
Bruno - Yes, OpenBIM tools will play a key role in my thesis, especially for analyzing sustainability metrics in modular building designs. Especially Detail checking and overview creation of proposed desgin and controlling mistakes will be a key element to keep track.
Janin - Probably yes.
Ioshka -


Are you likely to use OpenBIM tools in your professional life in the next 10 years?  

Bruno - Absolutely. OpenBIM workflows are essential for collaboration, automation, and sustainability in modern architectural and construction practices. In the future more and more companies will adapt and due to rising interest it will be one of the key elements for more efficient projects.
Janin - Yes, if i chose to stay in engineering for the next ten years.
Ioshka -

## **(Individual) Wrap-Up**

Conclude the journey through A1-A5.  
 
The journey from A1 to A5: 
- **A1-A2:** Built foundational knowledge of OpenBIM concepts and workflows. (Blender, IFC, Python connection/script) 
- **A3:** Defined our LCA use case, identifying gaps in current IFC workflows.  
- **A4:** Developed and tested a functional Python script to address these gaps.  
- **A5:** Integrated all elements into a cohesive tool, addressing peer feedback and delivering a polished solution.  

