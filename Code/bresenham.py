#Bresenham's line algorithm.
#Code ported from RogueBasin.

def getLine2D(start, end):
    #Setup initial conditions
    x1 = start[0]
    y1 = start[1]
    x2 = end[0]
    y2 = end[1]
    dx = x2 - x1
    dy = y2 - y1

    #Determine how steep the line is
    is_steep = abs(dy) > abs(dx)

    #Rotate line
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    #Swap start and end points if necessary and store swap state
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True

    #Recalculate differentials
    dx = x2 - x1
    dy = y2 - y1

    #Calculate error
    error = int(dx / 2.0)
    if y1 < y2:
        ystep = 1
    else:
        ystep = -1

    #Iterate over bounding box generating points between start and end
    y = y1
    points = []
    for x in range(x1, x2 + 1):
        if is_steep:
            coord = [y, x]
        else:
            coord = [x, y]
        points.append(coord)
        error -= abs(dy)
        if error < 0:
            y += ystep
            error += dx

    #Reverse the list if the coordinates were swapped
    if swapped:
        points.reverse()
    return points


def getLine3D(start, end): # Ported from Robotica.
    coords = []
    
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dz = end[2] - start[2]

    xxx = start[0]
    yyy = start[1]
    zzz = start[2]

    if dx < 0:
        x_inc = -1
    else:
        x_inc = 1

    if dy < 0:
        y_inc = -1
    else:
        y_inc = 1

    if dz < 0:
        z_inc = -1
    else:
        z_inc = 1

    adx = abs(dx)
    ady = abs(dy)
    adz = abs(dz)

    dx2 = adx*2
    dy2 = ady*2
    dz2 = adz*2

    if (adx >= ady) and (adx >= adz):

        err_1 = dy2 - adx
        err_2 = dz2 - adx

        for i in range(0, adx):
            if (err_1 > 0):
                yyy += y_inc
                err_1 -= dx2

            if (err_2 > 0):
                zzz += z_inc
                err_2 -= dx2

            err_1 += dy2
            err_2 += dz2
            xxx += x_inc

            coords.append([xxx, yyy, zzz])

    if (ady > adx) and (ady >= adz):

        err_1 = dx2 - ady
        err_2 = dz2 - ady

        for i in range(0, ady):
            if (err_1 > 0):
                xxx += x_inc
                err_1 -= dy2

            if (err_2 > 0):
                zzz += z_inc
                err_2 -= dy2

            err_1 += dx2
            err_2 += dz2
            yyy += y_inc

            coords.append([xxx, yyy, zzz])

    if (adz > adx) and (adz > ady):
        err_1 = dy2 - adz
        err_2 = dx2 - adz

        for i in range(0, adz):
            if (err_1 > 0):
                yyy += y_inc
                err_1 -= dz2

            if (err_2 > 0):
                xxx += x_inc
                err_2 -= dz2

            err_1 += dy2
            err_2 += dx2
            zzz += z_inc

            coords.append([xxx, yyy, zzz])


    return coords
