import glob
from PIL import Image

from classes import giftools

class Animation:
    """cdef int image_width, image_height, interframe_enabled, brightness, individual_frame_time
    cdef double delay
    cdef list frames
    cdef list raw_frames
    cdef str dir"""


    def __init__(self, **kwargs):
        self.dir = kwargs.pop('dir', None)
        self.image_width = kwargs.pop('width', None)
        self.image_height = kwargs.pop('height', None)
        self.interframe_enabled = True
        self.brightness = 255
        self.delay = 0.033 #30 fps
        self.individual_frame_time = False
        self.frames = [] #List of Image objects (PIL)
        self.raw_frames = []
        self.loop = False
        self.cur_index = 0 #Use this for frame stepping. Also could be used for pausing and passing off the class.

    def xy_to_index(self, x, y): #This should not be repetitively called be loops, but im doing it anyway lol
        if y % 2 == 0: #even, lines 0,2,4,etc.
            return (self.image_width * y) + x
        else: #even
            return (self.image_width * y) - x

    def encode_frames(self, frames, **kwargs): #Make sure to always pass the same kwargs when compiling an animation
        give_list = kwargs.pop("list", False)
        single_frame = False
        if not isinstance(frames, list) and not isinstance(frames, tuple):
            single_frame = True
        frames = [frames] if single_frame else frames
        done = []
        for frame in frames:
            interframe = kwargs.pop("interframe", False)
            pixels = frame.load()
            buffer = b""
            i = 0
            for y in range(frame.size[1]):
                for x in range(frame.size[0]):
                    ind = self.xy_to_index(x, y)
                    p = pixels[x,y]
                    i += 1
                    if interframe is True: #This could be optimized by moving it to encapsulate each for loop, but I'm putting readability over super optimization
                        buffer += ind.to_bytes(4, 'little')
                    buffer += p[0].to_bytes(1, 'little') + p[1].to_bytes(1, 'little') + p[2].to_bytes(1, 'little')
            #buffer += b"\x69\x04\x20"
            done.append(buffer)
        if single_frame:
            if give_list:
                return done
            else:
                return done[0]
        return done #give the caller their bytes back

    def decode_frames(self, data, **kwargs):
        give_list = kwargs.pop("list", False)
        single_frame = False
        if not isinstance(data, list) and not isinstance(data, tuple):
            single_frame = True
        data = [data] if single_frame else data
        done = []
        for frame in data:
            read_head = 0 #read offset
            interframe = kwargs.pop("interframe", True)
            pixel_len = 7 if interframe else 3
            d = []
            while read_head < len(frame):
                """if not interframe:
                    index = None
                else:
                    index = int.from_bytes(frame[read_head:read_head+4], 'little') #read the first four bytes
                    #print(data[read_head:read_head+4], index)"""
                index = None
                read_head -= 4 #Do this because im not implementing interframe right now (are maybe anymore)
                r = int.from_bytes(frame[read_head+4:read_head+5], 'little')
                g = int.from_bytes(frame[read_head+5:read_head+6], 'little')
                b = int.from_bytes(frame[read_head+6:read_head+7], 'little')
                d.append((r, g, b))
                read_head += pixel_len
            done.append(d)
        if single_frame:
            if give_list:
                return done
            else:
                return done[0]
        return done

    def construct_image(self,arr):
        img = Image.new(size=(16,16), mode='RGB')

        pixles = list(img.getdata())
        #print(len(pixles))
        cur_x = 0
        cur_y = 0
        """for i in range(32*32):
            if cur_x > 32:
                cur_x = 0
                cur_y +=1
            pixles[cur_y][cur_x] = (arr[i][1],arr[i][2],arr[i][3])"""
        img.putdata(arr)
        img.show()


    def decode_anim(self, data):
        read_head = 0
        self.frame_count = int.from_bytes(data[:2], 'little')
        self.image_width = int.from_bytes(data[2:4], 'little')
        self.image_height = int.from_bytes(data[4:6], 'little')
        self.delay = int.from_bytes(data[6:8], 'little')/1000
        self.brightness = int.from_bytes(data[8:9], 'little')
        self.interframe_enabled = True if data[9:10] == b"\xff" else False
        self.loop = True if data[10:11] == b"\xff" else False
        read_head = 11 #Skip over all the headers already parsed
        frames = []
        frame_len = 3*self.image_width*self.image_height #Length of bytes for non interframe encoded files
        buffer = b""
        while read_head < len(data):
            frames.append(data[read_head:read_head+frame_len])
            read_head += frame_len
        return self.decode_frames(frames)

    def save_anim_file(self, out, **kwargs): #converts frame into a proprietary format optimized for playback
        interframe = kwargs.pop("interframe", True) #Only record differences in frames, reduces file size
        headers = [] #Headers so we can automatically detect how to read the file back

        #header layout (fixed length)
        #00 00 00 00 00 00 00 00 00 00 00 .. .. .. (the rest of the encoded data goes here depedning on param #6)
        #|_1_| |_2_| |_3_| |_4_| 5  6  7
        #1: Frame count (2 bytes)
        #2: DISPLAY_WIDTH (2 bytes)
        #3: DISPLAY_HEIGHT (2 bytes)
        #4: Interframe Delay (2 bytes, in milliseconds, max of ~65 seconds)
        #5: Brightness (1 byte, 0 to 255)
        #6: Interframe Enabled (ff if on, 00 if off)
        #7: Loop (0xff: Loop, 0x00: Don't loop)

        #display instruction encoding (interframe compression enabled)
        #00 00 00 00 00 00 00 .. .. .. 69 04 20 (69 04 20 signifies EOF)
        #-----1----- 2  3  4
        #1: Display index (32 bit, 4.2 bil is the max)
        #2-4: R, G, B

        #display instruction encoding (interframe compression disabled)
        #00 00 00 .. .. .. 69 04 20 (69 04 20 signifies EOF)
        #1  2  3
        #1-3, R, G, B
        buffer = b""
        buffer += len(self.frames).to_bytes(2, 'little')
        buffer += self.image_width.to_bytes(2, 'little')
        buffer += self.image_height.to_bytes(2, 'little')
        buffer += int(self.delay*1000).to_bytes(2, 'little')
        buffer += self.brightness.to_bytes(1, 'little')
        buffer += b"\x00" #Interframe, not implemented
        buffer += b"\xff" if self.loop else b"\x00"
        #print(len(b"\x20\x00\x20\x00\x20\x00\x21\x00\xff\xff\xff"))
        #buffer += b"\x20\x00\x20\x00\x20\x00\x21\x00\xff\xff\xff"
        for frame in self.encode_frames(self.frames):
            buffer += frame
        with open(out, "wb") as f:
            f.write(buffer)

    def read_anim_file(self, file):
        with open(file, "rb") as f:
            self.raw_frames = self.decode_anim(f.read())
        return self

    def open_dir(self, dir):
        types = ("*.png", "*.jpg", "*.jpeg")
        files = []
        for f in types:
            fileslist = glob.glob(dir + "/" + f)
            fileslist.sort()
            files.append(fileslist)
        files = [inner for outer in files for inner in outer]
        self.frames = [Image.open(file).convert("RGB") for file in files]
        if not self.image_height:
            self.image_height = self.frames[0].size[1]
        if not self.image_width:
            self.image_width = self.frames[0].size[0]

    def open_gif(self, dir, **kwargs): #We have to average frame durations because I suck
        #gif = Image.open(dir)
        #gif.seek(0)
        #frames = duration = 0
        imdata = giftools.processImage(dir)
        """framelist = []
        while True:
            try:
                frames += 1
                duration += gif.info['duration']
                framelist.append(gif.convert("P").convert("RGB"))
                gif.seek(gif.tell() + 1) #Go forward a frame
            except EOFError:
                duration = frames / duration #Give the average speed
                break"""
        duration = kwargs.pop('duration', imdata[1])
        framelist = imdata[0]
        self.image_width, self.image_height = framelist[0].width, framelist[0].height
        self.frames = framelist

    #Iterator helpers
    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        self.n += 1
        if self.n < len(self.frames):
            return self.frames[self.n]
        else:
            raise StopIteration

    #Indexing helper
    def __getitem__(self, index):
        return self.frames[index]

class SequencedAnimation():

    def __get__(self, instance, owner):
        print(instance, owner)