"""
DISCONTINUED - USE CTFForPyhop_and_TK.py instead

Copyright 2024 Hector Munoz-Avila

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

Includes:

- A self-created implementation for a sinple capture the Flag Game: 3 blue vs 3 red players, 3 flag locations 
- A simple GUI
- Uses Pyhop 1.2.2: https://bitbucket.org/dananau/pyhop/src/master/
- Simply run and it will import pyhop and necessary lines
- Will call Pyhop to generate a plan to CTF. Pyhop is controlling Blue
- Opponent is red, which selects random flag locations

Key variables:

state.drawTheGrid = True  ## currently set on True so it will display the board; if set on False nothing is displayed
maxTurns = 100            ## currently set to 100 turns



"""

import pyhop
import random
import tkinter as tk
import time


### main functions to call in main. Call either CTFtraining() or playPyhop())

def CTFtraining(state):
    #### call this function with 

    aiPlayer = ['blue',0]
    locDest = state.flagLocs[random.randrange(0,len(state.flagLocs))]
    print("execute: Blue moves: ",[0,1,2],state.blueGoals)
    print("execute: Red moves: ",[0,1,2],state.redGoals)
    for i in range(0,maxTurns):
        action = returnNextAIAction(state,aiPlayer,locDest)
        #print(action)
        state = executeActionAIPlayer(state,aiPlayer,action)
        printPlayers(state)
        #input("enter")
        if i%10 == 0:
            print("after ", i, "turns:")
            printFlagsOwner(state)
            #printPlayers(state)
            print("new scores:", state.blueScore, " vs ", state.redScore, "\n")
            #input("enter")

    return state

def CTFplanning(state):
    print("""
    ********************************************************************************
    Call pyhop.pyhop(state1,[('travel','me','home','park')]) with different verbosity levels
    ********************************************************************************
    """)

    #print("- If verbose=0 (the default), Pyhop returns the solution but prints nothing.\n")
    #pyhop.pyhop(state,[('start','me', 0)])


    # print('- If verbose=1, Pyhop prints the problem and solution, and returns the solution:')
    clicks = 4
    pyhop.pyhop(state,[('ctf','me', clicks)],verbose=1)



    # print('- If verbose=2, Pyhop also prints a note at each recursive call:')
    # pyhop.pyhop(state,[('start','me', 0)],verbose=2)

    #print('- If verbose=3, Pyhop also prints the intermediate states:')
    #pyhop.pyhop(state,[('ctf','me', 0)],verbose=3)

    return



## functions for an external agent training on CTF game #######

def reset(state): ##resets the simulation and all parameters
	         ## returns the state

    state.rows=20
    state.cols=20
    state.grid=[]
    for i in range(state.cols):
        col=[]
        for j in range(state.rows):
            col.append(cell(0,[],[],None))
        state.grid.append(col)

    state.flagLocs= [[0,0],[9,9],[19,19]]

    for i in range(len(state.flagLocs)):
        state.grid[state.flagLocs[i][0]][state.flagLocs[i][1]].flag = 1 

    state.weapons = []
    
    excalibur = weapon("excalibur","sword", False, None, [15,15])  ##[4,4] default
    harpe = weapon("harpe","sword", False, None, [3,3])
    state.weapons = [excalibur,harpe]
    for i in range(len(state.weapons)):
        state.grid[state.weapons[i].loc[0]][state.weapons[i].loc[1]].weapon = state.weapons[i]
    #printWeaponsLocs(state)

    state.blueStart = [19,0]
    state.redStart =  [0,19]
    state.maxPlayers = 3

    state.blue=[]
    for i in range(0,state.maxPlayers):
        state.blue.append((state.blueStart[0],state.blueStart[1])) ## [x,y] location of blue player i
    #print("blue",state.blue)
    for i in range(0,state.maxPlayers):
        state.grid[state.blue[i][0]][state.blue[i][1]].blue.append(i) ## [x,y] location of red player i

    #print("initialize blue players")
    #printBluePlayers(state,rows,cols)

    state.red=[]
    for i in range(0,state.maxPlayers):
        state.red.append((state.redStart[0],state.redStart[1]))

    for i in range(0,len(state.red)):
        state.grid[state.red[i][0]][state.red[i][1]].red.append(i)

    state.blueScore = 0
    state.redScore = 0

    state.redGoals = randomMove(state)    ### random at the beginning of game.
    state.blueGoals = randomMove(state)

    
        
    return state


