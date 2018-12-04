#CS251 Projects
#Thomas Deng


import csv
import numpy as np
from datetime import datetime
import time

class Data:
    
    def __init__(self, filename = None):
        # create and initialize fields for the class
        
        self.filename = filename
        
        self.rawData = [] #will be empty unless the data is obtained from a file
        
        self.headers = []
        
        self.types = []
        
        self.header2col = {}
        
        self.enumDict = {}
        self.enumCounter = 0
        
        self.strings = []
        
        self.data = np.matrix([])

            
        # if filename is not None
        if (filename != None):
            # call self.read(filename)
            self.read(filename)    
            
    
    def read(self, filename):
        
        #read the csv
        fp = open(filename, 'rU')
        csv_reader = csv.reader( fp )
        
        #add in the headers
        line = next(csv_reader)
        t = []
        for x in range(0, len(line)):
            self.headers.append(line[x].strip())
            self.header2col[line[x].strip()] = x
            t.append(line[x])
        line = next(csv_reader)
        self.rawData.append(t)
        
        #add in the types
        t = []
        for obj in line:
            self.types.append(obj.strip())
            t.append(obj)
        self.rawData.append(t)
            
        #add in the data
        temp = [] #this is the list of list
        
        for line in csv_reader: #go through each line     
            temp2 = [] #this is a row of data
            strs = [] #this is a list of strings
            t = []
            for i in range(0,len(self.types)): #go through cols
                t.append(line[i])
                type = self.types[i]
                material = line[i].strip()
                if type == "numeric": #add in numeric cols to the matrix
                    try:
                        temp2.append(float(material))
                    except:
                        temp2.append(0)
                elif type == "enum":
                    if (material in self.enumDict):
                        index = self.enumDict[material]
                    else:
                        self.enumDict[material] = self.enumCounter
                        index = self.enumCounter
                        self.enumCounter += 1                   
                    temp2.append(index)
                elif type == "date":
                    timestamp = self.date2number(material) #converts a date to a number                                         
                    temp2.append(timestamp)
                elif type == "string":
                    strs.append(material)
                    temp2.append(0) #use 0 as the place holder
            temp.append(temp2)
            self.strings.append(strs)
            self.rawData.append(t)
            
        #make the list of list a matrix 
        self.data = np.matrix(temp)
        fp.close()
        
    #returns the data matrix
    def get_data(self):
        return self.data
        
    #returns a list of all of the headers        
    def get_headers(self):
        return self.headers
    
    #returns a list of all of the types
    def get_types(self):
        return self.types
    
    #returns the number of columns
    def get_num_dimensions(self):
        return np.shape(self.data)[1]
    
    #returns the number of points/rows in the data set
    def get_num_points(self):
        return np.shape(self.data)[0]
    
    #returns the specified row as a NumPy matrix
    def get_row(self, rowIndex):
        if rowIndex >= 0 and rowIndex < self.get_num_points():
            return self.data[rowIndex,:]
        
    #returns the specified col as a NumPy matrix
    def get_col(self, colIndex):
        if colIndex >= 0 and colIndex < self.get_num_dimensions():
            return self.data[:,colIndex]
    
    #returns the specified value in the given column
    def get_value(self, header, rowIndex):
        if header in self.headers and rowIndex >= 0 and rowIndex < self.get_num_points():
            return self.data[rowIndex,self.header2col[header]]
    
    #returns the specified value in the given column index 
    def get_value_with_index(self, colIndex, rowIndex):
        if colIndex >= 0 and colIndex < self.get_num_dimensions() and rowIndex >= 0 and rowIndex < self.get_num_points():
            return self.data[rowIndex,colIndex]
    
    #returns the raw data    
    def get_raw_data(self):
        return self.rawData   
    
    #return the string that displays the current numpy matrix 
    def __str__(self):
        my_str = "   The Data\n"
        #only prints out the first 200 points
        for i in range(0, min(self.get_num_points(), 200)):
            for j in range(0, self.get_num_dimensions()):
                my_str = my_str + " " + str(self.get_value_with_index(j,i))
            my_str += "\n"
        return my_str
    
    #select cols from the matrix and build a new matrix    
    def select_data(self, h_list):
        cols = []
        for i in range(len(h_list)): #strip all the white spaces
            h_list[i] = h_list[i].strip()
        for header in h_list: #loop through the desired headers to check if it's in our list
            if header in self.headers:
                col = self.get_col(self.header2col[header])
                cols.append(col)
                
        newMatrix = np.empty((self.get_num_points(),0)) #create an empty matrix
        for col in cols: #append all the columns to the empty matrix
            newMatrix = np.hstack((newMatrix, col))
        return newMatrix
        
    
    #add a new column to both the csv file and the data matrix. Any extra white spaces at the ends of header or type will get stripped   
    def add_column(self, header, type, data):
        
        t = type.strip()
        h = header.strip()   
        new_col = [] #new data column to be added
        
        if t != "numeric" and t != "string" and t != "enum" and t != "date": #make sure that the type is valid
            print ("Failed to add column, because type must be one of 'numeric','string','enum' or 'date'.") 
            return
            
        if not isinstance(data, list):
            print ("Failed to add column, because data must be a list.")        
        
        if self.filename != None: #if the Data object has read any file                 
            if not len(data)==self.get_num_points(): #make sure that the size of input data matches the number of points
                print ("Failed to add column, please make sure the input data is a list of appropriate size.") 
                return       
            #update raw data
            self.rawData[0].append(header)
            self.rawData[1].append(type)
            for i in range(self.get_num_points()):
                self.rawData[i+2].append(data[i])
        
        else: #if the data is currently empty
            self.data = np.empty((len(data),0)) #construct new matrix
            self.rawData.append([header])
            self.rawData.append([type])
            for i in range(len(data)):
                self.rawData.append([data[i]])
        
        self.header2col[h] = len(self.headers) #this is the index of the new column
        self.headers.append(h) #append header
        self.types.append(t) #append type       
        
                
        
        if t == 'string': #if type is string
            if not self.strings: #if self.strings is empty initially
                for i in range(len(data)): #add a sub-list to each entry
                    temp = [data[i]]
                    self.strings.append(temp) #add the corresponding data to the string list
                    new_col.append(temp) #add the corresponding data to new_col
            else:
                for i in range(len(data)):
                    self.strings[i].append(data[i])
                    new_col.append(temp)
        
        elif t == 'numeric':
            for i in range(len(data)):
                new_col.append(data[i]) #here the i is still string
            for obj in new_col:
                try:
                    obj = float(obj)
                except:
                    obj = 0
            new_col = np.array(new_col).reshape(len(data),1)
            self.data = np.hstack((self.data, new_col)) #add new column to matrix
        
        elif t == 'enum':            
            for i in range(len(data)):
                if (data[i] in self.enumDict):
                    index = self.enumDict[data[i]] #if data is already present
                else:
                    self.enumDict[data[i]] = self.enumCounter
                    index = self.enumCounter
                    self.enumCounter += 1             
                new_col.append(index) #here the i is still string
            new_col = np.array(new_col).reshape(len(data),1)
            self.data = np.hstack((self.data, new_col)) #add new column to matrix
        
        elif t == 'date':            
            for i in range(len(data)):
                index = self.date2number(data[i])    
                new_col.append(index) #here the i is still string
            new_col = np.array(new_col).reshape(len(data),1)
            self.data = np.hstack((self.data, new_col)) #add new column to matrix
            
        # now we write the extended data to a new csv 
        if self.filename != None:
            fp2 = open(self.filename, 'w+')
            csv_writer = csv.writer(fp2, lineterminator='\n') 
            csv_writer.writerows(self.rawData)
            fp2.close()
        else:
            fp2 = open("new.csv", 'w+')
            csv_writer = csv.writer(fp2, lineterminator='\n') 
            csv_writer.writerows(self.rawData)
            fp2.close()
            
        
        
    def date2number(self, material):
        try:
            # example: 12/1/18
            datetime_object = datetime.strptime(material, '%m/%d/%y')
            timestamp = int(time.mktime(datetime_object.timetuple())) #convert back by now = datetime.fromtimestamp(timestamp)
        except:
            try:
                # example: Dec/1/18
                datetime_object = datetime.strptime(material, '%b/%d/%y')
                timestamp = int(time.mktime(datetime_object.timetuple()))
            except:
                try:
                    # example: December/1/18
                    datetime_object = datetime.strptime(material, '%B/%d/%y')
                    timestamp = int(time.mktime(datetime_object.timetuple()))
                except:
                    try:
                        #example: 12/1/2018
                        datetime_object = datetime.strptime(material, '%m/%d/%Y')
                        timestamp = int(time.mktime(datetime_object.timetuple())) #convert back by now = datetime.fromtimestamp(timestamp)
                    except:
                        try:
                            #example: Dec/1/2018
                            datetime_object = datetime.strptime(material, '%b/%d/%Y')
                            timestamp = int(time.mktime(datetime_object.timetuple()))
                        except:
                            try:
                                #example: December/1/2018
                                datetime_object = datetime.strptime(material, '%B/%d/%Y')
                                timestamp = int(time.mktime(datetime_object.timetuple()))
                            except:
                                try:
                                    # example: 12-1-18
                                    datetime_object = datetime.strptime(material, '%m-%d-%y')
                                    timestamp = int(time.mktime(datetime_object.timetuple())) #convert back by now = datetime.fromtimestamp(timestamp)
                                except:
                                    try:
                                        # example: Dec-1-18
                                        datetime_object = datetime.strptime(material, '%b-%d-%y')
                                        timestamp = int(time.mktime(datetime_object.timetuple()))
                                    except:
                                        try:
                                            # example: December-1-18
                                            datetime_object = datetime.strptime(material, '%B-%d-%y')
                                            timestamp = int(time.mktime(datetime_object.timetuple()))
                                        except:
                                            try:
                                                #example: 12-1-2018
                                                datetime_object = datetime.strptime(material, '%m-%d-%Y')
                                                timestamp = int(time.mktime(datetime_object.timetuple())) #convert back by now = datetime.fromtimestamp(timestamp)
                                            except:
                                                try:
                                                    #example: Dec-1-2018
                                                    datetime_object = datetime.strptime(material, '%b-%d-%Y')
                                                    timestamp = int(time.mktime(datetime_object.timetuple()))
                                                except:
                                                    try:
                                                        #example: December-1-2018
                                                        datetime_object = datetime.strptime(material, '%B-%d-%Y')
                                                        timestamp = int(time.mktime(datetime_object.timetuple()))
                                                    except:                                                 
                                                        try:
                                                            # example: 12, 1, 18
                                                            datetime_object = datetime.strptime(material, '%m, %d, %y')
                                                            timestamp = int(time.mktime(datetime_object.timetuple())) #convert back by now = datetime.fromtimestamp(timestamp)
                                                        except:
                                                            try:
                                                                # example: Dec, 1, 18
                                                                datetime_object = datetime.strptime(material, '%b, %d, %y')
                                                                timestamp = int(time.mktime(datetime_object.timetuple()))
                                                            except:
                                                                try:
                                                                    # example: December, 1, 18
                                                                    datetime_object = datetime.strptime(material, '%B, %d, %y')
                                                                    timestamp = int(time.mktime(datetime_object.timetuple()))
                                                                except:
                                                                    try:
                                                                        #example: 12, 1, 2018
                                                                        datetime_object = datetime.strptime(material, '%m, %d, %Y')
                                                                        timestamp = int(time.mktime(datetime_object.timetuple())) #convert back by now = datetime.fromtimestamp(timestamp)
                                                                    except:
                                                                        try:
                                                                            #example: Dec, 1, 2018
                                                                            datetime_object = datetime.strptime(material, '%b, %d, %Y')
                                                                            timestamp = int(time.mktime(datetime_object.timetuple()))
                                                                        except:
                                                                            try:
                                                                                #example: December, 1, 2018
                                                                                datetime_object = datetime.strptime(material, '%B, %d, %Y')
                                                                                timestamp = int(time.mktime(datetime_object.timetuple()))
                                                                            except: 
                                                                                timestamp = 0 #meaning the format is unrecognized
        return timestamp
    
    
       
    
