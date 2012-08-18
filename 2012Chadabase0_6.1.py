# Database program - gets DS information and gives statistics
# 0.0
# To Do:
# Work on Getting the Teams and Ranking to work
#          Improve Framerate on Alliance Selection Tab
#imports
import math
import pygame
import tkFileDialog     #For open and save dialogs
import tkSimpleDialog   #Simple input
import pickle
import os
import csv # For using access filetype .csv
from Tkinter import *
from statlib import stats #to get prob(z-score), use stats.lzprob(z)
pygame.init()


# Main variables
running = True
calculated = False  #Whether or not the data was calculated (if it hasn't been, you can't view team data)
calculated2= False
HEIGHT = 700
WIDTH = 1100
x0 = 160  # initial x-coordinate for the TAB
y0 = 65  # initial y-coordinate for the TAB
bgcolor = (0,51,0)
txcolor = (255,223,0)
root = Tk()
root.withdraw()
#screen = pygame.display.set_mode((WIDTH,HEIGHT),pygame.FULLSCREEN)
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Chadabase Ver0.6 - Peck.Lewis compilation")
tab = 0     # The tab displayed:
            # 0 - blank
            # 1 - Match
            # 2 - Team
            # 3 - Rank
            # 4 - Search
            # 5 - Compare (Alliances)
            # 6 - Choose (During Actual Alliance Selection[Function: Alliance_Selection()])
last = 0    #used for measuring fps
curfile = ""    #Current data file

# Stored Data
entries = []    # All the entries; 6 entries per match (1 per team)
entries2 = []   # To enter the bot shape info
teams = []      # All of the teams and their data (see 'Team' class)
matches = []    # All of the match data.
overall_score = 0   # Overall score for all matches
tb_buttons = []     #task bar button
t1_tboxes = []  #tab 1(match) textboxes
t2_tboxes = []  #tab 2(team) textboxes
t2_update = 1 #update team 2; preset to one so tboxes are drawn the first time
t2_surface = pygame.Surface((WIDTH-160,HEIGHT-65)) # surface for the second tab (to improve framerate)
t2_lreg = 0 # linear regression graph
t7_tboxes = []
t7_update = 1
t7_surface = pygame.Surface((WIDTH-160,HEIGHT-65))
t3_scrolls = [] #tab 3 (rank) scrollers
t3_buttons = [] # rank buttons for scrolling
t8_scrolls = []
t8_buttons = []
t4_stuff = []  #tab 4(Search) textboxes and radio boxes
t4_scroll = 0 #tab 4's scroller; create later before main loop
t4_wscroll = 0 #tab 4's scroller for teams we want on our alliance
t4_tempbut = [] # Temporary buttons
t4_temprad = [] # Temporary radio buttons
t4_wbut = [] # Temporary buttons for wanted teams
t4_wrad = [] # Temporary radio buttons for wanted teams
update_wanted = 0 # Whether or not to update the wanted teams in tab 4
t4_buttons = [] #tab 4's buttons
t5_surface = pygame.Surface((WIDTH-160,HEIGHT-65)) #surface for the fifth tab (to improve framerate)
t5_update = 1 # Whether or not to update tab 5
t5_tboxes = [] # tab 5 (comparison) textboxes
r1o = r1d = r1a = r1bb = r1tb = r1bs = r1ab = r1bo = r1md = r1tp = r1hh = r1hs = r1po = r1pd = r1pa = 0
r2o = r2d = r2a = r2bb = r2tb = r2bs = r2ab = r2bo = r2md = r2tp = r2hh = r2hs = r2po = r2pd = r2pa = 0
r3o = r3d = r3a = r3bb = r3tb = r3bs = r3ab = r3bo = r3md = r3tp = r3hh = r3hs = r3po = r3pd = r3pa = 0
b1o = b1d = b1a = b1bb = b1tb = b1bs = b1ab = b1bo = b1md = b1tp = b1hh = b1hs = b1po = b1pd = b1pa = 0
b2o = b2d = b2a = b2bb = b2tb = b2bs = b2ab = b2bo = b2md = b2tp = b2hh = b2hs = b2po = b2pd = b2pa = 0
b3o = b3d = b3a = b3bb = b3tb = b3bs = b3ab = b3bo = b3md = b3tp = b3hh = b3hs = b3po = b3pd = b3pa = 0
r1 = r2 = r3 = b1 = b2 = b3 = 0
r1t = r2t = r3t = b1t = b2t = b3t = 0 #average total scores
r1ts = r2ts = r3ts = b1ts = b2ts = b3ts = 0 #total scores for each team
wanted = [] # List of teams we want on our alliance
tabnum = 0
accessinfo = "" #a file that can be opened in access will be created for editing purposes
t4_update = 0 # Whether or not tab 4's data needs to be updated
t4_redraw = 0 # Whether or not to redraw tab 4's scroller (so that radio buttons can become unchecked
t4_wbmov = [] # List for buttons that move wanted rank +/- 1
t6_tboxes = [] #All the text boxes for tab 6
t6_scroll = [] #Scroller for tab 6 (shows wanted teams [only those that have not been selected])
t6_buttons = [] # buttons for tab 6
t6_update = 1 # whether or not to update tab 6 (alliance selection)
t6_surface = pygame.Surface((WIDTH-160,HEIGHT-65))
available_teams = [] #Teams that are available for alliance selection
#ranking info
off_rank = []
def_rank = []
ast_rank = []
tot_rank = []

hyb_rank = []
tel_rank = []
brd_rank = []

team_list = [] #Made global so that button and radio objects can be created in search tab
old_list = [] #Old team list; compare to team_list to see if update needed


#Don't update tabs every cycle;
tcount = 0
skip = 10

#----------------------------------------------------------------------------------------------------
# Linear Regression class
# -- Gives you information on a linear regression, and can return a graph
#----------------------------------------------------------------------------------------------------
class lreg():
    def __init__(self,datax=[],datay=[],a=0,b=0,r=0):
        #Make all of the numbers floats
        self.x = []
        self.y = []
        for num in datax:
            self.x.append(long(num))
        for num in datay:
            self.y.append(long(num))
        self.b = 0 #slope
        self.a = 0 #constant
        self.r2 = 0 #coefficient of determination
    def get_ab(self):
        n = float(len(self.x))
        self.xy = []
        self.x2 = []
        self.y2 = []
        i = 0
        while i < len(self.x):
            self.xy.append(self.x[i]*self.y[i])
            self.x2.append(self.x[i]**2)
            self.y2.append(self.y[i]**2)
            i += 1
        try:
            self.b = (n*sum(self.xy)-sum(self.x)*sum(self.y))/(n*sum(self.x2)-sum(self.x)**2)
        except:
            self.b = 100000000000000000000000
        self.a = (sum(self.y)/float(len(self.y))) - self.b*(sum(self.x)/len(self.x))
        #Get r2
        hmy2 = []
        ymh2= []
        i = 0
        try:
            while i < len(self.y):
                hy = self.x[i]*self.b+self.a
                hmy2.append((hy-(sum(self.y)/len(self.y)))**2)
                ymh2.append((self.y[i]-(sum(self.y)/len(self.y)))**2)
                i += 1
            self.r2 = sum(hmy2)/sum(ymh2)
        except:
            self.r2 = "N\A"
    def get_image(self,sx,sy,bgcolor,txcolor,stx=20,sty=20):
        self.surface = pygame.Surface((sx,sy))
        self.surface.fill(bgcolor)
        self.tx = [] # x coordinates modified to fit
        self.ty = [] # y coordinates modified to fit
        maxy = 0
        for y in self.y:
            if y > maxy: maxy = y
        xmod = (sx-2*stx)/float(len(self.x))
        # Always start at x=0
        for point in self.x:
            self.tx.append(xmod*point+stx)
        # Start at y=0
        if maxy != 0: ymod = (sy-2*sty)/float(maxy)
        else: ymod = sy-2*sty
        for point in self.y:
            self.ty.append(ymod*point+sty)
        # Remember that the image is flipped.
        x1 = stx
        x2 = sx-stx
        y1 = sty
        y2 = sy-sty
        #Draw axes
        pygame.draw.line(self.surface,(0,0,0),(x1,y1),(x2,y1),1)
        pygame.draw.line(self.surface,(0,0,0),(x1,y1),(x1,y2),1)
        #Draw numbers at end of axes to indicate max value of each axis
        xmax = 0
        ymax = 0
        for num in self.x:
            if num > xmax: xmax = num
        for num in self.y:
            if num > ymax: ymax = num
        # Draw points on graph
        i = 0
        while i < len(self.tx):
            pygame.draw.circle(self.surface,(255,0,0),(self.tx[i],self.ty[i]),((sx+sy)/100))
            i += 1
        i = 1
        #pygame.draw.line(screen,(0,0,0),(302,65),(302,HEIGHT),1)
        while i < len(self.tx):
            pygame.draw.line(self.surface,(0,0,0),(self.tx[i-1],self.ty[i-1]),(self.tx[i],self.ty[i]))
            i += 1
        # Draw the line of best fit
        #self.tx.append(xmod*point+stx)
        #self.ty.append(ymod*point+sty)
        p1 = (stx,self.a*ymod+sty) # B = slope
        p2 = (len(self.x)*xmod+stx,(self.b*len(self.x)+self.a)*ymod+sty)
        pygame.draw.line(self.surface,(0,0,255),p1,p2)
        #Flip and add text
        newsurface = pygame.transform.flip(self.surface,0,1)
        font = pygame.font.Font(None,stx)
        text = font.render(str(ymax),True,txcolor,bgcolor)
        newsurface.blit(text,(0,.5*stx))
        text = font.render(str(xmax),True,txcolor,bgcolor)
        newsurface.blit(text,(sx-.5*stx,sy-stx))
        text = font.render("r^2="+str(self.r2),True,txcolor,bgcolor)
        newsurface.blit(text,(0,sy-stx))
        return newsurface    
#----------------------------------------------------------------------------------------------------
# Scroller Class
#----------------------------------------------------------------------------------------------------
class scroller():
    def __init__(self,surface,maxheight=100,x=0,y=0,t="test"):
        self.type = t
        self.x=x
        self.y=y
        self.surface=surface
        self.maxh=maxheight
        self.currenty=0 #Scroll distance
        self.maxy = pygame.Surface.get_height(self.surface)-self.maxh
        self.speed = 1.5*self.maxy/self.maxh
    def draw(self,screen):
        self.width = pygame.Surface.get_width(self.surface)
        screen.blit(self.surface,(self.x,self.y),[0,self.currenty,self.width,self.maxh])
    def update(self,direction):
        if direction == 1 and self.currenty >= self.speed: #Scroll up
            self.currenty -= self.speed
        if direction == 0 and self.currenty + self.speed <= self.maxy:#scroll down
            self.currenty += self.speed

#----------------------------------------------------------------------------------------------------
# Radio Button Class
#----------------------------------------------------------------------------------------------------
class radio():
    def __init__(self,t="t",x=0,y=0,caption="Test:",flip=0,fs=50,check=0,teamnum=0):
        global bgcolor
        global txcolor
        self.x=x
        self.y=y
        self.type=t
        self.caption=caption
        self.flip=flip  #1 = text shows up on right of button
        self.size=fs
        font=pygame.font.Font(None,self.size)
        self.text = font.render(self.caption,True,txcolor,bgcolor)
        self.w = pygame.Surface.get_width(self.text)
        self.check=check
        self.teamnum = teamnum #Only used in the search tab; has no other use
    def draw(self,screen):
        if self.check:
            if self.flip: # Button to left
                pygame.draw.circle(screen,(0,0,0),(self.x+.5*self.size,self.y+.4*self.size),
                                   .25*self.size,0)
                screen.blit(self.text,(self.x+self.size,self.y))
            else: # button to right
                screen.blit(self.text,(self.x,self.y))
                pygame.draw.circle(screen,(0,0,0),(self.x+self.w+.5*self.size,self.y+.4*self.size),
                                   .25*self.size,0)
        else:
            if self.flip: # button to left
                pygame.draw.circle(screen,(0,0,0),(self.x+.5*self.size,self.y+.4*self.size),
                                   .25*self.size,.1*self.size)
                screen.blit(self.text,(self.x+self.size,self.y))
            else:   # button to right
                screen.blit(self.text,(self.x,self.y))
                pygame.draw.circle(screen,(0,0,0),(self.x+self.w+.5*self.size,self.y+.4*self.size),
                                   .25*self.size,.1*self.size)
    def click(self):
        if self.check == 1:
            self.check = 0 # Now unchecked
        else:
            self.check = 1

#----------------------------------------------------------------------------------------------------
# Textbox Class
#----------------------------------------------------------------------------------------------------
class textbox():
    def __init__(self,t="t",x=0,y=0,w=100,caption="Test:",fs=50,thickness = 1,clickable=0,val=0):
        global bgcolor
        global txcolor
        self.x=x
        self.y=y
        self.w=w
        self.type = t
        self.click = clickable
        self.caption = caption
        self.size = fs
        self.value = val
        self.th = thickness
        self.type = t
        font= pygame.font.Font(None,self.size)
        self.text= font.render(self.caption,True,txcolor,bgcolor)
        self.cw = pygame.Surface.get_width(self.text)
        self.ch = pygame.Surface.get_height(self.text)
        if self.click == 1:
            self.color = (0,255,0)
        else:
            self.color = bgcolor
    def draw(self,screen):
        global txcolor
        global bgcolor
        #draw caption
        screen.blit(self.text,(self.x+.5*self.th,self.y+.5*self.th))
        #draw textbox
        pygame.draw.rect(screen, self.color, (self.x+self.cw+.5*self.th,
                                              self.y+.5*self.th,self.w+.5*self.th,self.size+.5*self.th-10),
                         self.th)
        f2 = pygame.font.Font(None,self.size-self.th) #Account for thickness in rectangle
        intxt = f2.render(str(self.value),True,txcolor,bgcolor)
        screen.blit(intxt,(self.x+self.cw+self.th,self.y+self.th))
    def clicked(self):
        global root
        global screen
        global WIDTH
        global HEIGHT
        if self.click == 1: #Is clickable
            root.focus()
            newval = tkSimpleDialog.askstring("New Value","_",parent=root,initialvalue=0)
            root.withdraw()
            if newval == "": newval = 0
            self.value = newval
    def update(self,surface):
        print "updating"
            
#----------------------------------------------------------------------------------------------------
# Button Class
#----------------------------------------------------------------------------------------------------
class button:
    def __init__(self,t="none",x=0,y=0,w=0,h=0,text="Press Me",font=50,thickness = 1,static=1):
        global bgcolor
        global txcolor
        self.x = x
        self.y = y
        self.h = h
        self.w = w
        self.text = text
        self.size = font
        self.type = t
        self.static=1
        self.th = thickness
        font = pygame.font.Font(None,self.size)
        self.text= font.render(self.text,True,txcolor,bgcolor)
        if w==0: self.w = pygame.Surface.get_width(self.text)
        else: self.w = w
        if h==0: self.h = pygame.Surface.get_height(self.text)
        else: self.h = h
    def draw(self,screen):
        screen.blit(self.text,(self.x+.5*self.th,self.y+.5*self.th))
        pygame.draw.rect(screen, (255,0,0), (self.x,self.y,self.w+.5*self.th,self.h+.5*self.th),self.th)
    def click(self):
        global entries
        global tab
        global root
        global screen
        global curfile
        if self.type == "s": # save
            print "Saving"
            try:
                root.focus()
                filename = tkFileDialog.asksaveasfilename(parent=root)
                root.withdraw()
                filename = str(filename)
                data = pickle.dumps(entries)
                dfile = open(filename,"w")
                dfile.write(data)
                dfile.close()
                curfile = filename
                pygame.display.set_caption("Database -- " + filename)
                output_data()
                save_csv()
            except:
                print "save failed"
        elif self.type == "t":    #view team data
            tab = 2
        elif self.type == "r": # View rankings
            tab = 3
        elif self.type == "se": # Search
            tab = 4
        elif self.type == "co": # Compare Alliances
            tab = 5
        elif self.type == "ch": # Choose Alliances
            tab = 6
        elif self.type == "ps":
            tab = 7
        elif self.type == "r2":
            tab = 8
        elif self.type == "i": #import data
            imported = False
            try:
                import_data()
                imported = True
            except:  print "Could Not Import Data"
            if imported: calculate()
        elif self.type == "ip":
            #if calculated == True:
                imported2 = False
                try:
                    import_data2()
                    imported2 = True
                except:  print "Could No Import Data 2"
                if imported2: calculate2()
        elif self.type == "o": #open
            print "opening"
            try:
                root.focus()
                filename = tkFileDialog.askopenfilename(parent=root)
                root.withdraw()
                filename = str(filename)
                dfile = open(filename,"r")
                data = pickle.load(dfile)
                print "data loaded"
                entries = data
                global teams
                global matches
                teams = []
                matches = []
                print str(entries)
                calculate()
                pygame.display.set_caption("Database -- " + filename)
            except:
                print "error opening"

