# This file patches the new Umineko1to4.exe to use full size videos. The PonscripterLabel_sound.cpp file has been changed, so the method of patching has changed too.
# In the future, open the .exe in IDA, lookup a known function (like SDL_RenderCopy), press X to chart xrefs to, and check all the xrefs.

import re, sys

# these bytes control the video offset
# controls the video offset (r2.x/y in the file PonscripterLabel_sound.cpp):
#leaPattern = re.escape(b'\xC7\x85\x58\xFF\xFF\xFF\x02\x00\x00\x00\xC7\x85\x5C\xFF\xFF\xFF\x02\x00\x00\x00') - this controls the video pixel offset, currently set to 2pix

#NOTE: before  re.escape was not used, which may have led to incorrect behavior depeding on the replacement string...this has now been fixed
leaPattern = re.escape(b'\x8d\x04\x09\x8b\x8d\xdc\xfe\xff\xff\x89\x85\x60\xff\xff\xff\x8d\x04\x09')

#calculate what the new instructions should be
newLeaPattern = b'\x8d\x01\x90\x8b\x8d\xdc\xfe\xff\xff\x89\x85\x60\xff\xff\xff\x8d\x01\x90' #replace with NOP

if len(sys.argv) <= 1:
    print("Must supply file to patch as first argument - no arguments supplied")
    exit(-1)
    
file_to_patch = sys.argv[1]

with open(file_to_patch, "rb") as f:
    exe_byte_array = f.read()

    #substitute the old byte sequence with the new byte sequence. Only replace the first instance
    (exe_byte_array, n_height_subs) = re.subn(leaPattern, newLeaPattern, exe_byte_array, count=2)
    print('Replacemnts Made:', n_height_subs)
    if n_height_subs != 1:
        print("Error: couldn't patch set height instruction!")
        exit(0)


#finally, save the file to disk with 'widescreen' appended to the name
with open(file_to_patch + 'video.exe', 'wb') as outFile:
    outFile.write(exe_byte_array)
    print("----------------")
    print("Finished, wrote to:", outFile.name)

# Original Version:
#.text:0044A68C                 call    SDL_UpdateTexture
#.text:0044A691                 mov     ecx, [ebp+var_128]
#.text:0044A697                 mov     [esp+1A8h+var_1A0], esi
#.text:0044A69B                 mov     [ebp+var_A8], 2      //load 2 (the video offset)
#.text:0044A6A5                 mov     [ebp+var_A4], 2      //load 2 (the video offset)
#.text:0044A6AF                 lea     eax, [ecx+ecx]       //multiply by 2 of ecx into eax (should be 8d 04 09)
#.text:0044A6B2                 mov     ecx, [ebp+var_124]
#.text:0044A6B8                 mov     [ebp+var_A0], eax
#.text:0044A6BE                 lea     eax, [ecx+ecx]       //multiply by 2 of ecx into eax (should be 8d 04 09)
#.text:0044A6C1                 mov     [ebp+var_9C], eax
#.text:0044A6C7                 lea     eax, [ebp+var_A8]
#.text:0044A6CD                 mov     [esp+1A8h+var_19C], eax
#.text:0044A6D1                 mov     eax, ds:dword_786130
#.text:0044A6D6                 mov     [esp+1A8h+var_1A4], eax
#.text:0044A6DA                 mov     eax, [ebp+var_164]
#.text:0044A6E0                 mov     eax, [eax+0D00h]
#.text:0044A6E6                 mov     [esp+1A8h+var_1A8], eax
#.text:0044A6E9                 call    SDL_RenderCopy
#
# Updated Version:
#.text:0044A68C                 call    SDL_UpdateTexture
#.text:0044A691                 mov     ecx, [ebp+var_128]
#.text:0044A697                 mov     [esp+1A8h+var_1A0], esi
#.text:0044A69B                 mov     [ebp+var_A8], 2
#.text:0044A6A5                 mov     [ebp+var_A4], 2
#.text:0044A6AF                 lea     eax, [ecx+ecx]       //change to just ecx NOP(should be 8d 01 90) (90 is NOP)
#.text:0044A6B2                 mov     ecx, [ebp+var_124]
#.text:0044A6B8                 mov     [ebp+var_A0], eax    
#.text:0044A6BE                 lea     eax, [ecx+ecx]       //change to just ecx NOP(should be 8d 01 90)
#.text:0044A6C1                 mov     [ebp+var_9C], eax
#.text:0044A6C7                 lea     eax, [ebp+var_A8]
#.text:0044A6CD                 mov     [esp+1A8h+var_19C], eax
#.text:0044A6D1                 mov     eax, ds:dword_786130
#.text:0044A6D6                 mov     [esp+1A8h+var_1A4], eax
#.text:0044A6DA                 mov     eax, [ebp+var_164]
#.text:0044A6E0                 mov     eax, [eax+0D00h]
#.text:0044A6E6                 mov     [esp+1A8h+var_1A8], eax
#.text:0044A6E9                 call    SDL_RenderCopy

    

#notes:
# I used IDA pro and Cheat Engine (especially cheat engine)
#
# The address is around >>>> [0044A47B] <<<< (it is just before the function call to SDL_RenderCopy(renderer, video_texture, &r, &r); in PonscripterLable_sound.cpp)
#
# SDL_Rect r;
# r.x = 0; r.y = 0; r.w = c.frame->image_width; r.h = c.frame->image_height;
# SDL_UpdateTexture(video_texture, &r, c.frame->image, c.frame->image_width);
# SDL_RenderCopy(renderer, video_texture, &r, &r);
#
# Where doubled width is set
# widescreen-1920x1080-Umineko5to8.exe+4A48F - 8D 44 00 04           - lea eax,[eax+eax+04]      <- uses 0xF04 = 3844
# widescreen-1920x1080-Umineko5to8.exe+4A493 - 89 85 60FFFFFF        - mov [ebp-000000A0],eax
#
# Where doubled height is set
# widescreen-1920x1080-Umineko5to8.exe+4A49F - 8D 44 00 04           - lea eax,[eax+eax+04]      <- uses 0x880 = 2176
# widescreen-1920x1080-Umineko5to8.exe+4A4A3 - 89 85 64FFFFFF        - mov [ebp-0000009C],eax
#
# when the lea instructions are disabled (set to NOP) for some reason it uses the old values (the previous arguments are 1922x1080 or something like that)
# I suspect the lea instruction is being used as multiply + add as an optimization by the compiler
# If you open the game with cheat engine, nopping will unstretch the screen as the video plays