def executeActionAIPlayer(state,aiplayer,aiaction):
    ### returns state
    ### executes one tick in the simulation
    ### aiplayer = (color, playerNumber); for example player = ('blue',2)
    ### executes aiaction: 'up', 'down', 'left','right','stay'; player = (color, playerNumber); for example player = ('blue',2)
    ### all other players move and conflicts are resolved
   


    movePlayer(state,aiplayer,aiaction)
    #print("AI player:", aiplayer, "action: ", aiaction)
    for j in range(state.maxPlayers):
        if j != aiplayer[1] or 'blue' != aiplayer[0]:
            action = returnNextAction(state,['blue',j],state.blueGoals[j])
            #print("player:", ['blue',j], "action: ", action)
            movePlayer(state,['blue',j],action)

    for j in range(state.maxPlayers):
         if j != aiplayer[1] or 'red' != aiplayer[0]:
            action = returnNextAction(state,['red',j],state.redGoals[j])
            #print("player:", ['red',j], "action: ", action)
            movePlayer(state,['red',j],action)   
    #print("\n")
    
    

    resolveConflicts(state)

    #printFlagsOwner(state)
    #print("new scores:", state.blueScore, " vs ", state.redScore, "\n")
    #printPlayers(state)
    #input("enter")

    return state

    


def returnNextAIAction(state,player,locDest): ### returns 'up', 'down', 'left', 'right' or 'stay' 
                                            ### player = (color, playerNumber); for example player = ('blue',2)
                                            ### locDest = [x,y] coordinates in the grid where a flag is located
                                            ### This is the action that will call your learning algorithm
		                                    ### right now it selects an action that moves the agent towards the LocDest; if agent is already there it returns ‘stay’

    
    if player[0]=='blue':
        locNow = state.blue[player[1]]
    else: ## must be 'red'
        locNow = state.red[player[1]]

    if (locNow[0] < locDest[0]):
        return 'down'       ### next location: [locNow[0]+1,locNow[1]]]
    elif (locNow[0] > locDest[0]):
        return 'up'     ### next location:  [locNow[0]-1,locNow[1]]]
    if (locNow[1] < locDest[1]):
        return 'right'    ### next location: [locNow[0],locNow[1]+1]]
    elif (locNow[1] > locDest[1]):
        return 'left'     ### next location: [locNow[0],locNow[1]-1]]
    else: ### (locNow[0] == locDest[0] and locNow[0] == locDest[0])
        return 'stay' ### next location: locNow[0],locNow[1]]




### operators ###########################

def move(state,bluePlayersList,blueFlagsList):  ### blue players bluePlayersList[0], bluePlayersList[1],...  are moved to flag locations BlueFlagsList[0], BlueFlagsList[1].... respectively

    #print("(moveBlue ",bluePlayersList,blueFlagsList")")

    redPlayersList = [0,1,2]
    ###redFlagsList = [state.flagLocs[0],state.flagLocs[1],state.flagLocs[2]]  ### this can be changed to whatever strategy red chooses its flags
    redFlagsList = randomMove(state) ### unflag if wants random selection of flags

    return execute(state,bluePlayersList,blueFlagsList,redPlayersList,redFlagsList)

def randomMove(state): ## test
    rf1 = random.randrange(0,3)  ### destination for red players 0, 1, 2
    rf2 = random.randrange(0,3)
    rf3 = random.randrange(0,3)
    return ([state.flagLocs[rf1],state.flagLocs[rf2],state.flagLocs[rf3]])

def halt(state,me):
    return state
    
def doNothing(state,me):
    return state
      


pyhop.declare_operators(move,halt,doNothing)
print('')
pyhop.print_operators()


### methods ###########################

 
def ctfM(state,a, clicks):
    (f1,f2,f3) = shortMedLong(state.flagLocs[0],state.flagLocs[1],state.flagLocs[2])
    ###(p1,p2,p3) = (0,1,2)
    #print(f1,f2,f3)
    (p1,p2,p3) = playersCLosestflagLocs(state,0,1,2,f1,f2)
    #print(p1,p2,p3)
    if clicks  < 1:
        return [('patrol',p1,p2,p3,f1,f2)] ### aim at controlling the two closest
    else:
        return [('patrol',p1,p2,p3,f1,f2),('ctf',a,clicks-2)] ### aim at controllign the two closest
    

