# Thomas Deng
# CS251 Project 5
# display3D.py

import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
import math
import random
import view
import data
import analysis
import numpy as np
import sys
from tkinter import messagebox
import logging
import pyscreenshot as ImageGrab
import csv
import classification as cf
from timeit import default_timer as timer

# create a class to build and manage the display
class DisplayApp:
    
    #initializer
    def __init__(self, width, height):
        
        # create a tk object, which is the root window
        self.root = tk.Tk()
        
        # width and height of the window
        self.initDx = width
        self.initDy = height

        # set up the geometry for the window
        self.root.geometry( "%dx%d+50+30" % (self.initDx, self.initDy) )

        # set the title of the window
        self.root.title("3D Data Display by Thomas Deng")

        # set the max and min size of the window for resizing
        self.root.minsize( 400, 800 )
        self.root.maxsize( 1600, 900 )
                
        # to handle opening multiple files
        self.filenameActive = tk.StringVar()
        self.filenameActive = None
        self.filenames = []
        self.filename_data = {}
                
        # setup the menus
        self.buildMenus()
        
        # build the controls
        self.buildControls()
        
        # build the stats frame
        self.buildStatsFrame()
                
        # build the objects on the Canvas
        self.buildCanvas()
        
        # bring the window to the front
        self.root.lift()
        
        # set up the key bindings
        self.setBindings()
        
        #set up the View object
        self.view = view.View()
        
        #set up the axis endpoints
        self.start_x = np.matrix([0, 0, 0, 1])
        self.end_x = np.matrix([1, 0, 0, 1])
        self.start_y = np.matrix([0, 0, 0, 1])
        self.end_y = np.matrix([0, 1, 0, 1])
        self.start_z = np.matrix([0, 0, 0, 1])
        self.end_z = np.matrix([0, 0, 1, 1])       
                
        #set up the list of axes
        self.axes = []
        self.ticks = [] # the ticks along the axes
        # build the axes
        self.buildAxes()
        
        #the x, y, z that are actually drawn on the canvas
        self.ids = []
        self.buildIDs()
        
        #the baselines to give user an visual cue about how much they're scaled in
        self.baselines= []
        self.baseline_data = {}
        self.buildBaselines()
        
        #regression line
        self.regression = None #the actual tkinter widget itself (can be a plane or a line)
        self.regressionCoords = None
        self.regressionHistory = []
        self.line_info = None #all the details about the linear regression
        
        #data structures to contain PCAs
        #a list of names of the PCA
        self.PCAnames = []
        #a list of PCAdata instances (in the same order as PCAnames)
        self.PCAs = []
        #see if the PCA frame is now enabled or ever initialized
        self.PCAenabled = False
        self.PCAinitialized = False
        
        #data structures to contain clusters
        #a list of names of the clusters
        self.clusternames = []
        #a list of ClusterData instances (in the same order as clusternames)
        self.clusters = []
        #see if the Cluster frame is now enabled or ever initialized
        self.clusterenabled = False
        self.clusterinitialized = False
        #colors used for clustering 
        self.colors = {}
        self.colors[0] = "#ff0000"
        self.colors[1] = "#ffff00"
        self.colors[2] = "#00ff00"
        self.colors[3] = "#0000ff"
        self.colors[4] = "#ff6600"
        self.colors[5] = "#ffcc99"
        self.colors[6] = "#993300"
        self.colors[7] = "#666633"
        self.colors[8] = "#00ccff"
        self.colors[9] = "#ccccff"
        #a list of rectangles that represent the means
        self.means_objects = []
        #a dictionary that maps each rectangle to its coords
        self.means_coords= {}
        
        #boolean values for classify frame
        self.classifyenabled = False
        self.classifyinitialized = False
        
        # set up the application state
        self.objects = [] # a list of oval objects representing the data points
        self.obj_coords = {} # a dict that maps the ovals to the (x,y,z,1) coords they are at
        self.obj_size = {} # a dict that maps the ovals to the size they have
        self.data = None
        self.baseClick = None # used to keep track of mouse movement
        self.baseClick2 = None
        self.baseClick3 = None
        
        self.boo1 = False
        
        #fields for speed parameters
        self.t_speed = 1 #translate
        self.r_speed = 1 #rotate
        self.s_speed = 1 #scale
        
        self.buildLegends() #set up the legends canvases
        
        # set up the mini window
        self.pointsDict = {} # a dictionary that maps the points from the main canvas to points on the mini window
        self.buildCanvas2() #build the mini canvas
        
        #gets the geometries for the canvas
        self.root.update_idletasks() 
        self.baseScreenSize = [self.canvas.winfo_width(),self.canvas.winfo_height()] #used to keep track of the screen size
        
        #meaning the app is newly created
        self.isFresh = True
        
        #classification data
        self.trainData = None
        self.testData = None
        self.trainPCA = None
        self.testPCA = None
        self.classify_result = None
        
        self.usingMainData = True
            
    
    #build the menu in top left corner
    def buildMenus(self):
        
        # create a new menu
        self.menu = tk.Menu(self.root)

        # set the root menu to our new menu
        self.root.config(menu = self.menu)

        # create a variable to hold the individual menus
        self.menulist = []

        # create a file menu
        filemenu = tk.Menu( self.menu )
        self.menu.add_cascade( label = "Menu", menu = filemenu )
        self.menulist.append(filemenu)


        # menu text for the elements
        menutext = [ ['Open', '-', 
        'Translate Speed', 'Rotate Speed', 'Scale Speed', '-', 
        'Create Regression', 'Read Regression File', 'Regression History', 'Save Regression' ,'-',
        'Show/hide PCA', '-', 
        'Show/hide Cluster', '-',
        'Show/hide Classification', '-',
        'Save Canvas', '-',
        'Quit'] ]

        # menu callback functions
        menucmd = [ [self.handleOpen, None, 
        self.changeTranslateSpeed, self.changeRotateSpeed, self.changeScaleSpeed, None, 
        self.handleLinearRegression, self.readRegression, self.handleRegressionHistory, self.saveRegression, None,
        self.handlePCA, None,
        self.handleCluster, None,
        self.handleClassify, None,  
        self.captureCanvas, None, 
        self.handleQuit]  ]
        
        # build the menu elements and callbacks
        for i in range( len( self.menulist ) ):
            for j in range( len( menutext[i]) ):
                if menutext[i][j] != '-':
                    self.menulist[i].add_command( label = menutext[i][j], command=menucmd[i][j] )
                else:
                    self.menulist[i].add_separator()

    # create the canvas object
    def buildCanvas(self):
        self.canvas = tk.Canvas( self.root, width=self.initDx, height=self.initDy, background = "#dbb997" )
        self.canvas.pack( expand=tk.YES, fill=tk.BOTH )
        return    

    # build a frame and put controls in it
    def buildControls(self):
        
        # make a master control frame
        self.cntlframemaster = tk.Frame(self.root)
        self.cntlframemaster.pack(side=tk.RIGHT, padx=2, pady=2, fill=tk.Y)
        # make a control frame
        self.cntlframe = tk.Frame(self.cntlframemaster)
        self.cntlframe.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.Y)

        sep = tk.Frame( self.cntlframe, height=self.initDy, width=2, bd=1, relief=tk.SUNKEN )
        sep.pack( side=tk.LEFT, padx = 2, pady = 2, fill=tk.Y)
        
        self.classifyframe = tk.Frame(self.cntlframemaster)
        self.classifyframe.pack(side=tk.RIGHT, padx=2, pady=2, fill=tk.Y) 
        
        self.clusterframe = tk.Frame(self.cntlframemaster)
        self.clusterframe.pack(side=tk.RIGHT, padx=2, pady=2, fill=tk.Y) 
        
        self.PCAframe = tk.Frame(self.cntlframemaster)
        self.PCAframe.pack(side=tk.RIGHT, padx=2, pady=2, fill=tk.Y)   

        # make thes buttons in the frame
        self.buttons = []
        
        #reset button
        self.buttons.append( ( 'reset', tk.Button( self.cntlframe, text="Reset", command=self.handleResetButton, width=5 ) ) )
        self.buttons[-1][1].pack(side=tk.TOP, pady = 20)  # default side is top
        
        l1 = tk.Label( self.cntlframe, text="Current Files", width=20 )
        l1.pack(side = tk.TOP)

        #list box widget that allows user to choose which file
        self.filelist = tk.Listbox(self.cntlframe,exportselection=0, height = 4, selectmode = tk.SINGLE)
        self.filelist.pack(side=tk.TOP, pady = 5)
        
        #apply button
        self.buttons.append( ( 'apply', tk.Button( self.cntlframe, text="Apply", 
                               command=self.addDataFromFile, width=10)))
        self.buttons[-1][1].pack(side=tk.TOP, pady = 10)

        # the frame that will contain the data selecting widgets for plotting data
        self.plotframe = tk.Frame(self.cntlframe)
        self.plotframe.pack(side=tk.TOP, padx=2, pady=15, fill=tk.Y)

        return
    
    # build the mini window    
    def buildCanvas2(self): 
        self.canvas2 = tk.Canvas( self.cntlframe, width=230, height=230, background = "#aaaaaa" )
        self.canvas2.pack( side = tk.BOTTOM, fill=tk.BOTH, pady = 5, padx = 15)
        self.view2 = view.View()
        self.view2.screen = np.array([200., 200.])
        self.view2.offset = np.array([20., 20.])

        #set up labels            
        label = tk.Label( self.cntlframe, text="Mini Window", width=20 )
        label.pack( side=tk.BOTTOM, pady = 4 )  
        
        #add labels to tell user about the aligning key commands            
