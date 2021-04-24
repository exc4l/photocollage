# photocollage
Stuff about photo collages

If you are looking for something functional which results in a printable collage you should check out [PhotoCollage](https://github.com/adrienverge/PhotoCollage) by Adrien Vergé.

I created this repository because Adrien's program crops pictures, which was undesirable. Therefore, I wanted something that is capable of creating pictures in a given ratio without losing something. Therefore I'm utilizing [rectpacker](https://github.com/secnot/rectpack) to solve the rectangle packing problem of the pictures.

Currently implemented are two ways of generating collages one which tries to fit all pictures into the given ratio and one that will try to find a collage with the least wasted area.

As can be seen in the example code you can plot the result before actually saving the collage.
true_size=False will divide width and height by 10 before saving it. The actual picture is still in col.img and could be saved via col.img.save().

```python
from pathlib import Path
from collage import Collage
picp = Path()
pics = list(picp.glob("*"))

col = Collage(80/60)
col.feed_pictures(pics)
col.solve_place_all_pics()
col.plot_result()

col = Collage(16/9)
col.feed_pictures(pics)
col.solve_all_area_used(min_pics=20)
col.plot_result()
col.save_collage("test.png", true_size=False, background_color="#FFFFFF")
```