def patrolM(state,p1,p2,p3,f1,f2):
        return [('move',[p1,p2,p3],[f1,f2,f2]),('move',[p1,p2,p3],[f1,f2,f1]) ]

    
pyhop.declare_methods('patrol',patrolM)
pyhop.declare_methods('ctf',ctfM)
pyhop.print_methods()
print('')


#### auxiliary Python methods  ###########################


def drawGrid(state):
    if state.drawTheGrid is False:
        return state
    
    for i,row in enumerate(state.grid):
        for j,column in enumerate(row):
            state = drawGridAtLoc(state,i,j)

    time.sleep(2)

    return state


def returnNextAction(state,player,locDest): ### returns 'up', 'down', 'left', 'right' or 'stay' 
                                            ### player = (color, playerNumber); for example player = ('blue',2)
                                            ### this is for the other players
    
    if player[0]=='blue':
        locNow = state.blue[player[1]]
    else: ## must be 'red'
        locNow = state.red[player[1]]

    if (locNow[0] < locDest[0]):
        return 'down'       ### next location: [locNow[0]+1,locNow[1]]]
    elif (locNow[0] > locDest[0]):
        return 'up'     ### next location:  [locNow[0]-1,locNow[1]]]
    if (locNow[1] < locDest[1]):
        return 'right'    ### next location: [locNow[0],locNow[1]+1]]
    elif (locNow[1] > locDest[1]):
        return 'left'     ### next location: [locNow[0],locNow[1]-1]]
    else: ### (locNow[0] == locDest[0] and locNow[0] == locDest[0])
        return 'stay' ### next location: locNow[0],locNow[1]]




def distance(loc1,loc2):
    return abs(loc1[0]-loc2[0])+abs(loc1[1]-loc2[1])

def shortMedLong(loc1,loc2,loc3):
    a = distance(loc1,loc2)
    b = distance(loc2,loc3)
    c = distance(loc1,loc3)

    
    if a < b:
        if b < c:
            return (loc1,loc2,loc3)
        elif c < a: ##c < a < b
            return (loc3,loc1,loc2)
        else: ## b< a, c < b, a < c
            return (loc1,loc3,loc2)
    else:##  b < a
        if a < c:## b < a < c
            return (loc2,loc1,loc3)
        elif b < c:## b < a, c < a, b < c
            return (loc2,loc3,loc1)
        else:## b < a, c < a, c < b
            return (loc3,loc2,loc1)    
        
def playersCLosestflagLocs(state,p1,p2,p3,f1,f2):
    players = [p1,p2,p3]
    a = distance(state.blue[p1],f1)
    b = distance(state.blue[p2],f1)
    c = distance(state.blue[p3],f1)
    if (a  < b):
        if (b < c):
            players.remove(p1)
            tof1 = p1
        elif (c < a): ## c < b, a < b, c < a
            players.remove(p3)
            tof1 = p3
        else: ## c < b, a < b, a < c
            players.remove(p1)
            tof1 = p1            
    elif a < c: ### b < a < c
        players.remove(p2)
        tof1 = p2
    elif b < c: ###b < a; c < a, b < c
        players.remove(p2)
        tof1 = p2
    else:    ###b < a; c < a,  c < b
        players.remove(p3)
        tof1 = p3
        
    d = distance(state.blue[players[0]],f2)
    e = distance(state.blue[players[1]],f2)
    if d < e:
        return(tof1,players[0],players[1])
    else:
        return(tof1,players[1],players[0])

def printWeaponsLocs(state):
    print("Weapons locations: ")
    for i in range(state.cols):
        print(i,"[", end='')
        for j in range(state.rows):
            onecell = state.grid[i][j]
            if onecell.weapon is None:
                print(" None ", end = "")
            else:
                print(onecell.weapon.id, " ", end='')
        print("]")   

def printFlagLocs(state):
    print("flag locations: ")
    for i in range(state.cols):
        print(i,"[", end='')
        for j in range(state.rows):
            onecell = state.grid[i][j]
            print(onecell.flag, " ", end='')
        print("]")

def printFlagsOwner(state):
    print("flags owners=[", end='')
    for loc in state.flagLocs:
        print(state.grid[loc[0]][loc[1]].flag, " ", end='')
    print("]","\n")
    


