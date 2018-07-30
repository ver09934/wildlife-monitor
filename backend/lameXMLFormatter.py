# Overly simple, crude, and specific module for formatting / writing XML files
# This is probably full of bad ideas, but the library examples I saw for writing XML looked annoying

# creates a file with the specified parent tag
def createFile(filepath, superParentTag):

    writeData = '<?xml version="1.0"?>' + '\n'
    writeData += '<' + str(superParentTag) + '>' + '\n'
    writeData += '</' + str(superParentTag) + '>' + '\n'

    # open file for writing
    with open(filepath, 'w') as f:
        f.write(writeData)

# child tags and child data must be lists of equal length
# appends data to the file within the parent tag
# should work as long as your line endings are LF only (Unix)
def appendFile(filepath, parentTag, childTags, childData):
    
    # open file for reading and writing
    f = open(filepath, 'r')
    
    lines = f.readlines()
    
    lastLine = lines[len(lines) - 1]
    del lines[len(lines) - 1]
    
    f.close()
    f = open(filepath, 'w')

    for line in lines:
        f.write(line)
    
    fileAppendList = []
    
    fileAppendList.append('  ' + '<' + parentTag + '>' + '\n')
    for i in range(0, len(childTags)):
        fileAppendList.append('  ' + '  ' + '<' + str(childTags[i]) + '>' + str(childData[i]) + '</' + str(childTags[i]) + '>' + '\n')
    fileAppendList.append('  ' + '</' + parentTag + '>' + '\n')
    fileAppendList.append(lastLine)
    
    writeString = ""
    for i in range(0, len(fileAppendList)):
        writeString += fileAppendList[i]
    
    f.write(writeString)
