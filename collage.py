from rectpack import newPacker
from PIL import Image
from math import sqrt
from matplotlib import pyplot as plt
import matplotlib.patches as patches


class Collage:
    def __init__(self, ratio, rotation=False):
        self.rotation = rotation
        self.ratio = ratio
        self.picbox = list()

    def _find_add(self, rects):
        r = self.ratio
        lenrec = len(rects)
        totarea = sum([a * b for a, b in rects])
        y = sqrt(totarea * (1 / r))
        x = y * r
        wstart = int(x)
        hstart = int(y)
        add = 0
        while True:
            packer = newPacker(rotation=self.rotation)
            bins = [(wstart + add, hstart + add)]
            for r in rects:
                packer.add_rect(*r)
            for b in bins:
                packer.add_bin(*b)
            packer.pack()
            if len(packer[0]) != lenrec:
                add = add + 1
            else:
                break
        return wstart + add, hstart + add

    def _find_100(self, rects, min_rects=1):
        r = self.ratio
        lenrec = len(rects)
        minarea = min([x * y for x, y in rects])
        minh = min([n[1] for n in rects])
        minw = min([n[0] for n in rects])
        totarea = sum([a * b for a, b in rects])
        y = sqrt(totarea * (1 / r))
        x = y * r
        wstart = int(x)
        hstart = int(y)
        sub = 0
        best_tot = 0
        while True:
            packer = newPacker(rotation=self.rotation)
            cw = wstart - sub
            ch = hstart - sub
            for r in rects:
                packer.add_rect(*r)
            packer.add_bin(cw, ch)
            packer.pack()
            total_area_used = sum([box.used_area() for box in packer])
            if (total_area_used / (cw * ch)) > best_tot:
                best_tot = total_area_used / (cw * ch)
                champ = (cw, ch)
            if (
                cw * ch < minarea
                or cw < minw
                or ch < minh
                or len(packer[0]) < min_rects
            ):
                print("no solution possible for current min_pics")
                print(f"returning best possible solution {100*best_tot:.2f}")
                return champ

            if abs((total_area_used / (cw * ch)) - 1) > 1e-2:
                sub = sub + 1
            else:
                break
        return wstart - sub, hstart - sub

    def feed_pictures(self, filelist):
        # self.picbox = list()
        for pic in filelist:
            im = Image.open(pic)
            self.picbox.append([im.size, pic])

    def solve_place_all_pics(self):
        self.rects = [k[0] for k in self.picbox]
        self.totw, self.toth = self._find_add(self.rects)
        self.packer = newPacker(rotation=self.rotation)
        for r in self.rects:
            self.packer.add_rect(*r)
        self.packer.add_bin(self.totw, self.toth)
        self.packer.pack()
        self.total_area_used = sum([bin.used_area() for bin in self.packer])

    def solve_all_area_used(self, min_pics=1):
        self.rects = [k[0] for k in self.picbox]
        self.totw, self.toth = self._find_100(self.rects, min_rects=min_pics)
        self.packer = newPacker(rotation=self.rotation)
        for r in self.rects:
            self.packer.add_rect(*r)
        self.packer.add_bin(self.totw, self.toth)
        self.packer.pack()
        self.total_area_used = sum([bin.used_area() for bin in self.packer])

    def plot_result(self):
        # taken from https://github.com/secnot/rectpack/issues/16#issuecomment-556886422
        # by https://github.com/Maralai
        for index, abin in enumerate(self.packer):
            bw, bh = abin.width, abin.height
            fig = plt.figure(figsize=(12, 8), dpi=100)
            ax = fig.add_subplot(111, aspect="equal")
            ax.set_title(
                f"Total Width = {self.totw}, Total Height = {self.toth}, Used Area = {100*self.total_area_used/(self.toth*self.totw):.2f}"
            )
            for rect in abin:
                x, y, w, h = rect.x, rect.y, rect.width, rect.height
                plt.axis([0, bw, 0, bh])
                patch = patches.Rectangle(
                    (x, y),  # (x,y)
                    w,  # width
                    h,  # height
                    facecolor="#00ffff",
                    edgecolor="black",
                    linewidth=3,
                )
                ax.add_patch(patch)
                rx, ry = patch.get_xy()
                cx = rx + patch.get_width() / 2.0
                cy = ry + patch.get_height() / 2.0

                ax.annotate(
                    f"w:{w}\nh:{h}",
                    (cx, cy),
                    color="b",
                    weight="bold",
                    fontsize=10,
                    ha="center",
                    va="center",
                )
            plt.show()

    def save_collage(self, filename, true_size=False, background_color="#FFFFFF"):
        img = Image.new("RGB", (self.totw, self.toth), color=background_color)
        for rect in self.packer[0]:
            x, y, w, h = rect.x, rect.y, rect.width, rect.height
            #     print(x, y, w, h)
            idx = self.rects.index((w, h))
            #     print(boxes[idx])
            _ = self.rects.pop(idx)
            a = self.picbox.pop(idx)
            im = Image.open(a[1])
            img.paste(im, (x, y))
        if true_size:
            img.save(filename)
        else:
            (width, height) = (img.width // 10, img.height // 10)
            im_resized = img.resize((width, height))
            im_resized.save(filename)
        self.img = img