def printPlayers(state):
    print("\n  players")
    for i in range(state.cols):
        print(i,"[", end='')
        for j in range(state.rows):
            onecell = state.grid[i][j]
            if len(onecell.blue) > 0 and len(onecell.red) > 0:
                print(onecell.blue, "v", onecell.red,end="")
            elif len(onecell.blue) > 0:
                print('b',onecell.blue, end='')
            elif len(onecell.red) > 0:
                print('r',onecell.red, end='')
            else:
                print("[]",end="")
        print("]")


def printBluePlayers(state):
    print("\n Blue players")
    for i in range(state.cols):
        print(i,"[", end='')
        for j in range(state,rows):
            onecell = state.grid[i][j]
            print(onecell.blue, end='')
        print("]")

def printRedPlayers(state):
    print("\n Red players")
    for i in range(state.cols):
        print(i,"[", end='')
        for j in range(state.rows):
            onecell = state.grid[i][j]
            print(onecell.red, end='')
        print("]")

def drawGridAtLoc(state,i,j):
    if state.drawTheGrid is False:
        return state
    
    tx = ""
    nBlueP = len(state.grid[i][j].blue)
    nRedP = len(state.grid[i][j].red)
    weapon = state.grid[i][j].weapon
    flag = state.grid[i][j].flag
    if nBlueP > 0:
        tx += "b"+str(nBlueP)
    if nRedP > 0:
        tx  += "r"+str(nRedP)
    if weapon != None:
        tx += "w"
    ltx = len(tx)
    tx = tx.ljust(6)
    if flag == 0:
        L = tk.Label(root,text=tx,bg='white')
        L.grid(row=i,column=j)
    elif flag == 1:
        L = tk.Label(root,text=tx,bg='yellow')
        L.grid(row=i,column=j)
    elif flag == 2:
        L = tk.Label(root,text=tx,bg='blue')
        L.grid(row=i,column=j)
    else:
        L = tk.Label(root,text=tx,bg='red')
        L.grid(row=i,column=j)

    root.update_idletasks()
    root.update()

    return state
    


def execute(state,bluePlayersList,bluePlayersFlags,redPlayersList,redPlayersFlags):

    print("execute: Blue moves: ",bluePlayersList,bluePlayersFlags)

    print("execute: Red moves: ",redPlayersList,redPlayersFlags)

    for i in range(round(state.cols*2+1)): ## have each player call the same move function and change so the corde ramins the same regardless of number of players
        for j in range(state.maxPlayers):
            nextAction = returnNextAction(state,['blue',j],bluePlayersFlags[j])
            movePlayer(state,['blue',j],nextAction) 

        for j in range(state.maxPlayers):
            nextAction = returnNextAction(state,['red',j],redPlayersFlags[j]) 
            movePlayer(state,['red',j],nextAction)   
        #print("\n")

        resolveConflicts(state)
        if state.drawTheGrid is True:
            time.sleep(1)

    printFlagsOwner(state)
    print("new scores:", state.blueScore, " vs ", state.redScore, "\n")
    #printPlayers(state)
    #input("enter")

    return state

def movePlayer(state,player,nextAction): ### move player in playersList to flag
                                         ### player = (color, number)
    
    #print("move player", player,nextAction)


    if player[0]=='blue':
        locNow = state.blue[player[1]]
    else: ## must be 'red'
        locNow = state.red[player[1]]

    
    if nextAction == 'down' and (locNow[0] + 1) in range(state.rows): 
        nextLocation = [locNow[0]+1,locNow[1]]
    elif nextAction == 'up' and (locNow[0] - 1) in range(state.rows):
        nextLocation = [locNow[0]-1,locNow[1]]
    elif nextAction == 'right' and (locNow[1] + 1) in range(state.cols):
        nextLocation = [locNow[0],locNow[1]+1]
    elif nextAction =='left' and (locNow[1] - 1) in range(state.cols):
        nextLocation = [locNow[0],locNow[1]-1]
    else: ### mextAction == 'stay' or out of range move
        nextLocation = locNow[0],locNow[1]
    

    #print("(moveBlue ", player, "to: ", nextlocation, "destination: ", flag, ")", end ="")

    #printBluePlayers(state)
    #input("enter")

    if player[0]=='blue':
        ### remove players from current location
        #printPlayers(state,rows,cols)
        state.grid[state.blue[player[1]][0]][state.blue[player[1]][1]].blue.remove(player[1])
        
        state.blue[player[1]] = nextLocation
       
        state.grid[nextLocation[0]][nextLocation[1]].blue.append(player[1])
        
    else: ## must be 'red'
        ### remove players from current location
        #printPlayers(state,rows,cols)
        state.grid[state.red[player[1]][0]][state.red[player[1]][1]].red.remove(player[1])
        
        state.red[player[1]] = nextLocation
        
        state.grid[nextLocation[0]][nextLocation[1]].red.append(player[1])

    drawGridAtLoc(state,locNow[0],locNow[1])
    drawGridAtLoc(state,nextLocation[0],nextLocation[1])
    
  

    return state