#         label2 = tk.Label( self.cntlframe, text="<Control-j>: \nLook perpendicular into the XY plane", width=30 )
#         label2.pack( side=tk.TOP, pady = 4 )    
#         label3 = tk.Label( self.cntlframe, text="<Control-k>: \nLook perpendicular into the XZ plane", width=30 )
#         label3.pack( side=tk.TOP, pady = 4 )    
#         label4 = tk.Label( self.cntlframe, text="<Control-l>: \nLook perpendicular into the YZ plane", width=30 )
#         label4.pack( side=tk.TOP, pady = 4 )
    
    #build the legends (size and color)
    def buildLegends(self):
        self.legendsframe = tk.Frame(self.cntlframe)
        self.legendsframe.pack(side = tk.BOTTOM, fill=tk.BOTH, pady = 10)
        #add in the labels
        tk.Label(self.legendsframe, text="min").grid(row=0,column=0)
        tk.Label(self.legendsframe, text="max").grid(row=0,column=1)
        tk.Label(self.legendsframe, text="min").grid(row=0,column=2)
        tk.Label(self.legendsframe, text="max").grid(row=0,column=3)
        #set up size canvas
        self.canvas_for_size = tk.Canvas(self.legendsframe, width=100, height=40, background = '#aaaaaa')
        self.canvas_for_size.grid(row=1, column=0, columnspan=2, padx = 15, pady = 5)
        #add in 3 ovals to illustrate
        self.canvas_for_size.create_oval(20-2, 20-2, 20+2, 20+2, fill = '#ffffff', outline='') #an oval to represent small
        self.canvas_for_size.create_oval(45-6, 20-6, 45+6, 20+6, fill = '#ffffff', outline='') #an oval to represent medium
        self.canvas_for_size.create_oval(80-10, 20-10, 80+10, 20+10, fill = '#ffffff', outline='') #an oval to represent large
        #set up color canvas
        self.canvas_for_color = tk.Canvas(self.legendsframe, width=100, height=40, background = '#000000')
        self.canvas_for_color.grid(row=1, column=2, columnspan=2, padx = 15, pady = 5)
        #add in 100 lines of different colors to create the gradient effect
        for i in range(0,105):
            rgb = self.generateColor(i/105)
            self.canvas_for_color.create_line(i,0,i,45, fill = rgb)
            
    def buildStatsFrame(self):
        # make a stats displaying frame at the bottom
        self.statsframe = tk.Frame(self.root)
        self.statsframe.pack(side=tk.BOTTOM, padx=2, pady=2, fill=tk.Y)
        # use a label to set the size of the right panel
        self.statsLabels = []
        title = tk.Label( self.statsframe, text="Stats Analysis")
        title.grid( row = 0, column = 0, columnspan = 5, pady = 5)   
        
    # create the axis line objects in their default location
    def buildAxes(self):
        vtm = self.view.build()
        #add x axes
        x1 = (vtm * self.start_x.T).T
        x2 = (vtm * self.end_x.T).T
        self.axes.append(self.canvas.create_line(x1.item(0),x1.item(1),x2.item(0),x2.item(1), fill = "#ff0000", width = 3))
        #add y axes
        y1 = (vtm * self.start_y.T).T
        y2 = (vtm * self.end_y.T).T
        self.axes.append(self.canvas.create_line(y1.item(0),y1.item(1),y2.item(0),y2.item(1),fill = "#0000ff", width = 3))
        #add z axes
        z1 = (vtm * self.start_z.T).T
        z2 = (vtm * self.end_z.T).T
        self.axes.append(self.canvas.create_line(z1.item(0),z1.item(1),z2.item(0),z2.item(1),fill = "#ffff00", width = 3))
        
        #add in the ticks in x
        c1 = (vtm * (self.start_x + np.matrix([0.25,-0.03,0,0])).T).T
        t1 = self.canvas.create_text(c1.item(0), c1.item(1), text = "", fill = "#ff0000")
        c2 = (vtm * (self.start_x + np.matrix([0.5,-0.03,0,0])).T).T
        t2 = self.canvas.create_text(c2.item(0), c2.item(1), text = "", fill = "#ff0000")
        c3 = (vtm * (self.start_x + np.matrix([0.75,-0.03,0,0])).T).T
        t3 = self.canvas.create_text(c3.item(0), c3.item(1), text = "", fill = "#ff0000")
        self.ticks.append([(t1,self.start_x + np.matrix([0.25,-0.03,0,0])), (t2,self.start_x + np.matrix([0.5,-0.03,0,0])), (t3,self.start_x + np.matrix([0.75,-0.03,0,0]))])
        #add in the ticks in y
        c4 = (vtm * (self.start_y + np.matrix([-0.06,0.25,0,0])).T).T
        t4 = self.canvas.create_text(c4.item(0), c4.item(1), text = "", fill = "#0000ff")
        c5 = (vtm * (self.start_y + np.matrix([-0.06,0.5,0,0])).T).T
        t5 = self.canvas.create_text(c5.item(0), c5.item(1), text = "", fill = "#0000ff")
        c6 = (vtm * (self.start_y + np.matrix([-0.06,0.75,0,0])).T).T
        t6 = self.canvas.create_text(c6.item(0), c6.item(1), text = "", fill = "#0000ff")
        self.ticks.append([(t4,self.start_y + np.matrix([-0.06,0.25,0,0])), (t5,self.start_y + np.matrix([-0.06,0.5,0,0])), (t6,self.start_y + np.matrix([-0.06,0.75,0,0]))])
        #add in the ticks in z
        c7 = (vtm * (self.start_z + np.matrix([-0.06,0,0.25,0])).T).T
        t7 = self.canvas.create_text(c7.item(0), c7.item(1), text = "", fill = "#ffff00")
        c8 = (vtm * (self.start_z + np.matrix([-0.06,0,0.5,0])).T).T
        t8 = self.canvas.create_text(c8.item(0), c8.item(1), text = "", fill = "#ffff00")
        c9 = (vtm * (self.start_z + np.matrix([-0.06,0,0.75,0])).T).T
        t9 = self.canvas.create_text(c9.item(0), c9.item(1), text = "", fill = "#ffff00")
        self.ticks.append([(t7,self.start_z + np.matrix([-0.06,0,0.25,0])), (t8,self.start_z + np.matrix([-0.06,0,0.5,0])), (t9,self.start_z + np.matrix([-0.06,0,0.75,0]))])
        
    # modify the endpoints of the axes to their new location
    def updateAxes(self):
        vtm = self.view.build()
        #update x axes
        x1 = (vtm * self.start_x.T).T
        x2 = (vtm * self.end_x.T).T
        self.canvas.coords(self.axes[0],x1.item(0),x1.item(1),x2.item(0),x2.item(1))
        #update y axes
        y1 = (vtm * self.start_y.T).T
        y2 = (vtm * self.end_y.T).T
        self.canvas.coords(self.axes[1],y1.item(0),y1.item(1),y2.item(0),y2.item(1))
        #update z axes
        z1 = (vtm * self.start_z.T).T
        z2 = (vtm * self.end_z.T).T
        self.canvas.coords(self.axes[2],z1.item(0),z1.item(1),z2.item(0),z2.item(1))
        
        #update ticks position
        for i in range(3):
            for t in self.ticks[i]:
                c = t[1]
                c1 = (vtm * c.T).T
                #print ("new c1", c1)
                self.canvas.coords(t[0],c1.item(0),c1.item(1))
                self.canvas.lift(t[0])
            #self.canvas.itemconfig(t,text = "Yes!")
            
    
    # build the x, y, z that are drawn on the screen    
    def buildIDs(self):
        vtm = self.view.build()
        x = (vtm * (self.end_x + np.matrix([0.02,0,0,0])).T).T
        idx = self.canvas.create_text(x.item(0), x.item(1), text = "X", fill = "#ff0000")
        self.ids.append(idx)
        y = (vtm * (self.end_y + np.matrix([0,0.02,0,0])).T).T
        idy = self.canvas.create_text(y.item(0), y.item(1), text = "Y", fill = "#0000ff")
        self.ids.append(idy) 
        z = (vtm * (self.end_z + np.matrix([0,0,0.02,0])).T).T
        idz = self.canvas.create_text(z.item(0), z.item(1), text = "Z", fill = "#ffff00")
        self.ids.append(idz)
    
    #update the x, y, z    
    def updateIDs(self):
        vtm = self.view.build()
        x = (vtm * (self.end_x + np.matrix([0.02,0,0,0])).T).T
        self.canvas.coords(self.ids[0], x.item(0), x.item(1))
        y = (vtm * (self.end_y + np.matrix([0,0.02,0,0])).T).T
        self.canvas.coords(self.ids[1], y.item(0), y.item(1))
        z = (vtm * (self.end_z + np.matrix([0,0,0.02,0])).T).T
        self.canvas.coords(self.ids[2], z.item(0), z.item(1))
    
    # build the base lines    
    def buildBaselines(self):
        bls = []
        vtm = self.view.build()
        for i in range(1,5):
            for j in range(1,5):
                bls.append((np.matrix([0.22*i, 0, 0.22*j, 1]),np.matrix([0.22*i, 1, 0.22*j, 1])))
                bls.append((np.matrix([0, 0.22*i, 0.22*j, 1]),np.matrix([1, 0.22*i, 0.22*j, 1])))
                bls.append((np.matrix([0.22*i, 0.22*j, 0, 1]),np.matrix([0.22*i, 0.22*j, 1, 1])))
        
        for line in bls:
            start = (vtm * line[0].T).T
            end = (vtm * line[1].T).T
            l = self.canvas.create_line(start.item(0),start.item(1),end.item(0),end.item(1), fill = "#d4d5d6")
            self.baselines.append(l) #store the line
            self.baseline_data[l] = line #store the original coordinates
        
        p1 = (vtm * np.matrix([0,0,0,1]).T).T
        p2 = (vtm * np.matrix([1,0,0,1]).T).T
        p3 = (vtm * np.matrix([0,0,1,1]).T).T
        p4 = (vtm * np.matrix([1,0,1,1]).T).T
        self.base = self.canvas.create_polygon(p1.item(0),p1.item(1),p2.item(0),
        p2.item(1),p3.item(0),p3.item(1),p4.item(0),p4.item(1), fill="#444444")
    
    #update the baselines and the base plain             
    def updateBaselines(self):
        vtm = self.view.build()
        for l in self.baselines:
            line = self.baseline_data[l]
            start = (vtm * line[0].T).T
            end = (vtm * line[1].T).T
            self.canvas.coords(l, start.item(0),start.item(1),end.item(0),end.item(1))
                        
        p1 = (vtm * np.matrix([0,0,0,1]).T).T
        p2 = (vtm * np.matrix([1,0,0,1]).T).T
        p3 = (vtm * np.matrix([1,0,1,1]).T).T
        p4 = (vtm * np.matrix([0,0,1,1]).T).T
        self.canvas.coords(self.base, p1.item(0),p1.item(1),p2.item(0),
        p2.item(1),p3.item(0),p3.item(1),p4.item(0),p4.item(1))
        
        #print ("vpn: ", self.view.get_vpn())
        if self.view.vpn[1] < 0: #if viewing from below then raise the base plain to top level
            self.canvas.lift(self.base)
        else:
            self.canvas.lower(self.base)    
        
          
        
    # adds data from filename
    # read the file to a Data object
    # then create widgets on the screen to let user choose which dimensions to plot on which columns     
    def addDataFromFile(self, filename=None):
        #if a filename is inputted
        if filename != None:
            if filename == self.filenameActive: #if the file is currently active
                return #don't need to read nothing
            self.filenameActive = filename
        #if no filename is inputted
        else:
            #gets the currently selected filename from listbox
            #will only proceed if there is a filename selected
            try:
                fileindex = self.filelist.curselection()[0]
                if self.filenameActive == self.filenames[fileindex]: #skip the entire procedure if the filename to read is currently active
                    return
                self.filenameActive = self.filenames[fileindex]
                print ("filename is: ", self.filenameActive)
            except:
                return
        
        #clear the previously added graphical elements
        self.clear()     
        
        #clear existing PCAs
        self.clearPCA()
        #clear existing clusters
        self.clearClusters()
        
        #reset the view
        self.view.reset()
        self.update()    
        
        self.data = data.Data(self.filenameActive) #creates a Data object that collects data from file
        self.headers = []
        for i in range(self.data.get_num_dimensions()):
            if self.data.types[i] == 'numeric': #if the type is numeric
                self.headers.append(self.data.headers[i])     
        
        headersNone = self.headers[:] #the same list of numeric headers but with 'None' added
        headersNone.insert(0,"None")
    
        
        #build the option menu widgets accordingly
        #set up the variables
        self.header_X = tk.StringVar() # the string for the selected header for X axis
        self.header_X.set(self.headers[0]) #default: use 1st numeric column for x axis 
        self.header_Y = tk.StringVar()
        self.header_Y.set(self.headers[1]) #default: use 2st numeric column for y axis --- Here I assumed there are at least 2 numeric columns in the data set
        self.header_Z = tk.StringVar()
        self.header_Z.set('None') #default: use None for z axis
        self.header_Color = tk.StringVar()
        self.header_Color.set('None') #default: use None for color axis
        self.header_Size = tk.StringVar()
        self.header_Size.set('None') #default: use None for color axis
        
        #clear the previously added menus (if there are any)
        try:
            for i in range(5):
                #self.datamenus[i][1].grid_forget()
                self.datamenus[i][1].destroy()
                #self.datalabels[i].grid_forget()
                self.datalabels[i].destroy()               
        except:
            pass
        
        self.datalabels = []
        #add in the labels
        self.datalabels.append(tk.Label(self.plotframe, text="X-axis"))
        self.datalabels[-1].grid(row=0)
        self.datalabels.append(tk.Label(self.plotframe, text="Y-axis"))
        self.datalabels[-1].grid(row=1)
        self.datalabels.append(tk.Label(self.plotframe, text="Z-axis (Optional)"))
        self.datalabels[-1].grid(row=2)
        self.datalabels.append(tk.Label(self.plotframe, text="Color-axis (Optional)"))
        self.datalabels[-1].grid(row=3)
        self.datalabels.append(tk.Label(self.plotframe, text="Size-axis (Optional)"))
        self.datalabels[-1].grid(row=4)

        self.datamenus = []
        #add in new menus
        self.datamenus.append(('x-axis', tk.OptionMenu(self.plotframe, self.header_X, *self.headers)))
        self.datamenus[-1][1].grid(row=0, column=1)
        self.datamenus.append(('y-axis', tk.OptionMenu(self.plotframe, self.header_Y, *self.headers)))
        self.datamenus[-1][1].grid(row=1, column=1)
        self.datamenus.append(('z-axis', tk.OptionMenu(self.plotframe, self.header_Z, *headersNone)))
        self.datamenus[-1][1].grid(row=2, column=1)
        self.datamenus.append(('color-axis', tk.OptionMenu(self.plotframe, self.header_Color, *headersNone)))
        self.datamenus[-1][1].grid(row=3, column=1)
        self.datamenus.append(('size-axis', tk.OptionMenu(self.plotframe, self.header_Size, *headersNone)))
        self.datamenus[-1][1].grid(row=4, column=1)
        
        # add plot data button (if it hasn't been initiated)
        if self.isFresh:
            self.buttons.append( ( 'plot data', tk.Button( self.plotframe, text="Plot Data", 
                                   command=self.handlePlotData, width=15)))
            self.buttons[-1][1].grid(row = 5, columnspan = 2, pady = 15)
        self.isFresh = False
    
    # plot data according to the selections made by the user
    # builds self.data_to_plot which is a matrix that holds all selected data that needs to be plotted (x, y, z, color, size)        
    def plotData(self, event=None):  
        self.view.reset() #reset the view
        self.update()
        
        #clear the previously added points
        self.clear()
        
        if self.data == None:
            return
        vtm = self.view.build()
        vtm2 = self.view2.build()         
        
        # get the list of headers specified the user and generate a 5 column matrix such that:
        # column 1 is the x values
        # column 2 is the y values
        # column 3 is the z values (0 if user don't want this dimension)
        # column 4 is the color values (0 if user don't want this dimension)
        # column 5 is the size values (0 if user don't want this dimension)
        hds = []
        
        hds.append(self.header_X.get())
        self.canvas.itemconfig(self.ids[0],text = hds[0]) #update the x axis id 
        # update the ticks for x
        xmin = analysis.data_range(self.data,hds[-1:])[0][0]
        xmax = analysis.data_range(self.data,hds[-1:])[0][1]
        for i in range(len(self.ticks[0])):
            t = self.ticks[0][i]
            val = str(round((i+1)/4 * (xmax-xmin) + xmin,2))
            self.canvas.itemconfig(t[0],text = val)
              
        hds.append(self.header_Y.get())
        self.canvas.itemconfig(self.ids[1],text = hds[1]) #update the y axis id 
        # update the ticks for y
        ymin = analysis.data_range(self.data,hds[-1:])[0][0]
        ymax = analysis.data_range(self.data,hds[-1:])[0][1]
        for i in range(len(self.ticks[1])):
            t = self.ticks[1][i]
            val = str(round((i+1)/4 * (ymax-ymin) + ymin,2))
            self.canvas.itemconfig(t[0],text = val)
        
        #for optional dimensions
        if self.header_Z.get() != 'None': #append only if the header is not selected to None in the option menu
            hds.append(self.header_Z.get())
            self.canvas.itemconfig(self.ids[2],text = hds[2]) #update the z axis id
            # update the ticks for z
            zmin = analysis.data_range(self.data,hds[-1:])[0][0]
            zmax = analysis.data_range(self.data,hds[-1:])[0][1]
            for i in range(len(self.ticks[2])):
                t = self.ticks[2][i]
                val = str(round((i+1)/4 * (zmax-zmin) + zmin,2))
                self.canvas.itemconfig(t[0],text = val)
        else:
            self.canvas.itemconfig(self.ids[2],text = "Z")
        
        #color                 
        if self.header_Color.get() != 'None':
            hds.append(self.header_Color.get())      
        #size     
        if self.header_Size.get() != 'None':
            hds.append(self.header_Size.get())   
               
        self.data_to_plot = analysis.normalize_columns_separately(self.data,hds) #select data from the original data to build a new matrix of corresponding coordinates
        if self.header_Z.get() == 'None': # if z-header is not selected
            # insert a column of place holders with default 0 at column index 2
            self.data_to_plot = np.insert(self.data_to_plot, 2, 0, axis=1)
        if self.header_Color.get() == 'None': # if color-header is not selected
            # insert a column of place holders with default 0 at column index 3
            self.data_to_plot = np.insert(self.data_to_plot, 3, 0, axis=1)
        if self.header_Size.get() == 'None': # if size-header is not selected
            # insert a column of place holders with default 0 at column index 4
            self.data_to_plot = np.insert(self.data_to_plot, 4, 0, axis=1)        
                
        print (self.data_to_plot)
        
        # add in the stats labels to statsframe
        if self.header_X.get() != 'None':
            stats_x = "X axis ("+hds[0]+") : " + "\nmean: " + str(round(analysis.mean(self.data,[hds[0]])[0],2)) + "\nmedian: " + str(round(analysis.median(self.data,[hds[0]])[0],2)) + "\nrange: " + str(analysis.data_range(self.data,[hds[0]])[0]) + "\nstdev: " + str(round(analysis.stdev(self.data,[hds[0]])[0],2))
            self.statsLabels.append(tk.Label( self.statsframe, text=stats_x)) #add in another label representing x column in statsframe 
            self.statsLabels[-1].grid( row = 1, column = 0, padx = 10, pady = 3)
        if self.header_Y.get() != 'None':
            stats_y = "Y axis ("+hds[1]+") : " + "\nmean: " + str(round(analysis.mean(self.data,[hds[1]])[0],2)) + "\nmedian: " + str(round(analysis.median(self.data,[hds[1]])[0],2)) + "\nrange: " + str(analysis.data_range(self.data,[hds[1]])[0]) + "\nstdev: " + str(round(analysis.stdev(self.data,[hds[1]])[0],2))
            self.statsLabels.append(tk.Label( self.statsframe, text=stats_y)) #add in another label representing y column in statsframe 
            self.statsLabels[-1].grid( row = 1, column = 1, padx = 10, pady = 3)
        if self.header_Z.get() != 'None':
            header_z = self.header_Z.get()
            stats_z = "Z axis ("+header_z+") : " + "\nmean: " + str(round(analysis.mean(self.data,[header_z])[0],2)) + "\nmedian: " + str(round(analysis.median(self.data,[header_z])[0],2)) + "\nrange: " + str(analysis.data_range(self.data,[header_z])[0]) + "\nstdev: " + str(round(analysis.stdev(self.data,[header_z])[0],2))
            self.statsLabels.append(tk.Label( self.statsframe, text=stats_z)) #add in another label representing z column in statsframe 
            self.statsLabels[-1].grid( row = 1, column = 2, pady = 3)
        if self.header_Color.get() != 'None':
            header_color = self.header_Color.get()
            stats_color = "Color axis ("+header_color+") : " + "\nmean: " + str(round(analysis.mean(self.data,[header_color])[0],2)) + "\nmedian: " + str(round(analysis.median(self.data,[header_color])[0],2)) + "\nrange: " + str(analysis.data_range(self.data,[header_color])[0]) + "\nstdev: " + str(round(analysis.stdev(self.data,[header_color])[0],2))
            self.statsLabels.append(tk.Label( self.statsframe, text=stats_color)) #add in another label representing color column in statsframe 
            self.statsLabels[-1].grid( row = 1, column = 3, pady = 3)
        if self.header_Size.get() != 'None':
            header_size = self.header_Size.get()
            stats_size = "Size axis ("+header_size+") : " + "\nmean: " + str(round(analysis.mean(self.data,[header_size])[0],2)) + "\nmedian: " + str(round(analysis.median(self.data,[header_size])[0],2)) + "\nrange: " + str(analysis.data_range(self.data,[header_size])[0]) + "\nstdev: " + str(round(analysis.stdev(self.data,[header_size])[0],2))
            self.statsLabels.append(tk.Label( self.statsframe, text=stats_size)) #add in another label representing size column in statsframe 
            self.statsLabels[-1].grid( row = 1, column = 4, pady = 3)
        
        #normalize the 4th and 5th columns
        print ("normalized 4", self.normalize(self.data_to_plot[:,3]))
        self.data_to_plot[:,3] = self.normalize(self.data_to_plot[:,3])
        self.data_to_plot[:,4] = self.normalize(self.data_to_plot[:,4])
        
        print ("after normalization", self.data_to_plot)
                    
        for i in range (self.data.get_num_points()): # for each point
            c = self.data_to_plot[i,0:3].tolist()[0] #get a point (with dimensions as the user specifies)
            c.append(1) #append normal homogeneous coordinate
            arr = np.matrix(c)
            arr1 = (vtm * arr.T).T
            arr2 = (vtm2 * arr.T).T #coords for mini map
            
            #add to main map
            #generate color    
            if self.header_Color.get() == 'None': #if user don't want color axis
                rgb = "#FFFFFF"
            else:
                rgb = self.generateColor(self.data_to_plot.item(i,3)) #generate color from the color value of the point
            #generate size
            if self.header_Size.get() != 'None': #if user does want size axis
                size = self.generateSize(self.data_to_plot.item(i,4))
            else:
                size = 5
            #build an oval accordingly
            pt = self.canvas.create_oval(arr1[0,0]-size, arr1[0,1]-size, arr1[0,0]+size, arr1[0,1]+size, fill = rgb, outline='')
            self.objects.append(pt) #append the oval
            self.obj_coords[pt] = np.matrix(c) # append the oval-coords mapping
            self.obj_size[pt] = size # append the oval-size mapping
            
            #add to mini map
            pt2 = self.canvas2.create_oval(arr2[0,0]-3, arr2[0,1]-3, arr2[0,0]+3, arr2[0,1]+3, fill = '#f8ff35', outline='')
            self.pointsDict[pt] = pt2 #link the oval in the big map with the oval in the small map
            
        self.usingMainData = True    
    
    #calculate sigmoid
    def sigmoid(self, x,alpha,beta):
        return 1 / (1 + math.exp(-alpha*(x-beta)))
    
    #takes in an numpy array and does sigmoid normalization
    def normalize(self,array):
        std = np.std(array)
        if std != 0:
            alpha = 1/std #use 1/std as alpha
        else: #happens only when all values are identical
            alpha = 1 #set alpha to 1
        beta = np.mean(array) #use mean as beta
        for x in np.nditer(array, op_flags=['readwrite']):
