#Thomas Deng
#CS251 Project 3
#View

import sys
import numpy as np
import math as m

class View:
    
    def __init__(self):  
        self.reset()
    
    #set all parameters to default    
    def reset(self):    
        self.vrp = np.array([0.5, 0.5, 1.])
        self.vpn = np.array([0., 0., -1.])
        self.vup = np.array([0., 1., 0.])
        self.u = np.array([-1., 0., 0.])
        self.extent = np.array([1., 1., 1.])
        self.screen = np.array([450., 450.])
        self.offset = np.array([100., 100.])
    
    #use the current viewing parameters to return a view matrix
    def build(self):
        vtm = np.identity(4, float)
        t1 = np.matrix( [[1, 0, 0, -self.vrp[0]],
                        [0, 1, 0, -self.vrp[1]],
                        [0, 0, 1, -self.vrp[2]],
                        [0, 0, 0, 1] ] )
        vtm = t1 * vtm
        
        tu = self.normalize(np.cross(self.vup, self.vpn))
        tvup = self.normalize(np.cross(self.vpn, tu))
        tvpn = self.normalize(np.copy(self.vpn))
        
        # align the axes
        r1 = np.matrix( [[ tu[0], tu[1], tu[2], 0.0 ],
                        [ tvup[0], tvup[1], tvup[2], 0.0 ],
                        [ tvpn[0], tvpn[1], tvpn[2], 0.0 ],
                        [ 0.0, 0.0, 0.0, 1.0 ] ] )

        vtm = r1 * vtm
        
        t2 = np.matrix( [[1, 0, 0, 0.5 * self.extent[0]],
                        [0, 1, 0, 0.5 * self.extent[1]],
                        [0, 0, 1, 0],
                        [0, 0, 0, 1] ] )
        
        vtm = t2 * vtm
        
        s1 = np.matrix( [[- self.screen[0] / self.extent[0], 0, 0, 0],
                        [0, -self.screen[1] / self.extent[1], 0, 0],
                        [0, 0, 1.0 / self.extent[2], 0],
                        [0, 0, 0, 1] ] )
                            
        vtm = s1 * vtm
        
        t3 = np.matrix( [[1, 0, 0, self.screen[0] + self.offset[0]],
                        [0, 1, 0, self.screen[1] + self.offset[1]],
                        [0, 0, 1, 0],
                        [0, 0, 0, 1] ] )
                            
        vtm = t3 * vtm
        
        return vtm
        
        
    #normalize a numpy vector
    def normalize(self, vector):
        length = np.linalg.norm(vector)
        if length != 0:
            vector *= 1/length
        return vector  
    
    #rotate the space by angleX aroundX axis and angleY around Y axis
    def rotateVRC(self, angleX, angleY):
        center = self.vrp + self.vpn * self.extent.item(2) * 0.5
        t1 = np.matrix( [[1, 0, 0, -center.item(0)],
                        [0, 1, 0, -center.item(1)],
                        [0, 0, 1, -center.item(2)],
                        [0, 0, 0, 1]] )
        
                        
        Rxyz = np.matrix( [[self.u[0], self.u[1], self.u[2], 0.0 ],
                        [ self.vup[0], self.vup[1], self.vup[2], 0.0 ],
                        [ self.vpn[0], self.vpn[1], self.vpn[2], 0.0 ],
                        [ 0.0, 0.0, 0.0, 1.0 ] ] )                   
                        
        r1 = np.matrix( [[m.cos(angleY), 0, m.sin(angleY), 0],
                        [0, 1, 0, 0],
                        [-m.sin(angleY), 0, m.cos(angleY), 0],
                        [0, 0, 0, 1] ] )            
        
        r2 = np.matrix( [[1, 0, 0, 0],
                        [0, m.cos(angleX), -m.sin(angleX), 0],
                        [0, m.sin(angleX), m.cos(angleX), 0],
                        [0, 0, 0, 1] ] )

        t2 = np.matrix( [[1, 0, 0, center.item(0)],
                        [0, 1, 0, center.item(1)],
                        [0, 0, 1, center.item(2)],
                        [0, 0, 0, 1]] )
                        
                        
        tvrc = np.matrix( [[self.vrp[0], self.vrp[1], self.vrp[2], 1],
                        [self.u[0], self.u[1], self.u[2], 0],
                        [self.vup[0], self.vup[1], self.vup[2], 0],
                        [self.vpn[0], self.vpn[1], self.vpn[2], 0]] )
                        
        tvrc = (t2*Rxyz.T*r2*r1*Rxyz*t1*tvrc.T).T
        
        self.vrp = np.array([tvrc[0,0],tvrc[0,1],tvrc[0,2]])
        self.u = self.normalize(np.array([tvrc[1,0],tvrc[1,1],tvrc[1,2]]))
        self.vup = self.normalize(np.array([tvrc[2,0],tvrc[2,1],tvrc[2,2]]))
        self.vpn = self.normalize(np.array([tvrc[3,0],tvrc[3,1],tvrc[3,2]]))
           
    
    #make a duplicate of the current View object and return it   
    def clone(self):
        v = View() 
        v.vrp = np.copy(self.vrp)
        v.vpn = np.copy(self.vpn)
        v.vup = np.copy(self.vup)
        v.u = np.copy(self.u)
        v.extent = np.copy(self.extent)
        v.screen = np.copy(self.screen)
        v.offset = np.copy(self.offset)
        return v
        
        
    def main(self):
        print(self.build())
        self.rotateVRC(0,0)
        print(self.build())
        
if __name__ == "__main__":
    view = View()
    view.main()    
            