def resolveConflicts(state):

    fightHappen = False
    for i in range(state.cols):
        for j in range(state.rows):
            nBlueP = len(state.grid[i][j].blue)
            nRedP = len(state.grid[i][j].red)
            if nBlueP > 0 and nRedP > 0:  ## players of both teams in same cell
                drawGridAtLoc(state,i,j) ### there is a fight
            
                print("fight",state.grid[i][j].blue," blues vs ", state.grid[i][j].red, " reds at location: [", i, ",", j,"] ", end='')
                blueWins = 0
                if checkBlueHasWeapon(state,i,j):
                    print("blue team has weapon ")
                    blueWins += 11  ## blue always wins
                if  checkRedHasWeapon(state,i,j):
                    print("red team has weapon")
                    blueWins -= 10 ## blue always loose; if both have weapons, they cancel each other.

                if nBlueP > nRedP:
                    blueWins += 10 ## always win; unless red has weapon; in which case they cancel each other
                elif nBlueP < nRedP:
                    blueWins += 0 ## red always win; unless blue has weapon; in which case they cancel each other
                else:
                    blueWins += 5
                rollFight = random.randrange(1,11)
                #print("BlueWins: ", blueWins," rollFight: ", rollFight)
                if rollFight <= blueWins:
                    #printRedPlayers(state)
                    killReds(state,i,j)   ## reds are relocated to redStart 
                    print("blue won, new red locations:", state.red, "\n")
                    #printRedPlayers(state)
                    #input("press enter")
                else:
                    #printBluePlayers(state)
                    killBlues(state,i,j) ## blues are relocated to blueStart
                    print("red won, new blue locations:", state.blue,"\n")
                    #printBluePlayers(state)
                    #input("press enter")
            
            nBlueP = len(state.grid[i][j].blue)
            nRedP = len(state.grid[i][j].red)
            if state.grid[i][j].flag > 0 : ## there is a flag
                    if nBlueP > 0: 
                        state.grid[i][j].flag = 2
                        state.blueScore += 1
                        if state.grid[i][j].weapon is None:
                            pass
                        else: ## there is a weapon; assign to first blue player in [i][j] without a weapon
                            for bply in state.grid[i][j].blue:
                                 if checkPlayerHasWeapon(state,["blue",bply]) is None:
                                    state = assignWeapon(state,["blue",bply],i,j)
                    elif nRedP > 0:
                        state.grid[i][j].flag = 3
                        state.redScore += 1
                        if state.grid[i][j].weapon is None:
                            pass
                        else: ## there is a weapon; assign to first red player in [i][j] without a weapon
                            for rply in state.grid[i][j].red:
                                 if checkPlayerHasWeapon(state,["red",rply]) is None:
                                    state = assignWeapon(state,["red",rply],i,j)
                    elif state.grid[i][j].flag == 2:  ##no players in flag and it belongs to blue
                        state.blueScore += 1
                    elif state.grid[i][j].flag == 3:  ##no players in flag and it belongs to red
                        state.redScore += 1
                    drawGridAtLoc(state,i,j) ## possible change of flag

            if state.grid[i][j].weapon is None:
                            pass
            elif nRedP > 0: ## there is a weapon; assign to first red player in [i][j] without a weapon
                    for rply in state.grid[i][j].red:
                        if checkPlayerHasWeapon(state,["red",rply]) is None:
                            state = assignWeapon(state,["red",rply],i,j)
                            break
            elif nBlueP > 0:
                    for bply in state.grid[i][j].blue:
                        if checkPlayerHasWeapon(state,["blue",bply]) is None:
                            state = assignWeapon(state,["blue",bply],i,j)
                            break
                        
            ### to do: pick weapon here << done but not working
            ### later: if carrying player dies, reset weapon to start location << done need to check
            ### later: if it player reaches reaches flag, reset weapon to starting location

    #input("\n calling  resolveConflicts \n")



    return state

