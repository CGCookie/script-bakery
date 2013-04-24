'''
Created on Apr 23, 2013

@author: Patrick Moore, patrick.moore.bu@gmail.com
some copy right?
some use agreement?
Open sourceness?
'''
import bpy
import bgl
import blf
from bpy_extras import view3d_utils 

def callback_register(self, context):
        if str(bpy.app.build_revision)[2:7] == "unkno" or eval(str(bpy.app.build_revision)[2:7]) >= 53207:
            self._handle = bpy.types.SpaceView3D.draw_handler_add(self.menu.draw, (self, context), 'WINDOW', 'POST_PIXEL')
        else:
            self._handle = context.region.callback_add(self.menu.draw, (self, context), 'POST_PIXEL')
        return None
            
def callback_cleanup(self, context):
    if str(bpy.app.build_revision)[2:7] == "unkno" or eval(str(bpy.app.build_revision)[2:7]) >= 53207:
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, "WINDOW")
    else:
        context.region.callback_remove(self._handle)
    return None

def draw_points(context, points, color, size):
    '''
    draw a bunch of dots
    args:
        points: a list of tuples representing x,y SCREEN coordinate eg [(10,30),(11,31),...]
        color: tuple (r,g,b,a)
        size: integer? maybe a float
    '''

    bgl.glColor4f(*color)
    bgl.glPointSize(size)
    bgl.glBegin(bgl.GL_POINTS)
    for coord in points:  
        bgl.glVertex2f(*coord)  
    
    bgl.glEnd()   
    return

def draw_polyline_from_points(context, points, color, thickness, LINE_TYPE):
    '''
    a simple way to draw a line
    args:
        points: a list of tuples representing x,y SCREEN coordinate eg [(10,30),(11,31),...]
        color: tuple (r,g,b,a)
        thickness: integer? maybe a float
        LINE_TYPE:  eg...bgl.GL_LINE_STIPPLE or 
    '''
    
    if LINE_TYPE == "GL_LINE_STIPPLE":  
        bgl.glLineStipple(4, 0x5555)  #play with this later
        bgl.glEnable(bgl.GL_LINE_STIPPLE)  
    
    bgl.glColor4f(*color)
    bgl.glLineWidth(thickness)
    bgl.glBegin(bgl.GL_LINE_STRIP)
    for coord in points:  
        bgl.glVertex2f(*coord)  
    
    bgl.glEnd()  
      
    if LINE_TYPE == "GL_LINE_STIPPLE":  
        bgl.glDisable(bgl.GL_LINE_STIPPLE)  
        bgl.glEnable(bgl.GL_BLEND)  # back to uninterupted lines  
      
    return