#             print ("x is: ", x)
#             print ("sigmoid x is: ", self.sigmoid(x, alpha, beta))
            x[...] = self.sigmoid(x, alpha, beta)
        return array
        
    
    #assumes a param between 0 and 1
    #small -- blue (0,0,255)
    #large -- orange (255,165,0)    
    def generateColor(self, param):
        r = int(255*param)
        g = int(165*param)
        b = int(255*(1-param))
        rgb = "#%02x%02x%02x" % (r,g,b)
        return rgb
        
    #assumes a param between 0 and 1
    #smallest -- 2
    #largest -- 10
    def generateSize(self, param):
        size = 2 + param * 8
        return size
    
    # updates the positions of every oval       
    def updatePoints(self):
        if len(self.objects) < 1:
            return
        vtm = self.view.build()
        for obj in self.objects:
            coords = self.obj_coords[obj]
            arr = (vtm * coords.T).T # the screen coordinates
            size = self.obj_size[obj]
            self.canvas.coords(obj,arr[0,0]-size, arr[0,1]-size, arr[0,0]+size, arr[0,1]+size)
            #check whether a point is currently viewable
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
            if arr.item(0) < 0 or arr.item(0) > width or arr.item(1) < 0 or arr.item(1) > height: #meaning it's out of scope
                self.canvas2.itemconfig(self.pointsDict[obj], fill='#000000')
            else:
                self.canvas2.itemconfig(self.pointsDict[obj], fill='#f8ff35')
                
    # update the means if necessary
    def updateMeans(self):
        if len(self.means_objects) < 1:
            return
        vtm = self.view.build()
        for obj in self.means_objects:
            coords = self.means_coords[obj]
            arr = (vtm * coords.T).T # the screen coordinates
            size = 6
            self.canvas.coords(obj,arr[0,0]-size, arr[0,1]-size, arr[0,0]+size, arr[0,1]+size)            
    
    #update the regressions
    def updateFits(self):
        if self.regression == None:
            return
        vtm = self.view.build()
        #if self.regression is a line
        print ("regression coords size: ", len(self.regressionCoords))
        if len(self.regressionCoords) == 2:
            start = self.regressionCoords[0] #start and end are each np array that represent a point
            end = self.regressionCoords[1]
            start_1 = (vtm * start.T).T
            end_1 = (vtm * end.T).T
            self.canvas.coords(self.regression, start_1.item(0),start_1.item(1),end_1.item(0),end_1.item(1))
        #if self.regression is a plane
        elif len(self.regressionCoords) == 4:            
            #build the 4 points that defines the plane
            point1 = self.regressionCoords[0]
            point2 = self.regressionCoords[1]
            point3 = self.regressionCoords[2]
            point4 = self.regressionCoords[3]
            
            #feed them into vtm
            p1 = (vtm * point1.T).T
            p2 = (vtm * point2.T).T
            p3 = (vtm * point3.T).T
            p4 = (vtm * point4.T).T
            
            self.canvas.coords(self.regression, p1.item(0),p1.item(1),p2.item(0),p2.item(1),p3.item(0),p3.item(1),p4.item(0),p4.item(1)) 
            self.canvas.lift(self.regression)
            
    # update everything that needs to be updated with user actions
    def update(self):
        self.updatePoints()   
        self.updateIDs()
        self.updateBaselines()
        self.updateAxes()
        self.updateFits()
        self.updateMeans()     
            
    # sets the bindings        
    def setBindings(self):
        self.root.bind( '<Button-1>', self.handleButton1 )
        self.root.bind( '<Button-2>', self.handleButton2 )
        self.root.bind( '<Control-Button-1>', self.handleButton2 )
        self.root.bind( '<ButtonRelease-2>', self.handleButtonRelease2 )
        self.root.bind( '<Control-ButtonRelease-1>', self.handleButtonRelease2 )
        self.root.bind( '<KeyRelease-Control_L>', self.handleButtonRelease2 )
        self.root.bind( '<Button-3>', self.handleButton3 )
        self.root.bind( '<ButtonRelease-3>', self.handleButtonRelease3 )
        self.root.bind( '<B1-Motion>', self.handleButton1Motion )
        self.root.bind( '<B2-Motion>', self.handleButton2Motion )
        self.root.bind( '<Control-B1-Motion>', self.handleButton2Motion )
        self.root.bind( '<B3-Motion>', self.handleButton3Motion )
        self.root.bind( '<Control-q>', self.handleQuit )
        self.root.bind( '<Control-o>', self.handleModO )
        self.root.bind( '<Control-r>', self.handleResetButton )
        self.root.bind( '<Control-j>', self.alignXY )
        self.root.bind( '<Control-k>', self.alignXZ )
        self.root.bind( '<Control-l>', self.alignYZ )
        self.root.bind( '<Control-o>', self.handleOpen )
        self.root.bind( '<Control-c>', self.clearEverything )
        self.canvas.bind( '<Configure>', self.handleResize )
        return
    
    #handle adding a new linear regression
    def handleLinearRegression(self, event=None):
        if self.data == None: #proceed only if data are already read from the file
            return
        dialog = MyDialog3(self.root, self.headers, "Choose the independent and dependent variables")    
        if dialog.userCancelled(): #disregard if user cancelled
            return
        #add in the regression features to the self.regressionHistory
        #self.regressionHistory will be a list of lists [ind_vars, dep_var, name of regression, name of data set]
        input = dialog.getInput()
        input.append(self.filenameActive)
        self.regressionHistory.append(input)
        self.ind_headers = input[0]
        self.dep_header = input[1]
        self.regressionNameActive = input[2]
        print ("ind headers: ", self.ind_headers)
        print ("dep headers: ", self.dep_header)
        
        self.buildLinearRegression()
        print ("Current regression history", self.regressionHistory)
    
    #handle reading from a past regression record   
    def handleRegressionHistory(self, event=None):
        if self.data == None: #proceed only if data are already read from the file
            return
        regressions = []
        for reg in self.regressionHistory:
            regressions.append(reg[2]) #append the name of the regression
        dialog = MyDialog4(self.root, regressions, "Choose from the saved selections")
        if dialog.userCancelled():
            return
        else:
            selected = dialog.getInput()
            for reg in self.regressionHistory:
                if selected == reg[2]: #if this is the one user specified
                    self.ind_headers = reg[0]
                    self.dep_header = reg[1]
                    if self.filenameActive != reg[3]: #if the current filename is not the filename of the specified linear regression
                        self.addDataFromFile(reg[3])
                    break
                    
        print ("ind headers: ", self.ind_headers)
        print ("dep headers: ", self.dep_header)               
        
        self.buildLinearRegression()                          
    
    #build the linear regression line and the points involved
    def buildLinearRegression(self):
        #generate the vtms
        self.view.reset()
        self.update()
        vtm = self.view.build()
        vtm2 = self.view2.build()
        
        #clear the previously added points
        self.clear()               
        
        #matrix to contain the columns of points used for regression
        if len(self.ind_headers) == 1: #if no second independent variable specified
            regression_matrix = analysis.normalize_columns_separately(self.data,[self.ind_headers[0], self.dep_header])
            regression_matrix = np.insert(np.insert(regression_matrix, 2, 0, axis=1), 3, 1, axis =1) #add a column of 0 at index 2 and a column of 1 at index 3 
        else: #if second independent variable specified
            regression_matrix = analysis.normalize_columns_separately(self.data,[self.ind_headers[0], self.dep_header, self.ind_headers[1]]) #note that the dependent column will be the y-column
            regression_matrix = np.insert(regression_matrix, 3, 1, axis =1)
        # print ("regression matrix: ", regression_matrix)
        
        #update the axes
        self.canvas.itemconfig(self.ids[0],text = self.ind_headers[0]) #update the x axis id
        self.canvas.itemconfig(self.ids[1],text = self.dep_header) #update the y axis id
        if len(self.ind_headers) > 1: #if there are more than 1 independent headers
            self.canvas.itemconfig(self.ids[2],text = self.ind_headers[1]) #update the z axis id to be the 2nd ind variable
        else:
            self.canvas.itemconfig(self.ids[2],text = 'Z') #reset the z axis id to be 'z'
        
        #add in points
        for i in range (self.data.get_num_points()): # for each point
            arr = regression_matrix[i, :] #the i-th row of the regression matrix
            arr1 = (vtm * arr.T).T #coords for the canvas
            arr2 = (vtm2 * arr.T).T #coords for mini map           
            #build ovals accordingly
            pt = self.canvas.create_oval(arr1[0,0]-5, arr1[0,1]-5, arr1[0,0]+5, arr1[0,1]+5, fill = '#ffffff', outline='')
            self.objects.append(pt) #append the oval
            self.obj_coords[pt] = arr # append the oval-coords mapping
            self.obj_size[pt] = 5 # append the oval-size mapping
            
            #add to mini map
            pt2 = self.canvas2.create_oval(arr2[0,0]-3, arr2[0,1]-3, arr2[0,0]+3, arr2[0,1]+3, fill = '#f8ff35', outline='')
            self.pointsDict[pt] = pt2 #link the oval in the big map with the oval in the small map
        
        #add in the regression
        #here I called it a "line" but it can actually be a plane
        self.line_info = analysis.linear_regression( self.data, self.ind_headers, self.dep_header)

        m0 = self.line_info[0][0].item(0) #m0 is the slope for y = m0 * x
        print ("m0 is: ", m0)
        b = self.line_info[0][-1].item(0)
        print ("b is: ", b)
        xmin = self.line_info[5][0][0].item(0) #x represents the first independent variable
        xmax = self.line_info[5][0][1].item(0)
        ymin = self.line_info[5][-1][0].item(0)
        ymax = self.line_info[5][-1][1].item(0)
        
        # update the ticks for x
        for i in range(len(self.ticks[0])):
            t = self.ticks[0][i]
            val = str(round((i+1)/4 * (xmax-xmin) + xmin,2))
            self.canvas.itemconfig(t[0],text = val)
        # update the ticks for y
        for i in range(len(self.ticks[1])):
            t = self.ticks[1][i]
            val = str(round((i+1)/4 * (ymax-ymin) + ymin,2))
            self.canvas.itemconfig(t[0],text = val) 
            
        if len(self.ind_headers) > 1: #if there are more than 1 independent headers
            #the slope of y against z
            m1 = self.line_info[0][1].item(0)
            #print ("m1 is: ", m1)
            zmin = self.line_info[5][1][0].item(0)
            zmax = self.line_info[5][1][1].item(0)
            
            # update the ticks for z
            for i in range(len(self.ticks[2])):
                t = self.ticks[2][i]
                val = str(round((i+1)/4 * (zmax-zmin) + zmin,2))
                self.canvas.itemconfig(t[0],text = val) 
            
            #the y value when x and z are both 0
            y00 = ((xmin * m0 + zmin * m1 + b) - ymin)/(ymax - ymin)
            #the y value when x is 1 and z is 0
            y10 = ((xmax * m0 + zmin * m1 + b) - ymin)/(ymax - ymin)
            #the y value when x is 1 and z is 0
            y01 = ((xmin * m0 + zmax * m1 + b) - ymin)/(ymax - ymin)
            #the y value when x and z are both 1
            y11 = ((xmax * m0 + zmax * m1 + b) - ymin)/(ymax - ymin)
            
            #build the 4 points that defines the plane
            point1 = np.matrix([0,y00,0,1])
            point2 = np.matrix([1,y10,0,1])
            point3 = np.matrix([1,y11,1,1])
            point4 = np.matrix([0,y01,1,1])
            
            #feed them into vtm
            p1 = (vtm * point1.T).T
            p2 = (vtm * point2.T).T
            p3 = (vtm * point3.T).T
            p4 = (vtm * point4.T).T
            
            plane = self.canvas.create_polygon(p1.item(0),p1.item(1),p2.item(0),
            p2.item(1),p3.item(0),p3.item(1),p4.item(0),p4.item(1), fill="#00ff00", stipple="gray25")
            self.canvas.lift(plane)
            self.regression = plane
            self.regressionCoords = (point1,point2,point3,point4)
            
        else:
            y0 = ((xmin * m0 + b) - ymin)/(ymax - ymin)
            y1 = ((xmax * m0 + b) - ymin)/(ymax - ymin)
            start = np.matrix([0,y0,0,1]) #(x,y,z,1) of the start of the line
            end = np.matrix([1,y1,0,1]) #(x,y,z,1) of the end of the line
            start_1 = (vtm * start.T).T
            end_1 = (vtm * end.T).T
            line = self.canvas.create_line(start_1.item(0),start_1.item(1),end_1.item(0),end_1.item(1), fill = "#00ff00", width = 2)
            self.regression = line
            self.regressionCoords = (start,end)
            
        # add in the stats labels to statsframe (this time also display regression data)
        stats_x = "X-independent1 (" + self.ind_headers[0] + ") : " + "\nmean: " + str(round(analysis.mean(self.data,[self.ind_headers[0]])[0],2))+ "\nmedian: " + str(round(analysis.median(self.data,[self.ind_headers[0]])[0],2)) + "\nrange: " + str(analysis.data_range(self.data,[self.ind_headers[0]])[0]) + "\nstdev: " + str(round(analysis.stdev(self.data,[self.ind_headers[0]])[0],2))
        # add in the 1st independent 
        self.statsLabels.append(tk.Label( self.statsframe, text=stats_x)) #add in another label representing ind1 in statsframe 
        self.statsLabels[-1].grid( row = 1, column = 0, padx = 10, pady = 3)
        # if there is a second ind variable
        if len(self.ind_headers) > 1:
            stats_z = "Z-independent2 (" + self.ind_headers[1] + ") : " + "\nmean: " + str(round(analysis.mean(self.data,[self.ind_headers[1]])[0],2))+ "\nmedian: " + str(round(analysis.median(self.data,[self.ind_headers[1]])[0],2)) + "\nrange: " + str(analysis.data_range(self.data,[self.ind_headers[1]])[0]) + "\nstdev: " + str(round(analysis.stdev(self.data,[self.ind_headers[1]])[0],2))
            self.statsLabels.append(tk.Label( self.statsframe, text=stats_z)) #add in another label representing ind2 in statsframe 
            self.statsLabels[-1].grid( row = 1, column = 1, padx = 10, pady = 3)
        # add in the dependent variable
        stats_y = "Y-dependent (" + self.dep_header + ") : " + "\nmean: " + str(round(analysis.mean(self.data,[self.dep_header])[0],2))+ "\nmedian: " + str(round(analysis.median(self.data,[self.dep_header])[0],2)) + "\nrange: " + str(analysis.data_range(self.data,[self.dep_header])[0]) + "\nstdev: " + str(round(analysis.stdev(self.data,[self.dep_header])[0],2))
        self.statsLabels.append(tk.Label( self.statsframe, text=stats_y)) #add in another label representing ind3 in statsframe
        self.statsLabels[-1].grid( row = 1, column = 2, padx = 10, pady = 3)
        # add in the regression stats
        stats_reg = "Regression: m0 = " + str(round(m0,2))
        if len(self.ind_headers) > 1:
            stats_reg += ", m1 = " + str(round(m1,2))
        #extract t value from line_info, change it into list and round its elements
        t = self.line_info[3].tolist()[0]
        for i in range(len(t)):
            t[i] = round(t[i],2)
        #extract p value from line_info, change it into list and round its elements
        p = self.line_info[4].tolist()[0]
        for i in range(len(p)):
            p[i] = round(p[i],2)
        stats_reg += ", b = " + str(round(b,2)) + ", sse = " + str(round(self.line_info[1].item(0),2)) + ", R^2 =  " + str(round(self.line_info[2].item(0),2)) + ", t = " + str(t) + ", p = " + str(p)
        self.statsLabels.append(tk.Label( self.statsframe, text=stats_reg))
        self.statsLabels[-1].grid( row = 2, column = 0, columnspan = 3, padx = 10, pady = 3)
        
    #handles building PCA frame
    def handlePCA(self, event = None):
        if self.PCAenabled == True: #disable the PCA feature, clear the frame if its already there, clear the data structures associated with PCA
            self.PCAframe.pack_forget() #destroy the frame too
            self.PCAenabled = False #set the boolean to be False
            return
        #else: enable the PCA feature       
        self.PCAframe.pack(side=tk.RIGHT, padx=2, pady=2, fill=tk.Y)  
        #if nothing has been initialized yet
        if self.PCAinitialized == False:
            sep = tk.Frame( self.PCAframe, height=self.initDy, width=2, bd=1, relief=tk.SUNKEN )
            sep.pack( side=tk.LEFT, padx = 2, pady = 2, fill=tk.Y)
            t = tk.Label( self.PCAframe, text="PCAnalysis")
            t.pack( side = tk.TOP, padx = 100, pady = 20)  
        
            self.b1 = tk.Button(self.PCAframe, text="Add New PCA", command=self.addNewPCA, width=15)
            self.b1.pack(side=tk.TOP, pady = 10, padx = 20)        
        
            self.PCAlist = tk.Listbox(self.PCAframe,exportselection=0, height = 4, selectmode=tk.SINGLE)
            self.PCAlist.pack(side=tk.TOP, padx = 2, pady = 15)
        
            self.b6 = tk.Button(self.PCAframe, text="Delete PCA", command=self.deletePCA, width=10)
            self.b6.pack(side=tk.TOP, pady = 10, padx = 20) 
        
            self.b2 = tk.Button(self.PCAframe, text="Project PCA", command=self.projectPCA, width=15)
            self.b2.pack(side=tk.TOP, pady = 10, padx = 20)
        
            self.b3 = tk.Button(self.PCAframe, text="View PCA Specs", command=self.displayPCAstats, width=15)
            self.b3.pack(side=tk.TOP, pady = 10, padx = 20)
        
            self.b4 = tk.Button(self.PCAframe, text="Save PCA to File", command=self.savePCAtofile, width=15)
            self.b4.pack(side=tk.TOP, pady = 10, padx = 20)
        
            self.b5 = tk.Button(self.PCAframe, text="Read PCA from File", command=self.readPCAfromfile, width=15)
            self.b5.pack(side=tk.TOP, pady = 10, padx = 20)
            
            self.PCAinitialized = True
        
        self.PCAenabled = True     
    
    #pop up a dialog for a new PCA
    def addNewPCA(self):
        if self.data == None: #proceed only if data are already read from the file
            messagebox.showwarning(
                "Data uninitialized", 
                "User must read in and apply a data file first before adding PCA"
            )
            return
        dialog = MyDialog7(self.root, self.headers, "Choose the columns for PCA")    
        if dialog.userCancelled(): #disregard if user cancelled
            return
        hds = dialog.getInput()[0]
        print ("received headers: ", hds)
        if dialog.getInput()[2] == "No":
            pcadata = analysis.pca( self.data, hds, False )
        else:
            pcadata = analysis.pca( self.data, hds )
        
        print("\nEigenvalues")
        print(pcadata.get_eigenvalues())
        print("\nEigenvectors")
        print(pcadata.get_eigenvectors())
        print("\nProjected Data")
        print(pcadata.select_data(pcadata.get_headers()))
        
        self.PCAs.append(pcadata)
        name = dialog.getInput()[1]
        self.PCAnames.append(name)
        self.PCAlist.insert(tk.END, name)
        self.PCAlist.selection_clear(0, tk.END)
        self.PCAlist.selection_set(tk.END)
    
    #delete a currently selected PCA
    def deletePCA(self):
        #make sure that there is a PCA selected before projecting
        try:
            index = self.PCAlist.curselection()[0]
            pcadata = self.PCAs[index]
        except:
            messagebox.showwarning(
                "Missing selection", 
                "User must select the PCA to delete"
            )
            return
        #delete
        self.PCAlist.delete(index)
        del self.PCAs[index]
        del self.PCAnames[index]      
    
    #project onto the PCAs
    def projectPCA(self, calledFromCluster = False):
        #make sure that there is a PCA selected before projecting
        try:
            index = self.PCAlist.curselection()[0]
            pcadata = self.PCAs[index]
        except:
            if not calledFromCluster:
                messagebox.showwarning(
                    "Missing selection", 
                    "User must create and specify the PCA before projecting"
                )
                return
            else: #if allow no PCA
                pcadata = data.Data() #then pcadata is a new data        
        
        K = 0
        #if called from cluster
        if calledFromCluster:
            index = self.clusterlist.curselection()[0]
            cdata = self.clusters[index] #get the cdata
            means = cdata.get_means()
            K = cdata.get_K()
            whiten = cdata.get_whiten()
        
        headers = pcadata.get_headers() + self.headers
        if not calledFromCluster:#if used for PCA projection
            dialog = MyDialog8(self.root, headers, "Choose the columns for PCA projection")
        else:
            dialog = MyDialog12(self.root, headers, "Choose the columns for clustering projection")    
        if dialog.userCancelled(): #disregard if user cancelled
            return
        selected = dialog.getInput()
        print("selected headers: ", selected)
        
        #start to work on the canvas drawing
        
        self.view.reset() #reset the view
        self.update()
        
        #clear the previously added points
        self.clear()
        vtm = self.view.build()
        vtm2 = self.view2.build()    
        
        # get the list of headers specified the user and generate a 5 column matrix such that:
        # column 1 is the x values
        # column 2 is the y values
        # column 3 is the z values (0 if user don't want this dimension)
        # column 4 is the color values (0 if user don't want this dimension)
        # column 5 is the size values (0 if user don't want this dimension)
        hds = selected
        
        self.canvas.itemconfig(self.ids[0],text = hds[0]) #update the x axis id 
        # update the ticks for x
        if hds[0] in pcadata.get_headers(): #if hds[0] is chosen from PCA0, PCA1...etc.
            xmin = analysis.data_range(pcadata,hds[0:1])[0][0]
            xmax = analysis.data_range(pcadata,hds[0:1])[0][1]
        else: #if hds[0] is chosen from original headers
            xmin = analysis.data_range(self.data,hds[0:1])[0][0]
            xmax = analysis.data_range(self.data,hds[0:1])[0][1]
        for i in range(len(self.ticks[0])):
            t = self.ticks[0][i]
            val = str(round((i+1)/4 * (xmax-xmin) + xmin,2))
            self.canvas.itemconfig(t[0],text = val)
              
        self.canvas.itemconfig(self.ids[1],text = hds[1]) #update the y axis id 
        # update the ticks for y
        if hds[1] in pcadata.get_headers():
            ymin = analysis.data_range(pcadata,hds[1:2])[0][0]
            ymax = analysis.data_range(pcadata,hds[1:2])[0][1]
        else:
            ymin = analysis.data_range(self.data,hds[1:2])[0][0]
            ymax = analysis.data_range(self.data,hds[1:2])[0][1]
        for i in range(len(self.ticks[1])):
            t = self.ticks[1][i]
            val = str(round((i+1)/4 * (ymax-ymin) + ymin,2))
            self.canvas.itemconfig(t[0],text = val)
        
        #for optional dimensions
        if hds[2] != 'None': #proceed only if the header is not selected to be None
            self.canvas.itemconfig(self.ids[2],text = hds[2]) #update the z axis id
            # update the ticks for z
            if hds[2] in pcadata.get_headers():
                zmin = analysis.data_range(pcadata,hds[2:3])[0][0]
                zmax = analysis.data_range(pcadata,hds[2:3])[0][1]
            else:
                zmin = analysis.data_range(self.data,hds[2:3])[0][0]
                zmax = analysis.data_range(self.data,hds[2:3])[0][1]
            for i in range(len(self.ticks[2])):
                t = self.ticks[2][i]
                val = str(round((i+1)/4 * (zmax-zmin) + zmin,2))
                self.canvas.itemconfig(t[0],text = val)
        else:
            self.canvas.itemconfig(self.ids[2],text = "Z")

        # select the columns according to the headers (for each header will check if it is a PCA header or an original header (assuming these two sets don't intersect), and select accordingly)
        temp = []