#----------------------------------------------------------------------------------------------------
# Entry Class
#   -- Equivalent to a single ms-access entry
#   -- Each amtch has 6 of these entries
#----------------------------------------------------------------------------------------------------
class entry():
    # 1 per team per match
    def __init__(self,data):
        self.match = data[0]        #The number of the match
        self.team = data[1]         #The team number
        self.color = data[2]        #The color for the match
        
        self.hasHybd = data[3]      #Whether or not they have hybrid
        self.UseKinect = data[4]    #If they used the kinect
        self.hybdlowrbrdg = data[5] #If the robot lower bridge in hybrid
        self.hybdassist = data[6]   #If the robot assisted in hybrid
        self.hybdother = data[7]   #If the robot had another strategy in hybrid
        self.HLow = data[8]         #Number of balls scored low in hybd
        self.HMid = data[9]         #Number of balls scored mid in hybd
        self.HHigh = data[10]        #Number of balls scored high in hybd

        self.disabledCounter = data[11]     #number of times disabled that match
        self.BallPU = data[12]      #Number balls picked up
        self.CrxBrdg = data[13]     #If they crossed the bridge
        self.CrxBar = data[14]      #If they crossed the bar
        self.TLow = data[15]        #Number of balls scored low
        self.TMid = data[16]        #Number of balls scored mid
        self.THigh = data[17]       #Number of balls scored high

        self.BrdgType = data[18]    #Type of bridge and attemped or not            ;0 = bal, 1 = co-op, 2 = att, 3 = co-op att, 4 = none, -1 = no button
        self.NumBots = data[19]     #Number of bots on bridge balanced or attemped ;0 = 1 bot , 1 = 2 bots, 2 = 3 bots , -1 = no button (okay: brdgType == 4)

        self.TechF = data[20]       #Number of tecnical fouls
        self.RegF = data[21]        #Number of regular fouls
        self.defensive = data[22]   #If robot was defensive
        self.assistive = data[23]   #If robot was assiting team
        self.yel = data[24]         #Did they get a yellow card
        self.red = data[25]         #Did they get a red card

        self.ball = self.TLow + self.TMid + self.THigh  #Number of Balls scored in tele
    def primary_sort(self):
        # Gets the match offensive score, whether the robot was offensive, etc.
        self.telescore = self.TLow + (2*self.TMid) + (3*self.THigh)
        self.hybdscore = self.HLow + (2*self.HMid) + (3*self.HHigh) + (3*(self.HLow + self.HMid + self.HHigh))
        
        self.scrhybd = 0
        self.scrtele = 0
        self.hasTfoul = 0
        self.hasRfoul = 0
        if self.hybdscore > 0: self.scrhybd = 1
        if self.telescore > 0: self.scrtele = 1
        if self.TechF > 0: self.hasTfoul = 1
        if self.RegF > 0: self.hasRfoul = 1
        #if(self.hybdScrType == 1):
        #    self.hybdother = 1
        #elif(self.hybdScrType == 2):
        #    self.hybdassist = 1
        #elif(self.hybdScrType == 3):
        #    self.hybdlowrbrdg = 1

        self.brdgsuc = 0
        self.teambrdgsuc = 0
        self.brdgscore = 0
        self.CObrdgsuc = 0
        self.AttteamBrdg = 0
        self.AttCOBrdg = 0
        if(self.BrdgType == 0):     #If team balanced on team bridge
            self.brdgsuc = 1
            self.teambrdgsuc = 1
            if(self.NumBots):
                self.brdgscore = (2**(self.NumBots - 1))*10
        elif(self.BrdgType == 1):     #If team balanced on Co-op bridge
            self.brdgsuc = 1
            self.CObrdgsuc = 1
            if(self.NumBots):
                self.brdgscore = (2**(self.NumBots - 1))*10
        elif(self.BrdgType == 2):     #If team attempted to balance on team bridge
            self.AttteamBrdg = 1
        elif(self.BrdgType == 3):     #If team attempted to balance on Co-op bridge
            self.AttCOBrdg = 1
        
        self.offensiveScore = self.telescore + self.hybdscore + self.brdgscore
        self.thscore = self.telescore + self.hybdscore
        # Is the robot defensive and/or offensive
        self.isOffensive = 0
        self.isDefensive = 0
        self.isAssistive = 0
        if (self.offensiveScore > 0): self.isOffensive = 1
        if (self.defensive > 0): self.isDefensive = 1
        if (self.assistive > 0): self.isAssistive = 1
    def secondary_sort(self,oppAvg,oppOff,allAvg,allOff,allDef,allAst,):
        # Gets the block defensive score, push defensive score, total defensive score
        # oppAvg = sum of opposing alliance's teams' offensive scores
        # oppOff = the opposing alliance's offensive score for the match
        # allAvg = the sum of own alliance's offensive score for the match
        # allOff = own alliance's offensive score for the match
        # allBlock = the number of blocking teams on own alliance
        # allPush = the number of pushing teams on own alliance
        if self.defensive == 1: self.defscore = (oppAvg - oppOff) / allDef
        else: self.defscore = 0
        if (self.assistive == 1): self.astscore = (allOff - allAvg) / allAst
        else: self.astscore = 0
    def tertiary_sort(self):
        self.total = self.defscore + self.astscore + self.offensiveScore
        self.thtotal = self.defscore + self.astscore + self.thscore

#----------------------------------------------------------------------------------------------------
# Entry2 Class
# -- Gets the robot chasis type
#----------------------------------------------------------------------------------------------------
class entry2():
    def __init__(self,data):
        self.team = data[0]
        
        self.roblength = data[1]
        self.robwidth = data[2]
        self.robheigth = data[3]
        self.robwieght = data[4]
        self.clearance = data[5]
        self.spacing = data[6]
        
        self.BrdgMech = data[7]
        self.SlideBrdg = data[8]
        self.balsensor = data[9]
        self.DriSys = data[10]
        self.ShiftGear = data[11]

        self.CenMass = data[12]

        self.Drive1 = data[13]
        self.exp1 = data[14]

        self.Drive2 = data[15]
        self.exp2 = data[16]

        self.Drive3 = data[17]
        self.exp3 = data[18]
        
#----------------------------------------------------------------------------------------------------
# Team Class
#   --Stores team data
#----------------------------------------------------------------------------------------------------
class Team():
    def __init__(self,num):
        self.number = num
        self.matches = []       # list holding all the matches the team is in
        self.oscores = []       # list holding all of the Elimination offensive scores
        self.dscores = []       # list holding all of the defensive scores
        self.ascores = []       # list holding all of the assistive scores
        self.tscores = []       # list holding all of the Elimination total scores
        self.wscores = []       # list holding all of the weighted scores
        self.woscores = []      # list holding all of the weighted offensive scores
        self.wdscores = []      # list holding all of the weighted defensive scores
        self.wascores = []      # list holding all of the weighted assistive scores
        self.THscores = []      # list holding the sum of tele and hybd scores for all the matches
        self.BrdgBalType = []   # list holding the type of bridge balace for  each match
        self.BrdgBalnum = []    # list holding the number of bots the robot attempted or succedded to balance with
        self.Brdgscores = []    # list holding all of the bridge scores
        self.BrdgSucc = 0       # the number of matches for which the team balanced a bridge successfully
        self.TeambrdgSucc = 0   # the number of matches for which the team balanced the team bridge successfully
        self.CoBrdgSucc = 0     # the number of matches for which the team balanced the Co-op bridge successfully
        self.AttTeamBRDG = 0    # the number of matches for which the team attepted to balance the team bridge
        self.AttCoBRDG = 0      # the number of matches for which the team attepted to balance the Co-op bridge
        self.noff = 0           # the number of matches for which the team was offensive
        self.ndef = 0           # the number of matches for which the team was defensive
        self.nast = 0           # the number of matches for which the team was assistive
        self.hadhybd = 0        # the number of matches for which the team had an autonomous mode
        self.hadtele = 0
        self.disabled = 0       # the number of matches for which the robot was disabled
        self.avgRfoul = []      # list holding the number of regular fouls for each match
        self.avgTechfoul = []   # list holding the number of technical fouls for each match
        self.hadRfoul = 0       # the number of matches for which the team had regular fouls
        self.hadTfoul = 0       # the number of matches for which the team had technical fouls
        self.hadyellow = 0      # the number of matches for which the team received a yellow card
        self.hadred = 0         # the number of matches for which the team received a red card
        self.hybdLwBrdg = 0     # the number of matches for which the team lowered the Co-op bridge in hybrid
        self.hybdast = 0        # the number of matches for which the team assisted the alliance in hybrid
        self.hybdoth = 0        # the number of matches for which the team performed stategies other than scoring, lower bridge, and assisted
        self.hybdscored = []    # the hybd scores for each match
        self.scorehybd = 0      # the number of matches for which the team scored in hybd
        self.AvgHybdScr = 0     # the average score for hybrid
        self.Hbballs = []       # balls scored in Hybrid on bottom
        self.Hmballs = []       # balls scored in Hybrid on middle
        self.Htballs = []       # balls scored in Hybrid on top
        self.ballscores = []    # balls scored in tele for each match
        self.telescores = []    # list of tele scores
        self.Tbballs = []       # balls scored bottom
        self.Tmballs = []       # balls scored middle
        self.Ttballs = []       # balls scored top
        self.ballsPU = []       # balls picked up
        self.defense = 0        # the number of matches the robot was defensive
        self.assist = 0         # the number of matches the robot was assistive
        self.off_rank = 0       #ranks among all teams
        self.def_rank = 0
        self.ast_rank = 0
        self.tot_rank = 0
        self.hyb_rank = 0
        self.tel_rank = 0
        self.brd_rank = 0
        self.matchplay = []
        self.robotlen = 0
        self.robotwid = 0
        self.robotheg = 0
        self.robotwig = 0
        self.floorclear = ""
        self.wheelspace = ""
        self.BridgeMechanics = ""
        self.SldBridge = ""
        self.ballsen = ""
        self.ShiftGear = ""
        self.DriveSystem = ""
        self.CenterMass = ""
        self.Driver1 = ""
        self.experince1 = None
        self.Driver2 = ""
        self.experince2 = None
        self.Driver3 = ""
        self.experince3 = None
    def get_avg_off(self):
        if self.noff > 0:
            self.avgthOff = sum(self.THscores)/len(self.matches)
            self.avgOff = sum(self.oscores)/len(self.matches)
        else:
            self.thavgOff = 0
            self.avgOff = 0
    def get_avg_defast(self):
        if self.ndef > 0: self.avgDef = sum(self.dscores)/len(self.matches)
        else: self.avgDef = 0
        if self.nast > 0: self.avgAst = sum(self.ascores)/len(self.matches)
        else: self.avgAst = 0
    def get_avg_Brdg(self):
        if self.BrdgSucc > 0:
            self.TotTbrdgSucc = self.TeambrdgSucc/self.BrdgSucc
            self.avgBrdgscr = sum(self.Brdgscores)/len(self.matches)
        else:
            self.TotTbrdgSucc = 0
            self.avgBrdgscr = 0
        if self.hadhybd > 0: self.avgHybd = sum(self.hybdscored)/len(self.matches)
        else: self.avgHybd = 0
        if self.hadtele > 0:
            self.avgTele = sum(self.telescores)/len(self.matches)
            self.compBpuBscr = sum(self.ballscores)/len(self.ballsPU)
        else:
            self.avgTele = 0
            self.compBpuBscr = 0
#----------------------------------------------------------------------------------------------------
# Match Class
#   -- Stores all match data
#----------------------------------------------------------------------------------------------------
class Match():
    def __init__(self,num):
        self.number = num   # Match Number
        self.teams = []     # The teams in the match
        self.team0 = []     # the teams in the first alliance
        self.team1 = []     # the teams in the second alliance
        self.all0 = []      # The teams in the first alliance
        self.all1 = []      # The teams in the second alliance
        self.off0 = 0       # The total offensive score for the first alliance
        self.off1 = 0       # The total offensive score for the second alliance
        self.noff0 = 0      # The nunber of offensive teams for the first alliance
        self.noff1 = 0      # The number of offensive teams for the second alliance
        self.TBrdgSucc0 = 0 # The number of matches first alliance balanced team bridge
        self.TBrdgSucc1 = 0 # The number of mathces second alliance balanced team bridge
        self.defense0 = 0   # The number of defensive teams in the first alliance
        self.assist0 = 0    # The number of assistive teams in the first alliance
        self.defense1 = 0   # The number of defensive teams in the second alliance
        self.assist1 = 0    # The number of assistive teams in the second alliance
        self.avgSum0 = 0    # The total of the average offensive scores for the first alliance
        self.avgSum1 = 0    # The total of the average offensive scores for the second alliance
        self.thavgSum0 = 0  # The average sum of the first alliance's hybrid and tele score
        self.thavgSum1 = 0  # The average sum of the second alliance's hybrid and tele score
        self.def0 = 0       # Total defensive score for first alliance
        self.def1 = 0       # Total defensive score for the second alliance
        self.ast0 = 0       # Total assistive score for the first alliance
        self.ast1 = 0       # Total assistive score for the second alliance
    def get_total(self):
        self.total0 = self.off0 + (2**(self.TBrdgSucc0 - 1))*10 #+ self.def0     #Total score for first alliance
        self.total1 = self.off1 + (2**(self.TBrdgSucc1 - 1))*10 #+ self.def1     #Total score for second alliance
        self.overall = self.total0 + self.total1    # Total match score


#----------------------------------------------------------------------------------------------------
# Output Data Function
# -- outputs access-importable text file with all information
#----------------------------------------------------------------------------------------------------
def output_data():
    global entries
    global curfile
    #if data file exists, destroy it
    try:
        os.delete(curfile+"_access.txt")
    except:
        print ""
    #open file for writing
    filetosave = open(curfile+"_access.txt","w")
    print "File Opened"
    n = 0
    outstring = ""
    while n < len(entries):
        outstring = ""
        for element in entries[n].stored_data:
            outstring += str(element) + ","
        oustring = outstring.strip(",")     #remove unnecessary last ","
        oustring += "\r\n" #new line at end
        filetosave.write(outstring)
        n += 1
    print "loop ended"
    filetosave.close()

def save_csv():
    global entries
    global curfile
    rows = []
    for entry in entries:
        rows.append(entry.stored_data)
    try:
        os.delete(curfile+"_access.txt")
    except:
        writer = csv.writer(open(curfile+"_access.txt","wb"))
        writer.writerows(rows)
    print writer
#----------------------------------------------------------------------------------------------------
# Import Data Function
#----------------------------------------------------------------------------------------------------
def import_data():
    global entries
    global calculated
    calculated = False
    if not calculated:
        filename = tkFileDialog.askopenfilename()
        filename = str(filename)
        print "file selected"
        filename = os.path.basename(filename)
        print filename
        new_data = open(filename,"r")
        print "file opened"
        # Clean out the data except for entries.  This way, data won't count multiple teams during
        # calculations
        global teams
        global matches
        teams = []
        matches = []
        # Now that the file is loaded, you need to parse it
        print "Parsing Data"
        for line in new_data:
            entries.append(parse_data(line))
        print "--Data parsed"
    #except:
    #    print "error"
#----------------------------------------------------------------------------------------------------
# Import Data2 Function
#----------------------------------------------------------------------------------------------------
def import_data2():
    global entries2
    global calculated2
    global teams
    calculated2 = False
    if not calculated2:
        filename = tkFileDialog.askopenfilename()
        filename = str(filename)
        print "file selected"
        filename = os.path.basename(filename)
        print filename
        new_data = open(filename,"r")
        print "file opened"

        print "Prasing Data 2"
        p=0
        for line in new_data:
            p +=1
            entries2.append(parse_data2(line))
            print "p"
            print p
        print "hi"
        print "--Data 2 parsed"
#----------------------------------------------------------------------------------------------------
# Parse Data Function - Takes each line in the file and transfers it to an entry
#----------------------------------------------------------------------------------------------------
def parse_data(info):
    data = []
    i = 0
    next = ""
    while i < 26:
        for character in info:
            if character != "," and character != "\n":
                next += str(character)
            else:
                data.append(int(next))
                next = ""
                i += 1
                if i >= 26: break
    return entry(data)

def parse_data2(info):
    data = []
    i = 0
    next = ""
    while i < 19:
        for character in info:
            if character != "," and character != "\n":
                next += str(character)
            else:
                data.append(int(next))
                next = ""
                i += 1
                print "i"
                print i
                if i >= 19: break
    return entry2(data)
