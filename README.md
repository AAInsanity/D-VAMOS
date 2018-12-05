# D-VAMOS
Data Visualization and Analysis Multi-Operational System
The project for CS251 (Data Visualization) at Colby College (Spring 18, Prof. Eaton)

Developed with Python 3.6.5 and X11 Tkinter (Isn't perfectly compatible with Aqua Tkinter as tested)

How to use:
Download the files
Change to the corresponding directory
Run python display3D.py


How to visualize data?

1) User reads the data from file (either with cntl-o or with the "open" menu-item on top left). 

2) The selected filename will be added to the listbox (reading multiple files is supported). User then choose what dataset they want to plot from the listbox. Then hit apply.

3) 5 option menus will be generated accordingly to let the user select which column to plot on which dimension. Once the selections are all set, user hits plot data.

4) When the data is plotted, user can perform all sorts of operations with the plot (pan, zoom, rotate, click on the dot to show full data, view analysis..)

5) If the user want to use another dataset, they can repeat the same procedure. If the user want to change the dimensions, they can just make their changes with the option menus and hit "plot data" again, and the plot will be updated.


How to create linear regression?

1) Make sure a data set is already read in. If not, use cntl-o or the open button in the menu to read in a data set. Then hit apply to apply the selection.

2) Find the Create Regression button on the menu bar, click on it.

3) In the pop-up dialog, choose the regression axes from the list boxes and give the progression a name

4) Hit OK and get your regression

5) User can save the regression as a file by clicking the Save Regression tab in the menu bar


How to revisit a previous linear regression?

1) Find the Regression History tab in the menu bar, click on it

2) Select the previous regression you would revisit, and hit OK. 

How to read a saved regression file

1) Find the Read Regression File in menu bar, click on it

2) From the dialog, select the file that contains the regression information and hit OK


How to run PCA?

1) Enable the PCA feature from menu

2) Read in (using Cntl-O) some data file if having already done so, hit apply

3) Click on "Add New PCA"

4) Select all columns you want for the PCA from the listbox, put in a name, and hit OK

5) Now the new PCA is in the listbox with the user specified name, make sure it is selected before you perform other actions

6) To project the PCA, click on the "Project Data" button, in the pop up dialog, select which column to plot on which axis, and hit OK.

7) To see the specs of the PCA, click on the "View PCA Specs" button for the pop up dialog


How to save PCA to file?

1) After the PCA is created, click on "Save PCA to File", type in the name you want, hit OK and the file will be in the app directory.


How to read the saved PCA file?
1) Click on "Read PCA from File", select the file you want to read, hit OK and the PCA will be read in.


How to run clustering?

1) Read in a file using cntl-o, then hit apply.

2) Show the clustering frame by clicking the "show/hide cluster" item, ignore this step if its already on.

3) Press the "Add New Cluster"

4) In the pop up dialog, select the columns to perform clustering, the K, whether or not to whiten, the distance metric, and give it a name. Hit OK after that.

5) Now you can draw the clustering you just created, by hitting. the "Draw Cluster" button. Select the columns you want to plot it on then hit OK.

6) You can also view the specs of the cluster by pressing "View Cluster Specs". It will give you the numeric values of the means, the color associated with each mean and the Description Length that tells you the quality of the clustering.

7) If you want to delete a clustering, you can simply select the clustering in the list box and hit "Delete Cluster"
