#funciones utilizadas en el manejo de la nube de puntos

import numpy as np
import math


#funcion que lee un archivo de texto, cuyas lineas contienen 3 numeros spearados por ',' (vertices), y devuelve un numpy array
def text2cloud(file):
    #tupla que contiene cada linea del .txt
    lines = tuple(open(file, 'r'))
    #lista cuyos elementos son a su vez listas de 3 numeros (coordenadas x,y,z)    
    cloud = [ vertix for vertix in [line.split() for line in lines] ]
    #casteo a int
    cloud = [[int(float(component)) for component in vertix] for vertix in cloud]
    #casteo a numpy array
    cloud = np.array(cloud)
    return cloud

#funcion para rotar una nube de puntos (de tipo numpy array) con respecto al eje x
def rotate_x(cloud, theta):
    #matriz de rotacion
    rotation_matrix = np.array([    [1, 0, 0],
                                    [0, math.cos( theta ), -math.sin( theta )],
                                    [0, math.sin( theta ), math.cos( theta )]
                                ])
    #rotacion de cada vertice
    for i in range( len(cloud) ): 
        cloud[i] = np.matmul( rotation_matrix , cloud[i])
        
    return cloud

#funcion para rotar una nube de puntos (de tipo numpy array) con respecto al eje y
def rotate_y(cloud, theta):
    #matriz de rotacion
    rotation_matrix = np.array([     [math.cos( theta ), 0, math.sin( theta )],
                                     [0, 1, 0],
                                     [-math.sin( theta ), 0, math.cos( theta )]
                                ])
    #rotacion de cada vertice
    for i in range( len(cloud) ):
        cloud[i] = np.matmul( rotation_matrix , cloud[i])
        
    return cloud

#funcion para rotar una nube de puntos (de tipo numpy array) con respecto al ele z
def rotate_z(cloud, theta):
    #matriz de rotacion
    rotation_matrix = np.array([     [math.cos( theta ), -math.sin( theta ), 0],
                                     [math.sin( theta ), math.cos( theta ), 0],
                                     [0, 0, 1]
                                ])    
    #rotacion de cada vertice
    for i in range( len(cloud) ):
        cloud[i] = np.matmul( rotation_matrix , cloud[i])

    return cloud


#funcion que toma una nube de puntos (de tipo numpy array) y devuelve una imagen en escala de grises (con 3 canales)     
def cloud2image(cloud):
    #se calcula el minimo y maximo en cada direccion
    min_x = min(cloud[:,0])
    min_y = min(cloud[:,1])
    min_z = min(cloud[:,2]) 
    max_x = max(cloud[:,0])
    max_y = max(cloud[:,1])
    max_z = max(cloud[:,2])
    
    #los valores en z se interpolan para obtener valores entre 0 y 255
    cloud[:,2] = np.interp(cloud[:,2], [min_z, max_z], [0,255])
    
    #se crea una matriz con 3 canales, de tamaño tal que entren todos los puntos x,y
    img = np.zeros( (max_y - min_y + 1, max_x - min_x + 1, 3) ).astype(int)
    
    #se llena cada pixel correspondiente a un vertice de la nube con el valor z de dicho vertice
    for i in range( len( cloud ) ):
        #si se quiere asignar un pixel cuyo valor x,y coincide con el de dos (o mas) vertices, entonces el pixel toma el valor del vertice con menor z
        if cloud[i][2] > img[ cloud[i][1]  - min_y][ cloud[i][0] - min_x, 0] :
            img[ cloud[i][1] - min_y ][ cloud[i][0] - min_x, 0] = cloud[i][2]
            img[ cloud[i][1] - min_y ][ cloud[i][0] - min_x, 1] = cloud[i][2]
            img[ cloud[i][1] - min_y ][ cloud[i][0] - min_x, 2] = cloud[i][2]
    
    return img / 255