#----------------------------------------------------------------------------------------------------
# Calculate Function - Calculates data for statistical analysis.
#                    - Both overall and team data created
#----------------------------------------------------------------------------------------------------
def calculate():
    global entries
    global teams
    global calculated
    global available_teams
    # Get offensive scores, whether the team was defensive this match, and whether
    # they were defensive.
    for entry in entries:
        entry.primary_sort()
    # Create team data
    for entry in entries:
        done = False
        for team in teams:
            if team.number == entry.team:
                team.oscores.append(entry.offensiveScore)
                team.THscores.append(entry.thscore)
                team.noff += entry.isOffensive
                team.ndef += entry.isDefensive
                team.nast += entry.isAssistive
                team.matches.append(entry.match)
                team.BrdgBalType.append(entry.BrdgType)
                if (entry.BrdgType > 1) and (entry.BrdgType < 4): team.BrdgBalnum.append(entry.NumBots)
                team.Brdgscores.append(entry.brdgscore)
                team.BrdgSucc += entry.brdgsuc
                team.TeambrdgSucc += entry.teambrdgsuc
                team.CoBrdgSucc += entry.CObrdgsuc
                team.AttTeamBRDG += entry.AttteamBrdg
                team.AttCoBRDG += entry.AttCOBrdg
                team.hadhybd += entry.hasHybd
                team.hadtele += entry.scrtele
                team.disabled += entry.disable
                team.avgRfoul.append(entry.RegF)
                team.avgTechfoul.append(entry.TechF)
                team.hadyellow += entry.yel
                team.hadred += entry.red
                team.hybdLwBrdg += entry.hybdlowrbrdg
                team.hybdast += entry.hybdassist
                team.hybdoth += entry.hybdother
                team.hybdscored.append(entry.hybdscore)
                team.Hbballs.append(entry.HLow)
                team.Hmballs.append(entry.HMid)
                team.Htballs.append(entry.HHigh)
                team.ballscores.append(entry.ball)
                team.telescores.append(entry.telescore)
                team.Tbballs.append(entry.TLow)
                team.Tmballs.append(entry.TMid)
                team.Ttballs.append(entry.THigh)
                team.ballsPU.append(entry.BallPU)
                team.defense += entry.defensive
                team.assist += entry.assistive
                team.matchplay.append(entry.match)
                done = True
        if done == False:
            teams.append(Team(entry.team))
            print "Added team#" + str(entry.team)
            teams[len(teams)-1].oscores.append(entry.offensiveScore)
            teams[len(teams)-1].THscores.append(entry.thscore)
            teams[len(teams)-1].noff += entry.isOffensive
            teams[len(teams)-1].ndef += entry.isDefensive
            teams[len(teams)-1].nast += entry.isAssistive
            teams[len(teams)-1].matches.append(entry.match)
            teams[len(teams)-1].BrdgBalType.append(entry.BrdgType)
            if (entry.BrdgType > 1) and (entry.BrdgType < 4): teams[len(teams)-1].BrdgBalnum.append(entry.NumBots)
            teams[len(teams)-1].Brdgscores.append(entry.brdgscore)
            teams[len(teams)-1].BrdgSucc += entry.brdgsuc
            teams[len(teams)-1].TeambrdgSucc += entry.teambrdgsuc
            teams[len(teams)-1].CoBrdgSucc += entry.CObrdgsuc
            teams[len(teams)-1].AttTeamBRDG += entry.AttteamBrdg
            teams[len(teams)-1].AttCoBRDG += entry.AttCOBrdg
            teams[len(teams)-1].hadhybd += entry.hasHybd
            teams[len(teams)-1].hadtele += entry.scrtele
            teams[len(teams)-1].disabled += entry.disable
            teams[len(teams)-1].avgRfoul.append(entry.RegF)
            teams[len(teams)-1].avgTechfoul.append(entry.TechF)
            teams[len(teams)-1].hadyellow += entry.yel
            teams[len(teams)-1].hadred += entry.red
            teams[len(teams)-1].hybdLwBrdg += entry.hybdlowrbrdg
            teams[len(teams)-1].hybdast += entry.hybdassist
            teams[len(teams)-1].hybdoth += entry.hybdother
            teams[len(teams)-1].hybdscored.append(entry.hybdscore)
            teams[len(teams)-1].Hbballs.append(entry.HLow)
            teams[len(teams)-1].Hmballs.append(entry.HMid)
            teams[len(teams)-1].Htballs.append(entry.HHigh)
            teams[len(teams)-1].ballscores.append(entry.ball)
            teams[len(teams)-1].telescores.append(entry.telescore)
            teams[len(teams)-1].Tbballs.append(entry.TLow)
            teams[len(teams)-1].Tmballs.append(entry.TMid)
            teams[len(teams)-1].Ttballs.append(entry.THigh)
            teams[len(teams)-1].ballsPU.append(entry.BallPU)
            teams[len(teams)-1].defense += entry.defensive
            teams[len(teams)-1].assist += entry.assistive
            teams[len(teams)-1].matchplay.append(entry.match)
            
    calculated = True
    # Get average Bridge Scores
    for team in teams:
        team.get_avg_Brdg()
    # Get average offensive scores
    for team in teams:
        team.get_avg_off()
    # Get match data
    for entry in entries:
        done = False
        for match in matches:
            if match.number == entry.match:
                match.teams.append(entry.team)
                if entry.color == 0:
                    match.all0.append(entry.team)
                    match.off0 += entry.thscore
                    match.noff0 += entry.isOffensive
                    match.defense0 += entry.defensive
                    match.assist0 += entry.assistive
                    match.TBrdgSucc0 += entry.teambrdgsuc
                    match.team0.append(entry.team)
                    if entry.isOffensive == 1:
                        for team in teams:
                            if team.number == entry.team:
                                match.thavgSum0 += team.avgthOff
                elif entry.color == 1:
                    match.all1.append(entry.team)
                    match.off1 += entry.thscore
                    match.noff1 += entry.isOffensive
                    match.defense1 += entry.defensive
                    match.assist1 += entry.assistive
                    match.TBrdgSucc1 += entry.teambrdgsuc
                    match.team1.append(entry.team)
                    if entry.isOffensive == 1:
                        for team in teams:
                            if team.number == entry.team:
                                match.thavgSum1 += team.avgthOff
                done = True
        if done == False:
            matches.append(Match(entry.match))
            print "Added match#" + str(entry.match)
            matches[len(matches)-1].teams.append(entry.team)
            if entry.color == 0:
                matches[len(matches)-1].all0.append(entry.team)
                matches[len(matches)-1].off0 += entry.thscore
                matches[len(matches)-1].noff0 += entry.isOffensive
                matches[len(matches)-1].defense0 += entry.defensive
                matches[len(matches)-1].assist0 += entry.assistive
                matches[len(matches)-1].TBrdgSucc0 += entry.teambrdgsuc
                matches[len(matches)-1].team0.append(entry.team)
                if entry.isOffensive == 1:
                    for team in teams:
                        if team.number == entry.team:
                            matches[len(matches)-1].thavgSum0 += team.avgthOff
            elif entry.color == 1:
                matches[len(matches)-1].all1.append(entry.team)
                matches[len(matches)-1].off1 += entry.thscore
                matches[len(matches)-1].noff1 += entry.isOffensive
                matches[len(matches)-1].defense1 += entry.defensive
                matches[len(matches)-1].assist1 += entry.assistive
                matches[len(matches)-1].TBrdgSucc1 += entry.teambrdgsuc
                matches[len(matches)-1].team1.append(entry.team)
                if entry.isOffensive == 1:
                    for team in teams:
                        if team.number == entry.team:
                            matches[len(matches)-1].thavgSum1 += team.avgthOff
    # Get defensive scores for each entry
    for entry in entries:
        entry.defscore = 0
        entry.astscore = 0
        if (entry.isDefensive + entry.isAssistive) > 0:
            for match in matches:
                if match.number == entry.match:
                    if entry.color == 0:
                        thavgOff = match.thavgSum1
                        oppOff = match.off1
                        allAvgth = match.thavgSum0
                        allOff = match.off0
                        allDefense = match.defense0
                        allAssist = match.assist0
                    if entry.color == 1:
                        thavgOff = match.thavgSum0
                        oppOff = match.off0
                        allAvgth = match.thavgSum1
                        allOff = match.off1
                        allDefense = match.defense1
                        allAssist = match.assist1
            entry.secondary_sort(thavgOff,oppOff,allAvgth,allOff,allDefense,allAssist)
        entry.tertiary_sort()
    # Get average defensive scores
    for entry in entries:
        for team in teams:
            if team.number == entry.team:
                team.dscores.append(entry.defscore)
                team.ascores.append(entry.astscore)
    for team in teams:
        team.get_avg_defast()
    # Get match defensive scores
    for entry in entries:
        for match in matches:
            if entry.match == match.number:
                if entry.color == 0:
                    match.def0 += (entry.defscore)
                    match.ast0 += (entry.astscore)
                elif entry.color == 1:
                    match.def1 += (entry.defscore)
                    match.ast1 += (entry.astscore)
    # Get match total scores
    for match in matches:
        match.get_total()
    # Get match weighted scores
    overall_score = 0
    for match in matches:
        overall_score += match.overall
    # weight = (S[m]/(S[w]-S[l])) * S[t]
    for entry in entries:
        for match in matches:
            if entry.match == match.number:
                tempweight = 0
                if (match.total0-match.total1) != 0:
                    entry.wscore = ((match.total0 + match.total1)*entry.total)/100
                    entry.woscore = ((match.total0 + match.total1)*entry.offensiveScore)/100
                    entry.wdscore = ((match.total0 + match.total1)*entry.defscore)/100
                    entry.wascore = ((match.total0 + match.total1)*entry.astscore)/100
                else:
                    entry.wscore = ((match.total0 + match.total1)*entry.total)
                    entry.woscore = ((match.total0 + match.total1)*entry.offensiveScore)
                    entry.wdscore = ((match.total0 + match.total1)*entry.defscore)
                    entry.wascore = ((match.total0 + match.total1)*entry.astscore)
    # Get team average weighted and total scores
    for team in teams:
        counter = 0
        for entry in entries:
            if team.number == entry.team:
                counter += 1
                team.wscores.append(entry.wscore)
                team.tscores.append(entry.total)
                team.woscores.append(entry.woscore)
                team.wdscores.append(entry.wdscore)
                team.wascores.append(entry.wascore)
        team.avg_wscore = sum(team.wscores)/len(team.wscores)
        team.avg_tscore = sum(team.tscores)/len(team.tscores)
        # Only take average weighted score for matches in which the team particpated
        if len(team.woscores)>0:team.avg_woscore = sum(team.woscores)/len(team.woscores)
        else: team.avg_woscore = 0 #only b/c they are used in ranking
        if len(team.wdscores)>0:team.avg_wdscore = sum(team.wdscores)/len(team.wdscores)
        else: team.avg_wdscore = 0
        if len(team.wascores)>0:team.avg_wascore = sum(team.wascores)/len(team.wascores)
        else: team.avg_wascore = 0
        if team.hadhybd>0: team.avg_hybdscore = sum(team.hybdscored)/team.hadhybd
        else: team.avg_hybdscore = "N\A"
        team.avg_balls = sum(team.ballscores)/len(team.ballscores)
        team.avg_bottom = sum(team.Tbballs)/len(team.Tbballs)
        team.avg_middle = sum(team.Tmballs)/len(team.Tmballs)
        team.avg_top = sum(team.Ttballs)/len(team.Ttballs)


    global off_rank, def_rank, ast_rank, tot_rank, hyb_rank, tel_rank, brd_rank
    off_rank = []
    def_rank = []
    ast_rank = []
    tot_rank = []

    hyb_rank = []
    tel_rank = []
    brd_rank = []
    for team in teams:
        if team.noff>0: off_rank.append([team.avgOff,team.number])
        if team.ndef>0: def_rank.append([team.avgDef,team.number])
        if team.nast>0: ast_rank.append([team.avgAst,team.number])
        tot_rank.append([team.avg_tscore,team.number])

        if team.hadhybd>0: hyb_rank.append([team.avgHybd,team.number])
        if team.hadtele>0: tel_rank.append([team.avgTele,team.number,team.compBpuBscr])
        if team.BrdgSucc>0: brd_rank.append([team.avgBrdgscr,team.number])
    # sort them
    off_rank.sort(reverse=True)
    def_rank.sort(reverse=True)
    ast_rank.sort(reverse=True)
    tot_rank.sort(reverse=True)

    hyb_rank.sort(reverse=True)
    tel_rank.sort(reverse=True)
    brd_rank.sort(reverse=True)

    # add all teams to available teams list
    available_teams = []
    offr = 0
    defr = 0
    astr = 0
    totr = 0

    hybr = 0
    telr = 0
    brdr = 0
    for rank in off_rank:
        offr += 1
        for team in teams:
            if team.number == rank[1]: team.off_rank = offr
    for rank in def_rank:
        defr += 1
        for team in teams:
            if team.number == rank[1]: team.def_rank = defr
    for rank in ast_rank:
        astr += 1
        for team in teams:
            if team.number == rank[1]: team.ast_rank = astr
    for rank in tot_rank:
        totr += 1
        for team in teams:
            if team.number == rank[1]: team.tot_rank = totr
    for rank in hyb_rank:
        hybr += 1
        for team in teams:
            if team.number == rank[1]: team.hyb_rank = hybr
    for rank in tel_rank:
        telr += 1
        for team in teams:
            if team.number == rank[1]: team.tel_rank = telr
    for rank in brd_rank:
        brdr +=1
        for team in teams:
            if team.number == rank[1]: team.brd_rank = brdr
    for team in teams:
        available_teams.append(team.number)
    
    
#----------------------------------------------------------------------------------------------------
# Calculate Function - Calculates data for statistical analysis from data2.
#----------------------------------------------------------------------------------------------------        
def calculate2():
    global entries2
    global teams
    global calculated2
    for entry in entries2:
        done = False
        for team in teams:
            if team.number == entry.team:
                team.robotlen = entry.roblength
                team.robotwid = entry.robwidth
                team.robotheg = entry.robheigth
                team.robotwig = entry.robwieght
                if entry.clearance == 1: team.floorclear = "Yes"
                elif entry.clearance == 2: team.floorclear = "No"
                else: team.floorclear = "IDK"
                if entry.spacing == 1: team.wheelspace = "Yes"
                elif entry.spacing == 2: team.wheelspace = "No"
                else: team.wheelspace = "IDK"
                if entry.BrdgMech == 1: team.BridgeMechanics = "Yes"
                elif entry.BrdgMech == 2: team.BridgeMechanics = "No"
                else: team.BridgeMechanics = "IDK"
                if entry.SlideBrdg == 1: team.SldBridge = "No"
                elif entry.SlideBrdg== 2: team.SldBridge = "Yes"
                else: team.SldBridge = "IDK"
                if entry.balsensor == 1: team.ballsen = "Yes"
                elif entry.balsensor == 2: team.ballsen = "No"
                else: team.ballsen = "IDK"
                if entry.ShiftGear == 1: team.ShiftGear = "Yes"
                elif entry.ShiftGear == 2: team.ShiftGear = "No"
                else: team.ShiftGear = "IDK"
                if entry.DriSys == 1: team.DriveSystem = "Crab"
                elif entry.DriSys == 2: team.DriveSystem = "McCannon"
                elif entry.DriSys == 3: team.DriveSystem = "Swerve"
                elif entry.DriSys == 4: team.DriveSystem = "Tank"
                elif entry.DriSys == 5: team.DriveSystem = "Arcade"
                elif entry.DriSys == 6: team.DriveSystem = "Other"
                else: team.DriveSystem = "IDK"
                if entry.CenMass == 1: team.CenterMass = "Low"
                elif entry.CenMass == 2: team.CenterMass = "Middle"
                elif entry.CenMass == 3: team.CenterMass = "High"
                else: team.CenterMass = "IDK"
                if entry.Drive1 == 1: team.Driver1 = "Yes"
                elif entry.Drive1 == 2: team.Driver1 = "No"
                else: team.Driver1 = "IDK"
                if entry.exp1 < 0: team.experince1 = "IDK"
                else: team.experince1 = entry.exp1
                if entry.Drive2 == 1: team.Driver2 = "Yes"
                elif entry.Drive2 == 2: team.Driver2 = "No"
                else: team.Driver2 = "IDK"
                if entry.exp2 < 0: team.experince2 = "IDK"
                else: team.experince2 = entry.exp2
                if entry.Drive3 == 1: team.Driver3 = "Yes"
                elif entry.Drive3 == 2: team.Driver3 = "No"
                else: team.Driver3 = "IDK"
                if entry.exp3 < 0: team.experince3 = "IDK"
                else: team.experince3 = entry.exp3
                done == True
        if done == False:
            teams.append(Team(entry.team))
            print "Added team#" + str(entry.team)
            teams[len(teams)-1].robotlen = entry.roblength
            teams[len(teams)-1].robotwid = entry.robwidth
            teams[len(teams)-1].robotheg = entry.robheigth
            teams[len(teams)-1].robotwig = entry.robwieght
            if entry.clearance == 1: teams[len(teams)-1].floorclear = "Yes"
            elif entry.clearance == 2: teams[len(teams)-1].floorclear = "No"
            else: teams[len(teams)-1].floorclear = "IDK"
            if entry.spacing == 1: teams[len(teams)-1].wheelspace = "Yes"
            elif entry.spacing == 2: teams[len(teams)-1].wheelspace = "No"
            else: teams[len(teams)-1].wheelspace = "IDK"
            if entry.BrdgMech == 1: teams[len(teams)-1].BridgeMechanics = "Yes"
            elif entry.BrdgMech == 2: teams[len(teams)-1].BridgeMechanics = "No"
            else: teams[len(teams)-1].BridgeMechanics = "IDK"
            if entry.SlideBrdg == 1: teams[len(teams)-1].SldBridge = "Yes"
            elif entry.SlideBrdg == 2: teams[len(teams)-1].SldBridge = "No"
            else: teams[len(teams)-1].SldBridge = "IDK"
            if entry.balsensor == 1: teams[len(teams)-1].ballsen = "Yes"
            elif entry.balsensor == 2: teams[len(teams)-1].ballsen = "No"
            else: teams[len(teams)-1].ballsen = "IDK"
            if entry.ShiftGear == 1: teams[len(teams)-1].ShiftGear = "Yes"
            elif entry.ShiftGear == 2: teams[len(teams)-1].ShiftGear = "No"
            else: teams[len(teams)-1].ShiftGear = "IDK"
            if entry.DriSys == 1: teams[len(teams)-1].DriveSystem = "Crab"
            elif entry.DriSys == 2: teams[len(teams)-1].DriveSystem = "McCannon"
            elif entry.DriSys == 3: teams[len(teams)-1].DriveSystem = "Swerve"
            elif entry.DriSys == 4: teams[len(teams)-1].DriveSystem = "Tank"
            elif entry.DriSys == 5: teams[len(teams)-1].DriveSystem = "Arcade"
            elif entry.DriSys == 6: teams[len(teams)-1].DriveSystem = "Other"
            else: teams[len(teams)-1].DriveSystem = "IDK"
            if entry.CenMass == 1: teams[len(teams)-1].CenterMass = "Low"
            elif entry.CenMass == 2: teams[len(teams)-1].CenterMass = "Middle"
            elif entry.CenMass == 3: teams[len(teams)-1].CenterMass = "High"
            else: teams[len(teams)-1].CenterMass = "IDK"
            if entry.Drive1 == 1: teams[len(teams)-1].Driver1 = "Yes"
            elif entry.Drive1 == 2: teams[len(teams)-1].Driver1 = "No"
            else: teams[len(teams)-1].Driver1 = "IDK"
            if entry.exp1 < 0: teams[len(teams)-1].experience1 = "IDK"
            else: teams[len(teams)-1].experience1 = entry.exp1
            if entry.Drive2 == 1: teams[len(teams)-1].Driver2 = "Yes"
            elif entry.Drive2 == 2: teams[len(teams)-1].Driver2 = "No"
            else: teams[len(teams)-1].Driver2 = "IDK"
            if entry.exp2 < 0: teams[len(teams)-1].experience2 = "IDK"
            else: teams[len(teams)-1].experience2 = entry.exp2
            if entry.Drive3 == 1: teams[len(teams)-1].Driver3 = "Yes"
            elif entry.Drive3 == 2: teams[len(teams)-1].Driver3 = "No"
            else: teams[len(teams)-1].Driver3 = "IDK"
            if entry.exp3 < 0: teams[len(teams)-1].experience3 = "IDK"
            else: teams[len(teams)-1].experience3 = entry.exp3
    calculated2 = True 
                
            
    