def assignWeapon(state,player,i,j): ## player = (color,playernumber)
    wpn = state.grid[i][j].weapon
    wpn.taken = True
    wpn.player = player
    print("weapon ", wpn.id, "taken by ", player)
    state.grid[i][j].weapon = None
    return state

def resetWeaponStart(state,weapon):
    
    weapon.taken = False
    weapon.player = None
    state.grid[weapon.loc[0]][weapon.loc[1]].weapon = weapon

    print("weapon ", weapon.id, "reset ")
    return state


def checkPlayerHasWeapon(state,player): ## if  player=(color,ply) has weapon return True
    for wpn in state.weapons:
        if wpn.taken is True:
            if player[0] == wpn.player[0] and player[1] == wpn.player[1]:
                #print("\n",player, "has ", wpn.id, "checkPlayerHasWeapon")
                return wpn
    return None

    

def checkRedHasWeapon(state,i,j): ## checks if a red player in (j,j) has weapon
    for rply in state.grid[i][j].red:
        if  checkPlayerHasWeapon(state,["red",rply]) is None:
            pass
        else:
            print("red player ", rply, " has weapon")
            #input("enter")
            return True
    return False

def checkBlueHasWeapon(state,i,j): ## checks if a blue player in (j,j) has weapon
    for bply in state.grid[i][j].blue:
        if  checkPlayerHasWeapon(state,["blue",bply]) is None:
            pass
        else:
            print("blue player ", bply, " has weapon")
            #input("enter")
            return True
    return False

def killReds(state,i,j):  ## reds are relocated to redStart 
    toRemove = [x for x in state.grid[i][j].red]
    for px in toRemove:
        state.grid[i][j].red.remove(px)
        state.grid[state.redStart[0]][state.redStart[1]].red.append(px)
        state.red[px] = (state.redStart[0],state.redStart[1])
        wpn = checkPlayerHasWeapon(state,["red",px])
        if wpn is None:
            pass
        else:
            resetWeaponStart(state,wpn)
    drawGridAtLoc(state,i,j)
    drawGridAtLoc(state,state.redStart[0],state.redStart[1])
    
    return state

def killBlues(state,i,j): ## blues are relocated to blueStart
    toRemove = [x for x in state.grid[i][j].blue]
    for px in toRemove:
        state.grid[i][j].blue.remove(px)
        state.grid[state.blueStart[0]][state.blueStart[1]].blue.append(px)
        state.blue[px] = (state.blueStart[0],state.blueStart[1])
        wpn = checkPlayerHasWeapon(state,["blue",px])
        if wpn is None:
            pass
        else:
            resetWeaponStart(state,wpn)

    drawGridAtLoc(state,i,j)
    drawGridAtLoc(state,state.blueStart[0],state.blueStart[1])
   
    return state
   
    
### defining state  ###########################

state = pyhop.State('state1')

class weapon:
    def __init__(self, id, type, taken, player, loc):
        self.id = id ### each weapon has a unique identifier
        self.type = type ## each weapon is of a type. For now all weaponds will be of type "sword"
        self.taken = taken ## true if a player has it; false if the weapon is in a map's location
        self.player = player ## (color, player number) of the player that carries the weapon
        self.loc = loc ## location of the weapon as (i,j); if player doesn't has it, it will be placed there
    


class cell: ### each cell in the grid
    def __init__(self, flag, blue, red, weapon): 
        self.flag = flag    ### flag = 0 (no flag), 1 (neutral), 2 (blue owns), 3 red owns
        self.blue = blue    ### blue list of blue players in cell 
        self.red = red      ### red list of red players in cell 
        self.weapon = weapon ### if of weapon in cell; otherwise None 


global root   #### for displaying
root = tk.Tk()
   
state.drawTheGrid = True  ## set True if wants grid to be displayed; False otherwise 

state = reset(state)

state= drawGrid(state)
#input("start")


maxTurns = 100

print("game start: ")
printFlagLocs(state)
printFlagsOwner(state)
printPlayers(state)




#input("enter")

### call one of the following if training (learning) or just planning
### CTFtraining(state)
CTFplanning(state)

if state.drawTheGrid == True:
    input("end")






