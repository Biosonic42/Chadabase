# Database program - gets DS data files and gives statistics
# 2nd Gen - 0.0
# To Do:
#   improve on 1st Gen functionality

#imports
import math
import pygame
import tkFileDialog         # for open and save dialogs
import tkSimpleDialog       # simple input
import pickle
import os
import csv                  # for using access filetype .csv
from Tkinter import *       # import everything for GUI
from statlib import stats   # for generating statistics, (note: to get prob(z_score), use stats.lzprob(z))
pygame.init()


# Main variables
running = True
DataCalc = False            # bool of data imported being calculated.  If !DataCalc: no view team data
PitDataCalc = False
HEIGHT = 700                # height of window (in pixels)
WIDTH = 1100                # width of window (in pixels)
INIT_X = 160                # initial x coordinate for the tab
INIT_Y = 65                 # initial y coordinate for the tab
BGCOLOR = (0, 51, 0)        # background color
TXCOLOR = (255, 223, 0)     # text color          
LastFPS = 0                 # used for measuring frames per second
curfile = ""                # current data file

root = Tk()
root.withdraw()

#screen display
screen = pygame.display.set_mode((WIDTH,HEIGHT))#,pygame.FULLSCREEN)
pygame.display.set_caption("Chadabase 2nd Gen Ver0.0 - Lewis Compilation")

tab = 0                     # the tab displayed:
                            # 0 - blank
                            # 1 - Team
                            # 2 - Pit Data
                            # 3 - Rank
                            # 4 - Rank 2
                            # 5 - Search
                            # 6 - Compare(Alliances)
                            # 7 - Choose(During Actual Alliance Selection[Function: Alliance_Selection()]

# Stored Data
Entries = []                # all the entries for matches; 6 entries per match (1 per team)
PitEntries = []             # pit data entries
Teams = []                  # all the teams and their data (see 'Team' class)
Matches = []                # all of the match data
Overall_Score = 0           # overall score for all matches

#task bar
TaskBar_Buttons = []        # task bar buttons

#team data
Tab1_TextBoxes = []         # Tab 1 textboxes
Tab1_Update = True          # update Tab 1, preset to 1 for initial update
Tab1_Surface = pygame.Surface((WIDTH-INIT_X, HEIGHT-INIT_Y)) # improves framerate
Tab1_LReg = 0               # linear regression graph

#pit data
Tab2_TextBoxes = []         # Tab 2 textboxes
Tab2_Update = True          # update Tab 2, preset to 1 for inital update
Tab2_Surface = pygame.Surface((WIDTH-INIT_X, HEIGHT-INIT_Y)) # improves framerate

#rank
Tab3_Scrolls = []           # Tab 3 scrollers
Tab3_Buttons = []           # Tab 3 Buttons for scrolling

#rank 2
Tab4_Scrolls = []           # Tab 4 scrollers
Tab4_Buttons = []           # Tab 4 Buttons for scrolling

#search
Tab5_Contents = []          # Textboxes and radio buttons
Tab5_Scroll = 0             # Tab 5's scroller; create later before main loop
Tab5_WantScroll = 0         # Tab 5's wanted teams scroller; create later before main loop
Tab5_TempButton = []        # Temporary buttons
Tab5_TempCB = []            # Temporary Checkboxes
Tab5_WantedBut = []         # Temporary Buttons for wanted teams
Tab5_WantedCB = []          # Temporary Checkbox for wanted teams
Tab5_UpdateWanted = False   # update wanted teams or no
Tab5_Update = False         # update Tab 5
Tab5_ReDraw = False         # reDraw Tab 5
Tab5_WantedMoveBut = []     # Buttons that move manted rank +/- 1
Tab5_Buttons = []           # Tab 5 Buttons

#Compare
Tab6_TextBoxes = []         # Tab 6 text boxes
Tab6_Update = True          # update Tab 6, preset to 1 for initial update
Tab6_Surface = pygame.Surface((WIDTH-INIT_X,HEIGHT-INIT_Y)) # improves framerate
Wanted = []                 # list of teams we want on our alliance

#Choose
Tab7_TextBoxes = []         # Tab 7 tex boxes
Tab7_Scrolls = []           # Tab 7 scroller - shows wanted teams (not selected)
Tab7_Buttons = []           # Tab 7 buttons
Tab7_Update = True          # update Tab 7, preset to 1 for initial update
Tab7_Surface = pygame.Surface((WIDTH-INIT_X,HEIGHT-INIT_Y)) # improves framerate
Available_Teams = []        # Teams available for alliance selection

tabnum = 0                  # current tab
accessinfo = ""             # a file that can be opened in access will be created for editing purposes

#Ranking Info

    #score categories (?)
r1o = r1d = r1a = r1bb = r1tb = r1bs = r1ab = r1bo = r1md = r1tp = r1hh = r1hs = r1po = r1pd = r1pa = 0
r2o = r2d = r2a = r2bb = r2tb = r2bs = r2ab = r2bo = r2md = r2tp = r2hh = r2hs = r2po = r2pd = r2pa = 0
r3o = r3d = r3a = r3bb = r3tb = r3bs = r3ab = r3bo = r3md = r3tp = r3hh = r3hs = r3po = r3pd = r3pa = 0
b1o = b1d = b1a = b1bb = b1tb = b1bs = b1ab = b1bo = b1md = b1tp = b1hh = b1hs = b1po = b1pd = b1pa = 0
b2o = b2d = b2a = b2bb = b2tb = b2bs = b2ab = b2bo = b2md = b2tp = b2hh = b2hs = b2po = b2pd = b2pa = 0
b3o = b3d = b3a = b3bb = b3tb = b3bs = b3ab = b3bo = b3md = b3tp = b3hh = b3hs = b3po = b3pd = b3pa = 0
    #----------------------
r1 = r2 = r3 = b1 = b2 = b3 = 0                                                     #team numbers (?)
r1t = r2t = r3t = b1t = b2t = b3t = 0                                               #average total scores
r1ts = r2ts = r3ts = b1ts = b2ts = b3ts = 0                                         #total scores for each team

Off_Rank = []
Def_Rank = []
Ast_Rank = []
Tot_Rank = []

Hyd_Rank = []
Tele_Rank = []
Brdg_Rank = []

Team_List = []              # Made global so that button and radio button objects can be created in search tab
Old_List = []               # Old team list; compare to Team_List to see if update needed


#Don't update tabs every cycle;
tcount = 0
skip = 10

#---------------------------------------------------------------------------------------------------------
# Linear Regression Class
# -- Gives you information on a linear regression, and can return a graph
#---------------------------------------------------------------------------------------------------------
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

#---------------------------------------------------------------------------------------------------------
# Scroller Class
# -- A scroll bar, to scroll through contents of an area
#---------------------------------------------------------------------------------------------------------
class Scroller():
    def __init__(self,surface,maxHeight = 100,x=0,y=0,t="test"):
        self.type = t 
        self.x = x              # x-coordinate
        self.y = y              # y-coordinate
        self.surface = surface  # surface to display on
        self.maxh = maxHeight   # height to display
        self.currenty=0         # scroll distance
        self.maxy = pygame.Surface.get_height(self.surface)-self.maxh # max y-coordinate to display
        self.speed = 1.5*self.maxy/self.maxh
    def draw(self, screen):
        self.width = pygame.Surface.get_width(self.surface)
        screen.blit(self.surface,(self.x,self.y),[0,self.currenty,self.width,self.maxh])
    def update(self, direction):
        if direction == 1 and self.currenty >= self.speed:  #scrolls up
            self.currenty -= self.speed
        if direction == 0 and self.currenty + self.speed <= self.maxy:  #scroll down
            self.currenty += self.speed

#---------------------------------------------------------------------------------------------------------
# Checkbox Class
# -- creates a checkbox (with a circle, not a box)
#---------------------------------------------------------------------------------------------------------
class Checkbox():
    def __init__(self, t="t",x=0,y=0,caption="Test:",flip=0,fs=50,check=False,teamnum=0):
        global BGCOLOR
        global TXCOLOR
        self.x = x
        self.y = y
        self.type = t
        self.caption = caption
        self.flip = flip # 1 = show text on right side of Radio Button
        self.size = fs
        font = pygame.font.Font(None,self.size)
        self.text = font.render(self.caption,True,TXCOLOR,BGCOLOR)
        self.w = pygame.Surface.get_width(self.text)
        self.check = check
        self.teamnum = teamnumn # only used in search tab; no other use
    def draw(self,screen):
        if self.check: # clicked
            if self.flip:   # text to right
                pygame.draw.circle(screen,(0,0,0),(self.x+.5*self.size,self.y+.4*self.size),
                                   .25*self.size,0)
                screen.blit(self.text,(self.x+self.size,self.y))
            else:           # text to left
                pygame.draw.circle(screen,(0,0,0),(self.x+self.w+.5*self.size,self.y+.4*self.size),
                                   .25*self.size,0)
                screen.blit(self.text,(self.x,self.y))
        else:           # not clicked
            if self.flip:   # text to right
                pygame.draw.circle(screen,(0,0,0),(self.x+.5*self.size,self.y+.4*self.size),
                                   .25*self.size,.1*self.size)
                screen.blit(self.text,(self.x+self.size,self.y))
            else:           # text to left
                pygame.draw.circle(screen,(0,0,0),(self.x+self.w+.5*self.size,self.y+.4*self.size),
                                   .25*self.size,.1*self.size)
                screen.blit(self.text,(self.x,self.y))
    def click(self):
        self.check = not(self.check) # opposite of whatever it was before