#         print ("means right before selecting PCA: ", means)
#         print ("the shape of means: ", np.shape(means))
#         print ("the ith column of means: ", means[:,i])
#         print ("the ith column of means I thought is: ", np.reshape(means[:,i],(K,1)))
        for i in range(len(hds)):
            h = hds[i]
            if h == 'None':
                continue
            elif h in pcadata.get_headers():
                ind = pcadata.header2col[h]
                col = pcadata.get_col(ind)
                if calledFromCluster: #if called from cluster then add in the means
                    std = np.std(col)
                    # print ("col: ", col, "means: ", means[:,ind])
                    try:
                        if whiten: #if was whitened then need to multiply by the std
                            col = np.vstack((col, std * np.reshape(means[:,i],(K,1))))
                        else:
                            col = np.vstack((col, np.reshape(means[:,i],(K,1))))
                    except:
                        col = np.vstack((col, np.zeros((K,1))))
                temp.append(col)
        
        # print("PCA original data is: ", pcadata.get_data())        
        #print("The Temp Is: ", temp)
        
        self.data_to_plot = np.empty((self.data.get_num_points() + K,0)) #create an empty matrix       
        
        #now the matrix temp is all the PCA columns (not including the columns from the original data)
        if len(temp) > 0: #if there are at least one col from PCA data
            for col in temp: #append all the columns to the empty matrix
                self.data_to_plot = np.hstack((self.data_to_plot, col))
            # print("Now the data is: ", self.data_to_plot)      
            #normalize the columns together
            min = np.amin(self.data_to_plot)
            self.data_to_plot -= min #shift the min to 0
            max = np.amax(self.data_to_plot)
            self.data_to_plot *= 1/max
        
        #now the PCA columns are normalized together
        
        #add in the separately-normalized columns from original data
        for i in range(len(hds)):
            if hds[i] in self.headers:
                ind = self.data.header2col[hds[i]]
                col = self.data.get_col(ind)
                if calledFromCluster: #if called from cluster then add in the means
                    std = np.std(col)
                    # print ("col: ", col, "means: ", means, "ind: ", ind)
                    try:#will success if there are enough dimensions for the mean (because the cluster might be done in 2d while user want to plot in 3D)
                        if whiten: #if was whitened then need to multiply by the std
                            col = np.vstack((col, std * np.reshape(means[:,i],(K,1))))
                        else:
                            col = np.vstack((col, np.reshape(means[:,i],(K,1))))
                    except:
                        col = np.vstack((col, np.zeros((K,1))))
                min = np.amin(col)
                col -= min #shift the min to 0
                max = np.amax(col)
                if max != 0:
                    col *= 1/max #make the max to be 1
                else:
                    pass #if max is 0 then don't change a thing
#                 print ("[i]: ", [i], "col: ", col)
#                 print ("before: ", self.data_to_plot)
                self.data_to_plot = np.insert(self.data_to_plot, [i], col, axis = 1)
#                 print ("executed for ", i)
#                 print ("after: ", self.data_to_plot)
            elif hds[i] == 'None':
                # insert a column of place holders with default 0 at column index i
                self.data_to_plot = np.insert(self.data_to_plot, i, 0, axis=1)
 
#         if hds[2] == 'None': # if z-header is not selected
#             # insert a column of place holders with default 0 at column index 2
#             self.data_to_plot = np.insert(self.data_to_plot, 2, 0, axis=1)
#         if hds[3] == 'None': # if color-header is not selected
#             # insert a column of place holders with default 0 at column index 3
#             self.data_to_plot = np.insert(self.data_to_plot, 3, 0, axis=1)
#         if hds[4] == 'None': # if size-header is not selected
#             # insert a column of place holders with default 0 at column index 4
#             self.data_to_plot = np.insert(self.data_to_plot, 4, 0, axis=1)        
                
        print ("data to plot: ", self.data_to_plot)
        
        #add in the stats labels to statsframe
        if hds[0] in pcadata.get_headers():
            data_obj = pcadata
        else:
            data_obj = self.data
        stats_x = "X axis ("+hds[0]+") : " + "\nmean: " + str(round(analysis.mean(data_obj,[hds[0]])[0],2)) + "\nmedian: " + str(round(analysis.median(data_obj,[hds[0]])[0],2)) + "\nrange: " + str([round(elem, 2) for elem in analysis.data_range(data_obj,[hds[0]])[0]]) + "\nstdev: " + str(round(analysis.stdev(data_obj,[hds[0]])[0],2))
        self.statsLabels.append(tk.Label( self.statsframe, text=stats_x)) #add in another label representing x column in statsframe 
        self.statsLabels[-1].grid( row = 1, column = 0, padx = 10, pady = 3)
        if hds[1] in pcadata.get_headers():
            data_obj = pcadata
        else:
            data_obj = self.data
        stats_y = "Y axis ("+hds[1]+") : " + "\nmean: " + str(round(analysis.mean(data_obj,[hds[1]])[0],2)) + "\nmedian: " + str(round(analysis.median(data_obj,[hds[1]])[0],2)) + "\nrange: " + str([round(elem, 2) for elem in analysis.data_range(data_obj,[hds[1]])[0]]) + "\nstdev: " + str(round(analysis.stdev(data_obj,[hds[1]])[0],2))
        self.statsLabels.append(tk.Label( self.statsframe, text=stats_y)) #add in another label representing y column in statsframe 
        self.statsLabels[-1].grid( row = 1, column = 1, padx = 10, pady = 3)
        if hds[2] != 'None':
            if hds[2] in pcadata.get_headers():
                data_obj = pcadata
            else:
                data_obj = self.data
            header_z = hds[2]
            stats_z = "Z axis ("+header_z+") : " + "\nmean: " + str(round(analysis.mean(data_obj,[header_z])[0],2)) + "\nmedian: " + str(round(analysis.median(data_obj,[header_z])[0],2)) + "\nrange: " + str([round(elem, 2) for elem in analysis.data_range(data_obj,[hds[2]])[0]]) + "\nstdev: " + str(round(analysis.stdev(data_obj,[header_z])[0],2))
            self.statsLabels.append(tk.Label( self.statsframe, text=stats_z)) #add in another label representing z column in statsframe 
            self.statsLabels[-1].grid( row = 1, column = 2, pady = 3)
        if hds[3] != 'None':
            if hds[3] in pcadata.get_headers():
                data_obj = pcadata
            else:
                data_obj = self.data
            header_color = hds[3]
            stats_color = "Color axis ("+header_color+") : " + "\nmean: " + str(round(analysis.mean(data_obj,[header_color])[0],2)) + "\nmedian: " + str(round(analysis.median(data_obj,[header_color])[0],2)) + "\nrange: " + str([round(elem, 2) for elem in analysis.data_range(data_obj,[hds[3]])[0]]) + "\nstdev: " + str(round(analysis.stdev(data_obj,[header_color])[0],2))
            self.statsLabels.append(tk.Label( self.statsframe, text=stats_color)) #add in another label representing color column in statsframe 
            self.statsLabels[-1].grid( row = 1, column = 3, pady = 3)
        if hds[4] != 'None':
            if hds[4] in pcadata.get_headers():
                data_obj = pcadata
            else:
                data_obj = self.data
            header_size = hds[4]
            stats_size = "Size axis ("+header_size+") : " + "\nmean: " + str(round(analysis.mean(data_obj,[header_size])[0],2)) + "\nmedian: " + str(round(analysis.median(data_obj,[header_size])[0],2)) + "\nrange: " + str([round(elem, 2) for elem in analysis.data_range(data_obj,[hds[4]])[0]]) + "\nstdev: " + str(round(analysis.stdev(data_obj,[header_size])[0],2))
            self.statsLabels.append(tk.Label( self.statsframe, text=stats_size)) #add in another label representing size column in statsframe 
            self.statsLabels[-1].grid( row = 1, column = 4, pady = 3)
        
        #normalize the 4th and 5th columns
        # print ("normalized 4", self.normalize(self.data_to_plot[:,3]))
        self.data_to_plot[:,3] = self.normalize(self.data_to_plot[:,3])
        self.data_to_plot[:,4] = self.normalize(self.data_to_plot[:,4])
        
        print ("after normalization", self.data_to_plot)         
        
        
        #add in the dots                        
        for i in range (self.data.get_num_points()): # for each point
            c = self.data_to_plot[i,0:3]
            shape = c.ndim
            if shape > 1: #there is a weird thing (why sometimes c is [a,b,c] and sometimes a is [[a,b,c]]) that I'm not quite getting, but checking this fixes the problem
                c = c.tolist()[0]
            else:
                c = c.tolist()
            c.append(1) #append normal homogeneous coordinate
            arr = np.matrix(c)
            arr1 = (vtm * arr.T).T
            arr2 = (vtm2 * arr.T).T #coords for mini map
            
            #add to main map
            #generate color    
            if hds[3] == 'None': #if user don't want color axis
                rgb = "#0000FF"
            else:
                rgb = self.generateColor(self.data_to_plot.item(i,3)) #generate color from the color value of the point
            #generate size
            if hds[4] != 'None': #if user does want size axis
                size = self.generateSize(self.data_to_plot.item(i,4))
            else:
                size = 5
                
            #build an oval accordingly
            pt = self.canvas.create_oval(arr1[0,0]-size, arr1[0,1]-size, arr1[0,0]+size, arr1[0,1]+size, fill = rgb, outline='')
            self.objects.append(pt) #append the oval
            self.obj_coords[pt] = np.matrix(c) # append the oval-coords mapping
            self.obj_size[pt] = size # append the oval-size mapping
            
            #add to mini map
            pt2 = self.canvas2.create_oval(arr2[0,0]-3, arr2[0,1]-3, arr2[0,0]+3, arr2[0,1]+3, fill = '#f8ff35', outline='')
            self.pointsDict[pt] = pt2 #link the oval in the big map with the oval in the small map
        
        #add in the means if necessary
        if calledFromCluster:
            length = np.shape(self.data_to_plot)[0]
            for i in range(length-K, length):
                c = self.data_to_plot[i,0:3]
                shape = c.ndim
                if shape > 1: #there is a weird thing (why sometimes c is [a,b,c] and sometimes a is [[a,b,c]]) that I'm not quite getting, but checking this fixes the problem
                    c = c.tolist()[0]
                else:
                    c = c.tolist()
                c.append(1) #append normal homogeneous coordinate
                arr = np.matrix(c)
                arr1 = (vtm * arr.T).T
                rect = self.canvas.create_rectangle(arr1[0,0]-6, arr1[0,1]-6, arr1[0,0]+6, arr1[0,1]+6, fill = rgb, outline='#ffffff',width = 2)
                self.means_objects.append(rect)
                self.means_coords[rect] = np.matrix(c)
                
        self.usingMainData = True        
        
    #display the stats of PCA, including eigenvalues and eigenvectors
    def displayPCAstats(self):
        #try to get the selection from the PCAlist
        try:
            index = self.PCAlist.curselection()[0]
            pcadata = self.PCAs[index]
        except:
            messagebox.showwarning(
                "Missing selection", 
                "User must create and specify the PCA before showing the specs"
            )
            return
        dialog = MyDialog9(self.root, pcadata, "Specs for this PCA")
    
    def savePCAtofile(self):
        #try to get the selection from the PCAlist
        try:
            index = self.PCAlist.curselection()[0]
            pcadata = self.PCAs[index]
        except:
            messagebox.showwarning(
                "Missing selection", 
                "User must create and specify the PCA before saving it"
            )
            return
        dialog = MyDialog6(self.root)
        if dialog.userCancelled():
            return
        else: 
            name = dialog.getInput()
        
        #build the content for the csv 
        content = []
        content.append(["Data set name", self.filenameActive])
        content.append(["PCA name", self.PCAnames[index]])
        content.append(["Evecs", "Evals", "Cumulative"]+pcadata.get_original_headers())
        size = pcadata.get_num_points()
        dim = pcadata.get_num_dimensions()
        evals = pcadata.get_eigenvalues()
        evecs = pcadata.get_eigenvectors()  
        sum_evals = np.sum(evals)
        #loop vertically through the dimension
        for i in range(dim):
            #the cumulative eigenvalues to i (inclusive)
            cumul = np.sum(evals[0:i+1])/sum_evals
            temp = [pcadata.get_headers()[i], evals[i], cumul] #this is a row
            for j in range(dim):
                temp.append(evecs.item(i,j)) #append the eigenvector
            content.append(temp)
        #print ("tolist: ", pcadata.get_original_means()[0].tolist())
        content.append(["Mean", '',''] + pcadata.get_original_means()[0].tolist()[0])
        content.append(["Projected Data"] + pcadata.get_headers())
        #loop vertically through the number of points
        for i in range(size):
            s = "Point " + str(i)
            content.append([s] + pcadata.get_data()[i,:].tolist()[0])          
        
        fp = open(name + ".csv", 'w+')
        csv_writer = csv.writer(fp, lineterminator='\n') 
        csv_writer.writerows(content)
        fp.close()    
     
    #read PCA from a pre-formatted .csv file    
    def readPCAfromfile(self):     
        fn = tk.filedialog.askopenfilename( parent=self.root,
        title='Choose a PCA file', initialdir='.' )
        # add the file name to self.filename and self.filelist (if the filename is not empty string)
        if fn == '':
            return        
        if not fn.endswith(".csv"): #the filename must end with .csv
            messagebox.showwarning(
            "Invalid filename", 
            "You must enter a filename that ends with '.csv'."
            )
            return
        fp = open(fn, 'rU')
        csv_reader = csv.reader( fp )
        num_rows = sum(1 for row in csv_reader)
        
        #try to parse info from the csv file
        #will work if the file is not properly formatted
        try:
            #start parsing
            fp = open(fn, 'rU')
            csv_reader = csv.reader( fp )
            line = next(csv_reader)
            self.addDataFromFile(line[1]) #read the data object from the file if necessary
            if line[1] not in self.filenames: #add in the filename to the list of filenames if necessary
                self.filenames.append(line[1])       
                self.filelist.insert(tk.END, line[1])
                self.filelist.selection_clear(0, tk.END)
                self.filelist.select_set(tk.END)
            line = next(csv_reader) #add in the PCA name to the PCA name list
            self.PCAnames.append(line[1])
            self.PCAlist.insert(tk.END, line[1]) #add also to the PCA list box
            self.PCAlist.selection_clear(0, tk.END)
            self.PCAlist.selection_set(tk.END)
            line = next(csv_reader)
            ori_headers = line[3:] #parse the original headers
            dim = len(ori_headers) #this is the number of eigen vectors
            evals = []
            evecs = []
            #parse the evals and evecs
            for i in range(dim):
                line = next(csv_reader)
                evals.append(float(line[1]))         
                evecs.append([float(elem) for elem in line[3:]])
            evals = np.array(evals)
            evecs = np.matrix(evecs)
            #parse the means
            line = next(csv_reader)
            means = np.matrix([float(elem) for elem in line[3:]])
            #parse the projected data
            num_points = num_rows-(dim+5) #that's how my csv is formatted
            pdata = []
            line = next(csv_reader)#skip a line
            for i in range(num_points):
                line = next(csv_reader)
                pdata.append([float(elem) for elem in line[1:dim+1]])
            pdata = np.matrix(pdata)
        
            #assemble the PCAData object
            pcadata = data.PCAData( pdata, evecs, evals, means, ori_headers )
            print("\nOriginal Data Headers")
            print(pcadata.get_original_headers())
            print("\nOriginal Data Means")
            print(pcadata.get_original_means())
            print("\nEigenvalues")
            print(pcadata.get_eigenvalues())
            print("\nEigenvectors")
            print(pcadata.get_eigenvectors())
            print("\nProjected Data")
            print(pcadata.select_data(pcadata.get_headers()))
            self.PCAs.append(pcadata)
        
        #if the format isn't right
        except:
            messagebox.showwarning(
            "Incorrect format", 
            "You must add the same csv file that is saved from this application."
            )
        
        
    #clear the existing PCAs, called when new file is read
    def clearPCA(self):
        try:
            self.PCAnames = []
            self.PCAs = []
            self.PCAlist.delete(0, tk.END)
        except:
            pass
    
    #handles setting up the classify frame
    def handleClassify(self, event = None):
        if self.classifyenabled == True: #disable the cluster feature, clear the frame if its already there, clear the data structures associated with cluster
            self.classifyframe.pack_forget() #destroy the frame too
            self.classifyenabled = False #set the boolean to be False
            return
        self.classifyframe.pack(side=tk.RIGHT, padx=2, pady=2, fill=tk.Y)
        if self.classifyinitialized == False:
            sep = tk.Frame( self.classifyframe, height=self.initDy, width=2, bd=1, relief=tk.SUNKEN )
            sep.pack( side=tk.LEFT, padx = 2, pady = 2, fill=tk.Y)
            t = tk.Label( self.classifyframe, text="Classification")
            t.pack( side = tk.TOP, padx = 100, pady = 20)
            self.b11 = tk.Button(self.classifyframe, text="Add Training Set", command=self.addTrain, width=15)
            self.b11.pack(side=tk.TOP, pady = 10, padx = 20)
            self.trainLabel = tk.Label( self.classifyframe, text="Train:")
            self.trainLabel.pack(side = tk.TOP)
            self.b12 = tk.Button(self.classifyframe, text="Add Testing Set", command=self.addTest, width=15)
            self.b12.pack(side=tk.TOP, pady = 10, padx = 20)
            self.testLabel = tk.Label( self.classifyframe, text="Test:")
            self.testLabel.pack(side = tk.TOP)           
            self.b13 = tk.Button(self.classifyframe, text="Pre-learning PCA", command=self.prePCA, width=15)
            self.b13.pack(side=tk.TOP, pady = 10, padx = 20)
            self.b14 = tk.Button(self.classifyframe, text="Make classification", command=self.addClassification, width=15)
            self.b14.pack(side=tk.TOP, pady = 10, padx = 20)
            self.b15 = tk.Button(self.classifyframe, text="Plot classification", command=self.plotClassification, width=15)
            self.b15.pack(side=tk.TOP, pady = 10, padx = 20)
            
            self.classifyinitialized = True
        self.classifyenabled = True
    
    #add in the train data set
    def addTrain(self):
        fn = tk.filedialog.askopenfilename( parent=self.root,
        title='Choose a train data file', initialdir='.' )
        # if the filename is not empty string
        if fn == '':
            return
        if not fn.endswith(".csv"): #the filename must end with .csv
            messagebox.showwarning(
            "Invalid filename", 
            "You must enter a filename that ends with '.csv'."
            )
            return    
        #record the training data set
        self.trainData = data.Data(fn)
        self.trainLabel['text'] = "Train: " + fn
        #will clear the classify result and PCA objects for safety
        self.classify_result = None
        self.testPCA = None
        self.trainPCA = None
        
    #add in the test data set
    def addTest(self):
        fn = tk.filedialog.askopenfilename( parent=self.root,
        title='Choose a test data file', initialdir='.' )
        # if the filename is not empty string
        if fn == '':
            return
        if not fn.endswith(".csv"): #the filename must end with .csv
            messagebox.showwarning(
            "Invalid filename", 
            "You must enter a filename that ends with '.csv'."
            )
            return    
        #record the test data set
        self.testData = data.Data(fn)
        self.testLabel['text'] = "Test: " + fn
        #will clear the classify result and PCA objects for safety
        self.classify_result = None
        self.testPCA = None
        self.trainPCA = None
    
    #does performing PCA to both the test and train data set before classifying
    def prePCA(self):
        if self.trainData == None or self.testData == None:
            messagebox.showwarning(
            "Missing Data", 
            "You must read in the trainData and testData first."
            )
            return
        headers = []
        for i in range(self.trainData.get_num_dimensions()):
            if self.trainData.get_types()[i] == "numeric":
                headers.append(self.trainData.get_headers()[i])
        print ("train data's numeric headers: ", headers)    
        dialog = MyDialog7(self.root, headers, "Choose the columns for PCA", name = False)    
        if dialog.userCancelled(): #disregard if user cancelled
            return
        hds = dialog.getInput()[0]
        print ("received headers: ", hds)
        if dialog.getInput()[2] == "No":
            self.trainPCA = analysis.pca( self.trainData, hds, False )
            self.testPCA = analysis.pca( self.testData, hds, False )
        else:
            self.trainPCA = analysis.pca( self.trainData, hds )
            self.testPCA = analysis.pca( self.testData, hds )
            print ("trainPCAdata: ", self.trainPCA.get_data())

    #add classification
    def addClassification(self):
        if self.trainData == None or self.testData == None:
            messagebox.showwarning(
            "Missing Data", 
            "You must read in the trainData and testData first."
            )
            return
        #add in the available headers
        if self.trainPCA != None:
            hds = self.trainPCA.get_headers()[:]
        else:
            hds = []
        print ("hds is: ", hds)
        for i in range(self.trainData.get_num_dimensions()):
            if self.trainData.get_types()[i] == "numeric":
                hds.append(self.trainData.get_headers()[i])
        print ("candidate headers: ", hds)
        self.classifyhds = hds
        dialog = MyDialog13(self.root, hds)    
        if dialog.userCancelled():
            return
        else: 
            result = dialog.getInput()
        print ("result is: ", result)
        
        m = result[4]
        k = result[5]
        
        
        #if category is in the dataset
        if result[1] != None:
