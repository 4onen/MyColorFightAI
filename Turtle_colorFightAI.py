# You need to import colorfight for all the APIs
import colorfight
import random
import time


def findMe(g):
    for usr in g.users:
        if usr.id == g.uid:
            return usr

def manhattanDist(p1,p2):
    (x1,y1),(x2,y2)=p1,p2
    x,y = abs(x1-x2),abs(y1-y2)
    return x+y

def calcCenter(cells,num):
    cx = 0
    cy = 0
    for c in cells:
        cx += c[0]/num
        cy += c[1]/num
    return (cx,cy)

#Takes (colorfight.Game, core@(x,y), current_x, current_y, opt_recursion_depth)
#Returns (score,depth,x,y)
def ogle(g,core,x,y,depth=0):
    maxDepth = max(g.width,g.height)//2+1
    if(depth>maxDepth):
        return (-200,x,y,depth)

    tc = core
    c = g.GetCell(x,y)
    if(type(c)!=colorfight.Cell): return (-9999,x,y,depth)
    
    closenessMod = maxDepth-depth
    timeMod = 33.0 - c.takeTime if (not c.isTaking) else -10000.0
    ownershipMod = 0.000000001 if c.owner == g.uid else 1.0
    coreMod = 0.1 if x==tc[0] and y==tc[1] else 1.0
    goldMod = 10.0 if c.cellType == 'gold' else 1.0
    score = coreMod*ownershipMod*goldMod*(closenessMod*closenessMod*closenessMod*closenessMod+timeMod)

    dirs = []
    if c.owner == g.uid:
        if(depth<1):
            dirs = [(-1,0),(1,0),(0,1),(0,-1)]
        else:
            dx,dy=0,0
            if(c.x!=tc[0]):
                if(c.x>tc[0]):
                    dirs.append((1,0))
                else:
                    dirs.append((-1,0))
            if(c.y!=tc[1]):
                if(c.y>tc[0]):
                    dirs.append((0,1))
                else: 
                    dirs.append((0,-1))

    recRets = [(score,depth,x,y)]
    for d in dirs:
        recRet=ogle(g,core,x+d[0],y+d[1],depth+1)
        if goldMod > 1.1:
            recRet = (recRet[0]*5.0,recRet[1],recRet[2],recRet[3])
        recRets.append(recRet)
    return max(recRets)


def guard(g,core,x,y,depth=0):
    maxDepth = max(g.width,g.height)//4+1
    if(depth>maxDepth):
        return (-200,x,y,depth)
    
    tc = core
    c = g.GetCell(x,y)
    if(type(c)!=colorfight.Cell): return (-9999,x,y,depth)
    if(c.owner != g.uid): return (-201,x,y,depth)
    
    closenessMod = maxDepth-depth
    timeMod = 33.0 - c.takeTime if (not c.isTaking) else -10000.0
    goldMod = 5.0 if c.cellType == 'gold' else 1.0
    score = goldMod*(closenessMod*closenessMod+timeMod*timeMod*timeMod)

    dirs = []
    if c.owner == g.uid:
        if(depth<1):
            dirs = [(-1,0),(1,0),(0,1),(0,-1)]
        else:
            dx,dy=0,0
            if(c.x!=tc[0]):
                if(c.x>tc[0]):
                    dirs.append((1,0))
                else:
                    dirs.append((-1,0))
            if(c.y!=tc[1]):
                if(c.y>tc[0]):
                    dirs.append((0,1))
                else: 
                    dirs.append((0,-1))

    recRets = [(score,depth,x,y)]
    for d in dirs:
        recRet=ogle(g,core,x+d[0],y+d[1],depth+1)
        if goldMod > 1.1:
            recRet = (recRet[0]*3.0,recRet[1],recRet[2],recRet[3])
        recRets.append(recRet)
    return max(recRets)