#---------------------------------------------------------------------------------------------------------
# Textbox Class
# -- textbox, displays text and takes entry
#---------------------------------------------------------------------------------------------------------
class Textbox():
    def __init__(self,t="t",x=0,y=0,w=100,caption="Test:",fs=50,thickness=1,clickable=False,val=0):
        global BGCOLOR
        global TXCOLOR
        self.x = x
        self.y = y
        self.w = w
        self.type = t
        self.click = clickable
        self.caption = caption
        self.size = fs
        self.value = val
        self.th = thickness
        self.type = t
        font = pygame.font.Font(None,self.size)
        self.text = fon.render(self.caption,True,TXCOLOR,BGCOLOR)
        self.cw = pygame.Surface.get_width(self.text)
        self.ch = pygame.Surface.get_height(self.text)
        if self.click:
            self.color = (0,255,0)
        else:
            self.color = BGCOLOR
    def draw(self,screen):
        global BGCOLOR
        global TXCOLOR
        #draw caption
        screen.blit(self.text,(self.x+.5*self.th,self.y+.5*self.th))
        #draw textbox
        pygame.draw.rect(screen, self.color, (self.x+self.cw+.5*self.th,
                                              self.y+.5*self.th,self.w+.5*self.th,self.size+.5*self.th-10),
                         self.th)
        f2 = pygame.fontFont(None,self.size-self.th)    #account for thickness in rectangle
        intxt = f2.render(str(self.value),True,TXCOLOR,BGCOLOR)
        screen.blit(intxt,(self.x+self.cw+self.th,self.y+self.th))
    def clicked(self):
        global root
        global screen
        global WIDTH
        global HEIGHT
        if self.click:
            foot.focus()
            newval = tkSimpleDialog.askstring("New Value","_",parent=root,initialvalue=0)
            root.withdraw()
            if newval == "": newval = 0
            self.value = newval
    def update(self,surface):
        print "updating"

#---------------------------------------------------------------------------------------------------------
# Button Class
# -- creates a button, clicked to perform an action
# EWWW THIS CLASS IS UGLY->->NEED TO REDO click FUNCT FOR 2nd GEN
#---------------------------------------------------------------------------------------------------------
class Button():
    def __init__(self,t="none",x=0,y=0,w=0,h=0,text="Press Me",font=50,thickness=1,static=1):
        global BGCOLOR
        global TXCOLOR
        self.x = x
        self.y = y
        self.h = h
        self.w = w
        self.text = text
        self.size = size
        self.type = t
        self.static = 1
        self.th = thickness
        font = pygame.font.Font(None,self.size)
        self.text = font.render(self.text,True,TXCOLOR,BGCOLOR)
        if not w: self.w = pygame.Surface.get_width(self.texT)
        else:   self.w = w
        if not h: self.h = pygame.Surface.get_height(self.text)
        else:   self.h = h
    def draw(self,screen):
        screen.blit(self.text,(self.x+.5*self.th,self.y+.5*self.th))
        pygame.draw.rect(screen, (255,0,0), (self.x,self.y,self.w+.5*self.th,self.h+.5*self.th),self.th)
    def click(self):
        global Entries
        global tab
        global root
        global screen
        global curfile
        if self.type == "s": #save
            print "Saving"
            try:
                root.focus()
                filename = tkFileDialog.asksaveasfilename(parent=root)
                root.withdraw()
                filename = str(filename)
                data = pick.dumps(Entries)
                dfile = open(filename,"w")
                dfile.write(data)
                dfile.close()
                curfile = filename
                pygame.display.set_caption("Database -- " + filename)
                output_data()
                save_csv()
            except:
                print "save failed"
        elif self.type == "i": #import data
            imported = False
            try:
                import_data()
                imported = True
            except: print "Could not Import Data"
            if imported: calculate()
        elif self.type == "ip": #import pit data
            pitImport = False
            try:
                import_dataPit()
                pitImport = True
            except: print "Could not Import Pit Data"
            if pitImport: pitCalculate()
        elif self.type == "o": #open
            print "opening"
            try:
                root.focus()
                filename = tkFileDialog.askopenfilename(parent=root)
                root.withdraw()
                filename = str(filename)
                dfile = open(filename, "r")
                data = pickle.load(dfile)
                print "data loaded"
                Entries = data
                global Teams
                global Matches
                Teams = []
                Matches = []
                print str(Entries)
                calculate()
                pygame.display.set_caption("Database -- " + filename)
            except:
                print "error opening"
        elif self.type == "t": #view team data
            tab = 1
        elif self.type == "ps": #view pit scout data
            tab = 2
        elif self.type == "r": #view rankings
            tab = 3
        elif self.type == "r2": #view ranking page 2
            tab = 4
        elif self.type == "se": #view search
            tab = 5
        elif self.type == "co": #view compare
            tab = 6
        elif self.type == "ch": # view choose
            tab = 7

#---------------------------------------------------------------------------------------------------------
# Entry Class
# -- Equivalent to a single ms-access entry
# -- Each match has 6 of these entries
#---------------------------------------------------------------------------------------------------------
class Entry():
    # 1 per team per match
    def __init__(self,data):
        self.Match = data[0]            # Match Number
        self.Team = data[1]             # Team Number
        self.Color = data[2]            # Alliance Color

        self.HasHyd = data[3]           # Team has hybrid
        self.UsesKINECT = data[4]       # Team used KINECT
        self.HydLowerBrdg = data[5]     # Team lowered bridge in Hyd
        self.HydAssist = data[6]        # Team assisted in Hyd
        self.HydOther = data[7]         # Team used other strategy in Hyd
        self.HydTopP = data[8]          # Number of baskets scored in top by Team
        self.HydMidP = data[9]          # Number of baskets scored in mid by Team
        self.HydLowP = data[10]         # Number of baskets scored in low by Team

        self.DisabledCount = data[11]   # Number of times Team disabled
        self.TeleLowerBrdg = data[12]   # Team lowered bridge in Tele
        self.TeleTravelBar = data[13]   # Team traveled across bar in Tele
        self.BallsPU = data[14]         # Number of balls picked up by Team
        self.TeleTopP = data[15]        # Number of baskets scored in top by Team
        self.TeleMidP = data[16]        # Number of baskets scored in mid by Team
        self.TeleLowP = data[17]        # Number of baskets scored in low by Team

        self.BalType = data[18]         # Balance State ( -1 = no pressed, 0 = Bal, 1 = Co-op Bal,
                                        #                  2 = Bal Att, 3 = Co-op Att, 4 = none  )
        self.BalAmnt = data[19]+1       # Numbots Balanced (-1 = no bots, 0 = 1 bot, 1 = two bots, 2 = three bots)
                                        #                   (before the +1)
        self.Defensive = data[20]       # Team played Defensively
        self.Assist = data[21]          # Team played Assistively
        self.Technical = data[22]       # Number of Technical Fouls incurred by Team
        self.Regular = data[23]         # Number of Regular Fouls incurred by Team
        self.YellowPenalty = data[24]   # Team received Yellow Card
        self.RedPenalty = data[25]      # Team received Red Card

        self.Disabled = True if self.DisabledCount else False           # Team was disabled
        self.HasTechFoul = True if self.Technical else False            # Team received Technical Foul
        self.HasRegFoul = True if self.Regular else False               # Team received Regular Foul
        self.Ball = self.TeleTopP + self.TeleMidP + self.TeleLowP       # total baskets scored by Team

    def primary_sort(self):
        # Gets the match offensive score, wether the robot was offensive, etc.
        self.TeleScore = self.TeleLowP + (2*self.TeleMidP) + (3*self.TeleHighP)
        self.HydScore = self.HydLowP + (2*self.HydMidP) + (3*self.HydTopP) + (3*(self.HydLowP + self.HydMidP + self.HydTopP))

        self.ScoreHyd = False
        self.ScoreTele = False
        if self.HydScore: self.ScoreHyd = True
        if self.TeleScore: self.ScoreTele = True

        self.BrdgSuccess = False
        self.TeamBrdgSuccess = False
        self.BrdgScore = 0
        self.COBrdgSuccess = False
        self.AttTeamBrdg = False
        self.AttCOBrdg = False

        if(self.BrdgType == 0):                 # Team balanced on Team Bridge
            self.BrdgSuccess = True
            self.TeamBrdgSuccess = True
            if(self.BalAmnt):
                self.BrdgScore = ((2**(self.BalAmnt - 1))*10)#/self.BalAmnt #(for individual score on bridge)
        elif(self.BrdgType == 1):               # Team balanced on Co-op Bridge
            self.BrdgSuccess = True
            self.COBrdgSuccess = True
            if(self.BalAmnt):
                self.BrdgScore = ((2**(self.BalAmnt - 1))*10)#/self.BalAmnt # (for individual score on bridge)
        elif(self.BrdgType == 2):               # Team attempted a balance on Team Bridge
            self.AttTeamBrdg = True
        elif(self.BrdgType == 3):               # Team attempted a balance on the Co-op Bridge
            self.AttCOBrdg = True

        self.OffensiveScore = self.TeleScore + self.HydScore + self.BrdgScore
        self.TeleHydScore = self.TeleScore + self.HydScore
        # Team defensive / assistive / offensive
        self.IsOffensive = True if Self.OffensiveScore else False
        self.IsDefensive = Self.Defensive
        self.IsAssistive = Self.Assist

    def secondary_sort(self,oppAvg,oppOff,allAvg,allOff,allDef,allAst):
        self.DefScore = (oppAvg - oppOff) / allDef if self.Defensive else 0
        self.AstScore = (allOff - allAvg) / allAst if self.Assist else 0

    def tertiary_sort(self):
        self.Total = self.DefScore + self.AstScore + self.OffensiveScore
        self.TeleHydTotal = self.DefScore + self.Astcore + self.TeleHydScore

