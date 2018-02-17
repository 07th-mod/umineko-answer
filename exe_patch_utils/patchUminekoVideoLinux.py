import re

leaPattern = b'\x8D\x44\x00\x04'

#calculate what the new instructions should be
newLeaPattern = b'\x90\x90\x90\x90' #replace with NOP

print('NOTE - Use the windows widescreen patcher to get 1080p Resolution for the linux executable\n\n')

with open(r'widescreen-1920x1080-Umineko5to8', "rb") as f:
    exe_byte_array_raw = f.read()
    
    #for linux_skip the first 352676 bytes to ignore an incorrect match
    start_of_exe = exe_byte_array_raw[:352576]
    area_to_patch = exe_byte_array_raw[352576:]

    #substitute the old byte sequence with the new byte sequence. Only replace the first instance
    (area_to_patch, n_height_subs) = re.subn(leaPattern, newLeaPattern, area_to_patch)
    print('Replacemnts Made:', n_height_subs)
    if n_height_subs != 2:
        print("Error: couldn't patch set height instruction!")
        exit(0)


#finally, save the file to disk with 'widescreen' appended to the name
with open(r'Umineko5to8w_video.exe', 'wb') as outFile:
    outFile.write(start_of_exe)
    outFile.write(area_to_patch)
    print("----------------")
    print("Finished, wrote to:", outFile.name)


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
