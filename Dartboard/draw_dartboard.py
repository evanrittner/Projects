# Script to generate a dartboard vector graphic

from math import pi, sin, cos
import cairo

SIZE = 500

R = [0.037383, 0.093458, 0.55989, 0.63551, 0.92352, 1.0, 1.09, 1.2]
side_len = int(SIZE * R[7])

slices = [6, 13, 4, 18, 1, 20, 5, 12, 9, 14, 11, 8, 16, 7, 19, 3, 17, 2, 15, 10]

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, side_len, side_len)
#surface = cairo.SVGSurface("dartboard.svg", side_len, side_len)
ctx = cairo.Context(surface)

# Transform axes
ctx.translate(side_len / 2, side_len / 2)
ctx.scale(SIZE / 2, SIZE / 2)

# Draw background black circle
ctx.set_source_rgba(0, 0, 0, 1.0)
ctx.arc(0, 0, R[7], 0, 2 * pi)
ctx.fill()

# Draw the slices, in pairs 
for i in range(10):
    # Need to draw the white slice, the double and triple segments for the 
    # black-background slice in red, and the double and triple segments for
    # the white-background slice in green

    # White slice
    ctx.set_source_rgba(1.0, 0.98, 0.81, 1.0)
    ctx.move_to(0, 0)
    ctx.line_to(R[5] * cos(-pi / 20), R[5] * sin(-pi / 20))
    ctx.arc(0, 0, R[5], -pi / 20, pi / 20)
    ctx.line_to(0, 0)
    ctx.fill()

    # Red double segment
    ctx.set_source_rgba(0.91, 0.33, 0.33, 1.0)
    ctx.move_to(R[4] * cos(pi / 20), R[4] * sin(pi / 20))
    ctx.arc(0, 0, R[4], pi / 20, 3 * pi / 20)
    ctx.line_to(R[5] * cos(3 * pi / 20), R[5] * sin(3 * pi / 20))
    ctx.arc_negative(0, 0, R[5], 3 * pi / 20, pi / 20)
    ctx.line_to(R[4] * cos(pi / 20), R[4] * sin(pi / 20))
    ctx.fill()

    # Red triple segment
    ctx.move_to(R[2] * cos(pi / 20), R[2] * sin(pi / 20))
    ctx.arc(0, 0, R[2], pi / 20, 3 * pi / 20)
    ctx.line_to(R[3] * cos(3 * pi / 20), R[3] * sin(3 * pi / 20))
    ctx.arc_negative(0, 0, R[3], 3 * pi / 20, pi / 20)
    ctx.line_to(R[2] * cos(pi / 20), R[2] * sin(pi / 20))
    ctx.fill()

    # Green double segment
    ctx.set_source_rgba(0, 0.67, 0.34, 1.0)
    ctx.move_to(R[4] * cos(-pi / 20), R[4] * sin(-pi / 20))
    ctx.arc(0, 0, R[4], -pi / 20, pi / 20)
    ctx.line_to(R[5] * cos(pi / 20), R[5] * sin(pi / 20))
    ctx.arc_negative(0, 0, R[5], pi / 20, -pi / 20)
    ctx.line_to(R[4] * cos(-pi / 20), R[4] * sin(-pi / 20))
    ctx.fill()

    # Green triple segment
    ctx.move_to(R[2] * cos(-pi / 20), R[2] * sin(-pi / 20))
    ctx.arc(0, 0, R[2], -pi / 20, pi / 20)
    ctx.line_to(R[3] * cos(pi / 20), R[3] * sin(pi / 20))
    ctx.arc_negative(0, 0, R[3], pi / 20, -pi / 20)
    ctx.line_to(R[2] * cos(-pi / 20), R[2] * sin(-pi / 20))
    ctx.fill()
    
    ctx.rotate(pi / 5)


# Draw the bullseyes
ctx.arc(0, 0, R[1], 0, 2 * pi)
ctx.fill()

ctx.set_source_rgba(0.91, 0.33, 0.33)
ctx.arc(0, 0, R[0], 0, 2 * pi)
ctx.fill()

# Place the slice labels
ctx.set_source_rgba(1.0, 0.98, 0.81, 1.0)
ctx.select_font_face("Open Sans")
ctx.set_font_size(60 / SIZE) # need to divide by SIZE since the axes are transformed

for i in range(20):
    _, _, width, height, _, _ = ctx.text_extents(str(slices[i])) 
    ctx.move_to(R[6] * cos(i * pi / 10) - width / 2, R[6] * -sin(i * pi / 10) + height / 2)
    ctx.show_text(str(slices[i]))

surface.write_to_png("dartboard.png")