#---------------------------------------------------------------------------------------------------------
# Pit Entry Class
# -- Gets the robot Chasis type
#---------------------------------------------------------------------------------------------------------
class PitEntry():
    def __init__(self,data):
        self.Team = data[0]

        self.RobotLength = data[1]
        self.RobotWidth = data[2]
        self.RobotHeight = data[3]
        self.RobotWeight = data[4]
        self.Clearance = data[5]
        self.Spacing = data[6]

        self.BrdgMech = data[7]
        self.SlideBrdg = data[8]
        self.BalSensor = data[9]
        self.DriveSystem = data[10]
        self.ShiftGear = data[11]

        self.CenterMass = data[12]

        self.Drive1 = data[13]
        self.exp1 = data[14]

        self.Drive2 = data[15]
        self.exp2 = data[16]

        self.Drive3 = data[17]
        self.exp3 = data[18]

#---------------------------------------------------------------------------------------------------------
# Team Class
# -- Stores team data
#---------------------------------------------------------------------------------------------------------
class Team():
    def __init__(self,num):
        self.Number = num               # Team Number
        self.Matches = []               # Matches played by Team
        self.OScores = []               # Team Offensive Scores
        self.DScores = []               # Team Defensive Scores
        self.AScores = []               # Team Assistive Scores
        self.TScores = []               # Team Total Scores
        self.WScores = []               # Team Weighted Scores
        self.WOScores = []              # Team Weighted Offensive Scores
        self.WDScores = []              # Team Weighted Defensive Scores
        self.WAScores = []              # Team Weighted Assistive Scores
        self.THScores = []              # Team TeleHyd Scores
        self.BrdgBalType = []           # Team Balance Types
        self.BrdgBalAmnt = []           # Team Balance Amounts
        self.BrdgScores = []            # Team Brdg Scores
        self.BrdgSuccess = 0            # NumMatches successful balance
        self.TeamBrdgSuccess = 0        # NumMatches successful team bridge balance
        self.COBrdgSuccess = 0          # NmuMatches successful co-op bridge balance
        self.AttTeamBrdg = 0            # NumMatches attempt team bridge balance
        self.AttCOBrdg = 0              # NumMatches attempt co-op bridge balance
        self.NumOff = 0                 # NumMatches played offensive
        self.NumDef = 0                 # NumMatches played defensive
        self.NumAst = 0                 # NumMatches played assistive
        self.HadHyd = 0                 # NumMatches HadHybrid
        self.OffenseTele = 0            # NumMatches Team Scored in Tele
        self.MatchesState = 0           # Team wasDisabled State each match
        self.Disabled = 0               # NumMatches Disabled
        self.DisabledCount = 0          # NumTimes Disabled Total
        self.AvgRegFoul = []            # NumFouls of regular type each match
        self.AvgTechFoul = []           # NumFouls of technical type each match
        self.HadRegFoul = 0             # NumMatches had regular foul
        self.HadTechFoul = 0            # NumMatches had technical foul
        self.HadYellow = 0              # NumMatches had yellow card
        self.HadRed = 0                 # NumMatches had red card
        self.HydLwrBrdg = 0             # NumMatches lowered bridge in hyd
        self.HydAst = 0                 # NumMatches assisted in hyd
        self.HydOth = 0                 # NumMatches had other strategy in hyd
        self.HydScores = []             # Team Hybrid Scores
        self.ScoreInHyd = 0             # NumMatches scored in Hyd
        self.AvgHydScr = 0              # Average Score in Hybrid
        self.HydBBalls = []             # NumBalls scored in Hyd on Bottom
        self.HydMBalls = []             # NumBalls scored in Hyd on Middle
        self.HydTBalls = []             # NumBalls scored in Hyd on Top
        self.BallsScores = []           # NumBalls Scored in Tele
        self.TeleScores = []            # Team Tele Scores
        self.TeleBBalls = []            # NumBalls scored in Tele on Bottom
        self.TeleMBalls = []            # NumBalls scored in Tele on Middle
        self.TeleTBalls = []            # NumBalls scored in Tele on Top
        self.BallsPU = []               # NumBalls picked up
        self.Defense = 0                # NumMatches was defensive
        self.Assist = 0                 # NumMatches was assistive
        self.off_rank = 0               # ranks among all teams
        self.def_rank = 0
        self.ast_rank = 0
        self.tot_rank = 0
        self.hyb_rank = 0
        self.tel_rank = 0
        self.brd_rank = 0
        self.matchplay = []             
        self.RobotLength = 0            # pit stats, length, drivers, etcetera
        self.RobotWidth = 0
        self.RobotHeight = 0
        self.RobotWeight = 0
        self.Clearance = ""
        self.Spacing = ""
        self.BridgeMech = ""
        self.SlideBrdg = ""
        self.BalSensor = ""
        self.ShiftGear = ""
        self.DriveSystem = ""
        self.CenterMass = ""
        self.Drive1 = ""
        self.exp1 = None
        self.Drive2 = ""
        self.exp2 = None
        self.Drive3 = ""
        self.exp3 = None
    def get_avg_off(self):
        if self.NumOff:
            self.AvgTHOff = sum(self.THScores)/len(self.Matches)
            self.AvgOff = sum(self.OffScores)/len(self.Matches)
        else:
            self.AvgTHOff = 0
            self.AvgOff = 0
    def get_avg_defast(self):
        if self.NumDef: self.AvgDef = sum(self.DefScores)/len(self.Matches)
        else: self.AvgDef = 0
        if self.NumAst: self.AvgAst = sum(self.AstScore)/len(self.Matches)
        else: self.AvgAst = 0
    def get_avg_brdg(self):
        if self.BrdgSuccess:
            self.TotTBrdgSuccess = self.TeamBrdgSuccess/self.BrdgSuccess
            self.AvgBrdgScore = sum(self.BrdgScores)/len(self.Matches)
        else:
            self.TotTBrdgSuccess = 0
            self.AvgBrdgScore = 0
        if self.HadHyd: self.AvgHyd = sum(self.HydScores)/len(self.Matches)
        else: self.AvgHyd = 0
        if self.HadTele:
            self.AvgTele = sum(self.TeleScores)/len(self.Matches)
            self.BallsRatio = sum(self.BallScores)/len(self.BallsPU)
        else:
            self.AvgTele = 0
            self.BallsRatio = 0

#---------------------------------------------------------------------------------------------------------
# Match Class
# -- stores all match data
#---------------------------------------------------------------------------------------------------------
class Match():
    def __init__(self,num):  
        self.Number = num               # Match Number
        self.Teams = []                 # Teams in Match
        self.Ally1 = []                 # Teams in Alliance 1
        self.Ally2 = []                 # Teams in Alliance 2
        self.OffScore1 = 0              # Alliance 1 offensive score
        self.OffScore2 = 0              # Alliance 2 offensive score
        self.NumOff1 = 0                # NumTeams offensive in Alliance 1
        self.NumOff2 = 0                # NumTeams offensive in Alliance 2
        self.TeamBrdgSucc1 = False      # Alliance1 Balances Team Bridge
        self.TeamBrdgSucc2 = False      # Alliance2 Balances Team Bridge
        self.Defense1 = 0               # NumTeams Defensive in Alliance 1
        self.Defense2 = 0               # NumTeams Defensive in Alliance 2
        self.Assist1 = 0                # NumTeams Assistive in Alliance 1
        self.Assist2 = 0                # NumTeams Assistive in Alliance 2
        self.AvgSum1 = 0                # Total Average Offensive Score Alliance 1
        self.AvgSum2 = 0                # Total Average Offensive Score Alliance 2
        self.AvgTHSum1 = 0              # Total Average TeleHyd Score Alliance 1
        self.AvgTHSum2 = 0              # Total Average TeleHyd Score Alliance 2
        self.DefScore1 = 0              # Total Defensive Score Alliance 1
        self.DefScore2 = 0              # Total Defensive Score Alliance 2
        self.AstScore1 = 0              # Total Assistive Score Alliance 1
        self.AstScore2 = 0              # Total Assistive Score Alliance 2
    def get_total(self):
        self.Total1 = self.OffScore1 + (2**(self.TeamBrdgSucc1 - 1))*10 #+self.DefScore1 + self.AstScore1
                                                                        # total score for first alliance
        self.Total2 = self.OffScore2 + (2**(self.TeamBrdgSucc2 - 1))*10 #+self.DefScore2 + self.AstScore2
                                                                        # total score for second alliance
        self.Overall = self.Total1 + self.Total2                        # total score for match

#---------------------------------------------------------------------------------------------------------
# Output Data Function
# -- ouputs access-importable text file with all information
#---------------------------------------------------------------------------------------------------------
def output_data():
    global Entries
    global curfile
    #if data file exists, delete it
    try:
        os.delete(curfile+"_access.txt")
    except:
        print "No file, procede to write"
    #open file for writing
    filetosave = open(curfile+"access.txt","w")
    print "File Opened"
    n = 0
    outstring = ""
    while n < len(Entries):
        outsrting = ""
        for element in Entries[n].stored_data:
            outstring += str(element) + ","
        outstring = outstring.strip(",")        # remove unnecessary last ","
        outstring += "\r\n"                     # newline
        filetosave.write(outstring)
        n+=1
    print "End loop"
    filetosave.close()

def save_csv():
    global Entries
    global curfile
    rows = []
    for entry in Entries:
        rows.append(entry.stored_data)
    try:
        os.delete(curfile+"_access.txt")
    except:
        writer = csv.wirter(open(curfile+"_access.txt","wb"))
        writer.writerows(rows)
    print writer

