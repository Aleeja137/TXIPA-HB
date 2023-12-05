import random as rm
import numpy as np
import check
import visualize
import sys

def random_solution(instance):
    scale,nconf,nchip,max_iter,n_pos,t_ext,tmax_chip,t_delta,tam,chip_info = instance
    
    solution = np.empty(nchip*2,dtype=np.int32)
    
    valid = False
    while not valid:
        
        for i in range(nchip):
            x = rm.randint(0,n_pos*2)
            y = rm.randint(0,n_pos)
            
            solution[i*2]   = x
            solution[i*2+1] = y
            
        valid = check.valid_solution(instance,solution)
            
    return solution

def constructive_solution(instance):
    # Va generando la solución poniendo los chips más calientes en la zona de refrigeración
    scale,nconf,nchip,max_iter,n_pos,t_ext,tmax_chip,t_delta,tam,chip_info = instance
    solution = np.empty(nchip*2,dtype=np.int32)
    chips_added = 0
    
    # Crear máximo bounding box
    chip_info_ys    = chip_info[0::3]
    chip_info_xs    = chip_info[1::3]
    chip_info_temps = chip_info[2::3] 
    
    # start_y = int(round(0.44*2*n_pos)) # Valor real, lo he relajado para aproximar una solución
    # end_y   = int(round(0.56*2*n_pos)) # Valor real, lo he relajado para aproximar una solución
    start_y = int(round(0.40*2*n_pos)) # Entre 0.35 y 0.44 es suficiente
    end_y   = int(round(0.60*2*n_pos)) # Entre 0.56 y 0.65 es suficiente
    wide_x  = n_pos
    
    y_max = max(chip_info_ys)
    x_max = max(chip_info_xs)
    alpha_y = round(y_max*0.05) # Dejar un hueco del 5% del mayor tamaño
    alpha_x = round(x_max*0.05) # Dejar un hueco del 5% del mayor tamaño
    
    num_cells = round(wide_x/(x_max+alpha_x))*round((end_y-start_y)/(y_max+alpha_y))
    
    # Solución arbitraria (pobre) a que haya demasiados chips que poner, en general no pasará
    if num_cells < nchip:
        print('\033[93m Error: nchip does not fit in middle zone, using random solution \033[0m', file=sys.stderr)
        return random_solution(instance)
    
    current_y = start_y
    current_x = 0
    
    while chips_added < nchip:
        # Encontrar el chip más caliente
        hottest_index = np.argmax(chip_info_temps)
        hottest_x = chip_info_xs[hottest_index]
        hottest_y = chip_info_ys[hottest_index]
                
        # Comprobar que entra a lo largo en la posición actual
        if (current_x + hottest_x) > wide_x:
            current_y += y_max + alpha_y
            current_x = 0
            
        # Colocar el chip en su posición
        solution[2*chips_added]   = current_y
        solution[2*chips_added+1] = current_x
        
        # Mover los punteros de posición actual 
        current_x += x_max + alpha_x
        
        # Eliminar el elemento más caliente de la lista de pendientes
        chip_info_xs    = np.delete(chip_info_xs,hottest_index)
        chip_info_ys    = np.delete(chip_info_ys,hottest_index)
        chip_info_temps = np.delete(chip_info_temps,hottest_index)

        # Incrementar los chips colocados
        chips_added += 1
        
    print(solution)
    visualize.visualizar_solucion(instance,solution)
    if check.valid_solution(instance,solution):
        return solution
    else:
        print('\033[93m Error: Created solution was not valid, using random one \033[0m', file=sys.stderr)
        return random_solution(instance)