# Radius generator, using the Spybot:TNI version of range.
# Basically: if abs(deltaX) + abs(deltaY) <= radius, it's in range.


def getRadius2D(radius, origin=[0,0,0]):
    # Return a list of coords in the radius.
    coords = []
    x = 0
    while x <= radius:
        for y in range(0, radius-x+1):
            if x != 0 and y != 0:
                coords.append([origin[0]+x, origin[1]+y, origin[2]])
                coords.append([origin[0]+x, origin[1]-y, origin[2]])
                coords.append([origin[0]-x, origin[1]+y, origin[2]])
                coords.append([origin[0]-x, origin[1]-y, origin[2]])
            elif x == 0 and y != 0:
                coords.append([origin[0]+x, origin[1]+y, origin[2]])
                coords.append([origin[0]+x, origin[1]-y, origin[2]])
            elif x != 0 and y == 0:
                coords.append([origin[0]+x, origin[1]+y, origin[2]])
                coords.append([origin[0]-x, origin[1]+y, origin[2]])
        x += 1

    coords.append([origin[0], origin[1], origin[2]])

    return coords


def getRadius3D(startingRadius, origin=[0,0,0]):
    coords = []
    currentRadius = startingRadius
    while currentRadius > 0:
        coords += getRadius2D(currentRadius, [origin[0], origin[1], origin[2] + startingRadius - currentRadius])

        currentRadius -= 1

    return coords


                              