#---------------------------------------------------------------------------------------------------------
# Import Data Function
# -- imports data file to calculate data
#---------------------------------------------------------------------------------------------------------
def import_data():
    global Entries
    global DataCalc
    DataCalc = False
    if not DataCalc:
        filename = tkFileDialog.askopenfilename()
        filename = str(filename)
        print "file selected"
        filename = os.path.basename(filename)
        print filename
        new_data = open(filename,"r")
        print "File Opened"
        # Clean out data except entries, data doesn't count multiple teams during calculations
        global Teams
        global Matches
        Teams = []
        Matches = []
        # now file is loaded, parse it
        print "Parsing Data"
        for line in new_data:
            Entries.append(parse_data(line))
        print "--Data parsed"

def import_dataPit():
    global PitEntries
    global PitDataCalc
    global Teams
    PitDataCalc = False
    if not PitDataCalc:
        filename = tkFileDialog.askopenfilename()
        filename = str(filename)
        print "file selected"
        filename = os.path.basename(filename)
        print filename
        new_data = open(filename,"r")
        print"File opened"

        # now file is loaded, parse it
        print "Parsing Data"
        for line in new_data:
            PitEntries.append(parse_Pitdata(line))
        print "--PitData parsed"

#---------------------------------------------------------------------------------------------------------
# Parse Data Function
# -- Takes each line in a file and transfers it into an entry
#---------------------------------------------------------------------------------------------------------
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
                i+=1
                if i>= 26: break
    return Entry(data)

def parse_Pitdata(info):
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
                i+=1
                if i>=19: break
    return PitEntry(data)

#---------------------------------------------------------------------------------------------------------
# Calculate Function
# -- calculates data for statistical analysis
# -- both overall and team data created
#---------------------------------------------------------------------------------------------------------
def calculate():
    global Entries
    global Teams
    global Calculated
    global Available_Teams
    
    #Get offensive scores, wasDefensive, etc.
    for Entry in Entries:
        Entry.primary_sort()
        
    # create team data
    for Entry in Entries:
        done = False
        for Team in Teams:
            if Team.Number == Entry.Team:
                Team.OScores.append(Entry.OffensiveScore)
                Team.THScores.append(Entry.THScore)
                Team.NumOff += Entry.IsOffensive
                Team.NumDef += Entry.IsDefensive
                Team.NumAst += Entry.IsAssistive
                Team.Matches.append(Entry.Match)
                Team.BrdgBalType.append(Entry.BrdgType)
                if Entry.BrdgType > -1: Team.BrdgBalAmnt.appened(Entry.BalAmnt)
                Team.BrdgScores.append(Entry.BrdgScore)
                Team.BrdgSuccess += Entry.BrdgSuccess
                Team.TeamBrdgSuccess += Entry.TeamBrdgSuccess
                Team.COBrdgSuccess += Entry.CoBrdgSuccess
                Team.AttTeamBrdg += Entry.AttTeamBrdg
                Team.AttCOBrdg += Entry.AttCOBrdg
                Team.HadHyd += Entry.HasHyd
                Team.OffenseTele += Entry.ScoreTele
                Team.Disabled += Entry.Disabled
                if Entry.Disabled: Team.DisabledState.append(Entry.Disabled)
                Team.DisabledCount += Entry.DisabledCount
                Team.AvgRegFoul.append(Entry.Regular)
                Team.AvgTechFoul.append(Entry.Technical)
                Team.HadRegFoul += Entry.HasRegFoul
                Team.HadTechFoul += Entry.HasTechFoul
                Team.HadYellow += Entry.YellowPenalty
                Team.HadRed += Entry.RedPenalty
                Team.HydLwrBrdg += Entry.HydLowerBrdg
                Team.HydAssist += Entry.HydAssist
                Team.HydOther += Entry.HydOther
                Team.HydScores.append(entry.HydScore)
                Team.HydBBalls.append(Entry.HydLowP)
                Team.HydMBalls.append(Entry.HydMidP)
                Team.HydTBalls.append(Entry.HydTopP)
                Team.BallsScores.append(Entry.Ball)
                Team.TeleScores.append(Entry.TeleScore)
                Team.TeleBBalls.append(Entry.TeleLowP)
                Team.TeleMBalls.append(Entry.TeleMidP)
                Team.TeleTBalls.append(Entry.TeleTopP)
                Team.BallsPU.append(Entry.BallsPU)
                Team.Defense += Entry.Defensive
                Team.Assist += Entry.Assist
                Team.matchplay.append(Entry.Match)
                done = True
        if done == False:
            Teams.append(Team(Entry.Team))
            print "Added Team #" + str(Entry.Team)
            Teams[len(Teams)-1].OScores.append(Entry.OffensiveScore)
            Teams[len(Teams)-1].THScores.append(Entry.THScore)
            Teams[len(Teams)-1].NumOff += Entry.IsOffensive
            Teams[len(Teams)-1].NumDef += Entry.IsDefensive
            Teams[len(Teams)-1].NumAst += Entry.IsAssistive
            Teams[len(Teams)-1].Matches.append(Entry.Match)
            Teams[len(Teams)-1].BrdgBalType.append(Enty.BrdgType)
            if Entry.BrdgType > -1: Teams[len(Teams)-1].BrdgBalAmnt.append(Entry.BalAmnt)
            Teams[len(Teams)-1].BrdgScores.append(Entry.BrdgScore)
            Teams[len(Teams)-1].BrdgSuccess += Entry.BrdgSuccess
            Teams[len(Teams)-1].TeamBrdgSuccess += Entry.TeamBrdgSuccess
            Teams[len(Teams)-1].COBrdgSuccess += Entry.COBrdgSuccess
            Teams[len(Teams)-1].AttTeamBrdg += Entry.AttTeamBrdg
            Teams[len(Teams)-1].AttCOBrdg += Entry.AttCOBrdg
            Teams[len(Teams)-1].HadHyd += Entry.HasHyd
            Teams[len(Teams)-1].OffenseTele += Entry.ScoreTele
            Teams[len(Teams)-1].Disabled += Entry.Disabled
            if Entry.Disabled: Teams[len(Teams)-1].DisabledState.append(Entry.Disabled)
            Teams[len(Teams)-1].DisabledCount += Entry.DisabledCount
            Teams[len(Teams)-1].AvgRegFoul.append(Entry.Regular)
            Teams[len(Teams)-1].AvgTechFoul.append(Entry.Technical)
            Teams[len(Teams)-1].HadRegFoul += Entry.HasRegFoul
            Teams[len(Teams)-1].HadTechFoul += Entry.HasTechFoul
            Teams[len(Teams)-1].HadYellow += Entry.YellowPenalty
            Teams[len(Teams)-1].HadRed += Entry.RedPenalty
            Teams[len(Teams)-1].HydLwrBrdg += Entry.HydLowerBrdg
            Teams[len(Teams)-1].HydAssist += Entry.HydAssist
            Teams[len(Teams)-1].HydOther += Entry.HydOther
            Teams[len(Teams)-1].HydScores.append(entry.HydScore)
            Teams[len(Teams)-1].HydBBalls.append(Entry.HydLowP)
            Teams[len(Teams)-1].HydMBalls.append(Entry.HydMidP)
            Teams[len(Teams)-1].HydTBalls.append(Entry.HydTopP)
            Teams[len(Teams)-1].BallsScores.append(Entry.Ball)
            Teams[len(Teams)-1].TeleScores.append(Entry.TeleScore)
            Teams[len(Teams)-1].TeleBBalls.append(Entry.TeleLowP)
            Teams[len(Teams)-1].TeleMBalls.append(Entry.TeleMidP)
            Teams[len(Teams)-1].TeleTBalls.append(Entry.TeleTopP)
            Teams[len(Teams)-1].BallsPU.append(Entry.BallsPU)
            Teams[len(Teams)-1].Defense += Entry.Defensive
            Teams[len(Teams)-1].Assist += Entry.Assist
            Teams[len(Teams)-1].matchplay.append(Entry.Match)

    Calculated = True
    
    # get average Bridge Scores
    for Team in Teams:
        Team.get_avg_Brdg()
        
    # get average offensive scores
    for Team in Teams:
        Team.get_avg_off()
        
    # get match data
    for Entry in Entries:
        done = False
        for Match in Matches:
            if Match.Numer == Entry.Match:
                Match.Teams.Append(Entry.Team)
                if not Entry.Color:
                    Match.Ally1.append(Entry.Team)
                    Match.OffScore1 += Entry.THScore
                    Match.NumOff1 += Entry.IsOffensive
                    Match.Defense1 += Entry.Defensive
                    Match.Assist1 += Entry.Assist
                    Match.TeamBrdgSucc1 += Entry.TeamBrdgSuccess
                    if Entry.IsOffensive:
                        for Team in Teams:
                            if Team.Numer == Entry.Team:
                                Match.AvgTHSum1 += Team.AvgTHOff
                elif Entry.Color:
                    Match.Ally2.append(Entry.Team)
                    Match.OffScore2 += Entry.THScore
                    Match.NumOff2 += Entry.IsOffensive
                    Match.Defense2 += Entry.Defensive
                    Match.Assist2 += Entry.Assist
                    Match.TeamBrdgSucc2 += Entry.TeamBrdgSuccess
                    if Entry.IsOffensive:
                        for Team in Teams:
                            if Team.Numer == Entry.Team:
                                Match.AvgTHSum2 += Team.AvgTHOff
                done = True
        if done == False:
            Matches.append(Match(Entry.Match))
            print "Added Match #" + str(Entry.Match)
            Matches[len(Matches)-1].Teams.append(Entry.Team)
            if not Entry.Color:
                Matches[len(Matches)-1].Ally1.append(Entry.Team)
                Matches[len(Matches)-1].OffScore1 += Entry.THScore
                Matches[len(Matches)-1].NumOff1 += Entry.IsOffensive
                Matches[len(Matches)-1].Defense1 += Entry.Defensive
                Matches[len(Matches)-1].Assist1 += Entry.Assist
                Matches[len(Matches)-1].TeamBrdgSucc1 += Entry.TeamBrdgSuccess
                if Entry.IsOffensive:
                    for Team in Teams:
                        if Team.Numer == Entry.Team:
                            Matches[len(Matches)-1].AvgTHSum1 += Team.AvgTHOff
            elif Entry.Color:
                Matches[len(Matches)-1].Ally2.append(Entry.Team)
                Matches[len(Matches)-1].OffScore2 += Entry.THScore
                Matches[len(Matches)-1].NumOff2 += Entry.IsOffensive
                Matches[len(Matches)-1].Defense2 += Entry.Defensive
                Matches[len(Matches)-1].Assist2 += Entry.Assist
                Matches[len(Matches)-1].TeamBrdgSucc2 += Entry.TeamBrdgSuccess
                if Entry.IsOffensive:
                    for Team in Teams:
                        if Team.Numer == Entry.Team:
                            Matches[len(Matches)-1].AvgTHSum2 += Team.AvgTHOff
                            
    # Get defensive + assistive scores for each entry
    for Entry in Entries:
        Entry.DefScore = 0
        Entry.AstScore = 0
        if Entry.IsDefensive or Entry.IsAssistive:
            for Match in Matches:
                if Match.Numer == Entry.Match:
                    if not Entry.Color:
                        OppAvgTHOff = Match.AvgTHSum2
                        OppOff = Match.OffScore2
                        AllyAvgTH = Match.AvgTHSum1
                        AllyOff = Match.OffScore1
                        AllyDefense = Match.Defense1
                        AllyAssist = Match.Assist1
                    elif Entry.Color:
                        OppAvgTHOff = Match.AvgTHSum1
                        OppOff = Match.OffScore1
                        AllyAvgTH = Match.AvgTHSum2
                        AllyOff = Match.OffScore2
                        AllyDefense = Match.Defense2
                        AllyAssist = Match.Assist2
            Entry.secondary_sort(OppAvgTHOff,OppOff,AllyAvgTH,AllyOff,AllyDefense,AllyAssist)
        Entry.tertiary_sort()
        
    # Get Avg Defensive + Assistive Scores
    for Entry in Entries:
        for Team in Teams:
            if Team.Number == Entry.Team:
                Team.DScores.append(Entry.DefScore)
                Team.AScores.append(Entry.AstScore)
    for Team in Teams:
        team.get_avg_defast()

    # Get Match Defensive + Assistive Scores
    for Entry in Entries:
        for Match in Matches:
            if Entry.Match == Match.Number:
                if not Entry.Color:
                    Match.DefScore1 += Entry.DefScore
                    Match.AstScore1 += Entry.DefScore
                elif Entry.Color:
                    Match.DefScore2 += Entry.DefScore
                    Match.AstScore2 += Entry.DefScore

    #Get Match Total Scores
    for Match in Matches:
        Match.get_total()

    # Get Match Weightscores
    overall_score = 0
    for Match in Matches:
        overall_score += Match.Overall
    # weight = (S[m]/S[w]-S[1])) * S[t]
    for Entry in Entries:
        for Match in Matches:
            if Entry.Match == Match.Number:
                tempweight = 0
                if Match.Total1 != MatchTotal2:
                    Entry.WScore = ((Match.Total1 + Match.Total2)*Entry.Total)/100            # ? if math is right
                    Entry.WOScore = ((Match.OffScore1 + Match.OffScore2)*Entry.THScore)/100
                    Entry.WDScore = ((Match.DefScore1 + Match.DefScore2)*Entry.DefScore)/100
                    Entry.WAScore = ((Match.AstScore1 + Match.AstScore2)*Entry.AstScore)/100
                else:
                    Entry.WScore = ((Match.Total1 + Match.Total2)*Entry.Total)           # ? if math is right
                    Entry.WOScore = ((Match.OffScore1 + Match.OffScore2)*Entry.THScore)
                    Entry.WDScore = ((Match.DefScore1 + Match.DefScore2)*Entry.DefScore)
                    Entry.WAScore = ((Match.AstScore1 + Match.AstScore2)*Entry.AstScore)

    #Get Team Average Weighted and Total Scores
    for Team in Teams:
        counter = 0
        for Entry in Entries:
            if Team.Number == Entry.Team:
                counter += 1
                Team.WScores.append(Entry.WScore)
                Team.TScores.append(Entry.Total)
                Team.WOScores.append(Entry.WOScore)
                Team.WDScores.append(Entry.WDScore)
                Team.WAScores.append(Entry.WAScore)

        #dont divide by zero!
        Team.Avg_WScore = sum(Team.WScores)/len(Team.WScores) if len(Team.WScores) else 0
        Team.Avg_TScore = sum(Team.TScores)/len(Team.TScores) if len(Team.TScores) else 0
        Team.Avg_WOScore = sum(Team.WOScores)/len(Team.WOScores) if len(Team.WOScores) else 0
        Team.Avg_WDScore = sum(Team.WDScores)/len(Team.WDScores) if len(Team.WDScores) else 0
        Team.Avg_WAScore = sum(Team.WAScores)/len(Team.WAScores) if len(Team.WAScores) else 0
        Team.Avg_HydScore = sum(Team.HydScores) / Team.HadHyd if Team.HadHyd else "N\A"
        Team.AvgBalls = sum(Team.BallsScores)/len(Team.BallsScores) if len(Team.BallsScores) else 0
        Team.AvgBottom = sum(Team.TeleBBalls)/len(Team.TeleBBalls) if len(Team.TeleBBalls) else 0
        Team.AvgMiddle = sum(Team.TeleMBalls)/len(Team.TeleMBalls) if len(Team.TeleMBalls) else 0
        Team.AvgTop = sum(Team.TeleTBalls)/len(Team.TeleTBalls) if len(Team.TeleTBalls) else 0

    # Get Team Rank
    global off_rank, def_rank, ast_rank, tot_rank, hyb_rank, tel_rank, brd_rank
    off_rank = def_rank = ast_rank = tot_rank = hyb_rank = tel_rank = brd_rank = []

    for Team in Teams:
        if Team.NumOff: off_rank.append([Team.AvgOff,Team.Number])
        if Team.NumDef: def_rank.append([Team.AvgDef,Team.Number])
        if Team.NumAst: ast_rank.append([Team.AvgAst,Team.Number])
        tot_rank.append([Team.Avg_TScore,Team.Number])

        if Team.HadHyd: hyb_rank.append([Team.AvgHyd,Team.Number])
        if Team.HadTele: tel_rank.append([Team.AvgTele, Team.Number, Team.BallsRatio])
        if Team.BrdgSuccess: brd_rank.append([Team.AvgBrdgScore, Team.Number])

    # Sort Them
    off_rank.sort(reverse=True)
    def_rank.sort(reverse=True)
    ast_rank.sort(reverse=True)
    tot_rank.sort(reverse=True)

    hyb_rank.sort(reverse=True)
    tel_rank.sort(reverse=True)
    brd_rank.sort(reverse=True)

    # Add all Teams to the available teams list
    Available_Teams = []
    offr = defr = astr = totr = hybr = telr= brdr = 0

    for rank in off_rank:
        offr+=1
        for Team in Teams:
            if Team.Number == rank[1]: Team.off_rank = offr
            
    for rank in def_rank:
        defr+=1
        for Team in Teams:
            if Team.Number == rank[1]: Team.def_rank = defr
            
    for rank in ast_rank:
        astr+=1
        for Team in Teams:
            if Team.Number == rank[1]: Team.ast_rank = astr
            
    for rank in tot_rank:
        totr+=1
        for Team in Teams:
            if Team.Number == rank[1]: Team.tot_rank = totr
            
    for rank in hyb_rank:
        hybr+=1
        for Team in Teams:
            if Team.Number == rank[1]: Team.hyb_rank = hybr
            
    for rank in tel_rank:
        telr+=1
        for Team in Teams:
            if Team.Number == rank[1]: Team.tel_rank = telr

    for rank in brd_rank:
        brdr+=1
        for Team in Teams:
            if Team.Number == rank[1]: Team.brd_rank = brdr

    for Team in Teams:
        Available_Teams.append(Team.Number)
               