#----------------------------------------------------------------------------------------------------
# Team Data Function
#   -- Allows the user to access data for specific teams
#----------------------------------------------------------------------------------------------------
def team_data():
    global teams
    global t2_tboxes
    global tabnum     # the number of the team currently being viewed
    global mpos
    global t2_update
    global t2_surface
    global teamdata
    #run = True
    # reference --------- pygame.draw.rect(screen,(0,0,0),(160,65,200,50),1)
    # Get the team numbers
    tnums = []
    for team in teams:
        tnums.append(team.number)
    tnums.sort()
    if len(tnums) > 0 and tabnum == 0:    #only for first time
        tnum = tnums[0]
    #else: tabnum = 0
    for textbox in t2_tboxes:
        if textbox.type == "tnum":
            if textbox.value is not None:
                try:
                    if int(textbox.value) == 0: textbox.value = tabnum #if value is 0, make it the current team number
                    elif int(textbox.value) != tabnum: #If the number has changed, then do updates
                        if int(textbox.value) in tnums:
                            tabnum = int(textbox.value)
                            t2_update = 1
                        else:
                            if len(tnums)>0: tabnum = tnums[0] #if the number is not found, reset to the first team in the list
                            else: tabnum = 0
                except:
                    #Not actually a number
                    print "Error: non-numerical characters inserted for team number"
            else: textbox.value = tabnum
            textbox.value = tabnum
    # Update values based on tabnum
        #-- start by getting team data from beginning
    if t2_update == 1:
        print "Update in tab 2 requested"
        teamdata = 0
        for team in teams:
            if team.number == tabnum: teamdata = team
        if teamdata != 0:
            for textbox in t2_tboxes:
                if textbox.type == "nmat": textbox.value = len(teamdata.matches)
                elif textbox.type == "poff": textbox.value = str(int(100*teamdata.noff/len(teamdata.matches))) + "%"
                elif textbox.type == "pdef": textbox.value = str(int(100*teamdata.ndef/len(teamdata.matches))) + "%"
                elif textbox.type == "past": textbox.value = str(int(100*teamdata.nast/len(teamdata.matches))) + "%"
                elif textbox.type == "aoff": textbox.value = teamdata.avgOff
                elif textbox.type == "adef": textbox.value = teamdata.avgDef
                elif textbox.type == "aast": textbox.value = teamdata.avgAst
                elif textbox.type == "atot": textbox.value = teamdata.avg_tscore
                elif textbox.type == "woff": textbox.value = teamdata.avg_woscore
                elif textbox.type == "wdef": textbox.value = teamdata.avg_wdscore
                elif textbox.type == "wast": textbox.value = teamdata.avg_wascore
                elif textbox.type == "hhyb": textbox.value = str(int(100*teamdata.hadhybd/len(teamdata.matches))) + "%"
                elif textbox.type == "hlbg": textbox.value = str(int(100*teamdata.hybdLwBrdg/len(teamdata.matches))) + "%"
                elif textbox.type == "hast": textbox.value = str(int(100*teamdata.hybdast/len(teamdata.matches))) + "%"
                elif textbox.type == "hoth": textbox.value = str(int(100*teamdata.hybdoth/len(teamdata.matches))) + "%"
                elif textbox.type == "ahyb": textbox.value = str(int(sum(teamdata.hybdscored)/len(teamdata.hybdscored)))
                elif textbox.type == "ahbt": textbox.value = str(int(sum(teamdata.Hbballs)/len(teamdata.Hbballs)))
                elif textbox.type == "ahmd": textbox.value = str(int(sum(teamdata.Hmballs)/len(teamdata.Hmballs)))
                elif textbox.type == "ahtp": textbox.value = str(int(sum(teamdata.Htballs)/len(teamdata.Htballs)))
                elif textbox.type == "wdis": textbox.value = str(int(100*teamdata.disabled/len(teamdata.matches)))+"%"
                elif textbox.type == "publ": textbox.value = str(int(sum(teamdata.ballsPU)/len(teamdata.ballsPU)))
                elif textbox.type == "abal": textbox.value = teamdata.avg_balls
                elif textbox.type == "abot": textbox.value = teamdata.avg_bottom
                elif textbox.type == "amid": textbox.value = teamdata.avg_middle
                elif textbox.type == "atop": textbox.value = teamdata.avg_top
                elif textbox.type == "bgbn":
                    if sum(teamdata.BrdgBalnum)>0: textbox.value = str(int(sum(teamdata.BrdgBalnum)/len(teamdata.BrdgBalnum)))
                    else: textbox.value = "None"
                elif textbox.type == "atbs": textbox.value = str(int(sum(teamdata.Brdgscores)/len(team.matches)))
                elif textbox.type == "abrb": textbox.value = str(int(100*teamdata.BrdgSucc/len(teamdata.matches))) + "%"
                elif textbox.type == "atbb": textbox.value = str(int(100*teamdata.TeambrdgSucc/len(teamdata.matches))) + "%"
                elif textbox.type == "acbb": textbox.value = str(int(100*teamdata.CoBrdgSucc/len(teamdata.matches))) + "%"
                elif textbox.type == "atba": textbox.value = str(int(100*teamdata.AttTeamBRDG/len(teamdata.matches))) + "%"
                elif textbox.type == "acba": textbox.value = str(int(100*teamdata.AttCoBRDG/len(teamdata.matches))) + "%"
                elif textbox.type == "hrfl": textbox.value = str(int(sum(teamdata.avgRfoul)/len(teamdata.avgRfoul))) # might also include percentage of matches fouls occur
                elif textbox.type == "htfl": textbox.value = str(int(sum(teamdata.avgTechfoul)/len(teamdata.avgTechfoul))) # might also include percentage of matches tech fouls occur
                elif textbox.type == "atdf": textbox.value = str(int(100*teamdata.defense/len(teamdata.matches))) + "%"
                elif textbox.type == "atas": textbox.value = str(int(100*teamdata.assist/len(teamdata.matches))) + "%"
                elif textbox.type == "ryel": textbox.value = str(int(100*teamdata.hadyellow/len(teamdata.matches))) + "%"
                elif textbox.type == "rred": textbox.value = str(int(100*teamdata.hadred/len(teamdata.matches))) + "%"
                elif textbox.type == "roff": textbox.value = str(teamdata.off_rank)
                elif textbox.type == "rdef": textbox.value = str(teamdata.def_rank)
                elif textbox.type == "rast": textbox.value = str(teamdata.ast_rank)
                elif textbox.type == "rtot": textbox.value = str(teamdata.tot_rank)
                elif textbox.type == "rhyb": textbox.value = str(teamdata.hyb_rank)
                elif textbox.type == "rtel": textbox.value = str(teamdata.tel_rank)
                elif textbox.type == "rbrd": textbox.value = str(teamdata.brd_rank)
                
    # Draw Them
    if t2_update == 1:
        t2_surface.fill(bgcolor)
        for textbox in t2_tboxes:
            textbox.draw(t2_surface)
        t2_update = 0
    screen.blit(t2_surface,(160,65))
    # See if a textbox needs to be drawn
    # -- This only occurs if the mouse is hovering over the textbox
    for tbox in t2_tboxes:
        x = tbox.x+tbox.cw+(.5*tbox.th)+160
        y = tbox.y+.5*tbox.th+65
        if x<=cmpos[0]<=x+tbox.w+.5*tbox.th \
            and y<=cmpos[1]<=y+tbox.size+.5*tbox.th-10 and teamdata != 0:
            if tbox.type=="aoff":
                # Get information for offensive score
                i = 0
                lx = []
                ly = []
                print teamdata.oscores
                while i <len(teamdata.oscores):
                    lx.append(i+1)
                    ly.append(teamdata.oscores[i])
                    i += 1
                display = lreg(lx,ly)
                display.get_ab()
                draw = display.get_image(300,300,(255,255,255),(0,0,0))
                screen.blit(draw,(x+tbox.w+.5*tbox.th,y+tbox.size+.5*tbox.th-10))
            elif tbox.type=="adef" and teamdata.ndef>0:
                # Get information for defensive score
                i = 0
                lx = []
                ly = []
                print teamdata.dscores
                while i <len(teamdata.dscores):
                    lx.append(i+1)
                    ly.append(teamdata.dscores[i])
                    i += 1
                display = lreg(lx,ly)
                display.get_ab()
                draw = display.get_image(300,300,(255,255,255),(0,0,0))
                screen.blit(draw,(x+tbox.w+.5*tbox.th,y+tbox.size+.5*tbox.th-10))
            elif tbox.type=="aast" and teamdata.nast>0:
                # Get information for assistive score
                i = 0
                lx = []
                ly = []
                print teamdata.ascores
                while i <len(teamdata.ascores):
                    lx.append(i+1)
                    ly.append(teamdata.ascores[i])
                    i += 1
                display = lreg(lx,ly)
                display.get_ab()
                draw = display.get_image(300,300,(255,255,255),(0,0,0))
                screen.blit(draw,(x+tbox.w+.5*tbox.th,y+tbox.size+.5*tbox.th-10))
            elif tbox.type=="atot" and teamdata.ndef+teamdata.noff+teamdata.nast>0:
                # Get information for total score
                i = 0
                lx = []
                ly = []
                print teamdata.tscores
                while i <len(teamdata.tscores):
                    lx.append(i+1)
                    ly.append(teamdata.tscores[i])
                    i += 1
                display = lreg(lx,ly)
                display.get_ab()
                draw = display.get_image(300,300,(255,255,255),(0,0,0))
                screen.blit(draw,(x+tbox.w+.5*tbox.th,y+tbox.size+.5*tbox.th-10))
                                    
    # See if any changes are requested from clicks
    for textbox in t2_tboxes:
        x = textbox.x+textbox.cw+textbox.th+160
        y = textbox.y+.5*textbox.th+65
        if x+textbox.w+.5*textbox.th>=mpos[0]>=x \
           and y+textbox.size+.5*textbox.th-10>=mpos[1]>=y:
           # click event
           textbox.clicked()


def team_pitdata():
    global teams
    global t7_tboxes
    global tabnum     # the number of the team currently being viewed
    global mpos
    global t7_update
    global t7_surface
    global teamdata
    tnums = []
    for team in teams:
        tnums.append(team.number)
    tnums.sort()
    if len(tnums) > 0 and tabnum == 0:    #only for first time
        tnum = tnums[0]
    for textbox in t7_tboxes:
        if textbox.type == "tnum":
            if textbox.value is not None:
                try:
                    if int(textbox.value) == 0: textbox.value = tabnum #if value is 0, make it the current team number
                    elif int(textbox.value) != tabnum: #If the number has changed, then do updates
                        if int(textbox.value) in tnums:
                            tabnum = int(textbox.value)
                            t7_update = 1
                        else:
                            if len(tnums)>0: tabnum = tnums[0] #if the number is not found, reset to the first team in the list
                            else: tabnum = 0
                except:
                    #Not actually a number
                    print "Error: non-numerical characters inserted for team number"
            else: textbox.value = tabnum
            textbox.value = tabnum
    if t7_update == 1:
        print "Update in tab 2 requested"
        teamdata = 0
        for team in teams:
            if team.number == tabnum: teamdata = team
        if teamdata != 0:
            for textbox in t7_tboxes:
                # textbox.type == "
                if textbox.type == "rbln": textbox.value = teamdata.robotlen
                elif textbox.type == "rbwd": textbox.value = teamdata.robotwid
                elif textbox.type == "rbhg": textbox.value = teamdata.robotheg
                elif textbox.type == "rbwg": textbox.value = teamdata.robotwig
                elif textbox.type == "frcr": textbox.value = teamdata.floorclear
                elif textbox.type == "wlsc": textbox.value = teamdata.wheelspace
                elif textbox.type == "bgmc": textbox.value = teamdata.BridgeMechanics
                elif textbox.type == "sdbg": textbox.value = teamdata.SldBridge
                elif textbox.type == "blsn": textbox.value = teamdata.ballsen
                elif textbox.type == "sggr": textbox.value = teamdata.ShiftGear
                elif textbox.type == "dvsy": textbox.value = teamdata.DriveSystem
                elif textbox.type == "cnms": textbox.value = teamdata.CenterMass
                elif textbox.type == "dri1": textbox.value = teamdata.Driver1
                elif textbox.type == "exp1": textbox.value = teamdata.experince1
                elif textbox.type == "dri2": textbox.value = teamdata.Driver2
                elif textbox.type == "exp2": textbox.value = teamdata.experince2
                elif textbox.type == "dri3": textbox.value = teamdata.Driver3
                elif textbox.type == "exp3": textbox.value = teamdata.experince3
    if t7_update == 1:
        t7_surface.fill(bgcolor)
        for textbox in t7_tboxes:
            textbox.draw(t7_surface)
        t7_update = 0
    screen.blit(t7_surface,(160,65))
    # linear regresssion/otherstuff
    for textbox in t7_tboxes:
        x = textbox.x+textbox.cw+textbox.th+160
        y = textbox.y+.5*textbox.th+65
        if x+textbox.w+.5*textbox.th>=mpos[0]>=x \
           and y+textbox.size+.5*textbox.th-10>=mpos[1]>=y:
           # click event
           textbox.clicked()
                
#----------------------------------------------------------------------------------------------------
# Ratings Functions
#   -- Delivers team ratings based upon user preferences
#----------------------------------------------------------------------------------------------------
def ratings():
    global teams
    global screen
    global HEIGHT
    global bgcolor
    global txcolor
    global t3_scrolls
    global t3_buttons
    global off_rank, def_rank, ast_rank, tot_rank
    run = False

    # Draw Average Offensive Score
    font = pygame.font.Font(None,20)
    text = font.render("Avg Offensive Score",True,txcolor,bgcolor)
    screen.blit(text,(160,65))
    # Draw Avg Off
    font = pygame.font.Font(None,20)
    x = 0
    y = 0
    n = 0
    t3_scrolls[0].surface.fill(bgcolor)
    for rank in off_rank:
        n += 1
        text = font.render("#"+str(n)+"--Team "+str(rank[1])+": " + str(rank[0]),True,txcolor,bgcolor)
        t3_scrolls[0].surface.blit(text,(x,y))
        y += 20
        for team in teams:
            if team.number == rank[1]: team.off_rank = n
    t3_scrolls[0].draw(screen)
    pygame.draw.line(screen,(0,0,0),(302,65),(302,HEIGHT),1)

    # Draw Average Defensive Score
    font = pygame.font.Font(None,20)
    text = font.render("Avg Defensive Score",True,txcolor,bgcolor)
    screen.blit(text,(305,65))
    # Draw Avg Def
    x = 0
    y = 0
    n=0
    t3_scrolls[1].surface.fill(bgcolor)
    for rank in def_rank:
        n += 1
        text = font.render("#"+str(n)+"--Team "+str(rank[1])+": " + str(rank[0]),True,txcolor,bgcolor)
        t3_scrolls[1].surface.blit(text,(x,y))
        y += 20
        for team in teams:
            if team.number == rank[1]: team.def_rank = n
    t3_scrolls[1].draw(screen)
    pygame.draw.line(screen,(0,0,0),(450,65),(460,HEIGHT),1)

    # Draw Average Assistive score
    font = pygame.font.Font(None,20)
    text = font.render("Avg Assistive Score",True,txcolor,bgcolor)
    screen.blit(text,(460,65))
    # Draw Avg Ast
    x = 0
    y = 0
    n=0
    t3_scrolls[2].surface.fill(bgcolor)
    for rank in ast_rank:
        n += 1
        text = font.render("#"+str(n)+"--Team "+str(rank[1])+": " + str(rank[0]),True,txcolor,bgcolor)
        t3_scrolls[2].surface.blit(text,(x,y))
        y += 20
        for team in teams:
            if team.number == rank[1]: team.ast_rank = n
    t3_scrolls[2].draw(screen)
    pygame.draw.line(screen,(0,0,0),(605,65),(605,HEIGHT),1)

    # Draw Average total score
    font = pygame.font.Font(None,20)
    text = font.render("Avg Total Score",True,txcolor,bgcolor)
    screen.blit(text,(607,65))
    x = 0
    y = 0
    n=0
    t3_scrolls[3].surface.fill(bgcolor)
    for rank in tot_rank:
        n += 1
        text = font.render("#"+str(n)+"--Team "+str(rank[1])+": " + str(rank[0]),True,txcolor,bgcolor)
        t3_scrolls[3].surface.blit(text,(x,y))
        y += 20
        for team in teams:
            if team.number == rank[1]: team.tot_rank = n
    t3_scrolls[3].draw(screen)
    # Draw Average Weighted Score
    #pygame.draw.line(sceen,(0,0,0),(600,65),(600,HEIGHT),1)
    #font = pygame.font.Font(None,20)
    #text = font.render("Avg Total Score(W)",True,txcolor,bgcolor)
    #screen.blit(text,(602,65))
    #team_wei = []   # Uses (avg_weighted,team_number) as the format
    #for team in teams:
    #    team_wei.append([team.avg_wscore,team.number])
    #team_wei.sort(reverse = True)
    #x = 602
    #y = 85
    #n=0
    #for rank in team_wei:
    #   n += 1
    #   text = font.render("#"+str(n)+"--Team "+str(rank[1])+": " + str(rank[0]),True,txcolor,bgcolor)
    #   screen.blit(text,(x,y))
    #   y += 20
    # Get Weighted Offensive Scores
    #pygame.draw.line(screen,(0,0,0),(740,65),(740,HEIGHT),1)
    #font = pygame.font.Font(None,20)
    #text = font.render("Avg Offensive Score(W)",True,txcolor,bgcolor)
    #screen.blit(text,(742,65))
    #team_weo = []
    #for team in teams:
    #    if team.noff > 0:
    #        team_weo.append([team.avg_woscore,team.number])
    #team_weo.sort(reverse = True)
    #x = 742
    #y = 85
    #n = 0
    #for rank in team_weo:
    #    n += 1
    #    text = font.render("#"+str(n)+"--Team "+str(rank[1])+": " + str(rank[0]),True,txcolor,bgcolor)
    #    screen.blit(text,(x,y))
    #    y += 20
    # Get Weighted Defensive Scores
    #pygame.draw.line(screen,(0,0,0),(910,65),(910,HEIGHT),1)
    #font = pygame.font.Font(None,20)
    #text = font.render("Avg Defensive Score(W)",True,txcolor,bgcolor)
    #screen.blit(text,(912,65))
    #team_wed = []
    #for team in teams:
    #    if team.ndef > 0:
    #        team_wed.append([team.avg_wdscore,team.number])
    #team_wed.sort(reverse = True)
    #x = 912
    #y = 85
    #n=0
    #for rank in team_wed:
    #    n += 1
    #    text = font.render("#"+str(n)+"--Team "+str(rank[1])+": " + str(rank[0]),True,txcolor,bgcolor)
    #    screen.blit(text,(x,y))
    #    y += 20
    for button in t3_buttons:
        button.draw(screen)
    for button in t3_buttons:
        if mbut[0] == 1:
            if button.x<=cmpos[0]<=button.x+button.w and button.y<=cmpos[1]<=button.y+button.h:
                if button.type == "ofup":
                    t3_scrolls[0].update(1)
                elif button.type == "ofdo":
                    t3_scrolls[0].update(0)
                elif button.type == "deup":
                    t3_scrolls[1].update(1)
                elif button.type == "dedo":
                    t3_scrolls[1].update(0)
                elif button.type == "atup":
                    t3_scrolls[2].update(1)
                elif button.type == "atdo":
                    t3_scrolls[2].update(0)
                elif button.type == "toup":
                    t3_scrolls[3].update(1)
                elif button.type == "todo":
                    t3_scrolls[3].update(0)