#             train = self.trainData.select_data(result[0]+result[1])
#             test = self.testData.select_data(result[0]+result[1])
            train = self.selectDataPCA(result[0]+result[1], self.trainData, self.trainPCA)
            test = self.selectDataPCA(result[0]+result[1], self.testData, self.testPCA)
            t1 = timer() #start timing
            self.classify_result = cf.classify2(train,test, mode = m, K = k)
            t2 = timer() #end timing
            print ("time taken to classify: ", t2-t1)
        #if category is provided seperately
        else: #implying result[2] != None and result[3] != None
            train = self.selectDataPCA(result[0], self.trainData, self.trainPCA)
            test = self.selectDataPCA(result[0], self.testData, self.testPCA)
            traincatdata = data.Data(result[2])
            testcatdata = data.Data(result[3])
            traincats = traincatdata.select_data( [traincatdata.get_headers()[0]] )
            testcats = testcatdata.select_data( [testcatdata.get_headers()[0]] )
            t1 = timer() #start timing
            self.classify_result = cf.classify2(train, test, traincats, testcats, mode = m, K = k)    
            t2 = timer() #end timing
            print ("time taken to classify: ", t2-t1)
    
    #select data from one original data and one pca data         
    def selectDataPCA(self, hds, original, pca):
        #if there isn't pca data
        if pca == None:
            matrix = original.select_data(hds)
            return matrix
        #if there are pca data
        matrix = np.empty((original.get_num_points(),0))
        cols = []
        for h in hds:
            if h in original.get_headers():
                cols.append(original.get_col(original.header2col[h]))
            elif h in pca.get_headers():
                cols.append(pca.get_col(pca.header2col[h]))
        
        for col in cols:
            matrix = np.hstack((matrix, col))
            
        return matrix
    
    #plot the classification 
    def plotClassification(self):
        if self.classify_result == None:
            messagebox.showwarning(
            "Missing classification", 
            "You must make the classification before plotting it."
            )
            return     
        
        headers = self.classifyhds
        dialog = MyDialog12(self.root, headers, "Choose the columns for classification projection")    
        if dialog.userCancelled(): #disregard if user cancelled
            return
        selected = dialog.getInput()
        print("selected headers: ", selected)
        
        #start to work on the canvas drawing
        
        self.view.reset() #reset the view
        self.update()
        
        #clear the previously added points
        self.clear()
        vtm = self.view.build()
        vtm2 = self.view2.build()    
        
        # get the list of headers specified the user and generate a 5 column matrix such that:
        # column 1 is the x values
        # column 2 is the y values
        # column 3 is the z values (0 if user don't want this dimension)
        # column 4 is the color values (0 if user don't want this dimension)
        # column 5 is the size values (0 if user don't want this dimension)
        hds = selected
        if self.testPCA == None:
            PCAheaders = []
        else:
            PCAheaders = self.testPCA.get_headers()  
        
        self.canvas.itemconfig(self.ids[0],text = hds[0]) #update the x axis id 
        # update the ticks for x
        if hds[0] in PCAheaders: #if hds[0] is chosen from PCA0, PCA1...etc.
            xmin = analysis.data_range(self.testPCA,hds[0:1])[0][0]
            xmax = analysis.data_range(self.testPCA,hds[0:1])[0][1]
        else: #if hds[0] is chosen from original headers
            xmin = analysis.data_range(self.testData,hds[0:1])[0][0]
            xmax = analysis.data_range(self.testData,hds[0:1])[0][1]
        for i in range(len(self.ticks[0])):
            t = self.ticks[0][i]
            val = str(round((i+1)/4 * (xmax-xmin) + xmin,2))
            self.canvas.itemconfig(t[0],text = val)
              
        self.canvas.itemconfig(self.ids[1],text = hds[1]) #update the y axis id 
        # update the ticks for y
        if hds[1] in PCAheaders:
            ymin = analysis.data_range(self.testPCA,hds[1:2])[0][0]
            ymax = analysis.data_range(self.testPCA,hds[1:2])[0][1]
        else:
            ymin = analysis.data_range(self.testData,hds[1:2])[0][0]
            ymax = analysis.data_range(self.testData,hds[1:2])[0][1]
        for i in range(len(self.ticks[1])):
            t = self.ticks[1][i]
            val = str(round((i+1)/4 * (ymax-ymin) + ymin,2))
            self.canvas.itemconfig(t[0],text = val)
        
        #for optional dimensions
        if hds[2] != 'None': #proceed only if the header is not selected to be None
            self.canvas.itemconfig(self.ids[2],text = hds[2]) #update the z axis id
            # update the ticks for z
            if hds[2] in PCAheaders:
                zmin = analysis.data_range(self.testPCA,hds[2:3])[0][0]
                zmax = analysis.data_range(self.testPCA,hds[2:3])[0][1]
            else:
                zmin = analysis.data_range(self.testData,hds[2:3])[0][0]
                zmax = analysis.data_range(self.testData,hds[2:3])[0][1]
            for i in range(len(self.ticks[2])):
                t = self.ticks[2][i]
                val = str(round((i+1)/4 * (zmax-zmin) + zmin,2))
                self.canvas.itemconfig(t[0],text = val)
        else:
            self.canvas.itemconfig(self.ids[2],text = "Z")
         
        
        # select the columns according to the headers (for each header will check if it is a PCA header or an original header (assuming these two sets don't intersect), and select accordingly)
        temp = []
        for i in range(len(hds)):
            h = hds[i]
            if h == 'None':
                continue
            elif h in PCAheaders:
                ind = self.testPCA.header2col[h]
                col = self.testPCA.get_col(ind)
                temp.append(col)
        
        self.data_to_plot = np.empty((self.testData.get_num_points(),0)) #create an empty matrix       
        
        #now the matrix temp is all the PCA columns (not including the columns from the original data)
        if len(temp) > 0: #if there are at least one col from PCA data
            for col in temp: #append all the columns to the empty matrix
                self.data_to_plot = np.hstack((self.data_to_plot, col))
            # print("Now the data is: ", self.data_to_plot)      
            #normalize the columns together
            min = np.amin(self.data_to_plot)
            self.data_to_plot -= min #shift the min to 0
            max = np.amax(self.data_to_plot)
            self.data_to_plot *= 1/max
        
        #now the PCA columns are normalized together
        
        #add in the separately-normalized columns from original data
        for i in range(len(hds)):
            if hds[i] in self.testData.get_headers():
                ind = self.testData.header2col[hds[i]]
                col = np.copy(self.testData.get_col(ind))
                min = np.amin(col)
                col -= min #shift the min to 0
                max = np.amax(col)
                if max != 0:
                    col *= 1/max #make the max to be 1
                else:
                    pass #if max is 0 then don't change a thing
                self.data_to_plot = np.insert(self.data_to_plot, [i], col, axis = 1)
            elif hds[i] == 'None':
                # insert a column of place holders with default 0 at column index i
                self.data_to_plot = np.insert(self.data_to_plot, i, 0, axis=1)      
                
        print ("data to plot: ", self.data_to_plot)
        
        #add in the stats labels to statsframe
        if hds[0] in PCAheaders:
            data_obj = self.testPCA
        else:
            data_obj = self.testData
        stats_x = "X axis ("+hds[0]+") : " + "\nmean: " + str(round(analysis.mean(data_obj,[hds[0]])[0],2)) + "\nmedian: " + str(round(analysis.median(data_obj,[hds[0]])[0],2)) + "\nrange: " + str([round(elem, 2) for elem in analysis.data_range(data_obj,[hds[0]])[0]]) + "\nstdev: " + str(round(analysis.stdev(data_obj,[hds[0]])[0],2))
        self.statsLabels.append(tk.Label( self.statsframe, text=stats_x)) #add in another label representing x column in statsframe 
        self.statsLabels[-1].grid( row = 1, column = 0, padx = 10, pady = 3)
        if hds[1] in PCAheaders:
            data_obj = self.testPCA
        else:
            data_obj = self.testData
        stats_y = "Y axis ("+hds[1]+") : " + "\nmean: " + str(round(analysis.mean(data_obj,[hds[1]])[0],2)) + "\nmedian: " + str(round(analysis.median(data_obj,[hds[1]])[0],2)) + "\nrange: " + str([round(elem, 2) for elem in analysis.data_range(data_obj,[hds[1]])[0]]) + "\nstdev: " + str(round(analysis.stdev(data_obj,[hds[1]])[0],2))
        self.statsLabels.append(tk.Label( self.statsframe, text=stats_y)) #add in another label representing y column in statsframe 
        self.statsLabels[-1].grid( row = 1, column = 1, padx = 10, pady = 3)
        if hds[2] != 'None':
            if hds[2] in PCAheaders:
                data_obj = self.testPCA
            else:
                data_obj = self.testData
            header_z = hds[2]
            stats_z = "Z axis ("+header_z+") : " + "\nmean: " + str(round(analysis.mean(data_obj,[header_z])[0],2)) + "\nmedian: " + str(round(analysis.median(data_obj,[header_z])[0],2)) + "\nrange: " + str([round(elem, 2) for elem in analysis.data_range(data_obj,[hds[2]])[0]]) + "\nstdev: " + str(round(analysis.stdev(data_obj,[header_z])[0],2))
            self.statsLabels.append(tk.Label( self.statsframe, text=stats_z)) #add in another label representing z column in statsframe 
            self.statsLabels[-1].grid( row = 1, column = 2, pady = 3)
        if hds[3] != 'None':
            if hds[3] in PCAheaders:
                data_obj = self.testPCA
            else:
                data_obj = self.testData
            header_color = hds[3]
            stats_color = "Color axis ("+header_color+") : " + "\nmean: " + str(round(analysis.mean(data_obj,[header_color])[0],2)) + "\nmedian: " + str(round(analysis.median(data_obj,[header_color])[0],2)) + "\nrange: " + str([round(elem, 2) for elem in analysis.data_range(data_obj,[hds[3]])[0]]) + "\nstdev: " + str(round(analysis.stdev(data_obj,[header_color])[0],2))
            self.statsLabels.append(tk.Label( self.statsframe, text=stats_color)) #add in another label representing color column in statsframe 
            self.statsLabels[-1].grid( row = 1, column = 3, pady = 3)
        if hds[4] != 'None':
            if hds[4] in PCAheaders:
                data_obj = self.testPCA
            else:
                data_obj = self.testData
            header_size = hds[4]
            stats_size = "Size axis ("+header_size+") : " + "\nmean: " + str(round(analysis.mean(data_obj,[header_size])[0],2)) + "\nmedian: " + str(round(analysis.median(data_obj,[header_size])[0],2)) + "\nrange: " + str([round(elem, 2) for elem in analysis.data_range(data_obj,[hds[4]])[0]]) + "\nstdev: " + str(round(analysis.stdev(data_obj,[header_size])[0],2))
            self.statsLabels.append(tk.Label( self.statsframe, text=stats_size)) #add in another label representing size column in statsframe 
            self.statsLabels[-1].grid( row = 1, column = 4, pady = 3)
        
        #normalize the 4th and 5th columns
        # print ("normalized 4", self.normalize(self.data_to_plot[:,3]))
        self.data_to_plot[:,3] = self.normalize(self.data_to_plot[:,3])
        self.data_to_plot[:,4] = self.normalize(self.data_to_plot[:,4])
        
        print ("after normalization", self.data_to_plot)
        
        #add in the dots                        
        for i in range (self.testData.get_num_points()): # for each point
            c = self.data_to_plot[i,0:3]
            shape = c.ndim
            if shape > 1: #there is a weird thing (why sometimes c is [a,b,c] and sometimes a is [[a,b,c]]) that I'm not quite getting, but checking this fixes the problem
                c = c.tolist()[0]
            else:
                c = c.tolist()
            c.append(1) #append normal homogeneous coordinate
            arr = np.matrix(c)
            arr1 = (vtm * arr.T).T
            arr2 = (vtm2 * arr.T).T #coords for mini map
            
            #add to main map
            #generate color    
            if hds[3] == 'None': #if user don't want color axis
                rgb = "#0000FF"
            else:
                rgb = self.generateColor(self.data_to_plot.item(i,3)) #generate color from the color value of the point
            #generate size
            if hds[4] != 'None': #if user does want size axis
                size = self.generateSize(self.data_to_plot.item(i,4))
            else:
                size = 5
                
            #build an oval accordingly
            pt = self.canvas.create_oval(arr1[0,0]-size, arr1[0,1]-size, arr1[0,0]+size, arr1[0,1]+size, fill = rgb, outline='')
            self.objects.append(pt) #append the oval
            self.obj_coords[pt] = np.matrix(c) # append the oval-coords mapping
            self.obj_size[pt] = size # append the oval-size mapping
            
            #add to mini map
            pt2 = self.canvas2.create_oval(arr2[0,0]-3, arr2[0,1]-3, arr2[0,0]+3, arr2[0,1]+3, fill = '#f8ff35', outline='')
            self.pointsDict[pt] = pt2 #link the oval in the big map with the oval in the small map
        
        #set each dot to the corresponding color based on their cluster index
        for i in range(len(self.objects)):
            classifyIdx = self.classify_result[i]
            try:
                self.canvas.itemconfig(self.objects[i], fill = self.colors[classifyIdx])
            except:
                #generate random color
                r = lambda: random.randint(0,255)
                rgb = '#%02X%02X%02X' % (r(),r(),r())
                self.colors[classifyIdx] = rgb
                self.canvas.itemconfig(self.objects[i], fill = self.colors[classifyIdx])
        
        self.usingMainData = False                
        
    #handles building Cluster frame
    def handleCluster(self, event = None):
        if self.clusterenabled == True: #disable the cluster feature, clear the frame if its already there, clear the data structures associated with cluster
            self.clusterframe.pack_forget() #destroy the frame too
            self.clusterenabled = False #set the boolean to be False
            return
        #else: enable the cluster feature       
        self.clusterframe.pack(side=tk.RIGHT, padx=2, pady=2, fill=tk.Y)  
        #if nothing has been initialized yet
        if self.clusterinitialized == False:
            sep = tk.Frame( self.clusterframe, height=self.initDy, width=2, bd=1, relief=tk.SUNKEN )
            sep.pack( side=tk.LEFT, padx = 2, pady = 2, fill=tk.Y)
            t = tk.Label( self.clusterframe, text="Cluster Analysis")
            t.pack( side = tk.TOP, padx = 100, pady = 20)  
        
            self.b7 = tk.Button(self.clusterframe, text="Add New Cluster", command=self.addCluster, width=15)
            self.b7.pack(side=tk.TOP, pady = 10, padx = 20)        
        
            self.clusterlist = tk.Listbox(self.clusterframe,exportselection=0, height = 4, selectmode=tk.SINGLE)
            self.clusterlist.pack(side=tk.TOP, padx = 2, pady = 15)
        
            self.b8 = tk.Button(self.clusterframe, text="Delete Cluster", command=self.deletecluster, width=10)
            self.b8.pack(side=tk.TOP, pady = 10, padx = 20) 
        
            self.b9 = tk.Button(self.clusterframe, text="Draw Cluster", command=self.drawcluster, width=15)
            self.b9.pack(side=tk.TOP, pady = 10, padx = 20)
        
            self.b10 = tk.Button(self.clusterframe, text="View Cluster Specs", command=self.displayclusterstats, width=15)
            self.b10.pack(side=tk.TOP, pady = 10, padx = 20)
        