#---------------------------------------------------------------------------------------------------------
# pitCalculate Function
# -- calculates pit scout data for statistical analysis
# -- individual team data created
#---------------------------------------------------------------------------------------------------------
def pitCalculate():
    global PitEntries
    global Teams
    global PitDataCalc

    for Entry in PitEntries:
        done = False
        for Team in Teams:
            if Team.Number == Entry.Team:
                Team.RobotLength = Entry.RobotLength
                Team.RobotWidth = Entry.RobotWidth
                Team.RobotHeight = Entry.RobotHeight
                Team.RobotWeight = Entry.RobotWeight
                if Entry.Clearance == 1: Team.Clearance = "Yes"
                elif Entry.Clearance == 2: Team.Clearance = "No"
                else: Team.Clearance = "IDK"
                if Entry.Spacing == 1: Team.Spacing = "Yes"
                elif Entry.Spacing == 2: Team.Spacing = "No"
                else: Team.Spacing = "IDK"
                if Entry.BrdgMech == 1: Team.BrdgMech = "Yes"
                elif Entry.BrdgMech == 2: Team.BrdgMech = "No"
                else: Team.BrdgMech = "IDK"
                if Entry.SlideBrdg == 1: Team.SlideBrdg = "No"
                elif Entry.SlideBrdg == 2: Team.SildeBrdg = "Yes"
                else: Team.SlideBrdg = "IDK"
                if Entry.BalSensor == 1: Team.BalSensor = "Yes"
                elif Entry.BalSensor == 2: Team.BalSensor = "No"
                else: Team.BalSensor = "IDK"
                if Entry.ShiftGear == 1: Team.ShiftGear = "Yes"
                elif Entry.ShiftGear == 2: Team.ShiftGear = "No"
                else: Team.ShiftGear = "IDK"
                if Entry.DriveSystem == 1: Team.DriveSystem = "Crab"
                elif Entry.DriveSystem == 2: Team.DriveSystem = "McCannon"
                elif Entry.DriveSystem == 3: Team.DriveSystem = "Swerve"
                elif Entry.DriveSystem == 4: Team.DriveSystem = "Tank"
                elif Entry.DriveSystem == 5: Team.DriveSystem = "Arcade"
                elif Entry.DriveSystem == 6: Team.DriveSystem = "Other"
                else: Team.DriveSystem = "IDK"
                if Entry.CenterMass == 1: Team.CenterMass = "Low"
                elif Entry.CenterMass == 2: Team.CenterMass = "Middle"
                elif Enter.CenterMass == 3: Team.CenterMass = "High"
                else: Team.CenterMass = "IDK"
                if Entry.Drive1 == 1: Team.Drive1 = "Yes"
                elif Entry.Drive1 == 2: Team.Drive1 = "No"
                else: Team.Drive1 = "IDK"
                if Entry.exp1 < 0: Team.exp1 = "IDK"
                else: Team.exp1 = Entry.exp1
                if Entry.Drive2 == 1: Team.Drive2 = "Yes"
                elif Entry.Drive2 == 2: Team.Drive2 = "No"
                else: Team.Drive2 = "IDK"
                if Entry.exp2 < 0: Team.exp2 = "IDK"
                else: Team.exp2 = Entry.exp2
                if Entry.Drive3 == 1: Team.Drive3 = "Yes"
                elif Entry.Drive3 == 2: Team.Drive3 = "No"
                else: Team.Drive3 = "IDK"
                if Entry.exp3 < 0: Team.exp3 = "IDK"
                else: Team.exp3 = Entry.exp3
                done = True
        if done == False:
            Teams.append(Team(Entry.Team))
            print "Added team #" + str(Entry.Team)
            Teams[len(Teams)-1].RobotLength = Entry.RobotLength
            Teams[len(Teams)-1].RobotWidth = Entry.RobotWidth
            Teams[len(Teams)-1].RobotHeight = Entry.RobotHeight
            Teams[len(Teams)-1].RobotWeight = Entry.RobotWeight
            if Entry.Clearance == 1: Teams[len(Teams)-1].Clearance = "Yes"
            elif Entry.Clearance == 2: Teams[len(Teams)-1].Clearance = "No"
            else: Teams[len(Teams)-1].Clearance = "IDK"
            if Entry.Spacing == 1: Teams[len(Teams)-1].Spacing = "Yes"
            elif Entry.Spacing == 2: Teams[len(Teams)-1].Spacing = "No"
            else: Teams[len(Teams)-1].Spacing = "IDK"
            if Entry.BrdgMech == 1: Teams[len(Teams)-1].BrdgMech = "Yes"
            elif Entry.BrdgMech == 2: Teams[len(Teams)-1].BrdgMech = "No"
            else: Teams[len(Teams)-1].BrdgMech = "IDK"
            if Entry.SlideBrdg == 1: Teams[len(Teams)-1].SlideBrdg = "No"
            elif Entry.SlideBrdg == 2: Teams[len(Teams)-1].SildeBrdg = "Yes"
            else: Teams[len(Teams)-1].SlideBrdg = "IDK"
            if Entry.BalSensor == 1: Teams[len(Teams)-1].BalSensor = "Yes"
            elif Entry.BalSensor == 2: Teams[len(Teams)-1].BalSensor = "No"
            else: Teams[len(Teams)-1].BalSensor = "IDK"
            if Entry.ShiftGear == 1: Teams[len(Teams)-1].ShiftGear = "Yes"
            elif Entry.ShiftGear == 2: Teams[len(Teams)-1].ShiftGear = "No"
            else: Teams[len(Teams)-1].ShiftGear = "IDK"
            if Entry.DriveSystem == 1: Teams[len(Teams)-1].DriveSystem = "Crab"
            elif Entry.DriveSystem == 2: Teams[len(Teams)-1].DriveSystem = "McCannon"
            elif Entry.DriveSystem == 3: Teams[len(Teams)-1].DriveSystem = "Swerve"
            elif Entry.DriveSystem == 4: Teams[len(Teams)-1].DriveSystem = "Tank"
            elif Entry.DriveSystem == 5: Teams[len(Teams)-1].DriveSystem = "Arcade"
            elif Entry.DriveSystem == 6: Teams[len(Teams)-1].DriveSystem = "Other"
            else: Teams[len(Teams)-1].DriveSystem = "IDK"
            if Entry.CenterMass == 1: Teams[len(Teams)-1].CenterMass = "Low"
            elif Entry.CenterMass == 2: Teams[len(Teams)-1].CenterMass = "Middle"
            elif Enter.CenterMass == 3: Teams[len(Teams)-1].CenterMass = "High"
            else: Teams[len(Teams)-1].CenterMass = "IDK"
            if Entry.Drive1 == 1: Teams[len(Teams)-1].Drive1 = "Yes"
            elif Entry.Drive1 == 2: Teams[len(Teams)-1].Drive1 = "No"
            else: Teams[len(Teams)-1].Drive1 = "IDK"
            if Entry.exp1 < 0: Teams[len(Teams)-1].exp1 = "IDK"
            else: Teams[len(Teams)-1].exp1 = Entry.exp1
            if Entry.Drive2 == 1: Teams[len(Teams)-1].Drive2 = "Yes"
            elif Entry.Drive2 == 2: Teams[len(Teams)-1].Drive2 = "No"
            else: Teams[len(Teams)-1].Drive2 = "IDK"
            if Entry.exp2 < 0: Teams[len(Teams)-1].exp2 = "IDK"
            else: Teams[len(Teams)-1].exp2 = Entry.exp2
            if Entry.Drive3 == 1: Teams[len(Teams)-1].Drive3 = "Yes"
            elif Entry.Drive3 == 2: Teams[len(Teams)-1].Drive3 = "No"
            else: Teams[len(Teams)-1].Drive3 = "IDK"
            if Entry.exp3 < 0: Teams[len(Teams)-1].exp3 = "IDK"
            else: Teams[len(Teams)-1].exp3 = Entry.exp3
    PitDataCalc = True