def ratings2():
    global teams
    global screen
    global HEIGHT
    global bgcolor
    global txcolor
    global t8_scrolls
    global t8_buttons
    global hyb_rank, tel_rank, brd_rank
    run = False

    # Draw Average hybrid Score
    font = pygame.font.Font(None,20)
    text = font.render("Avg Hybrid Score",True,txcolor,bgcolor)
    screen.blit(text,(160,65))
    # Draw Avg hyb
    font = pygame.font.Font(None,20)
    x = 0
    y = 0
    n = 0
    t8_scrolls[0].surface.fill(bgcolor)
    for rank in hyb_rank:
        n += 1
        text = font.render("#"+str(n)+"--Team "+str(rank[1])+": " + str(rank[0]),True,txcolor,bgcolor)
        t8_scrolls[0].surface.blit(text,(x,y))
        y += 20
        for team in teams:
            if team.number == rank[1]: team.hyd_rank = n
    t8_scrolls[0].draw(screen)
    pygame.draw.line(screen,(0,0,0),(302,65),(302,HEIGHT),1)
    
    # Draw Average Tele Score
    font = pygame.font.Font(None,20)
    text = font.render("Avg Tele Score",True,txcolor,bgcolor)
    screen.blit(text,(305,65))
    # Draw Avg Tel
    x = 0
    y = 0
    n=0
    t8_scrolls[1].surface.fill(bgcolor)
    for rank in tel_rank:
        n += 1
        text = font.render("#"+str(n)+"--Team "+str(rank[1])+": " + str(rank[0]),True,txcolor,bgcolor)
        t8_scrolls[1].surface.blit(text,(x,y))
        y += 20
        for team in teams:
            if team.number == rank[1]: team.yrl_rank = n
    t8_scrolls[1].draw(screen)
    pygame.draw.line(screen,(0,0,0),(450,65),(460,HEIGHT),1)

    # Draw Average Bridge score
    font = pygame.font.Font(None,20)
    text = font.render("Avg Bridge Score",True,txcolor,bgcolor)
    screen.blit(text,(460,65))
    # Draw Avg Ast
    x = 0
    y = 0
    n=0
    t8_scrolls[2].surface.fill(bgcolor)
    for rank in brd_rank:
        n += 1
        text = font.render("#"+str(n)+"--Team "+str(rank[1])+": " + str(rank[0]),True,txcolor,bgcolor)
        t8_scrolls[2].surface.blit(text,(x,y))
        y += 20
        for team in teams:
            if team.number == rank[1]: team.brd_rank = n
    t8_scrolls[2].draw(screen)
    pygame.draw.line(screen,(0,0,0),(605,65),(605,HEIGHT),1)

    for button in t3_buttons:
        button.draw(screen)
    for button in t3_buttons:
        if mbut[0] == 1:
            if button.x<=cmpos[0]<=button.x+button.w and button.y<=cmpos[1]<=button.y+button.h:
                if button.type == "hyup":
                    t3_scrolls[0].update(1)
                elif button.type == "hydo":
                    t3_scrolls[0].update(0)
                elif button.type == "teup":
                    t3_scrolls[1].update(1)
                elif button.type == "tedo":
                    t3_scrolls[1].update(0)
                elif button.type == "bgup":
                    t3_scrolls[2].update(1)
                elif button.type == "bgdo":
                    t3_scrolls[2].update(0)

    
#----------------------------------------------------------------------------------------------------
# Search
#---------------------------------------------------------------------------------------------------- 
def search():
    global screen
    global t4_stuff
    global tabnum
    global teams
    global mpos
    global t4_scroll
    global t4_tempbut
    global t4_temprad
    global team_list
    global t4_buttons
    global t4_update
    global old_list
    global tabnum
    global t2_tboxes
    global tab
    global wanted
    global update_wanted
    global t4_wscroll
    global t4_wbut
    global t4_wrad
    global t4_redraw
    global t4_wbmov
    global available_teams
    global t6_update

    # Add title text for each scroller
    font = pygame.font.Font(None,20)
    text = font.render(" Matches: ",True,txcolor,bgcolor)
    screen.blit(text,(510,65))
    text = font.render(" Alliance Wanted List: ",True,txcolor,bgcolor)
    screen.blit(text,(625,65))
    # Add tempbut and temprad to scroller image; only change if update needed
    if t4_update == 1 or t4_redraw == 1:
        t4_scroll.surface = pygame.Surface((180,2000)) # Reset surface
        t4_scroll.surface.fill(bgcolor)
        for b in t4_tempbut:
            b.draw(t4_scroll.surface)
        for r in t4_temprad:
            r.draw(t4_scroll.surface)
        t4_update = 0
    #Draw the scroller image
    t4_scroll.draw(screen)

    # Add wbut and wrad to wscroll image; only change if update needed
    if update_wanted:
        t4_wscroll.surface = pygame.Surface((180,2000)) # Reset surface
        t4_wscroll.surface.fill(bgcolor)
        for b in t4_wbut:
            b.draw(t4_wscroll.surface)
        for r in t4_wrad:
            r.draw(t4_wscroll.surface)
        for bu in t4_wbmov:
            bu.draw(t4_wscroll.surface)
        update_wanted = 0
    #Draw the scroller image
    t4_wscroll.draw(screen)

    #Draw buttons
    for but in t4_buttons:
        but.draw(screen)

    #Detect button clicks
    nx = mpos[0] - t4_wscroll.x
    ny = mpos[1] - t4_wscroll.y + t4_wscroll.currenty 
    for but in t4_wbmov:
        if but.x<=nx<=but.x+but.w and but.y<=ny<=but.y+but.h and \
           but.y+but.h<t4_scroll.currenty+t4_scroll.maxh and but.y>t4_scroll.currenty:
            number = ""
            t = ""
            counter = 0
            while counter < len(but.type):
                try:
                    int(but.type[counter]) #Only if it is a number will try continue
                    number += but.type[counter]
                except:
                    t += but.type[counter]
                counter += 1
            if t== "up": # move the rank of the team up; the rank of the team above it down
                for te in wanted:
                    if te[1][0] == int(number): # Is the team
                        rank = te[0]
                        print "Our rank was:" + str(rank)
                for te in wanted:
                    # First, move the rank of the other team down; prevents errors
                    if te[0] == rank+1: # Is the rank the team is a/b to replace
                        te[0] = rank
                for te in wanted:
                    if te[1][0] == int(number):
                        te[0] += 1
                        print "Our rank is now" + str(te[0])
                update_wanted = 1
            if t=="do":
                for te in wanted:
                    if te[1][0] == int(number): # Is the team
                        rank = te[0]
                        print "Our rank was:" + str(rank)
                for te in wanted:
                    # First, move the rank of the other team down; prevents errors
                    if te[0] == rank-1: # Is the rank the team is a/b to replace
                        te[0] = rank
                for te in wanted:
                    if te[1][0] == int(number):
                        te[0] -= 1
                        print "Our rank is now:" + str(te[0])
                update_wanted = 1
            
    for but in t4_buttons:
        if mbut[0] == 1:
            if but.x<=cmpos[0]<=but.x+but.w and but.y<=cmpos[1]<=but.y+but.h:
                if but.type == "tlup":
                    t4_scroll.update(1)
                elif but.type == "tldo":
                    t4_scroll.update(0)
                elif but.type == "wlup":
                    t4_wscroll.update(1)
                elif but.type == "wldo":
                    t4_wscroll.update(0)
    nx = mpos[0] - t4_scroll.x
    ny = mpos[1] - t4_scroll.y + t4_scroll.currenty
    for but in t4_tempbut:
        if but.x<=nx<=but.x+but.w and but.y<=ny<=but.y+but.h and but.y+but.h<t4_scroll.currenty+t4_scroll.maxh and but.y>t4_scroll.currenty:
            # Open team data in other tab
            for textbox in t2_tboxes:
                if textbox.type == "tnum":
                    textbox.value = but.type
            tabnum = int(but.type)
            tab = 2
    for rad in t4_temprad:
        if rad.flip:   #button to left:
            if rad.x+.75*rad.size>=nx>=rad.x+.25*rad.size and \
               rad.y+.75*rad.size>=ny>=rad.y+.25*rad.size: # Clicked
                if rad.check == 0: 
                    for t in team_list:
                        if t[0] == rad.teamnum: #Add team to wanted list
                            wanted.append([len(wanted)+1,t])
                            t6_update = 1
                    rad.click()
                    rad.draw(t4_scroll.surface)
                    update_wanted = 1
                    t4_redraw = 1
                else: # Already Selected; now, deselect and remove from wanted list
                    for t in team_list:
                        if t[0] == rad.teamnum:
                            i = 0
                            while i < len(wanted):
                                if wanted[i][1][0] == rad.teamnum:
                                    del wanted[i]
                                    i -= 1
                                i += 1
                    rad.click()
                    rad.draw(t4_scroll.surface)
                    update_wanted = 1
                    t4_redraw = 1
        else: #Button to right
            if rad.x+item.w+.75*rad.size>=nx>=rad.x+item.w+.25*rad.size and \
               rad.y+.75*rad.size>=ny>=rad.y+.25*rad.size:
                if rad.check == 0: 
                    for t in team_list:
                        if t[0] == rad.teamnum: #Add team to wanted list
                            wanted.append([len(wanted)+1,t])
                    rad.click()
                    rad.draw(t4_scroll.surface)
                    update_wanted = 1
                    t4_redraw = 1
                else: # Already Selected; now, deselct and remove from wanted list
                    for t in team_list:
                        if t[0] == rad.teamnum:
                            i = 0
                            while i < len(wanted):
                                if wanted[i][1][0] == rad.teamnum:
                                    del wanted[i]
                                    i -= 1
                                i += 1
                    rad.click()
                    rad.draw(t4_scroll.surface)
                    update_wanted = 1
                    t4_redraw = 1
    
    #click events
    for item in t4_stuff:   
        try:#uses this for radio buttons
            if item.flip:   #button to left:
                if item.x+.75*item.size>=mpos[0]>=item.x+.25*item.size and \
                   item.y+.75*item.size>=mpos[1]>=item.y+.25*item.size:
                    item.click()
            else:
                if item.x+item.w+.75*item.size>=mpos[0]>=item.x+item.w+.25*item.size and \
                   item.y+.75*item.size>=mpos[1]>=item.y+.25*item.size:
                    item.click()
        except:#uses this for textboxes
            # See if any changes are requested from clicks
            x = item.x+item.cw+item.th
            y = item.y+.5*item.th
            if x+item.w+.5*item.th>=mpos[0]>=x \
               and y+item.size+.5*item.th-10>=mpos[1]>=y:
               # click event
               item.clicked()
    #draw
    for item in t4_stuff:
        item.draw(screen)
    pygame.draw.line(screen,(0,0,0),(500,65),(500,HEIGHT),5)
    pygame.draw.line(screen,(0,0,0),(620,65),(620,HEIGHT),5)

    # Do Search
    old_list = []
    for t in team_list:
        old_list.append(t[0])
    old_list.sort()
    team_list = []
    for team in teams:
        team_list.append([team.number,team])
    if len(team_list) > 0:
        for item in t4_stuff:
            if item.type == "goff":     #greater than offensive score
                try:
                    i = 0
                    x = len(team_list)
                    while i < x:
                        if team_list[i][1].avgOff < int(item.value):
                            del team_list[i]
                            x = len(team_list)
                            i -= 1
                        i += 1
                except:
                    item.value = 0
            elif item.type == "gdef": #greater than defensive score
                try:
                    i = 0
                    x = len(team_list)
                    while i < x:
                        if team_list[i][1].avgDef < int(item.value):
                            del team_list[i]
                            x = len(team_list)
                            i -= 1
                        i += 1
                except:
                    item.value = 0
            elif item.type == "gast": #greater than assistive score
                try:
                    i = 0
                    x = len(team_list)
                    while i < x:
                        if team_list[i][1].avgAst < int(item.value):
                            del team_list[i]
                            x = len(team_list)
                            i -= 1
                        i += 1
                except:
                    item.value = 0
            elif item.type == "wo": #was offensive for at least 1 match
                try:
                    i = 0
                    x = len(team_list)
                    while i < x:
                        if team_list[i][i].noff<item.check:
                            del team_list[i]
                            x = len(team_list)
                            i -= 1
                        i += 1
                except:
                    item.value = 0
            elif item.type == "wd": #was defensive for at least 1 match
                try:
                    i = 0
                    x = len(team_list)
                    while i < x:
                        if team_list[i][1].ndef<item.check:
                            del team_list[i]
                            x = len(team_list)
                            i -= 1
                        i += 1
                except:
                    item.value = 0
            elif item.type == "wa": #was assistive for at least 1 match
                try:
                    i = 0
                    x = len(team_list)
                    while i < x:
                        if team_list[i][1].nast<item.check:
                            del team_list[i]
                            x = len(team_list)
                            i -= 1
                        i += 1
                except:
                    item.value = 0
            elif item.type == "hbsd": #scored in hybrid
                try:
                    i = 0
                    x = len(team_list)
                    while i < x:
                        if team_list[i][1].hadhybd<item.check:
                            del team_list[i]
                            x = len(team_list)
                            i -= 1
                        i += 1
                except:
                    item.value = 0
            elif item.type == "hylb": #lowered bridge in hybrid
                try:
                    i = 0
                    x = len(team_list)
                    while i < x:
                        if team_list[i][1].hybdLwBrdg<item.check:
                            del team_list[i]
                            x = len(team_list)
                            i -= 1
                        i += 1
                except:
                    item.value = 0
            elif item.type == "hyat": #assisted in hybrid
                try:
                    i = 0
                    x = len(team_list)
                    while i < x:
                        if team_list[i][1].hybdast<item.check:
                            del team_list[i]
                            x = len(team_list)
                            i -= 1
                        i += 1
                except:
                    item.value = 0
            elif item.type == "bdsc": #balaced a bridge successfully
                try:
                    i = 0
                    x = len(team_list)
                    while i < x:
                        if team_list[i][1].BrdgSucc<item.check:
                            del team_list[i]
                            x = len(team_list)
                            i -= 1
                        i += 1
                except:
                    item.value = 0
            elif item.type == "tbsc": #balanced the team bridge successfully
                try:
                    i = 0
                    x = len(team_list)
                    while i < x:
                        if team_list[i][1].TeambrdgSucc<item.check:
                            del team_list[i]
                            x = len(team_list)
                            i -= 1
                        i += 1
                except:
                    item.value = 0
            elif item.type == "cbsc": #balanced the Co-op bridge successfully
                try:
                    i = 0
                    x = len(team_list)
                    while i < x:
                        if team_list[i][1].CoBrdgSucc<item.check:
                            del team_list[i]
                            x = len(team_list)
                            i -= 1
                        i += 1
                except:
                    item.value = 0
            elif item.type == "disn": #never disabled
                try:
                    i = 0
                    x = len(team_list)
                    while i < x:
                        if item.check == 1 and team_list[i][1].disabled > 0:
                            del team_list[i]
                            x = len(team_list)
                            i -= 1
                        i += 1
                except:
                    item.value = 0
            elif item.type == "nrfl": #never got a Regular foul
                try:
                    i = 0
                    x = len(team_list)
                    while i < x:
                        if item.check == 1 and team_list[i][1].hadRfoul > 0:
                            del team_list[i]
                            x = len(team_list)
                            i -= 1
                        i += 1
                except:
                    item.value = 0
            elif item.type == "ntfl": #never got a Technical foul
                try:
                    i = 0
                    x = len(team_list)
                    while i < x:
                        if item.check == 1 and team_list[i][1].hadTfoul > 0:
                            del team_list[i]
                            x = len_list[i]
                            x = len(team_list)
                            i -= 1
                        i += 1
                except:
                    item.value = 0
            elif item.type == "noye": #no yellow cards
                try:
                    i = 0
                    x = len(team_list)
                    while i < x:
                        if item.check == 1 and team_list[i][1].hadyellow > 0:
                            del team_list[i]
                            x = len(team_list)
                            i -= 1
                        i += 1
                except:
                    item.value = 0
            elif item.type == "nore": #no red cards
                try:
                    i = 0
                    x = len(team_list)
                    while i < x:
                        if item.check == 1 and team_list[i][1].hadred > 0:
                            del team_list[i]
                            x = len(team_list)
                            i -= 1
                        i += 1
                except:
                    item.value = 0
    team_list.sort()
    nlist = []
    for t in team_list:
        nlist.append(t[0])
    nlist.sort()
    if nlist != old_list:
        t4_update = 1

    # Deal with the wanted scroller(t4_wscroll)
    if update_wanted:
        t4_wbut = []
        #t4_wrad = []
        t4_wbmov = []
        y = 5
        wanted.sort()
        n = 0
        if len(wanted)>0:
            while n < len(wanted):
                n += 1
                wanted[n-1][0] = n
        for t in wanted:
            t4_wbut.append(button(x=0,y=y,thickness=1,text=str(t[1][0]),font=30,w=50,t=str(t[1][0])))
            #t4_wrad.append(radio(x=55,y=y,caption=[],flip=1,t=str(t[1][0]),fs=30,teamnum=t[1][0]))
            t4_wbmov.append(button(x=55,y=y,thickness=1,text="<",font=30,w=30,t=str(t[1][0])+"up"))
            t4_wbmov.append(button(x=80,y=y,thickness=1,text="  >",font=30,w=30,t=str(t[1][0])+"do"))
            y += 30    
#----------------------------------------------------------------------------------------------------
# Compare Alliance Function
#   - Given two alliances, tells who is more likely to win
#     and why.
# x=160,y = 145
#---------------------------------------------------------------------------------------------------- 
def compare():
    global t5_surface
    global t5_update
    global teams
    #only changed locally
    global r1, r2, r3, b1, b2, b3
    global r1o,r1d,r1a,r1bb,r1tb,r1bs,r1ab,r1bo,r1md,r1tp,r1hh,r1hs,r1po,r1pd,r1pa,  r2o,r2d,r2a,r2bb,r2tb,r2bs,r2ab,r2bo,r2md,r2tp,r2hh,r2hs,r2po,r2pd,b2pa,    r3o,r3d,r3a,r3bb,r3tb,r3bs,r3ab,r3bo,r3md,r3tp,r3hh,r3hs,r3po,r3pd,b3pa
    global b1o,b1d,b1a,b1bb,b1tb,b1bs,b1ab,b1bo,b1md,b1tp,b1hh,b1hs,b1po,b1pd,b1pa,  b2o,b2d,b2a,b2bb,b2tb,b2bs,b2ab,b2bo,b2md,b2tp,b2hh,b2hs,b2po,b2pd,b2pa,    b3o,b3d,b3a,b3bb,b3tb,b3bs,b3ab,b3bo,b3md,b3tp,b3hh,b3hs,b3po,b3pd,b3pa
    global r1po,r2po,r3po,b1po,b2po,b3po,r1pd,r2pd,r3pd,b1pd,b2pd,b3pd,r1pa,r2pa,r3pa,b1pa,b2pa,b3pa
    global r1t, r2t,r3t,b1t,b2t,b3t
    global r1ts, r2ts, r3ts, b1ts, b2ts, b3ts
