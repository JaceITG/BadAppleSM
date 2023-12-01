import skvideo.io
import skvideo.utils
import shutil

fps = 12

def make_frame(frame):
    frame_str = ""

    for r in frame:
        for c in r:
            if c[0] < 127:
                frame_str += "0"
            else:
                frame_str += "M"
        frame_str += '\n'

    frame_str += ''.join(["00000000\n" for i in range(7)])

    return frame_str

def gen_notes():
    warps = []
    scrolls = []

    viddat = skvideo.io.vreader("badapple.mp4", as_grey=True,
                              outputdict={
                           "-sws_flags": "bilinear",
                           "-s": "8x8",
                           "-r": f"{fps}"
                       })
    #print(f"Parsed video with shape {viddat.shape}")
    print("Processing Frames: frame ", end='\r')

    with open("notes.txt", 'w') as f:
        counter = 0
        for framearr in viddat:
            frame = framearr[0]
            print(f"Processing Frames: frame {counter} shape {frame.shape}", end='\r')

            #check for start of new measure
            if counter % fps == 0 and counter > 0:
                f.write(",\n")

            f.write(make_frame(frame))

            # (4*counter) / fps gives us what beat we are on
            beat = (4*counter) / fps
            warp_len = 2/fps
            # put warp and scroll set (high) on starting beat of frame
            warps.append(f"{beat:.3f}={warp_len}")
            scrolls.append(f"{beat:.3f}={fps/2}")

            #reset scroll after warp
            scrolls.append(f"{beat+warp_len:.3f}=0.000")
            
            counter += 1
    
    return warps, scrolls


def main():
    #init ssc using header file
    shutil.copyfile("./header.txt", "./badapple.ssc")

    warps, scrolls = gen_notes()

    with open("badapple.ssc", 'a') as f:
        f.write("#WARPS:")
        f.write( ',\n'.join(warps) )
        f.write(";\n")

        f.write("#SCROLLS:")
        f.write( ',\n'.join(scrolls) )
        f.write(";\n")

        #Add header before note data
        with open("noteheader.txt", "r") as header:
            f.write( header.read() )

        #Add note data
        with open("notes.txt", 'r') as notes:
            f.write( notes.read() )
        
        f.write(';')

if __name__ == "__main__":
    main()