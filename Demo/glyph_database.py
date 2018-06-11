#diccionario que asocia cada codigo de un marcador con un archivo correspondiente a reemplazar por el glifo
#el archivo en cuestion puede ser una imagen o una nube de puntos
GLYPH_TABLE = {}

#las claves del diccionario son strings que representan los codigos 
g_1 = repr( [ [0, 1, 0], [1, 0, 0], [0, 1, 1] ] )
g_2 = repr([ [1, 0, 0], [0, 1, 0], [1, 0, 1] ] )

#el contenido de cada elemento es una tupla conformada por el nombre del archivo y su tipo
GLYPH_TABLE[g_1] = ("doge", "image")
GLYPH_TABLE[g_2] = ("napoleon", "point_cloud")


#matchear un patron con un valor del diccionario
def match_glyph_pattern(glyph_pattern):  
    #casteo del codigo binario a string
    
    str_glyph_pattern = repr(glyph_pattern)
    #se maneja el error de intentar acceder al diccionario con una clave invalida
    try :
        glyph_substitute = GLYPH_TABLE[str_glyph_pattern]
        glyph_found = True
    except KeyError:
        glyph_found = False
        glyph_substitute = (None,None)    
    return glyph_found, glyph_substitute   