if __name__ == '__main__':
    # Instantiate a Game object.
    g = colorfight.Game()
    # You need to join the game using JoinGame(). 'MyAI' is the name of your
    # AI, you can change that to anything you want. This function will generate
    # a token file in the folder which preserves your identity so that you can
    # stop your AI and continue from the last time you quit. 
    # If there's a token and the token is valid, JoinGame() will continue. If
    # not, you will join as a new player.
    if g.JoinGame("4's Turtle"):
        #Long-term memory
        cores = set()
        owned = set()
        golds = set()
        lastActed = (-1,-1)
        lastActedTurns = 0
        delayCount = 0
        
        #Setup memory
        for x in range(g.width):
            for y in range(g.height):
                c = g.GetCell(x,y)
                if c.owner == g.uid:
                    cores.add((x,y))
                    owned.add((x,y))
                    if c.cellType == 'gold':
                        golds.add((x,y))

        while True:
            g.Refresh()
            
            cooldown = g.cdTime - g.currTime
            if cooldown > 0:
                time.sleep(cooldown/2)
                continue
            print(cooldown,"   ",len(cores))
            delayCount += 1

            #Build short-term memory
            totalTimeToTakeMe = 0
            weakestCell = None
            #Update long-term memory
            coresMoved = []
            #Cores
            for s in cores:
                c = g.GetCell(s[0],s[1])
                if c and (c.owner!=g.uid or (not c.isBase)):
                    coresMoved.append(s)
            if coresMoved:
                for lc in coresMoved:
                    cores.remove(lc)
            del coresMoved[:]
            #Owned
            for s in owned:
                c = g.GetCell(s[0],s[1])
                if c and (c.owner!=g.uid):
                    coresMoved.append(s)
                else:
                    totalTimeToTakeMe += c.takeTime
                    if (weakestCell==None or c.takeTime < weakestCell.takeTime):
                        weakestCell = c
            if coresMoved:
                for ls in coresMoved:
                    owned.remove(ls)
            del coresMoved

            cn = len(owned)
            avgTT = totalTimeToTakeMe/cn

            success = False
            err_code = 9
            err_msg = 'No request sent???'
            #Choose
            if delayCount > 9:
                delayCount = 0
                if len(cores)<3 and len(cores)<(cn%10):
                    center = calcCenter(owned,cn)
                    center = (int(center[0]),int(center[1]))
                    for gold in golds:
                        if manhattanDist(gold,center)<3:
                            center = gold
                            break
                    centerC = g.GetCell(center[0],center[1])
                    if centerC and centerC.owner==g.uid and (not centerC.isBase):
                        response=g.BuildBase(center[0],center[1])
                        (success,err_code,err_msg) = (response[0],response[1],response[2])
                        if success:
                            cores.add(center)
                            print("!!!BASE BUILT!!! at ",center)
                        else:
                            print("!!!BASE... not built... at ",center)
                print((success,err_code,err_msg))
                continue
            
            opt = random.randint(int(-cn)*3*(len(cores)+1),int(avgTT))

            if(opt<0): #Defend
                defenseCore = random.sample(cores,1)[0] if cores else (weakestCell.x,weakestCell.y)
                defenseCore = (weakestCell.x,weakestCell.y) if manhattanDist((weakestCell.x,weakestCell.y),defenseCore)<3 else defenseCore
                (score,_,x,y) = guard(g,defenseCore,defenseCore[0],defenseCore[1])
                if lastActed == (x,y):
                    lastActedTurns += 1
                    if(lastActedTurns > 5): 
                        lastActed = (-1,-1)
                    continue
                (success,err_code,err_msg) = g.AttackCell(weakestCell.x,weakestCell.y)
                if success:
                    c = g.GetCell(x,y)
                    if c!=None and c.cellType == 'gold':
                        golds.add((x,y))
                    lastActed = (x,y)
                    lastActedTurns = 0
                    print("Defended (",weakestCell.x,',',weakestCell.y,")")
                else:
                    print("Failed to defend (",weakestCell.x,',',weakestCell.y,"):")
            else: #Attack
                spreadingCore = random.sample(cores,1)[0] if cores else (weakestCell.x,weakestCell.y)
                (score,_,x,y) = ogle(g,spreadingCore,spreadingCore[0],spreadingCore[1])
                if lastActed == (x,y): 
                    lastActedTurns += 1
                    if(lastActedTurns > 8):
                        lastActed = (-1,-1)
                    continue
                (success,err_code,err_msg) = g.AttackCell(x,y)
                if success:
                    owned.add((x,y))
                    c = g.GetCell(x,y)
                    if c!=None and c.cellType == 'gold':
                        golds.add((x,y))
                    lastActed = (x,y)
                    lastActedTurns = 0
                    print("Attacked (",weakestCell.x,',',weakestCell.y,")")
                else:
                    print("Failed to attack (",weakestCell.x,',',weakestCell.y,"):")
            print((success,err_code,err_msg))
    else:
        print("Failed to join the game!")