#             self.b11 = tk.Button(self.clusterframe, text="Save Cluster to File", command=self.saveclustertofile, width=15)
#             self.b11.pack(side=tk.TOP, pady = 10, padx = 20)
#         
#             self.b12 = tk.Button(self.clusterframe, text="Read Cluster from File", command=self.readclusterfromfile, width=15)
#             self.b12.pack(side=tk.TOP, pady = 10, padx = 20)
            
            self.clusterinitialized = True
        
        self.clusterenabled = True
        
    def addCluster(self):
        if self.data == None: #proceed only if data are already read from the file
            messagebox.showwarning(
                "Data uninitialized", 
                "User must read in and apply a data file first before adding cluster"
            )
            return
        try:
            index = self.PCAlist.curselection()[0]
            pcadata = self.PCAs[index]
            pcaheaders = pcadata.get_headers()
        except:
            pcaheaders = []
            
        dialog = MyDialog10(self.root, self.headers+pcaheaders, self.data.get_num_points()-1, "Choose the columns and the number of clusters")    
        if dialog.userCancelled(): #disregard if user cancelled
            return
        hds = dialog.getInput()[0]
        print ("received headers: ", hds)
        K = dialog.getInput()[1]
        print ("K is: ", K)
        name = dialog.getInput()[2]
        print ("Name is: ", name)
        whiten = dialog.getInput()[3]
        print ("Whiten is: ", whiten)
        d_metric = dialog.getInput()[4]
        print ("Distance metric: ", d_metric)
        
        
        #select the columns from either the original matrix or the PCA matrix
        matrix = np.empty((self.data.get_num_points(),0))
        cols = []
        for h in hds:
            if h in self.headers:
                cols.append(self.data.get_col(self.data.header2col[h]))
            elif h in pcadata.get_headers():
                cols.append(pcadata.get_col(pcadata.header2col[h]))
        
        for col in cols:
            matrix = np.hstack((matrix, col))
        
        #calculate the cluster specs using analysis.kmeans
        codebook, codes, errors = analysis.kmeans(matrix, hds, K, whiten, d_metric)
        #create a clusterdata object
        cdata = data.ClusterData(self.data.get_data(), K, codebook, codes, errors, whiten)
        
        self.clusters.append(cdata)
        name = dialog.getInput()[2]
        self.clusternames.append(name)
        self.clusterlist.insert(tk.END, name)
        self.clusterlist.selection_clear(0, tk.END)
        self.clusterlist.selection_set(tk.END)
    
    def deletecluster(self):
        #make sure that there is a cluster selected before projecting
        try:
            index = self.clusterlist.curselection()[0]
            cdata = self.clusters[index]
        except:
            messagebox.showwarning(
                "Missing selection", 
                "User must select the cluster to delete"
            )
            return
        #delete
        self.clusterlist.delete(index)
        del self.clusters[index]
        del self.clusternames[index]
    
    #draws the points and distinguish the clusters by the groups
    def drawcluster(self):
        #make sure that there is a cluster selected before projecting
        try:
            index = self.clusterlist.curselection()[0]
            cdata = self.clusters[index]
        except:
            messagebox.showwarning(
                "Missing selection", 
                "User must create and specify the cluster before visualizing"
            )
            return
        
        self.projectPCA(True) #use projectPCA to draw the dots
        #set each dot to the corresponding color based on their cluster index
        for i in range(len(self.objects)):
            clusterIdx = cdata.get_ids().tolist()[0][i]
            try:
                self.canvas.itemconfig(self.objects[i], fill = self.colors[clusterIdx])
            except:
                r = lambda: random.randint(0,255)
                rgb = '#%02X%02X%02X' % (r(),r(),r())
                self.colors[clusterIdx] = rgb
                self.canvas.itemconfig(self.objects[i], fill = self.colors[clusterIdx])
        #set the colors for the cluster means
        for i in range(len(self.means_objects)):
            self.canvas.itemconfig(self.means_objects[i], fill = self.colors[i])       
            
    
    def displayclusterstats(self):
        #try to get the selection from the PCAlist
        try:
            index = self.clusterlist.curselection()[0]
            cdata = self.clusters[index]
        except:
            messagebox.showwarning(
                "Missing selection", 
                "User must create and specify the cluster before showing its specs"
            )
            return
            
        for i in range(cdata.get_K()):
            try: #try if all the index gets a color
                rgb = self.colors[i]
            except: #otherwise create random color
                r = lambda: random.randint(0,255)
                rgb = '#%02X%02X%02X' % (r(),r(),r())
                self.colors[i] = rgb    
        dialog = MyDialog11(self.root, cdata, self.colors, "Specs for this cluster")
        
    #clear the existing PCAs, called when new file is read
    def clearClusters(self):
        try:
            self.clusternames = []
            self.clusters = []
            self.clusterlist.delete(0, tk.END)
        except:
            pass
    
            
                    
    # clear the canvas, as well as all the master lists except for regression history which is kept throughout the session even with change of files    
    def clear(self):
        #clear the previously added points
        for obj in self.objects:
            self.canvas2.delete(self.pointsDict[obj]) #clear from the mini map first
            self.canvas.delete(obj) #then clear from the big canvas
        del self.objects[:]
        self.obj_coords = {}
        self.obj_size = {}
        self.pointsDict = {}    
        #clear the linear regressions
        self.canvas.delete(self.regression)
        self.regression = None
        self.regressionCoords = None
        self.line_info = None
        #clear the cluster means
        for obj in self.means_objects:
            self.canvas.delete(obj)
        del self.means_objects[:]
        self.means_coords = {}
        #destroy the status labels
        try:
            for l in self.statsLabels:
                l.destroy()
            self.statsLabels = []
        except:
            pass
        #clear the ticks
        for tks in self.ticks:
            for t in tks:
                self.canvas.itemconfig(t[0], text = "")
        #reset the axes labels
        self.canvas.itemconfig(self.ids[0],text = 'X') #reset the X axis id to be 'X'
        self.canvas.itemconfig(self.ids[1],text = 'Y') #reset the Y axis id to be 'Y'
        self.canvas.itemconfig(self.ids[2],text = 'Z') #reset the Z axis id to be 'Z'
        
    
    # clear everything, back to the way it started out to be
    def clearEverything(self, event=None):
#         clear everything and reset the view
#         self.clear()
#         self.regressionHistory = []
#         self.view.reset()
#         self.update()
#         
        pass
        
            
    #handle resize events 
    def handleResize(self, event=None):
        # You can handle resize events here
        print ("Resizing...")
        try:
            x = float(self.canvas.winfo_width())
            y = float(self.canvas.winfo_height())
            diff_x = x/self.baseScreenSize[0] #how the new screen geometries compare with the old ones
            diff_y = y/self.baseScreenSize[1]
            new_size = max(400 * diff_x, 400 * diff_y) #to keep the cubic shape. I used max because I found it gives a better effect
            self.view.screen = np.array([new_size,new_size])
            self.view.offset = np.array([0.25*new_size,0.25*new_size]) #use 0.25 screen size as the offset
            self.update()
        except:
            pass    
    
    #opens a file using a filedialog
    def handleOpen(self, event=None):
        print('handleOpen')
        fn = tk.filedialog.askopenfilename( parent=self.root,
        title='Choose a data file', initialdir='.' )
        # add the file name to self.filename and self.filelist (if the filename is not empty string)
        if fn != '':
            if not fn.endswith(".csv"): #the filename must end with .csv
                messagebox.showwarning(
                "Invalid filename", 
                "You must enter a filename that ends with '.csv'."
                )
                return
            self.filenames.append(fn)       
            self.filelist.insert(tk.END, fn)
            self.filelist.selection_clear(0, tk.END)
            self.filelist.select_set(tk.END)
    
    #call self.plotData    
    def handlePlotData(self, event=None):
        self.plotData()
    
    #call self.handleOpen
    def handleModO(self, event):
        self.handleOpen()
    
    #quit the process
    def handleQuit(self, event=None):
        print('Terminating')
        self.root.destroy()
    
    #reset the view
    def handleResetButton(self, event=None):
        print('handling reset button')
        self.view.reset()
        self.update()
        if (event != None):
            self.baseClick2 = (event.x, event.y)
        
    # 1. helper for translation
    # 2. when user clicks on a point, pop up a dialog to display the data related to that point
    def handleButton1(self, event):
        print('handle button 1: %d %d' % (event.x, event.y))
        #sets the base click
        self.baseClick = ( event.x, event.y )
        
        #check if the click is on one of the dots, if yes, then show a dialog to display the information
        
        #if no dots then return
        if len(self.objects)<1:
            return
            
        x = event.x
        y = event.y
        min_distance = sys.maxsize
        #go through all points on canvas
        for i in range(len(self.objects)):
            obj = self.objects[i]
            loc = self.canvas.coords(obj)
            obj_x = (loc[0]+loc[2])/2
            obj_y = (loc[1]+loc[3])/2
            distance = math.pow((x-obj_x),2) + math.pow((y-obj_y),2) #calculate distance between the click and the dot
            if distance < min_distance: #if the distance is the smallest 
                min_distance = distance #make that distance the min distance
                closest = obj
                closest_index = i
                
        #if the click is actually close to the dot
        # print ("raw data is: ", self.data.rawData)
        if self.usingMainData == True:
            dataObj = self.data
        else:
            dataObj = self.testData #special case when the data is coming from self.testData (classifying)
        if min_distance < math.pow(self.obj_size[closest],2): # has to be closer to the center point than the dot size
            headers = dataObj.get_headers()
            values = dataObj.rawData[closest_index + 2] #this exploits the fact that the sequence of points in self.objects and self.data.rawValue is identical
                                                         # I used +2 because in the raw value, the first 2 rows are the headers and types
            # print ("to list values: ", values)
            MyDialog2(self.root, "Information", headers, values)
                
            

    # helper for rotation
    def handleButton2(self, event):
        print('handle button 2: %d %d' % (event.x, event.y))
        self.boo1 = True
        self.baseClick2 = ( event.x, event.y )
        self.original_view = self.view.clone()

    # helper for scaling
    def handleButton3(self, event):
        print('handle button 3: %d %d' % (event.x, event.y))
        self.baseClick3 = ( event.x, event.y )
        self.original_extent = np.copy(self.view.extent)
    
    #updates the base clicks for button 1 and 2
    #takes care of the case when button 3 are being pressed and dragged along with button 1 or 2  
    def handleButtonRelease3(self, event):
        self.baseClick = (event.x, event.y)
        self.baseClick2 = (event.x, event.y)
        self.original_view = self.view.clone()
    
    #update the base click of button 1 and update self.boo1    
    def handleButtonRelease2(self, event):
        self.baseClick = (event.x, event.y)
        self.boo1 = False 
        
    # translation
    def handleButton1Motion(self, event):
        
        # Calculate the differential motion since the last time the function was called
        diff = ( event.x - self.baseClick[0], event.y - self.baseClick[1] )
        print('handle button 1 motion: %d %d' % (diff[0],diff[1]) )
        self.baseClick = ( event.x, event.y )
        
        # Divide the differential motion (dx, dy) by the screen size (view X, view Y)
        x = diff[0]/self.canvas.winfo_width()
        y = diff[1]/self.canvas.winfo_height()
        # Multiply the horizontal and vertical motion by the horizontal and vertical extents.
        x = self.t_speed * x * self.view.extent.item(0)
        y = self.t_speed * y * self.view.extent.item(1)
        
        # The VRP should be updated by delta0 * U + delta1 * VUP (this is a vector equation)
        vrp = self.view.vrp + self.view.u * x + self.view.vup * y
