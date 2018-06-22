#funciones utilizadas para reconocer marcadores y reemplazarlos en la escena

import numpy as np
import cv2
import point_cloud_functions as pc
 
TOPDOWN_SIDE = 100
CELLS_IN_A_GLYPH = 5


#funcion que a partir de una imagen obtiene el codigo binario que representa
def get_glyph_pattern(image, black_threshold, white_threshold):
    
    #lista multidimensional de 5x5, llena de 0s, que representa el codigo binario que se desea determinar
    binary = [[0 for x in range(CELLS_IN_A_GLYPH)] for y in range(CELLS_IN_A_GLYPH)] 
    
    #ancho y alto de cada celda en un marcador
    cell_width = int((image.shape[1] / CELLS_IN_A_GLYPH))
    cell_height = int((image.shape[0] / CELLS_IN_A_GLYPH))

    #se visita cada celda y se cuenta la cantidad de pixeles sobre el umbral de blanco o debajo del umbral de negro
    for j in range(CELLS_IN_A_GLYPH):          
        for i in range(CELLS_IN_A_GLYPH):
            black_counter = 0
            white_counter = 0
            for iy in range(cell_height -1):
                for ix in range(cell_width -1):
                    val = image[cell_height*j + iy ,cell_width*i + ix ]
                    
                    if val < black_threshold:
                        black_counter += 1
                    elif val > white_threshold:
                        white_counter += 1
                    else:
                        pass
            #el valor correspondiente en el codigo binario tomara un valor dependiendo la cantidad de pixeles negros y blancos
            if white_counter < black_counter :
                binary[j][i] = 0
            else:
                binary[j][i] = 1


    return binary


#funcion para verificar si un codigo que se reconocio de la escena corresponde a un glifo valido (cada elemento de su frontera es 0)
def is_valid_glyph(glyph_pattern):
    valid_glyph = True
    for i in range(CELLS_IN_A_GLYPH):
        for j in range (5):
            #solo interesa analizar el contenido de la frontera
            if i>0 and i<CELLS_IN_A_GLYPH-1 and j>0 and j<CELLS_IN_A_GLYPH-1:
                continue
            #si un elemento de su frontera no es 0 entonces el patron no corresponde a un glifo valido
            if glyph_pattern[i][j] != 0:
                valid_glyph = False
                break
    return valid_glyph
    
#funcion que toma un arreglo de puntos, correspondientes a los vertices de un cuadrilatero, y devuelve un arreglo con estos puntos, en el orden
#vertice superior izquierdo, vertice superior derecho, vertice inferior derecho, vertice inferior izquierdo
def order_points(points):
    s = points.sum(axis=1)
    diff = np.diff(points, axis=1)
     
    ordered_points = np.zeros((4,2), dtype="float32")
 
    ordered_points[0] = points[np.argmin(s)]
    ordered_points[2] = points[np.argmax(s)]
    ordered_points[1] = points[np.argmin(diff)]
    ordered_points[3] = points[np.argmax(diff)]
 
    return ordered_points


#funcion que dado un ancho y alto devuelve un arreglo con vertices de un rectangulo, en el orden
#vertice superior izquierdo, vertice superior derecho, vertice inferior derecho, vertice inferior izquierdo
def topdown_points(width, height):
    return np.array([
        [0, 0],
        [width-1, 0],
        [width-1, height-1],
        [0, height-1]], dtype="float32")
    
    
#funcion utilizada para obtener una vista de frente del marcador hallado en una escena
def get_topdown_quad(image, src):
    #se ordenan los vertices del cuadrilatero hallado (src)
    src = order_points(src)
    
    #se busca una homografia que relacione los vertices en cuestion con un cuadrado de 100x100
    
    dst = topdown_points(TOPDOWN_SIDE, TOPDOWN_SIDE)
    matrix, mask = cv2.findHomography(src, dst, cv2.RANSAC, 5.0)
    
    #se aplica la homografia al cuadrilatero hallado, obteniendo una vista de frente del glifo
    warped = cv2.warpPerspective(image, matrix, (TOPDOWN_SIDE, TOPDOWN_SIDE))
    return warped