#r1o = r1d = r1bb = r1tb = r1bs = r1ab = r1bo = r1md = r1tp = r1hh = r1hs = r1po = r1pd = 0
    #Draw the surface
    if t5_update:
        t5_surface.fill((bgcolor)) # Clear out old stuff
        font = pygame.font.Font(None,30)
        text = font.render(" Red Alliance: ",True,txcolor,bgcolor)
        t5_surface.blit(text,(0,70))
        text = font.render("Blue Alliance: ",True,txcolor,bgcolor)
        t5_surface.blit(text,(0,220))
        font = pygame.font.Font(None,12)
        text = font.render("Team",True,txcolor,bgcolor)
        t5_surface.blit(text,(140,20))
        text = font.render("Offensive",True,txcolor,bgcolor)
        t5_surface.blit(text,(175,20))
        text = font.render("Defensive",True,txcolor,bgcolor)
        t5_surface.blit(text,(215,20))
        text = font.render("Assistive",True,txcolor,bgcolor)
        t5_surface.blit(text,(255,20))
        text = font.render("%BrdgBaln",True,txcolor,bgcolor)
        t5_surface.blit(text,(305,20))
        text = font.render("%TeamBaln",True,txcolor,bgcolor)
        t5_surface.blit(text,(365,20))
        text= font.render("BrdgScore",True,txcolor,bgcolor)
        t5_surface.blit(text,(430,20))
        text = font.render("AvgBallScore",True,txcolor,bgcolor)
        t5_surface.blit(text,(500,20))
        text = font.render("AvgBallBottom",True,txcolor,bgcolor)
        t5_surface.blit(text,(570,20))
        text = font.render("AvgBallMiddle",True,txcolor,bgcolor)
        t5_surface.blit(text,(630,20))
        text = font.render("AvgBallTop",True,txcolor,bgcolor)
        t5_surface.blit(text,(690,20))
        text = font.render("%HadHybd",True,txcolor,bgcolor)
        t5_surface.blit(text,(750,20))
        text = font.render("AvgHybdScore",True,txcolor,bgcolor)
        t5_surface.blit(text,(810,20))
        for textbox in t5_tboxes:
            textbox.draw(t5_surface)
        # if three teams on an alliance are selected, show their expected values
        if r1!=0 and r2!=0 and r3!=0:
            font = pygame.font.Font(None,20)
            text = font.render("Expected Offensive Score:" + str((r1o*r1po)+(r2o*r2po)+(r3o*r3po)),
                               True,txcolor,bgcolor)
            t5_surface.blit(text,(100,130))
            text = font.render("Expected Defensive Score:" + str((r1d*r1pd)+(r2d*r2pd)+(r3d*r3pd)),
                               True,txcolor,bgcolor)
            t5_surface.blit(text,(100,150))
            text= font.render("Expected Assistive Score:" + str((r1a*r1pa)+(r2a*r2pa)+(r3a*r3pa)),
                              True,txcolor,bgcolor)
            t5_surface.blit(text,(100,170))
        if b1!=0 and b2!=0 and b3!=0:
            font = pygame.font.Font(None,20)
            text = font.render("Expected Offensive Score:" + str((b1o*b1po)+(b2o*b2po)+(b3o*b3po)),
                               True,txcolor,bgcolor)
            t5_surface.blit(text,(100,300))
            text = font.render("Expected Defensive Score:" + str((b1d*b1pd)+(b2d*b2pd)+(b3d*b3pd)),
                               True,txcolor,bgcolor)
            t5_surface.blit(text,(100,320))
            text = font.render("Expected Assistive Score:" + str((b1a*b1pa)+(b2a*b2pa)+(b3a*b3pa)),
                               True,txcolor,bgcolor)
            t5_surface.blit(text,(100,340))
        if r1!=0 and r2!=0 and r3!=0 and b1!=0 and b2!=0 and b3!=0:
            # get standard deviations
            print "Calculating Probability"
            dr1 = [] #Differences from mean squared
            dr2 = []
            dr3 = []
            db1 = []
            db2 = []
            db3 = []
            for score in r1ts:
                dr1.append(((score-r1t)**2)/len(r1ts))
            for score in r2ts:
                dr2.append(((score-r2t)**2)/len(r2ts))
            for score in r3ts:
                dr3.append(((score-r3t)**2)/len(r3ts))
            for score in b1ts:
                db1.append(((score-b1t)**2)/len(b1ts))
            for score in b2ts:
                db2.append(((score-b2t)**2)/len(b2ts))
            for score in b3ts:
                db3.append(((score-b3t)**2)/len(b3ts))
            r1st = math.sqrt(sum(dr1))
            r2st = math.sqrt(sum(dr2))
            r3st = math.sqrt(sum(dr3))
            b1st = math.sqrt(sum(db1))
            b2st = math.sqrt(sum(db2))
            b3st = math.sqrt(sum(db3))
            mur = (float(1)/3)*(r1t+r2t+r3t)
            mub = (float(1)/3)*(b1t+b2t+b3t)
            rst = math.sqrt((float(1)/9)*(r1st**2+r2st**2+r3st**2))
            bst = math.sqrt((float(1)/9)*(b1st**2+b2st**2+b3st**2))
            if mur > mub:
                zval = (mur-mub)/math.sqrt(rst**2+bst**2)
                perr = stats.lzprob(zval)
                font = pygame.font.Font(None,30)
                text = font.render("Winner: Red Alliance, " + str(100*perr) + "%",True,
                                   txcolor,bgcolor)
                t5_surface.blit(text,(100,400))
            else:
                zval = (mub-mur)/math.sqrt(rst**2+bst**2)
                perr = stats.lzprob(zval)
                font = pygame.font.Font(None,30)
                text = font.render("Winner: Blue Alliance, " + str(100*1-perr) + "%",True,
                                   txcolor,bgcolor)
                t5_surface.blit(text,(100,400))
            
        t5_update = 0
   # Draw the main surface
    screen.blit(t5_surface,(160,65))
    

    #Check for changes
    for item in t5_tboxes:
        x = item.x+item.cw+item.th+160
        y = item.y+.5*item.th+65
        if x+item.w+.5*item.th>=mpos[0]>=x \
            and y+item.size+.5*item.th-10>=mpos[1]>=y:
            # click event
            item.clicked()
            exists = 0
            for team in teams:
                if str(team.number) == str(item.value): # Team exists
                    exists = 1
                    if item.type == "rtn1": r1 = item.value
                    if item.type == "rtn2": r2 = item.value
                    if item.type == "rtn3": r3 = item.value
                    if item.type == "btn1": b1 = item.value
                    if item.type == "btn2": b2 = item.value
                    if item.type == "btn3": b3 = item.value
            if exists != 1: item.value = 0
            t5_update = 1
    # Get the team names
    r1 = 0
    r2 = 0
    r3 = 0
    b1 = 0
    b2 = 0
    b3 = 0
    for tbox in t5_tboxes:
        if tbox.type == "rt1n":
            try:
                r1 = int(tbox.value)
            except:
                "Invalid value"
        elif tbox.type == "rt2n":
            try:
                r2 = int(tbox.value)
            except:
                "Invalid value"
        elif tbox.type == "rt3n":
            try:
                r3 = int(tbox.value)
            except:
                "Invalid value"
        elif tbox.type == "bt1n":
            try:
                b1 = int(tbox.value)
            except:
                "Invalid value"
        elif tbox.type == "bt2n":
            try:
                b2 = int(tbox.value)
            except:
                "Invalid value"
        elif tbox.type == "bt3n":
            try:
                b3 = int(tbox.value)
            except:
                "Invalid value"
    
    #reset variables
    #r1o = r1d = r1bb = r1tb = r1bs = r1ab = r1bo = r1md = r1tp = r1hh = r1hs = r1po = r1pd = 0
    #r2o = r2d = r2mc = r2mr = r2at = r2ba = r2tb = r2tm = r2tt = r2pl = r2po = r2pd = 0
    #r3o = r3d = r3mc = r3mr = r3at = r3ba = r3tb = r3tm = r3tt = r3pl = r3po = r3pd = 0
    #b1o = b1d = b1mc = b1mr = b1at = b1ba = b1tb = b1tm = b1tt = b1pl = b1po = b1pd = 0
    #b2o = b2d = b2mc = b2mr = b2at = b2ba = b2tb = b2tm = b2tt = b2pl = b2po = b2pd = 0
    #b3o = b3d = b3mc = b3mr = b3at = b3ba = b3tb = b3tm = b3tt = b3pl = b3po = b3pd = 0

    # Set variables based upon team number input
    #for team in teams:
    #    if team.number == r1:
    #        r1o = round(team.avgOff,1)
    #        r1d = round(team.avgDef,1)
    #        r1a = round(team.avgAst,1)
    #        r1bb = int(100*team.BrdgSucc/len(team.matches))
    #        r1tb = int(100*team.TeambrdgSucc/len(team.matches))
    #        if team.TeambrdgSucc>0:  r1bs = int(sum(team.Brdgscores)/len(team.Brdgscores))
	#    else: r1bs = "N\A"
    #        #r1bs = int(sum(team.Brdgscores)/len(team.Brdgscores))
	#    r1ab = round(team.avg_balls,1)
	 #   r1bo = round(team.avg_bottom,1)
	  #  r1md = round(team.avg_middle,1)
	  #  r1tp = round(team.avg_top,1)
	  #  r1hh = int(100*team.hadhybd/len(team.matches))
   #         r1hs = round(float(sum(team.hybdscored)/len(team.hybdscored)),2)
   #         r1po = round(float(team.noff)/len(team.matches),2)
   #         r1pd = round(float(team.ndef)/len(team.matches),2)
   #         r1pa = round(float(team.nast)/len(team.matches),2)
   #         r1t = round(float(sum(team.tscores))/len(team.tscores),2)
   #         r1ts = team.tscores
   #     elif team.number == r2:
   #         r2o = round(team.avgOff,1)
   #         r2d = round(team.avgDef,1)
   #         r2a = round(team.avgAst,1)
   #         r2bb = int(100*team.BrdgSucc/len(team.matches))
   #         r2tb = int(100*team.TeambrdgSucc/len(team.matches))
   #         if team.TeambrdgSucc>0:  r2bs = int(sum(team.Brdgscores)/len(team.Brdgscores))
	  #  else: r2bs = "N\A"
	  #  r2ab = round(team.avg_balls,1)
	  #  r2bo = round(team.avg_bottom,1)
	  #  r2md = round(team.avg_middle,1)
	  #  r2tp = round(team.avg_top,1)
	  #  r2hh = int(100*team.hadhybd/len(team.matches))
   #         r2hs = round(float(sum(team.hybdscored)/len(team.hybdscored)),2)
   #         r2po = round(float(team.noff)/len(team.matches),2)
   #         r2pd = round(float(team.ndef)/len(team.matches),2)
   #         r2pa = round(float(team.nast)/len(team.matches),2)
   #         r2t = round(float(sum(team.tscores))/len(team.tscores),2)
   #         r2ts = team.tscores
   #     elif team.number == r3:
   #         r3o = round(team.avgOff,1)
   #         r3d = round(team.avgDef,1)
   #         r3a = round(team.avgAst,1)
   #         r3bb = int(100*team.BrdgSucc/len(team.matches))
   #         r3tb = int(100*team.TeambrdgSucc/len(team.matches))
   #         if team.TeambrdgSucc>0:  r3bs = int(sum(team.Brdgscores)/len(team.Brdgscores))
	  #  else: r3bs = "N\A"
	  #  r3ab = round(team.avg_balls,1)
	  #  r3bo = round(team.avg_bottom,1)
	  #  r3md = round(team.avg_middle,1)
	  #  r3tp = round(team.avg_top,1)
	  #  r3hh = int(100*team.hadhybd/len(team.matches))
   #         r3hs = round(float(sum(team.hybdscored)/len(team.hybdscored)),2)
   #         r3po = round(float(team.noff)/len(team.matches),2)
   #         r3pd = round(float(team.ndef)/len(team.matches),2)
   #         r3pa = round(float(team.nast)/len(team.matches),2)
   #         r3t = round(float(sum(team.tscores))/len(team.tscores),2)
   #         r3ts = team.tscores
   #     elif team.number == b1:
   #         b1o = round(team.avgOff,1)
   #         b1d = round(team.avgDef,1)
   #         b1a = round(team.avgAst,1)
   #         b1bb = int(100*team.BrdgSucc/len(team.matches))
   #         b1tb = int(100*team.TeambrdgSucc/len(team.matches))
   #         if team.TeambrdgSucc>0:  b1bs = int(sum(team.Brdgscores)/len(team.Brdgscores))
	  #  else: b1bs = "N\A"
	  #  b1ab = round(team.avg_balls,1)
	  #  b1bo = round(team.avg_bottom,1)
	  #  b1md = round(team.avg_middle,1)
	  #  b1tp = round(team.avg_top,1)
	  #  b1hh = int(100*team.hadhybd/len(team.matches))
   #         b1hs = round(float(sum(team.hybdscored)/len(team.hybdscored)),2)
   #         b1po = round(float(team.noff)/len(team.matches),2)
   #         b1pd = round(float(team.ndef)/len(team.matches),2)
   #         b1pa = round(float(team.nast)/len(team.matches),2)
   #         b1t = round(float(sum(team.tscores))/len(team.tscores),2)
   #         b1ts = team.tscores
   #     elif team.number == b2:
   #         b2o = round(team.avgOff,1)
   #         b2d = round(team.avgDef,1)
   #         b2a = round(team.avgAst,1)
   #         b2bb = int(100*team.BrdgSucc/len(team.matches))
   #         b2tb = int(100*team.TeambrdgSucc/len(team.matches))
   #         if team.TeambrdgSucc>0:  b2bs = int(sum(team.Brdgscores)/len(team.Brdgscores))
	  #  else: b2bs = "N\A"
	  #  b2ab = round(team.avg_balls,1)
	  #  b2bo = round(team.avg_bottom,1)
	  #  b2md = round(team.avg_middle,1)
	  #  b2tp = round(team.avg_top,1)
	  #  b2hh = int(100*team.hadhybd/len(team.matches))
    #        b2hs = round(float(sum(team.hybdscored)/len(team.hybdscored)),2)
    #        b2po = round(float(team.noff)/len(team.matches),2)
    #        b2pd = round(float(team.ndef)/len(team.matches),2)
    #        b2pa = round(float(team.nast)/len(team.matches),2)
    #        b2t = round(float(sum(team.tscores))/len(team.tscores),2)
    #        b2ts = team.tscores
    #    elif team.number == b3:
    #        b3o = round(team.avgOff,1)
    #        b3d = round(team.avgDef,1)
    #        b3a = round(team.avgAst,1)
    #        b3bb = int(100*team.BrdgSucc/len(team.matches))
    #        b3tb = int(100*team.TeambrdgSucc/len(team.matches))
    #        if team.TeambrdgSucc>0:  b3bs = int(sum(team.Brdgscores)/len(team.Brdgscores))
	   # else: b3bs = "N\A"
	   # b3ab = round(team.avg_balls,1)
	   # b3bo = round(team.avg_bottom,1)
	   # b3md = round(team.avg_middle,1)
	   # b3tp = round(team.avg_top,1)
	   # b3hh = int(100*team.hadhybd/len(team.matches))
    #        b3hs = round(float(sum(team.hybdscored)/len(team.hybdscored)),2)
    #        b3po = round(float(team.noff)/len(team.matches),2)
    #        b3pd = round(float(team.ndef)/len(team.matches),2)
    #        b3pa = round(float(team.nast)/len(team.matches),2)
    #        b3t = round(float(sum(team.tscores))/len(team.tscores),2)
    #        b3ts = team.tscores
		
    for tbox in t5_tboxes:
        if tbox.type == "rt1o": tbox.value = r1o
        elif tbox.type == "rt1d": tbox.value = r1d
        elif tbox.type == "rt1a": tbox.value = r1a
        elif tbox.type == "r1bb": tbox.value = r1bb
        elif tbox.type == "r1tb": tbox.value = r1tb
        elif tbox.type == "r1bs": tbox.value = r1bs
        elif tbox.type == "r1ab": tbox.value = r1ab
        elif tbox.type == "r1bo": tbox.value = r1bo
        elif tbox.type == "r1md": tbox.value = r1md
        elif tbox.type == "r1tp": tbox.value = r1tp
        elif tbox.type == "r1hh": tbox.value = r1hh
        elif tbox.type == "r1hs": tbox.value = r1hs
        
        elif tbox.type == "rt2o": tbox.value = r2o
        elif tbox.type == "rt2d": tbox.value = r2d
        elif tbox.type == "rt2a": tbox.value = r2a
        elif tbox.type == "r2bb": tbox.value = r2bb
        elif tbox.type == "r2tb": tbox.value = r2tb
        elif tbox.type == "r2bs": tbox.value = r2bs
        elif tbox.type == "r2ab": tbox.value = r2ab
        elif tbox.type == "r2bo": tbox.value = r2bo
        elif tbox.type == "r2md": tbox.value = r2md
        elif tbox.type == "r2tp": tbox.value = r2tp
        elif tbox.type == "r2hh": tbox.value = r2hh
        elif tbox.type == "r2hs": tbox.value = r2hs
        
        elif tbox.type == "rt3o": tbox.value = r3o
        elif tbox.type == "rt3d": tbox.value = r3d
        elif tbox.type == "rt3a": tbox.value = r3a
        elif tbox.type == "r3bb": tbox.value = r3bb
        elif tbox.type == "r3tb": tbox.value = r3tb
        elif tbox.type == "r3bs": tbox.value = r3bs
        elif tbox.type == "r3ab": tbox.value = r3ab
        elif tbox.type == "r3bo": tbox.value = r3bo
        elif tbox.type == "r3md": tbox.value = r3md
        elif tbox.type == "r3tp": tbox.value = r3tp
        elif tbox.type == "r3hh": tbox.value = r3hh
        elif tbox.type == "r3hs": tbox.value = r3hs

        elif tbox.type == "bt1o": tbox.value = b1o
        elif tbox.type == "bt1d": tbox.value = b1d
        elif tbox.type == "bt1a": tbox.value = b1a
        elif tbox.type == "b1bb": tbox.value = b1bb
        elif tbox.type == "b1tb": tbox.value = b1tb
        elif tbox.type == "b1bs": tbox.value = b1bs
        elif tbox.type == "b1ab": tbox.value = b1ab
        elif tbox.type == "b1bo": tbox.value = b1bo
        elif tbox.type == "b1md": tbox.value = b1md
        elif tbox.type == "b1tp": tbox.value = b1tp
        elif tbox.type == "b1hh": tbox.value = b1hh
        elif tbox.type == "b1hs": tbox.value = b1hs

        elif tbox.type == "bt2o": tbox.value = b2o
        elif tbox.type == "bt2d": tbox.value = b2d
        elif tbox.type == "bt2a": tbox.value = b2a
        elif tbox.type == "b2bb": tbox.value = b2bb
        elif tbox.type == "b2tb": tbox.value = b2tb
        elif tbox.type == "b2bs": tbox.value = b2bs
        elif tbox.type == "b2ab": tbox.value = b2ab
        elif tbox.type == "b2bo": tbox.value = b2bo
        elif tbox.type == "b2md": tbox.value = b2md
        elif tbox.type == "b2tp": tbox.value = b2tp
        elif tbox.type == "b2hh": tbox.value = b2hh
        elif tbox.type == "b2hs": tbox.value = b2hs

        elif tbox.type == "bt3o": tbox.value = b3o
        elif tbox.type == "bt3d": tbox.value = b3d
        elif tbox.type == "bt3a": tbox.value = b3a
        elif tbox.type == "b3bb": tbox.value = b3bb
        elif tbox.type == "b3tb": tbox.value = b3tb
        elif tbox.type == "b3bs": tbox.value = b3bs
        elif tbox.type == "b3ab": tbox.value = b3ab
        elif tbox.type == "b3bo": tbox.value = b3bo
        elif tbox.type == "b3md": tbox.value = b3md
        elif tbox.type == "b3tp": tbox.value = b3tp
        elif tbox.type == "b3hh": tbox.value = b3hh
        elif tbox.type == "b3hs": tbox.value = b3hs

