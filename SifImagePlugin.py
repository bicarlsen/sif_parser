import Image, ImageFile

# Read Andor Technology Multi-Channel files with PIL.
# Based on Marcel Leutenegger's MATLAB script.

_MAGIC = 'Andor Technology Multi-Channel File\n'

# --------------------------------------------------------------------
# SIF reader

def _read_var_len_str(fp):
    '''Read a string of variable length.  This is encoded by the textual
    representation of the string length, followed by a newline, followed
    by the string itself.'''
    l = int(fp.readline())
    return fp.read(l)

class SifImageFile(ImageFile.ImageFile):
    format = "SIF"
    format_description = "Andor Technology Multi-Channel File"

    def _open(self):
        if self.fp.read(36) != _MAGIC:
            raise SyntaxError('not a SIF file')

        for i in range(2):
            self.fp.readline()

        self.info['Camera'] = self.fp.readline() #var
        self.info['DetectorDimensions'] = self.fp.readline()
        self.info['OriginalFilename'] = self.fp.readline()

        for i in range(3):
            self.fp.readline()

        self.fp.readline() # Contains shutter time?

        for i in range(15):
            self.fp.readline()
        
        self.info['FrameAxis'] = self.fp.readline()
        self.info['XAxis'] = self.fp.readline() #var
        self.info['ImageAxis'] = self.fp.readline() #var
	# var that follows is also a data type, probably YAxis

        foo = self.fp.readline()
        img_area = foo.strip().split()
        num_frames = 1 + int(img_area[7]) - int(img_area[6]) # What's going on here
        frame_area = self.fp.readline().strip().split()
        [x0,x1,y1,y0,ybin,xbin] = map(int,frame_area[1:7])
        width = (1 + x1 - x0) / xbin
        height = (1 + y1 - y0) / ybin
        for frame in range(num_frames):
            self.fp.read(int(self.fp.readline())) # vars, frame titles?

        self.mode = 'F'
        self.size = (width, height)

        self.tile = []
        offset = self.fp.tell() + 2
        for frame in range(num_frames):
            self.tile.append(('raw', (0,0) + self.size , offset + frame * 4 * width * height, ('F;32F', 0, 1)))


# --------------------------------------------------------------------
# Registry

Image.register_open("SIF", SifImageFile)
Image.register_extension("SIF", ".sif")
