# You need to import colorfight for all the APIs
import colorfight
import random


def dist(p1,p2):
    x1,y1=p1[0],p1[1]
    x2,y2=p2[0],p1[1]
    x,y=abs(x1-x2),abs(y1-y2)
    return math.sqrt(x*x+y*y)


class Territory:
    core = (0,0)
    radius = 0

class MyPlayer:
    vitals = []
    territory = None
    goldSpots = []

    def identify_territory(self, g):
        #Make an array of target homes
        homeSpots = []
        for x in [0,g.width//2,g.width-1]:
            for y in [0,g.height//2,g.height-1]:
                self.homeSpots.append((x,y,0))

        #Identify ideal spot
        for x in range (g.width):
            for y in range (g.height):
                c = g.GetCell(x,y)
                if c.cellType == 'gold':
                    map(
                        (lambda h:
                            d = dist(h,(x,y))
                            most = max(g.width,g.height)//2
                            if (dist<most):
                                tt = c.takeTime if c.owner!=g.uid else 0
                                score = most-dist-tt
                                return (h[0],h[1],h[2]+socre*score)
                            else:
                                return h
                        )
                        ,homeSpots)
                elif (c.buildType=='base'&&c.owner!=g.uid):
                    map(
                        (lambda h:
                            d = dist(h,(x,y))
                            most = max(g.width,g.height)//2
                            if (dist<most):
                                score = most-dist
                                return (h[0],h[1],h[2]-socre*score)
                            else:
                                return h
                        )
                        ,homeSpots)
                else:
                    pass
        filter((lambda h: h[2]>0),homeSpots)
        if(homeSpots):
            sorted(homeSpots,lambda h:h[2])
            return homeSpots[0][0:1]
        else:
            for x in range(g.width,0,-1):
                for y in range(g.width,0,-1):
                    c = g.GetCell(x,y)
                    if(c.owner==g.uid):
                        return homeSpots[0][0:1]
        #Home identified!


    def identify_territory_radius(self,g,x,y,depth=0):
        if(depth>max(g.width,g.height)//3):
            return depth
        tc = self.territory.core
        c = g.GetCell(tc[0],tc[1])
        if(type(c)!=colorfighter.Cell): return depth
        
        dirs = []
        if(depth<1):
            dirs = [(-1,0),(1,0),(0,1),(0,-1)]
        else:
            if(c.x==tc[0]):
                dx = 0
            else:
                dx = math.copysign(1,c.x-tc[0])
            if(c.y==tc[1]):
                dy = 0
            else:
                dy = math.copysign(1,c.y-tc[1])
            
            if(dx!=0): dirs.append((dx,0))
            if(dy!=0): dirs.append((0,dy))

        depths = [depth]
        for d in dirs:
            depths.append(self.identify_territory_radius(g,x+d[0],y+d[1],depth+1))
        return max(depths)




    def __init__(self, g):
        g.Refresh()
        self.territory = Territory()
        self.territory.core = identify_territory(g)
        self.territory.radius = identify_territory_rad(g)







if __name__ == '__main__':
    # Instantiate a Game object.
    g = colorfight.Game()
    # You need to join the game using JoinGame(). 'MyAI' is the name of your
    # AI, you can change that to anything you want. This function will generate
    # a token file in the folder which preserves your identity so that you can
    # stop your AI and continue from the last time you quit. 
    # If there's a token and the token is valid, JoinGame() will continue. If
    # not, you will join as a new player.
    if g.JoinGame('4onen'):
        me = MyPlayer(g)


        '''
        # Put you logic in a while True loop so it will run forever until you 
        # manually stop the game
        while True:
            # Use a nested for loop to iterate through the cells on the map
            for x in range(g.width):
                for y in range(g.height):
                    # Get a cell
                    c = g.GetCell(x,y)
                    # If the cell I got is mine
                    if c.owner == g.uid:
                        if g.gold > 60:
                            print(g.BuildBase(x,y))
                        # Pick a random direction based on current cell 
                        d = random.choice([(0,1), (0,-1), (1, 0), (-1,0)])
                        # Get that adjacent cell
                        cc = g.GetCell(x+d[0], y+d[1])
                        # If that cell is valid(current cell + direction could be
                        # out of range) and that cell is not mine
                        if cc != None:
                            if cc.owner != g.uid:
                                # Attack the cell and print the result
                                # if (True, None, None) is printed, it means attack
                                # is successful, otherwise it will print the error
                                # code and error message
                                print(g.AttackCell(x+d[0], y+d[1]))
                                # Refresh the game, get updated game data
                                g.Refresh()
        '''
    else:
        print("Failed to join the game!")
