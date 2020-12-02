"""
Image borderizer, for instagram and ""aesthetic"" borders on reddit.
"""
import argparse
from PIL import Image, ImageColor
from os.path import abspath, isfile, isdir, splitext
from os import listdir
import enum

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description="Borderizer")


class BorderUnit(enum.Enum):
    PIXELS = 0
    PERCENT = 1


def unroll_files(file_folder_list):
    result_list = []
    folders_to_check = []
    for file in file_folder_list:
        if isfile(abspath(file)):
            result_list.append(abspath(file))
        elif isdir(abspath(file)):
            folders_to_check.append(file)

    while len(folders_to_check) > 0:
        folder_name = folders_to_check.pop(0)
        folder = listdir(folder_name)
        for file in folder:
            file = "{}\\{}".format(folder_name, file)
            if isfile(abspath(file)):
                result_list.append(abspath(file))
            elif isdir(abspath(file)):
                folders_to_check.append(file)

    return result_list


parser.add_argument("files_folders",
                    nargs="*",
                    type=str,
                    default=["."],
                    help="Required, folder or files to convert. Will go recursively for folders.")

parser.add_argument('-s', '--savepath',
                    nargs=1,
                    type=str,
                    default=[None],
                    help="Optional: folder for save location (otherwise it will be done in the same folder as original)")

parser.add_argument('-mh', '--maxheight',
                    nargs=1,
                    type=int,
                    default=[None],
                    help="Optional: maximum height of a finished picture. Original will be scaled down to fit, with correct aspect ratio.")

parser.add_argument('-mw', '--maxwidth',
                    nargs=1,
                    type=int,
                    default=[None],
                    help="Optional: maximum width of the finished picture. Original will be scaled down to fit, with correct aspect ratio.")

parser.add_argument('-bw', '--borderwidth',
                    nargs=1,
                    type=str,
                    default=["0"],
                    help="Optional: width of the border, in %% of the original width, or px. e.g. 100px, 5%% [no unit -> %%]")


parser.add_argument('-bh', '--borderheight',
                    nargs=1,
                    type=str,
                    default=[None],
                    help="Optional: height of the border, in %% of the original height, or px. e.g. 100px, 5%% [no unit -> %%]; if none given, will take the value from ")

parser.add_argument('-c', '--bordercolor',
                    nargs=1,
                    type=str,
                    default=["#ffffff"],
                    help="Optional: color of the border, default is white ('#ffffff')")

parser.add_argument('-sq', '--square',
                    action='store_true',
                    help="Optional: for instagrammers, make a square picture (border will fill enough to make it square)")

parser.add_argument('-x', '--offsetx',
                    nargs=1,
                    type=int,
                    default=[0],
                    help="Optional: offset in the X axis of the base image on the bordered one.")

parser.add_argument('-y', '--offsety',
                    nargs=1,
                    type=int,
                    default=[0],
                    help="Optional: offset in the Y axis of the base image on the bordered one.")
					
parser.add_argument('-q', '--quality',
                    nargs=1,
                    type=int,
                    default=[95],
                    help="Optional: quality of the resulting JPEG file. Default: 95")

args = parser.parse_args()

file_list = unroll_files(args.files_folders)

if args.borderwidth[0][-1] == '%':
    border_width_unit = BorderUnit.PERCENT
    border_width = int(args.borderwidth[0][:-1])
elif args.borderwidth[0][-2:] == 'px':
    border_width_unit = BorderUnit.PIXELS
    border_width = int(args.borderwidth[0][:-2])
else:
    border_width_unit = BorderUnit.PERCENT
    border_width = int(args.borderwidth[0])

if not args.borderheight[0]:
    border_height = border_width
    border_height_unit = border_width_unit
else:
    if args.borderheight[0][-1] == '%':
        border_height_unit = BorderUnit.PERCENT
        border_height = int(args.borderheight[0][:-1])
    elif args.borderheight[0][-2:] == 'px':
        border_height_unit = BorderUnit.PIXELS
        border_height = int(args.borderheight[0][:-2])
    else:
        border_height_unit = BorderUnit.PERCENT
        border_height = int(args.borderheight[0])

i = 1
for file in file_list:
    print("[{}/{}] {}".format(i, len(file_list), file))
    i+=1
    base_img = Image.open(file)

    new_width = int(base_img.width + (border_width*2) if border_width_unit == BorderUnit.PIXELS else (1 + (
                border_width / 50)) * base_img.width)
    new_height = int(base_img.height + (border_height*2) if border_height_unit == BorderUnit.PIXELS else (1 + (
                border_height / 50)) * base_img.height)

    if args.square:
        max_dim = max(new_width, new_height)
        new_width = max_dim
        new_height = max_dim

    new_y = int(((new_height - base_img.height) / 2) + args.offsety[0])
    new_x = int(((new_width - base_img.width) / 2) + args.offsetx[0])

    new_img = Image.new(base_img.mode, [new_width, new_height], args.bordercolor[0])
    new_img.paste(base_img, (new_x, new_y))

    resize = False
    if args.maxwidth[0] and new_width > args.maxwidth[0]:
        ratio = args.maxwidth[0]/new_width
        new_width = args.maxwidth[0]
        new_height = int(ratio * new_height)
        resize = True
        
    if args.maxheight[0] and new_height > args.maxheight[0]:
        ratio = args.maxheight[0]/new_height
        new_height = args.maxheight[0]
        new_width = int(ratio * new_width)
        resize = True

    if resize:
        new_img = new_img.resize((new_width, new_height), resample=Image.LANCZOS)

    new_img.save(splitext(file)[0] + "-bordered" + splitext(file)[1], quality=args.quality[0], dpi=(72,72))