#         print ("original vrp: ", self.view.vrp)
#         print ("new vrp: ", vrp)
        self.view.vrp = vrp
        
        # call update()
        self.update()
    
    # rotation
    def handleButton2Motion(self, event):
        #I found out that sometimes handleButton2Motion can be called without calling handleButton2 first
        #So this is to take care of that case
        if self.boo1 == False:
            self.baseClick2 = ( event.x, event.y )
            self.original_view = self.view.clone()
            self.boo1 = True
        
        # Calculate the differential motion since the last time the function was called
        diff = ( event.x - self.baseClick2[0], event.y - self.baseClick2[1] )
        print('handle button 2 motion: %d %d' % (diff[0],diff[1]) )
        
        # Divide the differential motion (dx, dy) by 200 and multiplied by pi
        x = self.r_speed * diff[0] * math.pi /500
        y = self.r_speed * diff[1] * math.pi /500
        
        #Clone the original View object and assign it to standard view field 
        self.view = self.original_view.clone()
                
        #then rotate the view using the rotateVRC method
        self.view.rotateVRC(y,x)
        
        # call update()
        self.update()
        
    #scaling
    def handleButton3Motion( self, event):
        print('handle button 3 motion: %d %d' % (event.x, event.y) )
        # Calculate the vertical differential motion since the last time the function was called
        y = event.y - self.baseClick3[1]
        self.baseClick3 = ( event.x, event.y )
        
        # get a scalar from y displacement (between 0.1 and 3)
        scalar = (1 + y * self.s_speed/200)
        scalar = (min(max(scalar, 0.1), 3))
        
        #update extent
        extent = np.copy(self.view.extent)
        extent *= scalar
        self.view.extent = extent
        
        # call update()
        self.update()
    
    #initialize a dialog, lets user to put in the desired speed, and save the speed    
    def changeTranslateSpeed(self):
        dialog = MyDialog(self.root, self.t_speed, "Enter the translate speed (a number between 0.1 and 10)", 0.1, 10)    
        if dialog.userCancelled():
            return
        else: 
            self.t_speed = dialog.getInput()   
    
    #initialize a dialog, lets user to put in the desired speed, and save the speed         
    def changeRotateSpeed(self):
        dialog = MyDialog(self.root, self.r_speed, "Enter the rotate speed (a number between 0.1 and 10)", 0.1, 10)    
        if dialog.userCancelled():
            return
        else: 
            self.r_speed = dialog.getInput()   
    
    #initialize a dialog, lets user to put in the desired speed, and save the speed         
    def changeScaleSpeed(self):
        dialog = MyDialog(self.root, self.s_speed, "Enter the scale speed (a number between 0.1 and 10)", 0.1, 10)    
        if dialog.userCancelled():
            return
        else: 
            self.s_speed = dialog.getInput()
    
    #align the axes so that you're looking into the XZ plane             
    def alignXY(self, event=None):
        self.view.vpn = np.array([0., 0., -1.])
        self.view.vup = np.array([0., 1., 0.])
        self.view.u = np.array([-1., 0., 0.])
        self.update()
    
    #align the axes so that you're looking into the XZ plane        
    def alignXZ(self, event=None):
        self.view.vpn = np.array([0., 1., 0.])
        self.view.vup = np.array([0., 0., 1.])
        self.view.u = np.array([-1., 0., 0.])
        self.update()
    
    #align the axes so that you're looking into the YZ plane      
    def alignYZ(self, event=None):
        self.view.vpn = np.array([1., 0., 0.])
        self.view.vup = np.array([0., 1., 0.])
        self.view.u = np.array([0., 0., -1.])
        self.update()            
    
    # pop up a dialog, ask user for a filename, then save a JPG file with that filename                        
    def captureCanvas(self, event=None):
        #get the name from a dialog
        dialog = MyDialog5(self.root)    
        if dialog.userCancelled():
            return
        else: 
            name = dialog.getInput() 
            
        #calculate the coords for the screenshot    
        x = self.root.winfo_rootx() + self.canvas.winfo_x()
        y = self.root.winfo_rooty() + self.canvas.winfo_y()
        x1 = x+self.canvas.winfo_width()
        y1 = y+self.canvas.winfo_height()
        
        print ("image info: ", (x,y,x1,y1))
        ImageGrab.grab(bbox=(x,y,x1,y1)).convert("RGB").save(name+".jpg")     
        
    # save the current linear regression status into a csv file
    def saveRegression(self, event = None):
        if self.data == None or self.line_info == None: #if there is no regression line then return
            messagebox.showwarning(
                "No regression", 
                "The regression to save must be currently active (displayed on the screen)"
                )
            return
        #get the name from a dialog
        dialog = MyDialog6(self.root)    
        if dialog.userCancelled():
            return
        else: 
            name = dialog.getInput()
        
        #build the content for the csv 
        content = []
        content.append(["Data set name", self.filenameActive])
        content.append(["Regression name", self.regressionNameActive])
        #add the independent variables
        temp = ["Independent variable(s)"]
        temp.extend(self.ind_headers)
        content.append(temp)
        content.append(["Dependent variable", self.dep_header])
        content.append(["m0", self.line_info[0][0].item(0)])
        if len(self.ind_headers) > 1:
            content.append(["m1", self.line_info[0][1].item(0)])
        content.append(["b",self.line_info[0][-1].item(0)])
        content.append(["sum-squared error", self.line_info[1].item(0)])
        content.append(["R^2", self.line_info[2].item(0)])
        #extract t value from line_info, change it into list and round its elements
        t = self.line_info[3].tolist()[0]
        for i in range(len(t)):
            t[i] = round(t[i],2)
        t.insert(0,"t")
        #extract p value from line_info, change it into list and round its elements
        p = self.line_info[4].tolist()[0]
        for i in range(len(p)):
            p[i] = round(p[i],2)
        p.insert(0,"p")
        content.append(t)
        content.append(p)
        print ("content is: ", content)
        
        fp = open(name + ".csv", 'w+')
        csv_writer = csv.writer(fp, lineterminator='\n') 
        csv_writer.writerows(content)
        fp.close()
    
    #read regression from file    
    def readRegression(self, event=None):
        fn = tk.filedialog.askopenfilename( parent=self.root,
        title='Choose a regression file', initialdir='.' )
        # add the file name to self.filename and self.filelist (if the filename is not empty string)
        if fn == '':
            return        
        if not fn.endswith(".csv"): #the filename must end with .csv
            messagebox.showwarning(
            "Invalid filename", 
            "You must enter a filename that ends with '.csv'."
            )
            return
        fp = open(fn, 'rU')
        csv_reader = csv.reader( fp )
        
        #try to parse info from the csv file
        #will work if the file is not properly formatted
        try: 
            #parse the filename and read it in
            line = next(csv_reader)
            self.addDataFromFile(line[1])
            #add the data file read to the listbox if not already there
            if line[1] not in self.filenames:
                self.filenames.append(line[1])       
                self.filelist.insert(tk.END, line[1])
                self.filelist.selection_clear(0, tk.END)
                self.filelist.select_set(tk.END)
            #parse the regression name and save it 
            line = next(csv_reader)
            name = line[1]
            #parse the ind vars and save them to the field
            line = next(csv_reader)
            ind_vars = line[1:]
            #parse the dep vars and save them to the field
            line = next(csv_reader)
            dep_var = line[1]
            #add the [inds, dep, regression name, dataset name] into self.regressionHistory
            self.regressionHistory.append([ind_vars, dep_var, name, self.filenameActive])
            self.ind_headers = ind_vars
            self.dep_header = dep_var
            self.buildLinearRegression()
        
        #if the format isn't right
        except:
            messagebox.showwarning(
            "Incorrect format", 
            "You must add the same csv file that is saved from this application."
            )
    
    #needs to be tested    
    def write(self, outfile, headers = None):
        if self.data == None: #if there is no regression line then return
            messagebox.showwarning(
                "No data", 
                "There must be a data object first before writing"
                )
            return
        if headers == None:
            headers = self.data.get_headers                      
        content = []#the list of list to write to file
        #add in the contents
        line1 = headers
        line2 = []
        for h in headers:
            line2.append(self.data.types[self.data.header2col[h]])
        for i in range(len(self.data.get_num_points)):
            content.append(self.data.get_row(i))
        fp = open(outfile + ".csv", 'w+')
        csv_writer = csv.writer(fp, lineterminator='\n') 
        csv_writer.writerows(content)
        fp.close()
                               
    #main method
    def main(self):
        print('Entering main loop')
        self.root.mainloop()
        
        
# support class for dialog      
class Dialog(tk.Toplevel):
    
    #initializer
    def __init__(self, parent, title = None):

        tk.Toplevel.__init__(self, parent)
        self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent

        self.result = None

        body = tk.Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        self.initial_focus.focus_set()

        self.wait_window(self)

    #
    # construction hooks
     #create the dialog
    def body(self, master):
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden

        pass
    
    #builds the button box
    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = tk.Frame(self)

        w = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    #
    # standard button semantics

    def ok(self, event=None):

        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()

        self.cancel()

    #cancel
    def cancel(self, event=None):

        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    #
    # command hooks

    def validate(self):

        return 1 # override
    
    #apply
    def apply(self):

        pass # override
        
# custom dialog for speed input
class MyDialog(Dialog):
    
    #initializer for dialog
    def __init__(self, parent, default, title = None, low=0, high=100):
        self.low = low
        self.high = high
        self.cancelled = True
        self.default = default
        super(MyDialog,self).__init__(parent, title)
    
    #creates the dialog
    def body(self, master):
        tk.Label(master, text="Speed = ").grid(row=0)
        self.e1 = tk.Entry(master)
        self.e1.grid(row=0, column=1)
        self.e1.insert(tk.END, self.default)
        self.e1.selection_range(0, tk.END) 
        return self.e1 # initial focus
    
    #check if the input is valid(can be casted into float and is between the bounds)
    def validate(self):
        try:
            result = float(self.e1.get())
            if result >= self.low and result <= self.high:
                return 1
            else:
                messagebox.showwarning(
                "Illegal Value", 
                "Value should be between " + str(self.low) + " and " + str(self.high) + "."
                )
                return 0
        except ValueError:
            messagebox.showwarning(
                "Illegal Value", 
                "Value should be a number."
            )
            return 0
    
    #apply the input        
    def apply(self):
        self.input = tk.DoubleVar()
        self.input.set(float(self.e1.get()))
        self.cancelled = False
    
    #gets the input    
    def getInput(self):
        return self.input.get()
       
    #gets whether cancelled 
    def userCancelled(self):
        return self.cancelled 
        
# custom dialog for info display
class MyDialog2(simpledialog.Dialog):
    
    #initializer for dialog
    #info here should be a list of tuples
    #each tuple should look like (header, value)
    def __init__(self, parent, title = None, headers = [], values = []):
        self.headers = headers
        self.values = values
        super(MyDialog2,self).__init__(parent, title)
    
    #creates the dialog
    def body(self, master):
        num_dimensions = len(self.headers)
        for i in range(num_dimensions):
            my_string = self.headers[i] + ": " + str(self.values[i])
            tk.Label(master, text=my_string).grid(row=i, padx=10, pady=3)
    
    def buttonbox(self):
        pass        
        
# custom dialog for linear regression
class MyDialog3(Dialog):
    
    #initializer for dialog
    #options = a list of possible options
    def __init__(self, parent, options, title = None):
        self.cancelled = True
        self.options = options
        super(MyDialog3,self).__init__(parent, title)
    
    #creates the dialog
    def body(self, master):
        # add in listboxes to allow user to choose the independent/dependent variables
        tk.Label(master, text="independent 1").grid(row=0, column=0)
        tk.Label(master, text="independent 2 (optional)").grid(row=0, column=1)
        tk.Label(master, text="dependent").grid(row=0, column=2)
        self.list1 = tk.Listbox(master,exportselection=0, height = 4, selectmode = tk.SINGLE)
        self.list1.grid(row=1,column=0)
        self.list2 = tk.Listbox(master,exportselection=0, height = 4, selectmode = tk.SINGLE)
        self.list2.grid(row=1,column=1)
        self.list3 = tk.Listbox(master,exportselection=0, height = 4, selectmode = tk.SINGLE)
        self.list3.grid(row=1,column=2)
        for option in self.options:
            self.list1.insert(tk.END,option)
            self.list2.insert(tk.END,option)
            self.list3.insert(tk.END,option)
        
        # add in an entry to allow user to name the linear regression
        tk.Label(master, text="Name your regression = ").grid(row=2, column = 0, pady = 10)
        self.e1 = tk.Entry(master)
        self.e1.grid(row=2, column=1)   
    
    #check if the input is valid
    def validate(self):
        try:
            ind1 = self.options[self.list1.curselection()[0]]
            dep = self.options[self.list3.curselection()[0]]
            if self.e1.get() != '': #make sure there is a name given
                return 1
            else:
                messagebox.showwarning(
                "Missing name", 
                "You must name the regression."
                )
                return 0
        except:
            messagebox.showwarning(
                "Missing selection", 
                "You must select exactly one header for dependent and independent."
            )
            return 0
    
    #apply the input        
    def apply(self):
        self.ind = [] # a list to contain the independent variable
        ind1 = self.options[self.list1.curselection()[0]]
        self.ind.append(ind1)
        # try to add in the optional ind variable, if unsuccessful then never mind
        try:
            ind2 = self.options[self.list2.curselection()[0]]
            self.ind.append(ind2)
        except:
            pass
        # add in the dependent variable           
        self.dep = self.options[self.list3.curselection()[0]]
        self.cancelled = False
        self.name = self.e1.get()
    
    #gets the input    
    def getInput(self):
        return [self.ind, self.dep, self.name]
       
    #gets whether cancelled 
    def userCancelled(self):
        return self.cancelled
        
 
# custom dialog for linear regression history
class MyDialog4(Dialog):
    
    #initializer for dialog
    #options = a list of possible options
    def __init__(self, parent, options, title = None):
        self.cancelled = True
        self.options = options
        super(MyDialog4,self).__init__(parent, title)
    
    #creates the dialog
    def body(self, master):
        # add in listbox to allow user to choose the regression
        tk.Label(master, text="Choose one from below").grid(row=0, column=0)
        self.list1 = tk.Listbox(master,exportselection=0, height = 4, selectmode = tk.SINGLE)
        self.list1.grid(row=1,column=0)
        for option in self.options:
            self.list1.insert(tk.END,option)
    
    #check if the input is valid
    def validate(self):
        try:
            selected = self.options[self.list1.curselection()[0]]
            return 1
        except:
            messagebox.showwarning(
                "Missing selection", 
                "You must select exactly one regression."
            )
            return 0
    
    #apply the input        
    def apply(self):
        self.selection = self.options[self.list1.curselection()[0]] # a list to contain the independent variable
        self.cancelled = False
    
    #gets the input    
    def getInput(self):
        return self.selection
       
    #gets whether cancelled 
    def userCancelled(self):
        return self.cancelled     
        
# custom dialog for saving the image
class MyDialog5(Dialog):
    
    #initializer for dialog
    #options = a list of possible options
    def __init__(self, parent):
        self.cancelled = True
        super(MyDialog5,self).__init__(parent, "Name your image")
    
    #creates the dialog
    def body(self, master):
        tk.Label(master, text="File will be saved as JPEG, no suffix needed").grid(row=1)
        # add in entry to allow user to name the image
        self.e1 = tk.Entry(master)
        self.e1.grid(row=0)
    
    #check if the input is valid
    def validate(self):
        if self.e1.get() != '':
            return 1
        else:
            messagebox.showwarning(
                "Missing name", 
                "You must name your image."
            )
            return 0
    
    #apply the input        
    def apply(self):
        self.name = self.e1.get() # a list to contain the independent variable
        self.cancelled = False
    
    #gets the input    
    def getInput(self):
        return self.name
       
    #gets whether cancelled 
    def userCancelled(self):
        return self.cancelled 
        
# custom dialog for saving the line info/PCA info
class MyDialog6(Dialog):
    
    #initializer for dialog
    def __init__(self, parent):
        self.cancelled = True
        super(MyDialog6,self).__init__(parent, "Name your file")
    
    #creates the dialog
    def body(self, master):
        tk.Label(master, text="File will be saved as .csv, no suffix needed").grid(row=1)
        # add in entry to allow user to name the image
        self.e1 = tk.Entry(master)
        self.e1.grid(row=0)
    
    #check if the input is valid
    def validate(self):
        if self.e1.get() != '':
            return 1
        else:
            messagebox.showwarning(
                "Missing name", 
                "You must name your file."
            )
            return 0
    
    #apply the input        
    def apply(self):
        self.name = self.e1.get() # a list to contain the independent variable
        self.cancelled = False
    
    #gets the input    
    def getInput(self):
        return self.name
       
    #gets whether cancelled 
    def userCancelled(self):
        return self.cancelled                       

# custom dialog for new PCA
class MyDialog7(Dialog):
    
    #initializer for dialog
    #options = a list of possible options
    def __init__(self, parent, options, title = None, name = True):
        self.cancelled = True
        self.options = options
        self.name = name
        super(MyDialog7,self).__init__(parent, title)
    
    #creates the dialog
    def body(self, master):
        # add in listboxes to allow user to choose the independent/dependent variables
        tk.Label(master, text="Choose which columns to perform PCA").grid(row=0, column=0)
        self.list1 = tk.Listbox(master,exportselection=0, height = 4, selectmode = tk.MULTIPLE)
        self.list1.grid(row=1, column = 0)
        for option in self.options:
            self.list1.insert(tk.END,option)
            
        #a list box to ask whether or not to normalize
        tk.Label(master, text="Normalize?").grid(row=0, column=1)
        self.list2 = tk.Listbox(master,exportselection=0, height = 2, selectmode = tk.SINGLE)
        self.list2.grid(row=1,column=1)
        self.list2.insert(tk.END, "Yes")
        self.list2.insert(tk.END, "No")
        self.list2.select_set(0)    
        
        # add in an entry to allow user to name the linear regression
        if self.name == True:
            tk.Label(master, text="Name your PCA: ").grid(row=2, column = 0, pady = 10)
            self.e1 = tk.Entry(master)
            self.e1.grid(row=2, column=1)   
    
    #check if the input is valid
    def validate(self):
        if len(self.list1.curselection())<3:
            messagebox.showwarning(
                "Missing selection", 
                "You must select at least three columns for projection."
            )
            return 0
        if self.name == True:
            if self.e1.get() == '':
                messagebox.showwarning(
                    "Missing name", 
                    "You must name the PCA."
                )
                return 0
        return 1
    
    #apply the input        
    def apply(self):
        self.result = []
        for i in self.list1.curselection():
            self.result.append(self.options[i])
        self.cancelled = False
        if self.name == True:
            self.named = self.e1.get()
        else:
            self.named = "Nameless"
        self.normalize = ["Yes", "No"][self.list2.curselection()[0]]
    
    #gets the input    
    def getInput(self):
        return (self.result,self.named,self.normalize)
       
    #gets whether cancelled 
    def userCancelled(self):
        return self.cancelled
        
        
