# TIOM stuff.  Functions and formulas to calculate the offset of a sprite during an animation.  Also, how long an animation will take.

def noOffset(source, frameNum):
    return (0, 0)

# Offset functions
def simpleMovementOffset(source, frameNum):
    startingCoord = (source.coord[0] - source.direction[0], source.coord[1] - source.direction[1], source.coord[2] - source.direction[2])
    directionToStart = (-source.direction[0], -source.direction[1], -source.direction[2])
    # The coord we're heading to is the coord the source is pointing towards.
    totalDistanceInMeters = (source.direction[0]**2 + source.direction[1]**2 + source.direction[1]**2)**0.5
    totalFrames = simpleMovementTime(source)
    
    distanceInPixels = (source.direction[0]*32, source.direction[1]*32 + source.direction[2]*32)

    xOffset = distanceInPixels[0] / totalFrames * frameNum
    yOffset = distanceInPixels[1] / totalFrames * frameNum

    totalOffset = (xOffset + directionToStart[0] * 32, yOffset + (directionToStart[1] + directionToStart[1]) * 32 / 2)

    return totalOffset

def simpleJumpOffset(source, frameNum):
    startingCoord = (source.coord[0] - source.direction[0], source.coord[1] - source.direction[1], source.coord[2] - source.direction[2])
    directionToStart = (-source.direction[0], -source.direction[1], -source.direction[2])
    # The coord we're heading to is the coord the source is pointing towards.
    totalDistanceInMeters = (source.direction[0]**2 + source.direction[1]**2 + source.direction[1]**2)**0.5
    totalFrames = simpleJumpTime(source)
    
    distanceInPixels = (source.direction[0]*32, source.direction[1]*32 + source.direction[2]*32)

    xOffset = distanceInPixels[0] / totalFrames * frameNum
    yOffset = distanceInPixels[1] / totalFrames * frameNum

    totalOffset = (xOffset + directionToStart[0] * 32, yOffset + (directionToStart[1] + directionToStart[1]) * 32 / 2)

    return totalOffset


# Time functions
def simpleMovementTime(source):
    framesPerMeter = 10
    if source.speed == 0:
        framesPerMeter = 10
    elif source.speed == 1:
        framesPerMeter = 7
    elif source.speed == 2:
        framesPerMeter = 4
        
    totalDistanceInMeters = (source.direction[0]**2 + source.direction[1]**2 + source.direction[1]**2)**0.5
    totalFrames = int(totalDistanceInMeters * framesPerMeter)
    return totalFrames

def simpleJumpTime(source): # Basically simpleMovementTime(), but triple speed
    totalDistanceInMeters = (source.direction[0]**2 + source.direction[1]**2 + source.direction[1]**2)**0.5
    totalFrames = int(totalDistanceInMeters * 3)
    return totalFrames

# Cutscene motion functions
def noMotion(frameNum, direction):
    return (0,0)

def walkMotion(frameNum, direction):
    return (direction[0] * 7, direction[1] * 7)