#----------------------------------------------------------------------------------------------------
# Alliance Selection
#----------------------------------------------------------------------------------------------------
def alliance_selection():
    global available_teams
    global wanted
    global t6_scroll
    global t6_tboxes
    global t6_update
    global t6_surface
    global screen

    screen.blit(t6_surface,(160,65))
    # Draw the team numbers on the scroller
    if t6_update:
        t6_surface.fill(bgcolor)
        for tb in t6_tboxes:
            tb.draw(t6_surface)
        x = 0
        y = 5
        t6_scroll.surface.fill(bgcolor)
        draw_list = []
        for te in wanted:
            for tea in available_teams:
                if int(te[1][0]) == int(tea):
                    draw_list.append(tea)
        #print "Draw list: " + str(draw_list)
        font = pygame.font.Font(None,20)
        for tm in draw_list:
            text = font.render("Team "+str(tm)+"",True,txcolor,bgcolor)
            t6_scroll.surface.blit(text,(x,y))
            y += 30
        t6_scroll.draw(t6_surface)

        # Start coordinates: (160,65)
        x=0
        y=5
        n = 1
        font = pygame.font.Font(None,40)
        #text = font.render(" Matches: ",True,txcolor,bgcolor)
        #t6_surface.blit(text,(510,65))
        while n < 9:
            text = font.render(str(n)+":",True,txcolor,bgcolor)
            t6_surface.blit(text,(x,y))
            y += 40
            n += 1
        t6_update = 0

        # Draw the scroller buttons
        for but in t6_buttons:
            but.draw(t6_surface)

    # Scroller button click detection
    for but in t6_buttons:
        if mbut[0] == 1:
            if but.x<=cmpos[0]<=but.x+but.w and but.y<=cmpos[1]<=but.y+but.h:
                if but.type == "tlup":
                    t6_scroll.update(1)
                    t6_update = 1
                elif but.type == "tldo":
                   t6_scroll.update(0)
                   t6_update = 1

    # Textbox click detection (also, check to see if that team can be selected
    for tb in t6_tboxes:
        if tb.x+160<=mpos[0]<=tb.x+160+tb.w and tb.y+65<=mpos[1]<=tb.y+65+tb.size:
            tb.clicked()
            try: int(tb.value)
            except: tb.value = 0
            t6_update = 1
            n = 0
            while n < len(available_teams):
                if str(tb.value) == str(available_teams[n]):
                    del available_teams[n] # So this team can no longer be chosen
                    break
                n += 1
            #if in_there != 1: textbox.value = 0 # Commented out b/c a user error would require a restart of the database
        
#----------------------------------------------------------------------------------------------------
# Main Loop
#----------------------------------------------------------------------------------------------------
#Main  Buttons
tb_buttons.append(button(x=6,y=6,thickness=4,text="New",t="n"))
tb_buttons.append(button(x=81,y=6,thickness=4,text="Open",t="o"))
tb_buttons.append(button(x=176,y=6,thickness=4,text="Save",t="s"))
tb_buttons.append(button(x=263,y=6,thickness=4,text="Import Data",t="i"))
tb_buttons.append(button(x=457,y=6,thickness=4,text="Import Pit Data",t="ip"))
#tb_buttons.append(button(x=6,y=65,thickness=4,text="Matches",t="m"))
tb_buttons.append(button(x=6,y=100,thickness=4,text="  Teams  ",t="t"))
tb_buttons.append(button(x=6,y=135,thickness=4,text="  Pit  ",t="ps"))
tb_buttons.append(button(x=6,y=170,thickness=4,text="Ranking",t="r"))
tb_buttons.append(button(x=6,y=205,thickness=4,text="Rank2",t="r2"))
tb_buttons.append(button(x=6,y=240,thickness=4,text="Search  ",t="se"))
tb_buttons.append(button(x=6,y=275,thickness=4,text="Compare",t="co"))
tb_buttons.append(button(x=6,y=310,thickness=4,text=" Choose",t="ch"))
#tab2 text boxes *top left = 160,65
t2_tboxes.append(textbox(x=0,y=0,thickness=1,caption="Team:",t="tnum",clickable=1))
t2_tboxes.append(textbox(x=0,y=35,thickness=1,caption="Matches:",t="nmat",fs=25,w=40))
t2_tboxes.append(textbox(x=0,y=70,thickness=1,caption="Played Offensive:",t="poff",fs=25,w=40))
t2_tboxes.append(textbox(x=0,y=90,thickness=1,caption="Played Defensive:",t="pdef",fs=25,w=40))
t2_tboxes.append(textbox(x=0,y=110,thickness=1,caption="Played Assistive:",t="past",fs=25,w=40))
t2_tboxes.append(textbox(x=0,y=140,thickness=1,caption="Avg Offensive Score:",t="aoff",fs=25,w=40))
t2_tboxes.append(textbox(x=0,y=160,thickness=1,caption="Avg Defensive Score:",t="adef",fs=25,w=40))
t2_tboxes.append(textbox(x=0,y=180,thickness=1,caption="Avg Assistive Score:",t="aast",fs=25,w=40))
t2_tboxes.append(textbox(x=0,y=200,thickness=1,caption="Avg Total Score:",t="atot",fs=25,w=40))
#t2_tboxes.append(textbox(x=0,y=260,thickness=1,caption="Avg Weighted Off Score:",t="woff",fs=30,w=50))
#t2_tboxes.append(textbox(x=0,y=290,thickness=1,caption="Avg Weighted Def Score:",t="wdef",fs=30,w=50))
t2_tboxes.append(textbox(x=0,y=230,thickness=1,caption="Offensive Rank:",t="roff",fs=25,w=40))
t2_tboxes.append(textbox(x=0,y=250,thickness=1,caption="Defensive Rank:",t="rdef",fs=25,w=40))
t2_tboxes.append(textbox(x=0,y=270,thickness=1,caption="Assitive Rank:",t="rast",fs=25,w=40))
t2_tboxes.append(textbox(x=0,y=290,thickness=1,caption="Total Rank:",t="rtot",fs=25,w=40))
#other ranks


t2_tboxes.append(textbox(x=400,y=20,thickness=1,caption="Had Hybrid Mode:",t="hhyb",fs=25,w=40))                            
t2_tboxes.append(textbox(x=400,y=45,thickness=1,caption="Lowered Bridge in Hybrid:",t="hlbg",fs=25,w=40))
t2_tboxes.append(textbox(x=400,y=65,thickness=1,caption="Assisted in Hybrid:",t="hast",fs=25,w=40))
t2_tboxes.append(textbox(x=400,y=85,thickness=1,caption="Other Hybrid:",t="hoth",fs=25,w=40))
t2_tboxes.append(textbox(x=400,y=110,thickness=1,caption="Average Hybrid Score:",t="ahyb",fs=25,w=40))
t2_tboxes.append(textbox(x=400,y=130,thickness=1,caption="Average Hybrid Low Score:",t="ahbt",fs=25,w=40))
t2_tboxes.append(textbox(x=400,y=150,thickness=1,caption="Average Hybrid Middle Score:",t="ahmd",fs=25,w=40))
t2_tboxes.append(textbox(x=400,y=170,thickness=1,caption="AverageHybrid Top Score:",t="ahtp",fs=25,w=40))

t2_tboxes.append(textbox(x=400,y=225,thickness=1,caption="Was Disabled:",t="wdis",fs=25,w=40))
t2_tboxes.append(textbox(x=400,y=245,thickness=1,caption="Average balls picked up:",t="publ",fs=25,w=40))
t2_tboxes.append(textbox(x=400,y=265,thickness=1,caption="Average Balls Scored:",t="abal",fs=25,w=40))
t2_tboxes.append(textbox(x=400,y=285,thickness=1,caption="Average Scored on Bottom:",t="abot",fs=25,w=40))
t2_tboxes.append(textbox(x=400,y=305,thickness=1,caption="Average Scored on Middle:",t="amid",fs=25,w=40))
t2_tboxes.append(textbox(x=400,y=325,thickness=1,caption="Average Scored on Top:",t="atop",fs=25,w=40))

#t2_tboxes.append(textbox(x=500,y=400,thickness=1,caption="Helped Complete Logo:",t="hlog",fs=30,w=50))
t2_tboxes.append(textbox(x=400,y=360,thickness=1,caption="Average Number of bots balanced with:",t="bgbn",fs=24,w=40))
t2_tboxes.append(textbox(x=400,y=380,thickness=1,caption="Average Bridge Score(elim):",t="atbs",fs=25,w=40))
t2_tboxes.append(textbox(x=400,y=400,thickness=1,caption="Average Bridge Baln Suc:",t="abrb",fs=25,w=40))
t2_tboxes.append(textbox(x=400,y=420,thickness=1,caption="Average Team Brdg Baln Succ:",t="atbb",fs=25,w=40))
t2_tboxes.append(textbox(x=400,y=440,thickness=1,caption="Average Coop Brdg Baln Succ:",t="acbb",fs=25,w=40))
t2_tboxes.append(textbox(x=400,y=460,thickness=1,caption="Average Team Brdg Baln Atmp:",t="atba",fs=25,w=40))
t2_tboxes.append(textbox(x=400,y=480,thickness=1,caption="Average Coop Brdg Baln Atmp:",t="acba",fs=25,w=40))
t2_tboxes.append(textbox(x=400,y=510,thickness=1,caption="Robot Type:",t="rbty",fs=25,w=40))
t2_tboxes.append(textbox(x=0,y=450,thickness=1,caption="Average number of Fouls:",t="hrfl",fs=25,w=40))
t2_tboxes.append(textbox(x=0,y=470,thickness=1,caption="Average number of Tech Fouls:",t="htfl",fs=25,w=40))
t2_tboxes.append(textbox(x=0,y=490,thickness=1,caption="Defense:",t="atdf",fs=25,w=40))
t2_tboxes.append(textbox(x=0,y=510,thickness=1,caption="Assistive:",t="atas",fs=25,w=40))
t2_tboxes.append(textbox(x=0,y=530,thickness=1,caption="Received Yellow Card:",t="ryel",fs=25,w=40))
t2_tboxes.append(textbox(x=0,y=550,thickness=1,caption="Received Red Card:",t="rred",fs=25,w=40))
#tab4 stuff
t4_stuff.append(textbox(x=160,y=65,thickness=1,caption="Offensive Score >= ",clickable=1,val=-30,fs=30,w=50,t="goff"))
t4_stuff.append(textbox(x=160,y=95,thickness=1,caption="Defensive Score >= ",clickable=1,val=-30,fs=30,w=50,t="gdef"))
t4_stuff.append(textbox(x=160,y=125,thickness =1,caption="Assistive Score >= ",clickable=1,val=-30,fs=30,w=50,t="gast"))
t4_stuff.append(radio(x=160,y=155,fs=30,caption="Played Offensive",t="wo"))
t4_stuff.append(radio(x=160,y=185,fs=30,caption="Played Defensive",t="wd"))
t4_stuff.append(radio(x=160,y=215,fs=30,caption="Played Assistive",t="wa"))
t4_stuff.append(radio(x=160,y=245,fs=30,caption="Scored in Hybrid",t="hasd"))
t4_stuff.append(radio(x=160,y=275,fs=30,caption="Lowered Brdg in Hybrid",t="hylb"))
t4_stuff.append(radio(x=160,y=305,fs=30,caption="Assisted in Hybrid",t="hyat"))
t4_stuff.append(radio(x=160,y=335,fs=30,caption="Balanced a Bridge",t="bdsc"))
t4_stuff.append(radio(x=160,y=365,fs=30,caption="Balanced Team Bridge",t="tbsc"))
t4_stuff.append(radio(x=160,y=395,fs=30,caption="Balanced Coop Bridge",t="cbsc"))
t4_stuff.append(radio(x=160,y=425,fs=30,caption="Never Disabled",t="disn"))
t4_stuff.append(radio(x=160,y=455,fs=30,caption="No Regular Fouls",t="nrfl"))
t4_stuff.append(radio(x=160,y=485,fs=30,caption="No Technical Fouls",t="ntfl"))
t4_stuff.append(radio(x=160,y=515,fs=30,caption="No Yellow Cards",t="noye"))
t4_stuff.append(radio(x=160,y=545,fs=30,caption="No Red Cards",t="nore"))
#tab 4's scroller
t4_scroll = scroller(pygame.Surface((100,2000)),maxheight=400,x=510,y=105,t="")
t4_wscroll = scroller(pygame.Surface((110,2000)),maxheight=400,x=630,y=105,t="")
#tab 4 buttons
t4_buttons.append(button(x=510,y=84,thickness=1,text="",t="tlup",w=100,h=20))
t4_buttons.append(button(x=510,y=510,thickness=1,text="",t="tldo",w=100,h=20))
t4_buttons.append(button(x=630,y=84,thickness=1,text="",t="wlup",w=110,h=20))
t4_buttons.append(button(x=630,y=510,thickness=1,text="",t="wldo",w=110,h=20))

#tab3 stuff
t3_scrolls.append(scroller(pygame.Surface((143,2000)),maxheight=500,x=160,y=105,t="")) #Offensive Score Scroller
t3_buttons.append(button(x=160,y=85,thickness=1,text="",t="ofup",w=143,h=20)) #scroll offensive score up
t3_buttons.append(button(x=160,y=605,thickness=1,text="",t="ofdo",w=143,h=20)) #scroll offensive score down
t3_scrolls.append(scroller(pygame.Surface((143,2000)),maxheight=500,x=305,y=105,t="")) #Defensive Score Scroller
t3_buttons.append(button(x=305,y=85,thickness=1,text="",t="deup",w=143,h=20))#scroll defensive score up
t3_buttons.append(button(x=305,y=605,thickness=1,text="",t="dedo",w=143,h=20))#scroll defensive score down
t3_scrolls.append(scroller(pygame.Surface((143,2000)),maxheight=500,x=455,y=105,t="")) #Assistive Score Scroller
t3_buttons.append(button(x=455,y=85,thickness=1,text="",t="atup",w=143,h=20))#scroll assistive score up
t3_buttons.append(button(x=455,y=605,thickness=1,text="",t="atdo",w=143,h=20))#scroll assistive score down
t3_scrolls.append(scroller(pygame.Surface((143,2000)),maxheight=500,x=605,y=105,t="")) #Total Score Scroller
t3_buttons.append(button(x=605,y=85,thickness=1,text="",t="toup",w=143,h=20))#scroll total score up
t3_buttons.append(button(x=605,y=605,thickness=1,text="",t="todo",w=143,h=20))#scroll total score down