# custom dialog for PCA projection
class MyDialog8(Dialog):
    
    #initializer for dialog
    #options = a list of possible options
    def __init__(self, parent, options, title = None):
        self.cancelled = True
        self.options = options
        super(MyDialog8,self).__init__(parent, title)
    
    #creates the dialog
    def body(self, master):
        # add in listboxes to allow user to choose which eigenvectors to be the x, y, z axis
        tk.Label(master, text="X axis").grid(row=0, column=0)
        tk.Label(master, text="Y axis").grid(row=0, column=1)
        tk.Label(master, text="Z axis").grid(row=0, column=2)
        tk.Label(master, text="Color axis").grid(row=0, column=3)
        tk.Label(master, text="Size axis").grid(row=0, column=4)
        self.list1 = tk.Listbox(master,exportselection=0, height = 4, selectmode = tk.SINGLE)
        self.list1.grid(row=1,column=0)
        self.list2 = tk.Listbox(master,exportselection=0, height = 4, selectmode = tk.SINGLE)
        self.list2.grid(row=1,column=1)
        self.list3 = tk.Listbox(master,exportselection=0, height = 4, selectmode = tk.SINGLE)
        self.list3.grid(row=1,column=2)
        self.list4 = tk.Listbox(master,exportselection=0, height = 4, selectmode = tk.SINGLE)
        self.list4.grid(row=1,column=3)
        self.list5 = tk.Listbox(master,exportselection=0, height = 4, selectmode = tk.SINGLE)
        self.list5.grid(row=1,column=4)
        #add 'None' to optional columns
        self.list3.insert(tk.END,"None")
        self.list4.insert(tk.END,"None")
        self.list5.insert(tk.END,"None")
        #add the options
        for option in self.options:
            self.list1.insert(tk.END,option)
            self.list2.insert(tk.END,option)
            self.list3.insert(tk.END,option) 
            self.list4.insert(tk.END,option) 
            self.list5.insert(tk.END,option) 
        
        self.list3.select_set(0)
        self.list4.select_set(0)
        self.list5.select_set(0)
        
    
    #check if the input is valid
    def validate(self):
        try:
            hd_x = self.options[self.list1.curselection()[0]]
            hd_y = self.options[self.list2.curselection()[0]]
        except:
            messagebox.showwarning(
                "Missing selection", 
                "You must select exactly one column for each axis."
            )
            return 0
        
        return 1
        
    #apply the input        
    def apply(self):
        hd_x = self.options[self.list1.curselection()[0]]
        hd_y = self.options[self.list2.curselection()[0]]
        
        optionsNone = ['None']+self.options
        hd_z = optionsNone[self.list3.curselection()[0]]
        hd_color = optionsNone[self.list4.curselection()[0]]
        hd_size = optionsNone[self.list5.curselection()[0]]
        self.result = [hd_x, hd_y, hd_z, hd_color, hd_size] # a list to contain the selected eigenvectors
        self.cancelled = False
    
    #gets the input    
    def getInput(self):
        return self.result
     
    #gets whether cancelled 
    def userCancelled(self):
        return self.cancelled   
        
# custom dialog for PCA info display
class MyDialog9(simpledialog.Dialog):
    
    #initializer for dialog
    def __init__(self, parent, pcadata, title = None):
        self.pcadata = pcadata
        super(MyDialog9,self).__init__(parent, title)
    
    #creates the dialog
    def body(self, master):
        #add in the first line of headers
        line1 = ['E-vec', 'E-val', 'Cumulative'] + self.pcadata.get_original_headers()
        for i in range(len(line1)):
            tk.Label(master, text=line1[i]).grid(row=0, column=i, padx = 5, pady = 5)
        #add in the first column of PCA headers e.g PCA0, PCA1, etc.
        pcaheaders = self.pcadata.get_headers()
        for i in range(len(pcaheaders)):
            tk.Label(master, text=pcaheaders[i]).grid(row=i+1, column=0, padx = 5, pady = 5)
        #add in the second column of eigenvalues
        evals = self.pcadata.get_eigenvalues()  
        sum_evals = np.sum(evals)
        for i in range(len(evals)):
            tk.Label(master, text=round(evals[i],3)).grid(row=i+1, column=1, padx = 5, pady = 5)
            #the cumulative eigenvalues to i (inclusive)
            cumul = np.sum(evals[0:i+1])/sum_evals
            tk.Label(master,text=round(cumul,3)).grid(row=i+1, column=2, padx = 5, pady = 5)
        evecs = self.pcadata.get_eigenvectors() 
        for i in range(np.shape(evecs)[0]):
            for j in range(np.shape(evecs)[1]):
                tk.Label(master, text=round(evecs.item(i,j),3)).grid(row=i+1, column=j+3, padx = 5, pady = 5)
    
    def buttonbox(self):
        pass         

# custom dialog for adding new cluster
class MyDialog10(Dialog):
    
    #initializer for dialog
    #options = a list of possible options
    def __init__(self, parent, options, upper, title = None):
        self.cancelled = True
        self.options = options
        self.upper = upper
        super(MyDialog10,self).__init__(parent, title)
    
    #creates the dialog
    def body(self, master):
        # add in listboxes to allow user to choose the independent/dependent variables
        tk.Label(master, text="Choose the columns and the K\n K shoule be between 1 and " + str(self.upper) + ".").grid(row=0, column=0, columnspan=2)
        self.list1 = tk.Listbox(master,exportselection=0, height = 4, selectmode = tk.MULTIPLE)
        self.list1.grid(row=1, column = 0, columnspan=2)
        for option in self.options:
            self.list1.insert(tk.END,option)
            
        # add in an entry to allow user to type in K
        tk.Label(master, text="Number of clusters: ").grid(row=2, column = 0, pady = 10)
        self.e1 = tk.Entry(master)
        self.e1.grid(row=2, column=1)
        
        tk.Label(master, text="Select a distance metric: ").grid(row=3, column = 0, columnspan=2, pady = 10)
        self.list2 = tk.Listbox(master,exportselection=0, height = 4, selectmode = tk.SINGLE)
        self.list2.grid(row = 4, column =0, columnspan = 2)
        for c in ["L2 Norm", "L1 Norm", "Correlation", "Hamming", "Cosine"]:
            self.list2.insert(tk.END, c)
        self.list2.select_set(0)
        
        # add in a checkbox to see ask if the user wants whiten
        self.whiten = tk.IntVar()
        self.cb1 = tk.Checkbutton(master, text = "Whiten?", variable = self.whiten)
        self.cb1.grid(row=5, column = 0, columnspan = 2, pady = 10)
        self.cb1.select()
          
        # add in an entry to allow user to name the linear regression
        tk.Label(master, text="Name your cluster: ").grid(row=6, column = 0, pady = 10)
        self.e2 = tk.Entry(master)
        self.e2.grid(row=6, column=1)   
    
    #check if the input is valid
    def validate(self):
        try:
            K = int(self.e1.get()) #make sure K is int
            if K < 1 or K > self.upper: #make sure K is between the bounds
                messagebox.showwarning(
                    "Invalid number of cluster", 
                    "K must be between 1 and " + str(self.upper) + "."
                )
                return 0
        except:
            messagebox.showwarning(
                "Invalid format for K", 
                "You must type in an positive integer."
            )
            return 0
        
        #make sure there are at least one column selected
        if len(self.list1.curselection())<1:
            messagebox.showwarning(
                "Missing selection", 
                "You must select at least three columns for PCA."
            )
            return 0
        #make sure there is a name given    
        if self.e1.get() == '':
            messagebox.showwarning(
                "Missing name", 
                "You must name the PCA."
            )
            return 0
        
        return 1
    
    #apply the input        
    def apply(self):
        self.result = []
        for i in self.list1.curselection():
            self.result.append(self.options[i])
        self.cancelled = False
        self.K = int(self.e1.get())
        self.name = self.e2.get()
        self.whiten = self.whiten.get()
        self.distance = self.list2.curselection()[0]
    
    #gets the input    
    def getInput(self):
        return (self.result, self.K, self.name, self.whiten, self.distance)
       
    #gets whether cancelled 
    def userCancelled(self):
        return self.cancelled

# custom dialog for cluster info display
class MyDialog11(simpledialog.Dialog):
    
    #initializer for dialog
    def __init__(self, parent, cdata, colors, title = None):
        self.cdata = cdata
        self.colors = colors
        super(MyDialog11,self).__init__(parent, title)
    
    #creates the dialog
    def body(self, master):
        K = self.cdata.get_K()
        means = self.cdata.get_means()
        for i in range(K):
            shape = np.shape(means[i])
            try:
                s = shape[1] #if it is a 1*n matrix not a 0*n array.....I think numpy is stupid.
                m = means[i].tolist()[0]
            except:
                m = means[i].tolist()
            print ("m is: ", m)
            tk.Label(master, text = "mean "+str(i)).grid(row = 0, column = i, padx = 5, pady = 5)
            tk.Label(master, text = str([round(item,2) for item in m])).grid(row = 1, column = i, padx = 5, pady = 5)
            #get the color from colors
            rgb = self.colors[i]
            c = tk.Canvas( master, width=20, height=15, background = rgb )
            c.grid(row = 2, column = i, padx = 5, pady =5)
        
        errors = self.cdata.get_errors().tolist()[0]
        print ("errors is: ", errors)
        sum = 0
        for e in errors:
            # print ("e is", e, "e^2 is", e**2)
            sum += e**2
        print ("data of cdata: ", self.cdata.get_data())
        print ("sum is: ", sum)
        term2 = K/2 * math.log(self.cdata.get_num_points(),2)
        tk.Label(master, text = "Description Length").grid(row = 0, column = K+1, padx = 5, pady = 5)
        tk.Label(master, text = str(round(sum+term2,2))).grid(row = 1, column = K+1, padx = 5, pady = 5)
    
    def buttonbox(self):
        pass         
        
# custom dialog for cluster projection
class MyDialog12(Dialog):
    
    #initializer for dialog
    #options = a list of possible options
    def __init__(self, parent, options, title = None):
        self.cancelled = True
        self.options = options
        super(MyDialog12,self).__init__(parent, title)
    
    #creates the dialog
    def body(self, master):
        # add in listboxes to allow user to choose which eigenvectors to be the x, y, z axis
        tk.Label(master, text="X axis").grid(row=0, column=0)
        tk.Label(master, text="Y axis").grid(row=0, column=1)
        tk.Label(master, text="Z axis").grid(row=0, column=2)
        tk.Label(master, text="Size axis").grid(row=0, column=3)
        self.list1 = tk.Listbox(master,exportselection=0, height = 4, selectmode = tk.SINGLE)
        self.list1.grid(row=1,column=0)
        self.list2 = tk.Listbox(master,exportselection=0, height = 4, selectmode = tk.SINGLE)
        self.list2.grid(row=1,column=1)
        self.list3 = tk.Listbox(master,exportselection=0, height = 4, selectmode = tk.SINGLE)
        self.list3.grid(row=1,column=2)
        self.list5 = tk.Listbox(master,exportselection=0, height = 4, selectmode = tk.SINGLE)
        self.list5.grid(row=1,column=3)
        #add 'None' to optional columns
        self.list3.insert(tk.END,"None")
        self.list5.insert(tk.END,"None")
        #add the options
        for option in self.options:
            self.list1.insert(tk.END,option)
            self.list2.insert(tk.END,option)
            self.list3.insert(tk.END,option)
            self.list5.insert(tk.END,option) 
        
        self.list3.select_set(0)
        self.list5.select_set(0)
        
    
    #check if the input is valid
    def validate(self):
        try:
            hd_x = self.options[self.list1.curselection()[0]]
            hd_y = self.options[self.list2.curselection()[0]]
        except:
            messagebox.showwarning(
                "Missing selection", 
                "You must select exactly one column for each axis."
            )
            return 0
        
        return 1
        
    #apply the input        
    def apply(self):
        hd_x = self.options[self.list1.curselection()[0]]
        hd_y = self.options[self.list2.curselection()[0]]
        
        optionsNone = ['None']+self.options
        hd_z = optionsNone[self.list3.curselection()[0]]
        hd_size = optionsNone[self.list5.curselection()[0]]
        self.result = [hd_x, hd_y, hd_z, "None", hd_size] # a list to contain the selected eigenvectors
        self.cancelled = False
    
    #gets the input    
    def getInput(self):
        return self.result
     
    #gets whether cancelled 
    def userCancelled(self):
        return self.cancelled
        
# custom dialog for new classification
class MyDialog13(Dialog):
    
    #initializer for dialog
    #options = a list of possible options for headers
    def __init__(self, parent, options, title = None):
        self.cancelled = True
        self.options = options
        self.traincats = None
        self.testcats = None
        super(MyDialog13,self).__init__(parent, title)
    
    #check if user wants separate file for categories
    def checkSeparate(self):
        #if the user wants a separate file
        if self.separate.get() == 1:
            self.clist2.grid_forget()
            self.b1 = tk.Button(self.master, text="Select TrainCats", command=self.addTrainCats, width=15)
            self.b1.grid(row = 5)
            self.b1label = tk.Label(self.master, text="Traincats: ")
            self.b1label.grid(row = 6)
            self.b2 = tk.Button(self.master, text="Select TestCats", command=self.addTestCats, width=15)
            self.b2.grid(row = 7)
            self.b2label = tk.Label(self.master, text="Testcats: ")
            self.b2label.grid(row = 8)
        #if the user doesn't want a separate file
        elif self.separate.get() == 0:
            self.clist2.grid(row = 3, column = 0)
            self.clist2.select_set(tk.END)
            self.b1.grid_forget()
            self.b2.grid_forget()
            self.b1label.grid_forget()
            self.b2label.grid_forget()
            self.traincats = None
            self.testcats = None
    
    #check if user wants KNN        
    def checkKNN(self, *args):
        if self.algo.get() == "K-NN":
            self.l1 = tk.Label(self.master, text="Enter the K: ")
            self.l1.grid(row=10)
            self.e1 = tk.Entry(self.master)
            self.e1.grid(row=11)
        else:
            try:
            	self.l1.grid_forget()
            	self.e1.grid_forget()
            except:
            	pass
    
    #select file for traincats
    def addTrainCats(self):
        fn = tk.filedialog.askopenfilename( parent=self.master,
            title='Choose a file for traincats', initialdir='.' )
        # if the filename is not empty string
        if fn != '':
            if fn.endswith(".csv"): #the filename must end with .csv
                #record the category filename
                self.traincats = fn
                self.b1label['text'] = "Traincats: " + fn
   
    #select file for testcats
    def addTestCats(self):
        fn = tk.filedialog.askopenfilename( parent=self.master,
            title='Choose a file for testcats', initialdir='.' )
        # if the filename is not empty string
        if fn != '':
            if fn.endswith(".csv"): #the filename must end with .csv
                #record the category filename
                self.testcats = fn
                self.b2label['text'] = "Testcats: " + fn
    
    #creates the dialog
    def body(self, master):
        self.master = master
        # add in listboxes to allow user to choose the independent/dependent variables
        tk.Label(master, text="Choose the columns to classify with").grid(row=0, column=0)
        self.clist1 = tk.Listbox(master,exportselection=0, height = 4, selectmode = tk.MULTIPLE)
        self.clist1.grid(row=1, column = 0)
        for option in self.options:
            self.clist1.insert(tk.END,option)
        
        tk.Label(master, text="Choose the column for category").grid(row=2, column=0)
        self.clist2 = tk.Listbox(master,exportselection=0, height = 4, selectmode = tk.SINGLE)
        self.clist2.grid(row=3, column = 0)
        for option in self.options:
            self.clist2.insert(tk.END,option)
        self.clist2.select_set(tk.END)
            
        #a check box to ask whether categories is from an outside file
        self.separate = tk.IntVar()
        self.cb2 = tk.Checkbutton(master, 
            text="Separate Files for Categories?", 
            variable=self.separate, 
            command=self.checkSeparate)
        self.cb2.grid(row = 4)
        
        self.algo = tk.StringVar()
        self.algo.set("Naive Bayes") #default algorithm is Naive Bayes
        self.algo.trace('w', self.checkKNN)
        menu = tk.OptionMenu(master, self.algo, "Naive Bayes", "K-NN")
        menu.grid(row=9)

    #check if the input is valid
    def validate(self):
    
        if len(self.clist1.curselection())<1:
            messagebox.showwarning(
                "Missing selection", 
                "You must select at least 1 column for classification."
            )
            return 0
        #if the user wants a separate file
        if self.separate.get() == 1:
            #then there must be a filename selected
            if self.traincats == None or self.testcats == None:
                messagebox.showwarning(
                    "Missing selection", 
                    "You must select a file for each category (if you choose to use separate files)."
                )
                return 0
                
        #if user wants KNN
        if self.algo.get() == "K-NN":
            K = self.e1.get()
            try:
                K = int(K)
                if K < 0:
                    messagebox.showwarning(
                        "Illegal value", 
                        "You must enter an integer > 0."
                    )
                    return 0 
            except:
                messagebox.showwarning(
                    "Wrong format", 
                    "You must enter an integer."
                )
                return 0     
        return 1
    
    #apply the input        
    def apply(self):
        self.result = []
        for i in self.clist1.curselection():
            self.result.append(self.options[i])
        self.cancelled = False
        
        self.result2 = None
        #if the user doesn't want a separate file 
        if self.separate.get() == 0:
            self.result2 = [self.options[self.clist2.curselection()[0]]]
        
        self.mode = 0
        if self.algo.get() == "K-NN":
            self.mode = 1
            
        self.K = None
        if self.algo.get() == "K-NN":
            self.K = int(self.e1.get())
            
    
    #gets the input    
    def getInput(self):
        return (self.result,self.result2,self.traincats, self.testcats, self.mode, self.K) #note: either the 2nd or the (3rd and 4th) is None
       
    #gets whether cancelled 
    def userCancelled(self):
        return self.cancelled        


#test
if __name__ == "__main__":
    dapp = DisplayApp(1100, 900)
    dapp.main()