#subclass PCAData    
class PCAData(Data):

    #takes in np-matrices: pdata, evecs, evals, means, and list: headers
    #assumes all the data are numeric
    def __init__(self, pdata, evecs, evals, means, headers):
        #initiate as an empty Data object
        super(PCAData, self).__init__()
    
        #set the original headers
        self.original_headers = headers
        
        #set the new headers
        count = 0
        for i in range(len(headers)):
            s = 'PCA' + str(count)
            self.headers.append(s)
            count += 1
    
        #set the types
        for i in range(len(headers)):
            self.types.append("numeric")
    
        #set the data
        self.data = pdata
    
        #set the header-to-column dictionary
        for i in range(len(headers)):
            self.header2col[self.headers[i]] = i
    
        #the following fields of the Data class are intentionally left empty
        #self.filename
        #self.rawData
        #self.strings
        #self.enumDict
        #self.enumCounter
    
        #initiate the new fields
        self.evecs = evecs
        self.evals = evals
        self.means = means

    #returns a copy of the eigenvalues as a single-row numpy matrix.    
    def get_eigenvalues(self):
        return self.evals

    #returns a copy of the eigenvectors as a numpy matrix with the eigenvectors as rows.
    def get_eigenvectors(self):
        return self.evecs

    #returns the means for each column in the original data as a single row numpy matrix.
    def get_original_means(self):
        return self.means

    #returns a copy of the list of the headers from the original data used to generate the projected data.
    def get_original_headers(self):
        return self.original_headers        
    
#subclass ClusterData    
class ClusterData(Data):
    
    def __init__(self, original_data, K, means, ids, errors, whiten=True):
        super(ClusterData, self).__init__()
        
        self.data = original_data
        self.means = means
        self.K = K
        self.ids = ids
        self.errors = errors
        self.whiten = whiten
                
    def get_original_data(self):
    	return self.data
                
    def get_means(self):
        return self.means
    
    def get_K(self):
        return self.K
        
    def get_ids(self):
        return self.ids 
    
    def get_errors(self):
    	return self.errors 
    
    def get_whiten(self):
    	return self.whiten  
      
      
      
      
      
      
      
      
      