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

def getTo(g,t,x,y,depth=0):
    if depth>max(g.width,g.height)//2:
        return None

    c = g.GetCell(x,y)
    if type(c)!=colorfight.Cell:
        return None

    dirs = []
    if c.owner != g.uid:
        if(depth<1):
            dirs = [(-1,0),(1,0),(0,1),(0,-1)]
        else:
            dx,dy=0,0
            if(c.x!=t[0]):
                if(c.x>t[0]):
                    dirs.append((1,0))
                else:
                    dirs.append((-1,0))
            if(c.y!=t[1]):
                if(c.y>t[0]):
                    dirs.append((0,1))
                else: 
                    dirs.append((0,-1))
    else:
        print("Sol'n found!",t,"to",(x,y))
        return 256

    recRets = []
    for d in dirs:
        recRet = getTo(g,t,x+d[0],y+d[1],depth+1)
        if recRet != None:
            if recRet==256:
                print("Sol'n is ",(depth,x,y))
                return (depth,x,y)
            else:
                recRets.append(recRet)
    if recRets:
        return min(recRets)
    return None



if __name__ == '__main__':
    # Instantiate a Game object.
    g = colorfight.Game()
    # You need to join the game using JoinGame(). 'MyAI' is the name of your
    # AI, you can change that to anything you want. This function will generate
    # a token file in the folder which preserves your identity so that you can
    # stop your AI and continue from the last time you quit. 
    # If there's a token and the token is valid, JoinGame() will continue. If
    # not, you will join as a new player.
    if g.JoinGame("Digitalis"):

        owned = set()
        golds = set()

        xsizes = [0,g.width//2,g.width-1]
        ysizes = [0,g.height//2,g.height-1]
        corners = []
        for xc in xsizes:
            for yc in ysizes:
                corners.append((xc,yc))

        for x in range(g.width):
            for y in range(g.height):
                c = g.GetCell(x,y)
                if c!=None and c.owner == g.uid:
                    owned.add((x,y))
                if c!=None and c.cellType == 'gold':
                    golds.add((x,y))
        gold = frozenset(golds)

        cornerScores = [0]*len(corners)
        maxDim = max(g.width,g.height)
        for i in range(len(corners)):
            for gold in golds:
                s = manhattanDist(corners[i],gold)
                cornerScores[i]=s*s
        corners = zip(cornerScores,corners)
        bestCorner = max(corners)[1:2]


        while True:
            g.Refresh()


            cooldown = g.cdTime - g.currTime
            if cooldown > -0.005:
                time.sleep(cooldown/2)
                continue
            print(len(owned),"    ",cooldown)

            notOwnedGolds = []
            for gold in golds:
                c = g.GetCell(x,y)
                if c!=None and c.owner != g.uid:
                        notOwnedGolds.append(gold)
            

            success = False
            err_code = 9
            err_msg = "No request sent???"

            if(notOwnedGolds):
                tgt = random.sample(notOwnedGolds,1)[0]
                (x,y)=tgt
                grow = getTo(g,tgt,x,y)
                if grow==None:
                    err_msg = "No path found to target."
                    err_code = 10
                else:
                    (success,err_code,err_msg)=g.AttackCell(grow[0],grow[1])
            else:
                weakestGold = None
                for gold in golds:
                    c = g.GetCell(x,y)
                    if weakestGold == None:
                        weakestGold = c
                    elif c!=None and (not c.isTaking) and (weakestGold.takeTime > c.takeTime):
                        weakestGold = c

                dirs = [(-1,0),(1,0),(0,1),(0,-1)]
                d = random.sample(dirs,1)
                (success,err_code,err_msg)=g.AttackCell(c.x+d[0],c.y+d[1])

            print((success,err_code,err_msg))







    else:
        print("Failed to join the game!")