#---------------------------------------------------------------------------------------------------------
# Team Data Function
# -- allows the user to access data for specific teams
#---------------------------------------------------------------------------------------------------------
def team_data():
    global Teams
    global Tab1_TextBoxes, Tab1_Update, Tab1_Surface
    global tabnum, mpos, teamdata
    global BGCOLOR, INIT_X, INIT_Y

    # Get Team Numbers
    TNums = []
    for Team in Teams:
        TNums.append(Team.Number)
    TNums.sort()
    if len(TNums) and tabnum == 0:
        TNum = TNums[0]
    #else: tabnum = 0
    for Textbox in Tab1_TextBoxes:
        if Textbox.Type == "tnum":
            if not Textbox.value:
                try:
                    if not int(Textbox.value): Textbox.value = tabnum    # make current team number value if it is 0
                    elif int(Textbox.value) != tabnum:                   # do updates
                        if int(Textbox.value) in TNums:
                            tabnum = int(Textbox.value)
                            Tab1_Update = True
                        else:
                            tabnum = TNums[0] if len(TNums) else 0       # number is not found, reset to first team in list
                except:
                    print "Error: non-numerical characters inserted for team number"
                    
            Textbox.value = tabnum

    #update values based on tabnum
            #-- start by getting teamdata from beginning
    if Tab1_Update:
        print "Update in Tab1(Team) requested"
        teamdata = 0
        for Team in Teams:
            teamdata = team if Team.Number == tabnum else 0
        if teamdata:
            for Textbox in Tab1_Textboxes:
                if   Textbox.type == "nmat": Textbox.value = str(len(teamdata.Matches))
                elif Textbox.type == "poff": Textbox.value = str(int(100*teamdata.NumOff/len(teamdata.Matches))) + "%"
                elif Textbox.type == "pdef": Textbox.value = str(int(100*teamdata.NumDef/len(teamdata.Matches))) + "%"
                elif Textbox.type == "past": Textbox.value = str(int(100*teamdata.NumAst/len(teamdata.Matches))) + "%"
                elif Textbox.type == "aoff": Textbox.value = str(teamdata.AvgOff)
                elif Textbox.type == "adef": Textbox.value = str(teamdata.AvgDef)
                elif Textbox.type == "aast": Textbox.value = str(teamdata.AvgAst)
                elif Textbox.type == "atot": Textbox.value = str(teamdata.Avg_TScore)
                elif Textbox.type == "woff": Textbox.value = str(teamdata.Avg_WOScore)
                elif Textbox.type == "wdef": Textbox.value = str(teamdata.Avg_WDScore)
                elif Textbox.type == "wast": Textbox.value = str(teamdata.Avg_WAScore)
                elif Textbox.type == "hhyb": Textbox.value = str(int(100*teamdata.HadHyd/len(teamdata.Matches))) + "%"
                elif Textbox.type == "hlbg": Textbox.value = str(int(100*teamdata.HydLwrBrdg/len(teamdata.Matches))) + "%"
                elif Textbox.type == "hast": Textbox.value = str(int(100*teamdata.HydAssist/len(teamdata.Matches))) + "%"
                elif Textbox.type == "hoth": Textbox.value = str(int(100*teamdata.HydOther/len(teamdata.Matches))) + "%"
                elif Textbox.type == "ahyb": Textbox.value = str(int(sum(teamdata.HydScores)/len(teamdata.HydScores)))
                elif Textbox.type == "ahbt": Textbox.value = str(int(sum(teamdata.HydBBalls)/len(teamdata.HydBBalls)))
                elif Textbox.type == "ahmd": Textbox.value = str(int(sum(teamdata.HydMBalls)/len(teamdata.HydMBalls)))
                elif Textbox.type == "ahtp": Textbox.value = str(int(sum(teamdata.HydTBalls)/len(teamdata.HydTBalls)))
                elif Textbox.type == "wdis": Textbox.value = str(int(100*teamdata.Disabled/len(teamdata.Matches)))+"%"
                elif Textbox.type == "ndis": Textbox.value = str(teamdata.DisabledCount)
                elif Textbox.type == "publ": Textbox.value = str(int(sum(teamdata.BallsPU)/len(teamdata.BallsPU)))
                elif Textbox.type == "abal": Textbox.value = str(teamdata.AvgBalls)
                elif Textbox.type == "abot": Textbox.value = str(teamdata.AvgBottom)
                elif Textbox.type == "amid": Textbox.value = str(teamdata.AvgMiddle)
                elif Textbox.type == "atop": Textbox.value = str(teamdata.AvgTop)
                elif Textbox.type == "bgbn": Textbox.value = str(int(sum(teamdata.BrdgBalAmnt)/len(teamdata.BrdgBalAmnt))) if sum(teamdata.BrdgBalAmnt) else "None"
                elif Textbox.type == "atbs": Textbox.value = str(int(sum(teamdata.BrdgScores)/len(teamdata.Matches))) + "%"
                elif Textbox.type == "abrb": Textbox.value = str(int(100*teamdata.BrdgSuccess/len(teamdata.Matches))) + "%"
                elif Textbox.type == "atbb": Textbox.value = str(int(100*teamdata.TeamBrdgSuccess/len(teamdata.Matches))) + "%"
                elif Textbox.type == "acbb": Textbox.value = str(int(100*teamdata.COBrdgSuccess/len(teamdata.Matches))) + "%"
                elif Textbox.type == "atba": Textbox.value = str(int(100*teamdata.AttTeamBrdg/len(teamdata.Matches))) + "%"
                elif Textbox.type == "acba": Textbox.value = str(int(100*teamdata.AttCOBrdg/len(teamdata.Matches))) + "%"
                elif Textbox.type == "hrfl": Textbox.value = str(int(sum(teamdata.AvgRegFoul)/len(teamdata.AvgRegFoul)))
                elif Textbox.type == "htfl": Textbox.value = str(int(sum(teamdata.AvgTechFoul)/len(teamdata.AvgTechFoul)))
                elif Textbox.type == "atdf": Textbox.value = str(int(100*teamdata.Defense/len(teamdata.Matches))) + "%"
                elif Textbox.type == "atas": Textbox.value = str(int(100*teamdata.Assist/len(teamdata.Matches))) + "%"
                elif Textbox.type == "ryel": Textbox.value = str(int(100*teamdata.HadYellow/len(teamdata.Matches))) + "%"
                elif Textbox.type == "rred": Textbox.value = str(int(100*teamdata.HadRed/len(teamdata.Matches))) + "%"
                elif Textbox.type == "roff": Textbox.value = str(teamdata.off_rank)
                elif Textbox.type == "rdef": Textbox.value = str(teamdata.def_rank)
                elif Textbox.type == "rast": Textbox.value = str(teamdata.ast_rank)
                elif Textbox.type == "rtot": Textbox.value = str(teamdata.tot_rank)
                elif Textbox.type == "rhyb": Textbox.value = str(teamdata.hyb_rank)
                elif Textbox.type == "rtel": Textbox.value = str(teamdata.tel_rank)
                elif Textbox.type == "rbrd": Textbox.value = str(teamdata.brd_rank)
                
    if Tab1_Update:
        Tab1_Surface.fill(BGCOLOR)
        for Textbox in Tab1_TextBoxes:
            Textbox.draw(Tab1_Surface)
        Tab1_Update = False
    screen.blit(Tab1_Surface,(INIT_X,INIT_Y))
    # see if a textbox needs to be drawn
    # -- this only occures if the mouse is hovering over the textbox
    for tbox in Tab1_TextBoxes:
        x = tbox.x+tbox.cw+(.5*tbox.th)+INIT_X
        y = tbox.y+.5*tbox.th+INIT_Y
        if x <= cmpos[0] <= x+tbox.w+.5*tbox.th and y <= cmpos[1] <= y+tbox.size+.5*tbox.th-10 and teamdata != 0:
            if tbox.type=="aoff":
                # Get information for offensive score
                i = 0
                lx = []
                ly = []
                print teamdata.OScores
                while i <len(teamdata.OScores):
                    lx.append(i+1)
                    ly.append(teamdata.OScores[i])
                    i += 1
                display = lreg(lx,ly)
                display.get_ab()
                draw = display.get_image(300,300,(255,255,255),(0,0,0))
                screen.blit(draw,(x+tbox.w+.5*tbox.th,y+tbox.size+.5*tbox.th-10))
            elif tbox.type=="adef" and teamdata.NumDef:
                # Get information for defensive score
                i = 0
                lx = []
                ly = []
                print teamdata.DScores
                while i <len(teamdata.DScores):
                    lx.append(i+1)
                    ly.append(teamdata.DScores[i])
                    i += 1
                display = lreg(lx,ly)
                display.get_ab()
                draw = display.get_image(300,300,(255,255,255),(0,0,0))
                screen.blit(draw,(x+tbox.w+.5*tbox.th,y+tbox.size+.5*tbox.th-10))
            elif tbox.type=="aast" and teamdata.NumAst:
                # Get information for assistive score
                i = 0
                lx = []
                ly = []
                print teamdata.AScores
                while i <len(teamdata.AScores):
                    lx.append(i+1)
                    ly.append(teamdata.AScores[i])
                    i += 1
                display = lreg(lx,ly)
                display.get_ab()
                draw = display.get_image(300,300,(255,255,255),(0,0,0))
                screen.blit(draw,(x+tbox.w+.5*tbox.th,y+tbox.size+.5*tbox.th-10))
            elif tbox.type=="atot" and (teamdata.NumOff or teamdata.NumDef or teamdata.NumOff):
                # Get information for total score
                i = 0
                lx = []
                ly = []
                print teamdata.TScores
                while i <len(teamdata.TScores):
                    lx.append(i+1)
                    ly.append(teamdata.TScores[i])
                    i += 1
                display = lreg(lx,ly)
                display.get_ab()
                draw = display.get_image(300,300,(255,255,255),(0,0,0))
                screen.blit(draw,(x+tbox.w+.5*tbox.th,y+tbox.size+.5*tbox.th-10))

    # Check for changes requested from clicks
    for Textbox in Tab1_TextBoxes:
        x = TextBox.x+Textbox.cw+Textbox.th+INIT_X
        y = TextBox.y+.5*Textbox.th+INIT_Y
        if x+Textbox.w+.5*Textbox.th >= mpos[0] >= x and y+Textbox.size+.5*Textbox.th-10 >= mpos[1] >= y:
            texbox.clicked()

