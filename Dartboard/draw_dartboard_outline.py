# ffmpeg A on top of B:
# ffmpeg -i B.png -i A.png -filter_complex "[1]scale=iw/2:-1[b];[0:v][b] overlay" out.png

from math import pi, sin, cos
import cairo

DB_SIZE = 4000
TOTAL_SIZE = 6000

DRAW_NUMS = False

R = [0.037383, 0.093458, 0.55989, 0.63551, 0.92352, 1.0, 1.09, 1.2]
slices = [6, 13, 4, 18, 1, 20, 5, 12, 9, 14, 11, 8, 16, 7, 19, 3, 17, 2, 15, 10]

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, TOTAL_SIZE, TOTAL_SIZE)
#surface = cairo.SVGSurface("outline.svg", TOTAL_SIZE, TOTAL_SIZE)
ctx = cairo.Context(surface)

# Transform axes
ctx.translate(TOTAL_SIZE / 2, TOTAL_SIZE / 2)
ctx.scale(DB_SIZE / 2, DB_SIZE / 2)

# Set line color and width
# ctx.set_source_rgba(0.67, 0.67, 0.69, 0.8)
# ctx.set_line_width(1 / SIZE) # scaled down since axes are transformed
ctx.set_source_rgba(1, 1, 1, 1)
ctx.set_line_width(10 / DB_SIZE) # scaled down since axes are transformed

# Draw slice borders
ctx.rotate(pi / 20)

for i in range(20):
    ctx.move_to(R[1], 0)
    ctx.line_to(R[5], 0)
    ctx.stroke()
    
    ctx.rotate(pi / 10)

ctx.rotate(-pi / 20)


# Draw rings
for i in range(6):
    ctx.arc(0, 0, R[i], 0, 2 * pi)
    ctx.stroke()

if DRAW_NUMS:
    ctx.select_font_face("Open Sans")
    ctx.set_font_size(350 / DB_SIZE) # need to divide by SIZE since the axes are transformed

    for i in range(20):
        _, _, width, height, _, _ = ctx.text_extents(str(slices[i])) 
        ctx.move_to(R[6] * cos(i * pi / 10) - width / 2, R[6] * -sin(i * pi / 10) + height / 2)
        ctx.show_text(str(slices[i]))

surface.write_to_png("outline.png")
