# Overly simple, crude, and specific module for formatting / writing XML files
# Provides a quick alternative to the murky depths of xml.etree.ElementTree
# Will probably only work if files are only ever created/written with these methods

# creates a file with the specified parent tag
def createFile(filepath, superParentTag):

    writeData = '<?xml version="1.0"?>' + '\n'
    writeData += '<' + str(superParentTag) + '>' + '\n'
    writeData += '</' + str(superParentTag) + '>' + '\n'

    # open file for writing
    with open(filepath, 'w') as f:
        f.write(writeData)

# append one top-level element to the xml file
# if nested, append one child element to the last top-level element... in a bodged-together fashion
def appendFile(filepath, parentTag, parentData, nested):

    # open file for reading and writing
    f = open(filepath, 'r')
    
    lines = f.readlines()
    
    lastLine = lines[len(lines) - 1]
    del lines[len(lines) - 1]

    secondLastLine = ''
    if nested:
        secondLastLine = lines[len(lines) - 1]
        del lines[len(lines) - 1]
    
    f.close()
    f = open(filepath, 'w')

    for line in lines:
        f.write(line)
        
    writeString = '  ' + '<' + parentTag + '>' + str(parentData) + '</' + parentTag + '>' + '\n'
    writeString += secondLastLine + lastLine

    f.write(writeString)

# append arrays of elements to the file within the specified parent tag
# childTags and childData must be arrays of equal length
def appendFileChildren(filepath, parentTag, childTags, childData):

    if len(childTags ) != len(childData):
        print('childTags and childData not same length in lameXMLFormatter.appendFileChildren()... not writing data.')
        return
    
    # open file for reading and writing
    f = open(filepath, 'r')
    
    lines = f.readlines()
    
    lastLine = lines[len(lines) - 1]
    del lines[len(lines) - 1]
    
    f.close()
    f = open(filepath, 'w')

    for line in lines:
        f.write(line)

    writeString = ""
    
    writeString += '  ' + '<' + parentTag + '>' + '\n'
    for i in range(0, len(childTags)):
        writeString += '  ' + '  ' + '<' + str(childTags[i]) + '>' + str(childData[i]) + '</' + str(childTags[i]) + '>' + '\n'
    writeString += '  ' + '</' + parentTag + '>' + '\n'
    writeString += lastLine

    f.write(writeString)