#---------------------------------------------------------------------------------------------------------
# Team Pit Data Function
# -- allows the user to access pit data for specific teams
#---------------------------------------------------------------------------------------------------------
def team_pitdata():
    global Teams
    global Tab2_TextBoxes, Tab2_Update, Tab2_Surface
    global tabnum, mpos, teamdata
    global BGCOLOR, INIT_X, INIT_Y
    TNums = []
    
    for Team in Teams:
        TNums.append(Team.Number)
    TNums.sort()
    if len(TNums) and tabnum == 0:          #only for first time
        TNum = TNums[0]
    for Textbox in Tab2_TextBoxes:
        if Textbox.type == "tnum":
            if not Textbox.value:
                try:
                    if not int(Textbox.value): Textbox.value = tabnum       # if value is 0, make it current team number
                    elif int(Textbox.value) != tabnum:                      # number has been changed, do updates
                        if int(Textbox.value) in TNums:
                            tabnum = int(Textbox.value)
                            Tab2_Update = True
                        else:
                            tabnum = TNums[0] if len(TNums) else 0          # number not found, reset to first team number
                except:
                    #not a number
                    print "Error: non-numerical characters inserted for team number"

            Textbox.value = tabnum

    if Tab2_Update:
        print "Update in tab2 (pitdata) requested"
        teamdata = 0
        for Team in Teams:
            teamdata = Team if Team.Number == tabnum else 0
        if teamdata:
            for Textbox in Tab2_Textboxes:
                if   Textbox.type == "rbln": Textbox.value = str(teamdata.RobotLength)
                elif Textbox.type == "rbwd": Textbox.value = str(teamdata.RobotWidth)
                elif Textbox.type == "rbhg": Textbox.value = str(teamdata.RobotHeight)
                elif Textbox.type == "rbwg": Textbox.value = str(teamdata.RobotWeight)
                elif Textbox.type == "frcr": Textbox.value = str(teamdata.Clearance)
                elif Textbox.type == "wlsc": Textbox.value = str(teamdata.Spacing)
                elif Textbox.type == "bgmc": Textbox.value = str(teamdata.BridgeMech)
                elif Textbox.type == "sdbg": Textbox.value = str(teamdata.SlideBrdg)
                elif Textbox.type == "blsn": Textbox.value = str(teamdata.BalSensor)
                elif Textbox.type == "sggr": Textbox.value = str(teamdata.ShiftGear)
                elif Textbox.type == "dvsy": Textbox.value = str(teamdata.DriveSystem)
                elif Textbox.type == "cnms": Textbox.value = str(teamdata.CenterMass)
                elif Textbox.type == "dri1": Textbox.value = str(teamdata.Drive1)
                elif Textbox.type == "exp1": Textbox.value = str(teamdata.exp1)
                elif Textbox.type == "dri2": Textbox.value = str(teamdata.Drive2)
                elif Textbox.type == "exp2": Textbox.value = str(teamdata.exp2)
                elif Textbox.type == "dri3": Textbox.value = str(teamdata.Drive3)
                elif Textbox.type == "exp3": Textbox.value = str(teamdata.exp3)

    if Tab2_Update:
        Tab2_Surface.fill(BGCOLOR)
        for Textbox in Tab2_TextBoxes:
            Textbox.draw(Tab2_Surface)
        Tab2_Update = False
    screen.blit(Tab2_Surface,(INIT_X,INIT_Y))
    
    # linear regression and other stuff
    for Textbox in Tab2_Textboxes:
        x = TextBox.x+Textbox.cw+Textbox.th+INIT_X
        y = TextBox.y+.5*Textbox.th+INIT_Y
        if x+Textbox.w+.5*Textbox.th >= mpos[0] >= x and y+Textbox.size+.5*Textbox.th-10 >= mpos[1] >= y:
            texbox.clicked()

