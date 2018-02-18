# sequence of instructions can be decoded at https://defuse.ca/online-x86-assembler.htm#disassembly
# mov edx, 960
# mov ecx, 1280
# BA C0030000   -> mov edx, 0x03c0 (note immediate operand is little-endian for x86)
# B9 00050000   -> mov ecx, 0x0500
# or reference, expected values for 1920 x 1080 are: width: 80 07 00 00, height: 38 04 00 00
import re, hashlib, argparse

########################################## Function/Constant Definitions ###############################################

# a list of output .exe files' sha-1 values which are known to work
valid_sha1 = ['f9f26593d5dc5a5efd917404699a7f0c04ad3c26']

#target instructions to be modified
heightPattern = b'\xBA\xC0\x03\x00\x00'
widthPattern = b'\xB9\x00\x05\x00\x00'

#functions only for printing - not critical
def getInstructionString(arr, offset = 0):
    return ' '.join(['{:02x}'.format(b) for b in arr[offset:offset + 5]])

def printInstruction(arr, offset):
    print(getInstructionString(arr,offset))

################################################# Begin code execution #################################################

print("""Remember that the background images and effect images must be patched to a 16:9 aspect ratio!
Movie files should also be changed to 1080p otherwise they will not fill the screen.
Please use --width and --height if you would like a custom aspect ratio.""")

#read in height/width/filename from command line if provided
parser = argparse.ArgumentParser(description='Patch Umineko to use a different resolution')
parser.add_argument('--filename', default = "Umineko5to8.exe")
parser.add_argument('--width', type=int, default = 1920)
parser.add_argument('--height', type=int, default = 1080)
parser.add_argument('--script', default ='0.utf')
parser.add_argument('--windows_line_endings', action='store_true')
parser.add_argument('--debug', action='store_true') #enter debug mode if '-d' given

args = parser.parse_args()
print('Settings used:', args)

#set line ending mode (either force windows newlines, or use whatever is given
newlineMode=''
if args.windows_line_endings:
    newlineMode = None

#calculate what the new instructions should be
newHeightPattern = b'\xBA' + args.height.to_bytes(4, 'little')
newWidthPattern = b'\xB9' + args.width.to_bytes(4, 'little')

print("\n\n----------------")
print("Begin exe widescreen patch")
print("----------------")

output_name = 'widescreen-' + str(args.width) + 'x' + str(args.height)

with open(args.filename, "rb") as f:
    exe_byte_array = f.read()

    #calculate sha1 of the exe and check if it is as expected. if not, possibly different .exe version but will still work
    m = hashlib.sha1()
    m.update(exe_byte_array)

    print('Input file SHA-1 [{}]'.format(m.hexdigest()))
    if m.hexdigest() in valid_sha1:
        print('SHA-1 OK, patch should work')
    else:
        print('SHA-1 does not match, however may still work. Please report this new SHA-1 value, along with whether patch was successful')

    print("----------------")
    print("Trying to patch resolution to {}x{}. Changes:".format(args.width, args.height))
    print("\tHeight: [{}] -> [{}]".format(getInstructionString(heightPattern),getInstructionString(newHeightPattern)))
    print("\tWidth : [{}] -> [{}]".format(getInstructionString(widthPattern), getInstructionString(newWidthPattern)))

    #substitute the old byte sequence with the new byte sequence. Only replace the first instance
    (exe_byte_array, n_height_subs) = re.subn(heightPattern, newHeightPattern, exe_byte_array, count=1)
    if n_height_subs != 1:
        print("Error: couldn't patch set height instruction!")
        exit(0)

    (exe_byte_array, n_width_subs) = re.subn(widthPattern, newWidthPattern, exe_byte_array, count=1)
    if n_width_subs != 1:
        print("Error: couldn't patch set width instruction!")
        exit(0)

    #finally, save the file to disk with 'widescreen' appended to the name
    with open(output_name + '-' + args.filename, 'wb') as outFile:
        outFile.write(exe_byte_array)
        print("----------------")
        print("Finished, wrote to:", outFile.name)