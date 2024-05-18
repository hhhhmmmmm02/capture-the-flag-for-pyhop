"""
Copyright 2024 Hector Munoz-Avila

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

###This repository is created for  collaborators and should be considered in "pre-alpha" state.

Includes:

- A self-created implementation for a simple capture the Flag Game: 3 blue vs 3 red players, 3 flag locations 
- A simple GUI
- Uses Pyhop 1.2.2: https://bitbucket.org/dananau/pyhop/src/master/
- Simply run and it will import pyhop and necessary files
- Will call Pyhop to generate a plan to CTF. Pyhop is controlling Blue
- Opponent is red, which selects random flag locations

Key variables:

state.drawTheGrid = True  ## currently set on True so it will display the board; if set on False nothing is displayed

maxTurns = 100            ## currently set to 100 turns


Call one of the following if training (learning) or just planning:

CTFtraining(state)  ### this option in case someone wants to create an aiPlayer that learns. Annotated with locations to add own methods
CTFplanning(state)      ### by default is doing (HTN) planning




"""