#---------------------------------------------------------------------------------------------------------
# Ratings Functions
# -- delivers team ratings based upon user preferences
#---------------------------------------------------------------------------------------------------------
def ratings():
    global Teams
    global screen, HEIGHT, BGCOLOR, TXCOLOR
    global Tab3_Scrolls, Tab3_Buttons
    global off_rank, def_rank, ast_rank, tot_rank
    run = False

    # draw avg offensive score
    font = pygame.font.Font(None,20)
    text = font.render("Avg Offensive Score",True,TXCOLOR,BGCOLOR)
    screen.blit(text(160,65))
    # draw Avg Off
    font = pygame.font.Font(None,20)
    x = 0
    y = 0
    i = 0
    Tab3_Scrolls[0].surface.fill(BGCOLOR)
    for rank in off_rank:
        i += 1
        text = font.render("#"+str(i)+"--Team "+str(rank[1])+": "+str(rank[0]),True,TXCOLOR,BGCOLOR)
        Tab3_Scrolls[0].surface.blit(text,(x,y))
        y+=20
        for Team in Teams:
            if Team.Number == rank[1]: Team.off_rank = i
    Tab3_Scrolls[0].draw(screen)
    pygame.draw.line(screen,(0,0,0),(302,65),(302,HEIGHT),1)

    # draw average defensive
    font = pygame.font.Font(None,20)
    text = font.render("Avg Defensive Score",True,TXCOLOR,BGCOLOR)
    screen.blit(text,(305,65))
    # draw avg def
    x = 0
    y = 0
    i = 0
    Tab3_Scrolls[1].surface.fill(BGCOLOR)
    for rank in def_rank:
        i += 1
        text = font.render("#"+str(i)+"--Team "+str(rank[1])+": "+str(rank[0]),True,TXCOLOR,BGCOLOR)
        Tab3_Scrolls[1].surface.blit(text,(x,y))
        y+=20
        for Team in Teams:
            if Team.Number == rank[1]: Team.def_rank = i
    Tab3_Scrolls[1].draw(screen)
    pygame.draw.line(screen,(0,0,0),(450,65),(450,HEIGHT),1)

    # draw avgerage assistive score
    font = pygame.font.Font(None,20)
    text = font.render("Avg Assistive Score",True,TXCOLOR,BGCOLOR)
    screen.blit(text,(460,65))
    # draw avg ast
    x = 0
    y = 0
    i = 0
    Tab3_Scrolls[2].surface.fill(BGCOLOR)
    for rank in ast_rank:
        i += 1
        text = font.render("#"+str(i)+"--Team "+str(rank[1])+": "+str(rank[0]),True,TXCOLOR,BGCOLOR)
        Tab3_Scrolls[2].surface.blit(text,(x,y))
        y+=20
        for Team in Teams:
            if Team.Number == rank[1]: Team.ast_rank = i
    Tab3_Scrolls[2].draw(screen)
    pygame.draw.line(screen,(0,0,0),(605,65),(605,HEIGHT),1)

    # draw avgerage total score
    font = pygame.font.Font(None,20)
    text = font.render("Avg Total Score",True,TXCOLOR,BGCOLOR)
    screen.blit(text,(607,65))
    # draw avg tot
    x = 0
    y = 0
    i = 0
    Tab3_Scrolls[3].surface.fill(BGCOLOR)
    for rank in tot_rank:
        i += 1
        text = font.render("#"+str(i)+"--Team "+str(rank[1])+": "+str(rank[0]),True,TXCOLOR,BGCOLOR)
        Tab3_Scrolls[3].surface.blit(text,(x,y))
        y+=20
        for Team in Teams:
            if Team.Number == rank[1]: Team.tot_rank = i
    Tab3_Scrolls[3].draw(screen)
    pygame.draw.line(screen,(0,0,0),(750,65),(750,HEIGHT),1)

    #update scroller buttons
    for button in Tab3_Buttons:
        button.draw(screen)
    for button in Tab3_Buttons:
        if mbut[0] == 1:
            if button.x<=cmpos[0]<=button.x+button.w and button.y<=cmpos[1]<=button.y+button.h:
                if button.type == "ofup":
                    Tab3_Scrolls[0].update(True)
                elif button.type == "ofdo":
                    Tab3_Scrolls[0].update(False)
                if button.type == "deup":
                    Tab3_Scrolls[1].update(True)
                elif button.type == "dedo":
                    Tab3_Scrolls[1].update(False)
                if button.type == "atup":
                    Tab3_Scrolls[2].update(True)
                elif button.type == "atdo":
                    Tab3_Scrolls[2].update(False)
                if button.type == "toup":
                    Tab3_Scrolls[3].update(True)
                elif button.type == "todo":
                    Tab3_Scrolls[3].update(False)

#---------------------------------------------------------------------------------------------------------
# Ratings 2 Function
# -- delivers team ratings based off user preferances
#---------------------------------------------------------------------------------------------------------
def ratings2():
    global Teams
    global screen, HEIGHT, BGCOLOR, TXCOLOR
    global Tab4_Scrolls, Tab4_Buttons
    global hyb_rank, off_rank, brd_rank
    run = False

    # draw avgerage Hybrid score
    font = pygame.font.Font(None,20)
    text = font.render("Avg Hybrid Score",True,TXCOLOR,BGCOLOR)
    screen.blit(text,(160,65))
    # draw avg hyd
    x = 0
    y = 0
    i = 0
    Tab4_Scrolls[0].surface.fill(BGCOLOR)
    for rank in hyb_rank:
        i += 1
        text = font.render("#"+str(i)+"--Team "+str(rank[1])+": "+str(rank[0]),True,TXCOLOR,BGCOLOR)
        Tab4_Scrolls[0].surface.blit(text,(x,y))
        y+=20
        for Team in Teams:
            if Team.Number == rank[1]: Team.hyd_rank = i
    Tab4_Scrolls[0].draw(screen)
    pygame.draw.line(screen,(0,0,0),(302,65),(302,HEIGHT),1)
    
    # draw avgerage tele score
    font = pygame.font.Font(None,20)
    text = font.render("Avg Tele Score",True,TXCOLOR,BGCOLOR)
    screen.blit(text,(305,65))
    # draw avg tel
    x = 0
    y = 0
    i = 0
    Tab4_Scrolls[1].surface.fill(BGCOLOR)
    for rank in tel_rank:
        i += 1
        text = font.render("#"+str(i)+"--Team "+str(rank[1])+": "+str(rank[0]),True,TXCOLOR,BGCOLOR)
        Tab4_Scrolls[1].surface.blit(text,(x,y))
        y+=20
        for Team in Teams:
            if Team.Number == rank[1]: Team.tel_rank = i
    Tab4_Scrolls[1].draw(screen)
    pygame.draw.line(screen,(0,0,0),(450,65),(450,HEIGHT),1)

    # draw avgerage bridge score
    font = pygame.font.Font(None,20)
    text = font.render("Avg Bridge Score",True,TXCOLOR,BGCOLOR)
    screen.blit(text,(460,65))
    # draw avg brd
    x = 0
    y = 0
    i = 0
    Tab4_Scrolls[2].surface.fill(BGCOLOR)
    for rank in brd_rank:
        i += 1
        text = font.render("#"+str(i)+"--Team "+str(rank[1])+": "+str(rank[0]),True,TXCOLOR,BGCOLOR)
        Tab4_Scrolls[2].surface.blit(text,(x,y))
        y+=20
        for Team in Teams:
            if Team.Number == rank[1]: Team.brd_rank = i
    Tab4_Scrolls[2].draw(screen)
    pygame.draw.line(screen,(0,0,0),(605,65),(605,HEIGHT),1)

    # draw buttons
    for button in Tab4_Buttons:
        button.draw(screen)
    for button in Tab4_Buttons:
        if button.x<=cmpos[0]<=button.x+button.w and button.y<=cmpos[1]<=button.y+button.h:
            if button.type == "hyup":
                Tab4_Scrolls[0].update(True)
            elif button.type == "hydo":
                Tab4_Scrolls[0].update(False)
            if button.type == "teup":
                Tab4_Scrolls[1].update(True)
            elif button.type == "tedo":
                Tab4_Scrolls[1].update(False)
            if button.type == "bgup":
                Tab4_Scrolls[2].update(True)
            elif button.type == "bgdo":
                Tab4_Scrolls[2].update(False)

#---------------------------------------------------------------------------------------------------------
# Search Function
# -- allows user to access teams based off specific preferances
#---------------------------------------------------------------------------------------------------------

                
                
    