#funcion para reemplazar un glifo hallado en la escena por una imagen sustituto 
def add_substitute_quad(image, substitute_quad, dst):
    #se ordenan los vertices del glifo en la escena
    dst = order_points(dst)
    #se determinan los minimos y maximos valores de x, y 
    (tl, tr, br, bl) = dst
    min_x = min(int(tl[0]), int(bl[0]))
    min_y = min(int(tl[1]), int(tr[1]))
    max_x = max(int(tr[0]), int(br[0]))
    max_y = max(int(bl[1]), int(br[1]))
    
    new_width = max_x - min_x
    new_height = max_y - min_y  
    
    #se desplazan los puntos de dst, para poder encontrar correctamente la homografia necesaria
    for point in dst:
        point[0] = point[0] - min_x
        point[1] = point[1] - min_y
        
    #con las variables new_width, new_height se determinan los vertices de un rectangulo    
    src = topdown_points(new_width, new_height)

    #se redimensiona la imagen sustituto
    substitute_quad = cv2.resize(substitute_quad, (new_width, new_height))

    #variable en la que se almacenara la imagen sustituto puesta en perspectiva
    warped = np.zeros((new_height,new_width, 3), np.uint8) 
    warped[:,:,:] = 0
 
    #se halla la homografia entre src y dst (esta subrutina funciona como findHomography)
    matrix = cv2.getPerspectiveTransform(src, dst)

    #se aplica la transformacion
    cv2.warpPerspective(substitute_quad, matrix, (new_width,new_height), warped, borderMode=cv2.BORDER_TRANSPARENT)

    #se reemplazan los pixeles de la escena por los pixeles de warped
    for i in range(new_height):
        for j in range(new_width):
            #el reemplazo se hace si el valor del pixel en warped es mayor a 0
            image[min_y + i, min_x + j] = warped[i,j] if (warped[i,j].all() != 0) else image[min_y + i, min_x + j]
            
    return image, dst

#funcion para reemplazar un glifo hallado en la escena por una nube de puntos
def add_substitute_cloud(image, cloud, dst):
    #se ordenan los puntos destino
    dst = order_points(dst)

    #se determinan los minimos y  maximos valores de x, utilizados para hacer un resizing mas adelante   
    (tl, tr, br, bl) = dst
    min_x = min(int(tl[0]), int(bl[0]))
    max_x = max(int(tr[0]), int(br[0]))
    
    new_width = max_x - min_x

    #se determina el centro del marcador
    center = (tl+tr+br+bl) / 4
    center[0] = int(center[0])
    center[1] = int(center[1])
    
    #se obtiene una imagen a partir de la nube de puntos (en formato numpy array) 
    cloud_img = pc.cloud2image(cloud)

    #se redimensiona la nube de puntos para colocarla sobre la escena
    ratio = cloud_img.shape[0] / cloud_img.shape[1] #height/width
    new_height = int(new_width*ratio)
    resized = cv2.resize(cloud_img, (new_width, new_height) )

    half_h = int(new_height / 2)
    half_w = int(new_width / 2)    
    
    #se reemplazan los pixeles de la escena por los pixeles de cloud_img
    for i in range(-half_h, half_h):
        for j in range(-half_w, half_w):
            y = int( center[1] + i  ) 
            x = int( center[0] + j )     
            #si son posiciones validas
            if (y >= 0) and (y < image.shape[0]) and (x >= 0) and (x < image.shape[1]):
                #el reemplazo se hace si el valor del pixel cloud_img es mayor a 0
                image[y , x, :] = resized[i + half_h, j + half_w, :]*255 if (resized[i + half_h, j + half_w, :].all() != 0) else image[y,  x, :]
            
    return image








