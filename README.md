# Bioloop


## Description
This project evaluates the carbon storage potential of the Swiss building stock through the use of bio-based materials in the construction and renovation of buildings in Switzerland.

See project definition in https://www.buildinglowcarbon.com/projects/bioloop

Project funded by HES-SO University of Applied Sciences and Arts Western Switzerland

Collaboration:

Energy Institute, HEIA University of Applied Sciences of Engineering and Architecture, HES-SO University of Applied Sciences and Arts Western Switzerland, Fribourg, Switzerland

inPACT Institute, HEPIA University of Applied Sciences of Landscape, Engineering and Architecture, HES-SO University of Applied Sciences and Arts Western Switzerland, Geneva, Switzerland


## Usage
The primary objectives of this project are:
1. Quantify the total carbon emission of the Swiss building stock
2. Quantify the potential carbon sink capacity of the Swiss building stock by estimating the carbon storage contribution of construction and renovation activities
3. Identify the most influential parameters affecting carbon emissions and storage potential
4. Identify future material demand for the Swiss building stock.

## How it works
This project builds a dynamic numerical model to estimate the evolution of construction activities and their respective emissions up to 2050.

Using life cycle assessments (LCA) of buildings based on real-world cases, we calculate the environmental impacts and material requirements. The current building stock is reconstructed using building registry data, and archetypes are applied to define the surface areas of building elements. This allows the impact to be calculated per square meter of energy reference area.

Key Steps in the Model:
1. Calculating Total Impact of the Building Stock
   
The total environmental impact is based on the evolution of the energy reference area:
a) Renovated areas are computed annually using a configurable renovation rate.
b) Demolished areas are calculated similarly.

2. Calculating Newly Constructed Areas
   
The model assumes population growth projections from the Swiss 2050 scenario.

Total surface requirements are estimated as the population (configurable) multiplied by the square meters per person (also configurable).
The difference between the total required surface and the existing stock (including demolished areas) determines the area to be newly constructed.

3. Impact and Material Calculations
   
For each scenario, archetype, and building type, the evolution of building surfaces is multiplied by the impacts and material requirements per square meter.

Configurable Parameters:
1. Renovated areas
2. Demolished areas
3. Square Meters Per Inhabitant
4. Scenario:
The impact and material data are derived from LCAs of four building types (SFH and MFH) across real-world cases, including both new construction and renovation. For each case, three scenarios are provided: Optimistic, Medium Business-as-Usual (BAU)
This flexibility allows users to simulate various scenarios and evaluate the potential outcomes on emissions and resource use.

## Code description
The main running code is "main.py" where input parameters can be modified in section "INPUT" and the desired outcome for the graphs in section "Outcome"

a) "Class_dev_V5" create object as the archetype and the building

b) "graph_function" is used to compute graphs

c) "Regbl" folder is used to create the building stock from the RegBl database

## Main results

The results are visualized using parallel coordinate plots and other graphical tools available in Bioloop. These visualizations provide insights into the relationship between key parameters and their impact on cumulative emissions and material demand.
Available in https://www.buildinglowcarbon.com/toolbioloop

<table>
  <tr>
    <td>
      <img src="https://github.com/LuleSc/Bioloop/blob/main/Surface_evolution.png?raw=true" alt="Image 1" width="500"/>
    </td>
    <td>
      <img src="https://github.com/LuleSc/Bioloop/blob/main/Renovation_surface_evolution.png?raw=true" alt="Image 2" width="500"/>
    </td>
  </tr>
  <tr>
    <td>
      <img src="https://github.com/LuleSc/Bioloop/blob/main/Image3.png?raw=true" alt="Image 3" width="500"/>
    </td>
    <td>
      <img src="https://github.com/LuleSc/Bioloop/blob/main/Image4.png?raw=true" alt="Image 4" width="500"/>
    </td>
  </tr>
</table>

## License
CC BY 4.0