# Tab 5 stuff
t5_tboxes.append(textbox(x=140,y=40,thickness=1,caption="",clickable=1,fs=20,w=30,t="rt1n"))  #Red alliance, team 1's number
t5_tboxes.append(textbox(x=140,y=70,thickness=1,caption="",clickable=1,fs=20,w=30,t="rt2n"))  #Red alliamce, team 2's number
t5_tboxes.append(textbox(x=140,y=100,thickness=1,caption="",clickable=1,fs=20,w=30,t="rt3n")) #Red alliance, team 3's number
t5_tboxes.append(textbox(x=175,y=40,thickness=1,caption="",fs=20,w=50,t="rt1o"))    #Red alliance, team 1's offensive score
t5_tboxes.append(textbox(x=175,y=70,thickness=1,caption="",fs=20,w=50,t="rt2o"))    #Red alliance, team 2's offensive score
t5_tboxes.append(textbox(x=175,y=100,thickness=1,caption="",fs=20,w=50,t="rt3o"))   #Red alliance, team 3's offensive score
t5_tboxes.append(textbox(x=215,y=40,thickness=1,caption="",fs=20,w=50,t="rt1d"))    #Red alliance, team 1's defensive score
t5_tboxes.append(textbox(x=215,y=70,thickness=1,caption="",fs=20,w=50,t="rt2d"))    #Red alliance, team 2's defensive score
t5_tboxes.append(textbox(x=215,y=100,thickness=1,caption="",fs=20,w=50,t="rt3d"))   #Red alliance, team 3's defensive score
t5_tboxes.append(textbox(x=255,y=40,thickness=1,caption="",fs=20,w=50,t="rt1a"))    #Red alliance, team 1's assistive score
t5_tboxes.append(textbox(x=255,y=70,thickness=1,caption="",fs=20,w=50,t="rt2a"))    #Red alliance, team 2's assistive score
t5_tboxes.append(textbox(x=255,y=100,thickness=1,caption="",fs=20,w=50,t="rt3a"))   #Red alliance, team 3's assistive score
t5_tboxes.append(textbox(x=305,y=40,thickness=1,caption="",fs=20,w=50,t="r1bb"))    #Red alliance, team 1 balance bridge
t5_tboxes.append(textbox(x=305,y=70,thickness=1,caption="",fs=20,w=50,t="r2bb"))    #Red alliance, team 2 balance bridge
t5_tboxes.append(textbox(x=305,y=100,thickness=1,caption="",fs=20,w=50,t="r3bb"))   #Red alliance, team 3 balance bridge
t5_tboxes.append(textbox(x=365,y=40,thickness=1,caption="",fs=20,w=50,t="r1tb"))    #Red alliance, team 1 balance team bridge
t5_tboxes.append(textbox(x=365,y=70,thickness=1,caption="",fs=20,w=50,t="r2tb"))    #Red alliance, team 2 balance team bridge
t5_tboxes.append(textbox(x=365,y=100,thickness=1,caption="",fs=20,w=50,t="r3tb"))   #Red alliance, team 3 balance team bridge
t5_tboxes.append(textbox(x=430,y=40,thickness=1,caption="",fs=20,w=50,t="r1bs"))    #Red alliance, team 1 bridge score
t5_tboxes.append(textbox(x=430,y=70,thickness=1,caption="",fs=20,w=50,t="r2bs"))    #Red alliance, team 2 bridge score
t5_tboxes.append(textbox(x=430,y=100,thickness=1,caption="",fs=20,w=50,t="r3bs"))   #Red alliance, team 3 bridge score
t5_tboxes.append(textbox(x=500,y=40,thickness=1,caption="",fs=20,w=50,t="r1ab"))    #Red alliance, team 1 Average balls scored
t5_tboxes.append(textbox(x=500,y=70,thickness=1,caption="",fs=20,w=50,t="r2ab"))    #Red alliance, team 2 Average balls scored
t5_tboxes.append(textbox(x=500,y=100,thickness=1,caption="",fs=20,w=50,t="r3ab"))   #Red alliance, team 3 Average balls scored
t5_tboxes.append(textbox(x=570,y=40,thickness=1,caption="",fs=20,w=50,t="r1bo"))    #Red alliance, team 1 Average balls bottom
t5_tboxes.append(textbox(x=570,y=70,thickness=1,caption="",fs=20,w=50,t="r2bo"))    #Red alliance, team 2 Average balls bottom
t5_tboxes.append(textbox(x=570,y=100,thickness=1,caption="",fs=20,w=50,t="r3bo"))   #Red alliance, team 3 Average balls bottom
t5_tboxes.append(textbox(x=630,y=40,thickness=1,caption="",fs=20,w=50,t="r1md"))    #Red alliance, team 1 Average balls middle
t5_tboxes.append(textbox(x=630,y=70,thickness=1,caption="",fs=20,w=50,t="r2md"))    #Red alliance, team 2 Average balls middle
t5_tboxes.append(textbox(x=630,y=100,thickness=1,caption="",fs=20,w=50,t="r3md"))   #Red alliance, team 3 Average balls middle
t5_tboxes.append(textbox(x=690,y=40,thickness=1,caption="",fs=20,w=50,t="r1tp"))    #Red alliance, team 1 Average balls top
t5_tboxes.append(textbox(x=690,y=70,thickness=1,caption="",fs=20,w=50,t="r2tp"))    #Red alliance, team 2 Average balls top
t5_tboxes.append(textbox(x=690,y=100,thickness=1,caption="",fs=20,w=50,t="r3tp"))   #Red alliance, team 3 Average balls top
t5_tboxes.append(textbox(x=750,y=40,thickness=1,caption="",fs=20,w=50,t="r1hh"))    #Red alliance, team 1 had hybrid
t5_tboxes.append(textbox(x=750,y=70,thickness=1,caption="",fs=20,w=50,t="r2hh"))    #Red alliance, team 2 had hybrid
t5_tboxes.append(textbox(x=750,y=100,thickness=1,caption="",fs=20,w=50,t="r3hh"))   #Red alliance, team 3 had hybrid
t5_tboxes.append(textbox(x=810,y=40,thickness=1,caption="",fs=20,w=50,t="r1hs"))    #Red alliance, team 1 hybrid score
t5_tboxes.append(textbox(x=810,y=70,thickness=1,caption="",fs=20,w=50,t="r2hs"))    #Red alliance, team 2 hybrid score
t5_tboxes.append(textbox(x=810,y=100,thickness=1,caption="",fs=20,w=50,t="r3hs"))   #Red alliance, team 3 hybrid score
t5_tboxes.append(textbox(x=140,y=200,thickness=1,caption="",clickable=1,fs=20,w=30,t="bt1n")) #Blue alliance, team 1's number
t5_tboxes.append(textbox(x=140,y=230,thickness=1,caption="",clickable=1,fs=20,w=30,t="bt2n")) #blue alliamce, team 2's number
t5_tboxes.append(textbox(x=140,y=260,thickness=1,caption="",clickable=1,fs=20,w=30,t="bt3n")) #blue alliance, team 3's number
t5_tboxes.append(textbox(x=175,y=200,thickness=1,caption="",fs=20,w=50,t="bt1o"))   #blue alliance, team 1's offensive score
t5_tboxes.append(textbox(x=175,y=230,thickness=1,caption="",fs=20,w=50,t="bt2o"))   #blue alliance, team 2's offensive score
t5_tboxes.append(textbox(x=175,y=260,thickness=1,caption="",fs=20,w=50,t="bt3o"))   #blue alliance, team 3's offensive score
t5_tboxes.append(textbox(x=215,y=200,thickness=1,caption="",fs=20,w=50,t="bt1d"))   #blue alliance, team 1's defensive score
t5_tboxes.append(textbox(x=215,y=230,thickness=1,caption="",fs=20,w=50,t="bt2d"))   #blue alliance, team 2's defensive score
t5_tboxes.append(textbox(x=215,y=260,thickness=1,caption="",fs=20,w=50,t="bt3d"))   #blue alliance, team 3's defensive score
t5_tboxes.append(textbox(x=255,y=200,thickness=1,caption="",fs=20,w=50,t="bt1a"))   #blue alliance, team 1's assistive score
t5_tboxes.append(textbox(x=255,y=230,thickness=1,caption="",fs=20,w=50,t="bt2a"))   #blue alliance, team 2's assistive score
t5_tboxes.append(textbox(x=255,y=260,thickness=1,caption="",fs=20,w=50,t="bt3a"))   #blue alliance, team 3's assistive score
t5_tboxes.append(textbox(x=305,y=200,thickness=1,caption="",fs=20,w=50,t="b1bb"))   #blue alliance, team 1 balanced bridge
t5_tboxes.append(textbox(x=305,y=230,thickness=1,caption="",fs=20,w=50,t="b2bb"))   #blue alliance, team 2 balanced bridge
t5_tboxes.append(textbox(x=305,y=260,thickness=1,caption="",fs=20,w=50,t="b3bb"))   #blue alliance, team 3 balanced bridge
t5_tboxes.append(textbox(x=365,y=200,thickness=1,caption="",fs=20,w=50,t="b1tb"))   #blue alliance, team 1 balanced team bridge
t5_tboxes.append(textbox(x=365,y=230,thickness=1,caption="",fs=20,w=50,t="b2tb"))   #blue alliance, team 2 balanced team bridge
t5_tboxes.append(textbox(x=365,y=260,thickness=1,caption="",fs=20,w=50,t="b3tb"))   #blue alliance, team 3 balanced team bridge
t5_tboxes.append(textbox(x=430,y=200,thickness=1,caption="",fs=20,w=50,t="b1bs"))   #blue alliance, team 1 bridge score
t5_tboxes.append(textbox(x=430,y=230,thickness=1,caption="",fs=20,w=50,t="b2bs"))   #blue alliance, team 2 bridge score
t5_tboxes.append(textbox(x=430,y=260,thickness=1,caption="",fs=20,w=50,t="b3bs"))   #blue alliance, team 3 bridge score
t5_tboxes.append(textbox(x=500,y=200,thickness=1,caption="",fs=20,w=50,t="b1ab"))   #blue alliance, team 1 Average balls scored
t5_tboxes.append(textbox(x=500,y=230,thickness=1,caption="",fs=20,w=50,t="b2ab"))   #blue alliance, team 2 Average balls scored
t5_tboxes.append(textbox(x=500,y=260,thickness=1,caption="",fs=20,w=50,t="b3ab"))   #blue alliance, team 3 Average balls scored
t5_tboxes.append(textbox(x=570,y=200,thickness=1,caption="",fs=20,w=50,t="b1bo"))   #blue alliance, team 1 Average balls bottom
t5_tboxes.append(textbox(x=570,y=230,thickness=1,caption="",fs=20,w=50,t="b2bo"))   #blue alliance, team 2 Average balls bottom
t5_tboxes.append(textbox(x=570,y=260,thickness=1,caption="",fs=20,w=50,t="b3bo"))   #blue alliance, team 3 Average balls bottom
t5_tboxes.append(textbox(x=630,y=200,thickness=1,caption="",fs=20,w=50,t="b1md"))   #blue alliance, team 1 Average balls middle
t5_tboxes.append(textbox(x=630,y=230,thickness=1,caption="",fs=20,w=50,t="b2md"))   #blue alliance, team 2 Average balls middle
t5_tboxes.append(textbox(x=630,y=260,thickness=1,caption="",fs=20,w=50,t="b3md"))   #blue alliance, team 3 Average balls middle
t5_tboxes.append(textbox(x=690,y=200,thickness=1,caption="",fs=20,w=50,t="b1tp"))   #blue alliance, team 1 Average balls top
t5_tboxes.append(textbox(x=690,y=230,thickness=1,caption="",fs=20,w=50,t="b2tp"))   #blue alliance, team 2 Average balls top
t5_tboxes.append(textbox(x=690,y=260,thickness=1,caption="",fs=20,w=50,t="b3tp"))   #blue alliance, team 3 Average balls top
t5_tboxes.append(textbox(x=750,y=200,thickness=1,caption="",fs=20,w=50,t="b1hh"))   #blue alliance, team 1 had hybrid 
t5_tboxes.append(textbox(x=750,y=230,thickness=1,caption="",fs=20,w=50,t="b2hh"))   #blue alliance, team 2 had hybrid
t5_tboxes.append(textbox(x=750,y=260,thickness=1,caption="",fs=20,w=50,t="b3hh"))   #blue alliance, team 3 had hybrid
t5_tboxes.append(textbox(x=810,y=200,thickness=1,caption="",fs=20,w=50,t="b1hs"))   #blue alliance, team 1 hybrid score
t5_tboxes.append(textbox(x=810,y=230,thickness=1,caption="",fs=20,w=50,t="b2hs"))   #blue alliance, team 2 hybrid score
t5_tboxes.append(textbox(x=810,y=260,thickness=1,caption="",fs=20,w=50,t="b3hs"))   #blue alliance, team 3 hybrid score
screen.fill(bgcolor)

# Tab 6 stuff
t6_tboxes.append(textbox(x=100,y=5,thickness=1,caption="",fs=40,w=50,t="a1t1",clickable=1)) # alliance 1, team 1
t6_tboxes.append(textbox(x=165,y=5,thickness=1,caption="",fs=40,w=50,t="a1t2",clickable=1)) # alliance 1, team 2
t6_tboxes.append(textbox(x=230,y=5,thickness=1,caption="",fs=40,w=50,t="a1t3",clickable=1)) # alliance 1, team 3
t6_tboxes.append(textbox(x=100,y=45,thickness=1,caption="",fs=40,w=50,t="a2t1",clickable=1)) # alliance 2, team 1
t6_tboxes.append(textbox(x=165,y=45,thickness=1,caption="",fs=40,w=50,t="a2t2",clickable=1)) # alliance 2, team 2
t6_tboxes.append(textbox(x=230,y=45,thickness=1,caption="",fs=40,w=50,t="a2t3",clickable=1)) # alliance 2, team 3
t6_tboxes.append(textbox(x=100,y=85,thickness=1,caption="",fs=40,w=50,t="a3t1",clickable=1)) # alliance 3, team 1
t6_tboxes.append(textbox(x=165,y=85,thickness=1,caption="",fs=40,w=50,t="a3t2",clickable=1)) # alliance 3, team 2
t6_tboxes.append(textbox(x=230,y=85,thickness=1,caption="",fs=40,w=50,t="a3t3",clickable=1)) # alliance 3, team 3
t6_tboxes.append(textbox(x=100,y=125,thickness=1,caption="",fs=40,w=50,t="a4t1",clickable=1)) # alliance 4, team 1
t6_tboxes.append(textbox(x=165,y=125,thickness=1,caption="",fs=40,w=50,t="a4t2",clickable=1)) # alliance 4, team 2
t6_tboxes.append(textbox(x=230,y=125,thickness=1,caption="",fs=40,w=50,t="a4t3",clickable=1)) # alliance 4, team 3
t6_tboxes.append(textbox(x=100,y=165,thickness=1,caption="",fs=40,w=50,t="a1t1",clickable=1)) # alliance 5, team 1
t6_tboxes.append(textbox(x=165,y=165,thickness=1,caption="",fs=40,w=50,t="a1t2",clickable=1)) # alliance 5, team 2
t6_tboxes.append(textbox(x=230,y=165,thickness=1,caption="",fs=40,w=50,t="a1t3",clickable=1)) # alliance 5, team 3
t6_tboxes.append(textbox(x=100,y=205,thickness=1,caption="",fs=40,w=50,t="a2t1",clickable=1)) # alliance 6, team 1
t6_tboxes.append(textbox(x=165,y=205,thickness=1,caption="",fs=40,w=50,t="a2t2",clickable=1)) # alliance 6, team 2
t6_tboxes.append(textbox(x=230,y=205,thickness=1,caption="",fs=40,w=50,t="a2t3",clickable=1)) # alliance 6, team 3
t6_tboxes.append(textbox(x=100,y=245,thickness=1,caption="",fs=40,w=50,t="a3t1",clickable=1)) # alliance 7, team 1
t6_tboxes.append(textbox(x=165,y=245,thickness=1,caption="",fs=40,w=50,t="a3t2",clickable=1)) # alliance 7, team 2
t6_tboxes.append(textbox(x=230,y=245,thickness=1,caption="",fs=40,w=50,t="a3t3",clickable=1)) # alliance 7, team 3
t6_tboxes.append(textbox(x=100,y=285,thickness=1,caption="",fs=40,w=50,t="a4t1",clickable=1)) # alliance 8, team 1
t6_tboxes.append(textbox(x=165,y=285,thickness=1,caption="",fs=40,w=50,t="a4t2",clickable=1)) # alliance 8, team 2
t6_tboxes.append(textbox(x=230,y=285,thickness=1,caption="",fs=40,w=50,t="a4t3",clickable=1)) # alliance 8, team 3
t6_scroll = scroller(pygame.Surface((100,2000)),maxheight=500,x=410,y=25,t="")
t6_buttons.append(button(x=410,y=4,thickness=1,text="",t="tlup",w=100,h=20))
t6_buttons.append(button(x=410,y=530,thickness=1,text="",t="tldo",w=100,h=20))

t7_tboxes.append(textbox(x=0,y=0,thickness=1,caption="Team:",t="tnum",clickable=1))
t7_tboxes.append(textbox(x=0,y=40,thickness=1,caption="Robot Length:",t="rbln",fs=30,w=50))
t7_tboxes.append(textbox(x=0,y=60,thickness=1,caption="Robot Width:",t="rbwd",fs=30,w=50))
t7_tboxes.append(textbox(x=0,y=80,thickness=1,caption="Robot Heigth:",t="rbhg",fs=30,w=50))
t7_tboxes.append(textbox(x=0,y=100,thickness=1,caption="Robot Wieght:",t="rbwg",fs=30,w=50))
t7_tboxes.append(textbox(x=0,y=120,thickness=1,caption="Floor Clearance to Frame:",t="frcr",fs=30,w=50))
t7_tboxes.append(textbox(x=0,y=140,thickness=1,caption="Spacing between the wheels:",t="wlsc",fs=30,w=50))
t7_tboxes.append(textbox(x=0,y=160,thickness=1,caption="Ability to lower bridge:",t="bgmc",fs=30,w=50))
t7_tboxes.append(textbox(x=0,y=180,thickness=1,caption="Tracktion on Bridge:",t="sdbg",fs=30,w=50))
t7_tboxes.append(textbox(x=0,y=200,thickness=1,caption="Has a sensor for balance:",t="blsn",fs=30,w=50))
t7_tboxes.append(textbox(x=0,y=220,thickness=1,caption="Has gear shifting system:",t="sggr",fs=30,w=50))
t7_tboxes.append(textbox(x=0,y=260,thickness=1,caption="Type of Drive System:",t="dvsy",fs=30,w=50))
t7_tboxes.append(textbox(x=0,y=280,thickness=1,caption="Center of Mass:",t="cnms",fs=30,w=50))
t7_tboxes.append(textbox(x=0,y=300,thickness=1,caption="Do they have a Drive Team:",t="dri1",fs=30,w=50))
t7_tboxes.append(textbox(x=0,y=320,thickness=1,caption="How many years have they played:",t="exp1",fs=30,w=50))
t7_tboxes.append(textbox(x=0,y=360,thickness=1,caption="Do they have a second Drive team:",t="dri2",fs=30,w=50))
t7_tboxes.append(textbox(x=0,y=380,thickness=1,caption="How many years have they played:",t="exp2",fs=30,w=50))
t7_tboxes.append(textbox(x=0,y=420,thickness=1,caption="Do they have a third  Drive team:",t="dri3",fs=30,w=50))
t7_tboxes.append(textbox(x=0,y=440,thickness=1,caption="How many years have they played:",t="exp3",fs=30,w=50))


t8_scrolls.append(scroller(pygame.Surface((143,2000)),maxheight=500,x=160,y=105,t="")) #Offensive Score Scroller
t8_buttons.append(button(x=160,y=85,thickness=1,text="",t="hyup",w=143,h=20)) #scroll offensive score up
t8_buttons.append(button(x=160,y=605,thickness=1,text="",t="hydo",w=143,h=20)) #scroll offensive score down
t8_scrolls.append(scroller(pygame.Surface((143,2000)),maxheight=500,x=305,y=105,t="")) #Defensive Score Scroller
t8_buttons.append(button(x=305,y=85,thickness=1,text="",t="teup",w=143,h=20))#scroll defensive score up
t8_buttons.append(button(x=305,y=605,thickness=1,text="",t="tedo",w=143,h=20))#scroll defensive score down
t8_scrolls.append(scroller(pygame.Surface((143,2000)),maxheight=500,x=455,y=105,t="")) #Assistive Score Scroller
t8_buttons.append(button(x=455,y=85,thickness=1,text="",t="bgup",w=143,h=20))#scroll assistive score up
t8_buttons.append(button(x=455,y=605,thickness=1,text="",t="bgdo",w=143,h=20))#scroll assistive score down

#draw top bar
pygame.draw.rect(screen, (0,0,0), (2,2,1276,46),5)
pygame.draw.rect(screen, (0,0,0), (2,50,1276,10),5)
for but in tb_buttons:
    if but.static == 1:
        but.draw(screen)
#draw side bar
pygame.draw.rect(screen, (0,0,0), (2,60,155,1000),5)

while running:
    mpos = (-1,-1)  #reset
    cmpos = pygame.mouse.get_pos() #current mouse position
    mbut = pygame.mouse.get_pressed() #which buttons are pressed
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print "quit has been pressed"
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:    #Click on buttons
            mpos = pygame.mouse.get_pos()
            for but in tb_buttons:
                if mpos[0]>=but.x and mpos[0]<=but.x+but.w and mpos[1]>=but.y and mpos[1]<=but.y+but.h:
                    but.click()
    key = pygame.key.get_pressed()
    if key[pygame.K_ESCAPE]: running = False
    # draw the tab
    tcount += 1
    go = 1
    if tcount == skip:
        tcount = 0
        go = 1
    if go == 1:
        screen.fill(bgcolor,[x0,y0,WIDTH-x0,HEIGHT-y0])#Fill in case of update
        if tab == 2:    #Team Data
            team_data()
        elif tab == 3:  #Rank data
            ratings()
        elif tab == 4:  #Search Tab
            search()
            # Present list of teams that meet criteria on right, if needed to update
            if t4_update:
                y = 5
                team_list.sort()
                t4_tempbut = []
                t4_temprad = []
                for t in team_list:
                    #add the buttons to the list
                    t4_tempbut.append(button(x=0,y=y,thickness=1,text=str(t[0]),font=30,w=50,t=str(t[0])))
                    t4_temprad.append(radio(x=55,y=y,caption=[],flip = 1,t=str(t[0]),fs=30,teamnum=t[0]))
                    y += 30
        elif tab == 5:  #Alliance Comparison Tab
            compare()
        elif tab == 6: #Alliance Selection tab
            alliance_selection()
        elif tab == 7:
            team_pitdata()
        elif tab == 8:
            ratings2()
    pygame.display.flip()
    new = pygame.time.get_ticks()
    print str(1000/(new-last))
    last = new
for team in teams:
    if str(team.number) == "253":
        print team.oscores
        print team.dscores
        print team.tscores
