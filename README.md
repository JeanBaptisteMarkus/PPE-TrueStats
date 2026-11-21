# True Stats: Basketball Rebound Analysis

## Overview

This project aims to analyze and evaluate basketball rebounds using data-driven methods. The main objective is to develop an algorithm capable of estimating the probability of a player winning a rebound based on several parameters, such as player positions, distances, and their relative locations on the court.

The project combines two main components:
- **Virtual Court Simulation:** A virtual basketball court where players can be manually positioned to create different rebound scenarios.
- **Rebound Calculation Algorithm:** An algorithm that evaluates rebound situations and estimates which player is most likely to secure the rebound.

A Computer Vision component is also being developed to automatically detect players and extract their positions from real basketball footage. The long-term goal is to combine real-world data extraction with the rebound calculation algorithm.

## Current Project Status

<ins>**The Computer Vision component is not yet fully implemented.**</ins>

At this stage, the project does not provide a complete automated analysis of basketball footage. However, the rebound calculation algorithm is already functional and can be tested using manually created virtual situations.

Users can:
- Select the players involved in a rebound situation.
- Manually position players on the virtual basketball court.
- Create different hypothetical rebound scenarios.
- Run the algorithm to evaluate the situation and obtain rebound predictions.

This makes it possible to test and evaluate the algorithm independently of the Computer Vision component.

## Main Features

### 1. Virtual Basketball Court

The project includes a virtual representation of a basketball court, allowing users to create custom situations.

Players can be manually placed on the court, making it possible to reproduce different game situations and study how player positioning affects rebound outcomes.

### 2. Rebound Calculation Algorithm

The core of the project is an algorithm designed to estimate the probability of a player securing a rebound.

It takes into account several parameters related to the players' positions and their spatial relationships to the rebound situation.

The algorithm can be executed on virtual scenarios, allowing users to compare different configurations and observe how changes in player positioning influence the results.

### 3. Computer Vision (In Development)

An additional objective is to implement a Computer Vision system capable of analyzing basketball videos.

The intended functionality includes:
- Detecting players in video footage.
- Identifying and tracking players across frames.
- Extracting player positions on the basketball court.
- Using these positions as inputs for the rebound calculation algorithm.

This component is still under development and is not yet fully operational.

## Project Objectives

The long-term objective is to combine the different components into a single system capable of analyzing real basketball situations.

The expected workflow is:

1. Input a basketball video.
2. Detect and track the players using Computer Vision.
3. Extract their positions on the court.
4. Identify rebound situations.
5. Feed the extracted data into the rebound calculation algorithm.
6. Evaluate and predict the most likely rebound outcome.


## Conclusion

Although the Computer Vision component is not yet complete, the project already provides a functional foundation for basketball rebound analysis.

The virtual court and rebound calculation algorithm can be used independently to simulate and evaluate different situations. The next major step is to connect this existing functionality to real-world basketball footage, ultimately creating a more complete and automated rebound analysis tool.