import numpy as np
from PIL import Image, ImageDraw, ImageFont

SIZE = 100
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
COLORS = (
    (156, 56, 255), (0, 153, 0), (148, 253, 255), (30, 7, 233),
    (255, 218, 51), (244, 102, 162), (214, 24, 0), (148, 255, 82)
)

font = ImageFont.truetype("C:/Windows/Fonts/Arial/arialbd.ttf", size=36)


def get_corners(pts):
    #https://math.stackexchange.com/questions/3800582/getting-corner-coordinates-of-polygon-on-a-grid
    # Algorithm: 
    #   - determine all corners for each component square
    #   - count how often each occurs:                  (out)|(in)         (in) | (out)
    #       outer corners will have a count of 1:            +--- => 1      ----+-----  => 3
    #       'inner' corners will have a count of 3:        (out)           (in) | (in)
    #       interior non-corners will have a count of 4
    #       exterior edges (non-corners) will have a count of 2
    #   - therefore: even => non-corner, odd => corner

    # adjustment: points are passed in (row, col) (from numpy.argwhere), 
    # but that corresponds to  (y, x), and everything with PIL is (x, y),
    # so we need to switch.
    pts[:, [1, 0]] = pts[:, [0, 1]]

    corner_counts = dict()
    for point in pts:
        for col_offset in (0, SIZE):
            for row_offset in (0, SIZE):

                corner = (point[0] * SIZE + col_offset + 1, point[1] * SIZE + row_offset + 1)
                if corner in corner_counts:
                    corner_counts[corner] += 1
                else:
                    corner_counts[corner] = 1

    # Now, put them in order
    odd_corners = [corner for corner in corner_counts.keys() if corner_counts[corner] % 2]
    ordered = [odd_corners.pop(0)]

    while odd_corners: # until unordered corners list has no items
        # find the next corner (the one matching either the x or y coordinate of the previous)
        for corner in odd_corners:
            # make sure we're not crossing back over the shape
            # check if all boxes to the left are filled and none to the right are (or vice versa)
            
            pts_tolist = pts.tolist() # (since checking if a row is part of an array is weird)

            if corner[0] == ordered[-1][0]: # edge aligned vertically
                grid_c = (corner[0] -1) // SIZE
                r_min = (min(corner[1], ordered[-1][1]) - 1) // SIZE
                r_max = (max(corner[1], ordered[-1][1]) - 1) // SIZE
                
                # lists of points to the left and right of the potential edge
                left = [[grid_c - 1, grid_r] for grid_r in range(r_min, r_max)]
                right = [[grid_c, grid_r] for grid_r in range(r_min, r_max)]

                # 'continue' if not (either all of one are part of the shape and none of the other are, or vice versa)
                if not (
                    all(pt in pts_tolist for pt in left) and not any(pt in pts_tolist for pt in right) 
                    or not any(pt in pts_tolist for pt in left) and all(pt in pts_tolist for pt in right)
                ):
                    continue


            elif corner[1] == ordered[-1][1]: # edge aligned horizontally
                grid_r = (corner[1] - 1) // SIZE
                c_min = (min(corner[0], ordered[-1][0]) - 1) // SIZE
                c_max = (max(corner[0], ordered[-1][0]) - 1) // SIZE

                # lists of points above and below the potential edge
                top = [[grid_c, grid_r - 1] for grid_c in range(c_min, c_max)]
                bottom = [[grid_c, grid_r] for grid_c in range(c_min, c_max)]

                # continue if not (either all of one are part of the shape and none of the other are, or vice versa)
                if not (
                    all(pt in pts_tolist for pt in top) and not any(pt in pts_tolist for pt in bottom) 
                    or not any(pt in pts_tolist for pt in top) and all(pt in pts_tolist for pt in bottom)
                ):
                    continue

                
            else: # there is no edge (the corners are not aligned)
                continue
            
            # If we haven't 'continue'd yet, the edge is valid
            ordered.append(corner)
            odd_corners.remove(corner)
            break

        else:
            raise RuntimeError("Issue when determining shape boundaries")

    return ordered


def make_img(grid, month, day, save=True):
    # First, the grayscale image (just borders, text, and grayed regions)
    img = Image.new("RGB", (7 * SIZE + 2, 7 * SIZE + 2), (255, 255, 255))

    # Get a drawing context
    draw = ImageDraw.Draw(img)

    # Draw grayed out regions
    draw.rectangle(
        [(3 * SIZE + 1, 6 * SIZE + 1), (7 * SIZE + 1, 7 * SIZE + 1)],
        outline=(0, 0, 0), fill=(204, 204, 204), width=1
    )
    draw.rectangle(
        [(6 * SIZE + 1, 1), (7 * SIZE + 1, 2 * SIZE + 1)],
        outline=(0, 0, 0), fill=(204, 204, 204), width=1
    )

    # Draw month and day, plus text
    mo_x = SIZE * ((month - 1) % 6) + 1
    mo_y = SIZE * ((month - 1) // 6) + 1
    day_x = SIZE * ((day - 1) % 7) + 1
    day_y = SIZE * ((day - 1) // 7 + 2) + 1

    draw.rectangle([(mo_x, mo_y), (mo_x + SIZE, mo_y + SIZE)], outline=(0, 0, 0), fill=None, width=1)
    draw.rectangle([(day_x, day_y), (day_x + SIZE, day_y + SIZE)], outline=(0, 0, 0), fill=None, width=1)

    draw.text((mo_x + SIZE // 2, mo_y + SIZE // 2), MONTHS[month - 1], fill=(0, 0, 0), font=font, align="center", anchor="mm")
    draw.text((day_x + SIZE // 2, day_y + SIZE // 2), str(day), fill=(0, 0, 0), font=font, align="center", anchor="mm")

    # Draw the outlines of the shapes
    for shape_num in range(1, 9):
        pts = np.argwhere(grid == shape_num)
        corners = get_corners(pts)
        draw.line(corners, fill=(0, 0, 0), width=1)

    # Draw outer border
    draw.rectangle([(1, 1), (7 * SIZE + 1, 7 * SIZE + 1)], outline=(0, 0, 0), fill=None, width=2)

    if save:
        img.save(f"{month}-{day}_BW.png")
    else:
        img.show()


    # Now the color image
    img = Image.new("RGB", (7 * SIZE + 2, 7 * SIZE + 2), (255, 255, 255))

    # Get a drawing context
    draw = ImageDraw.Draw(img)

    # Draw grayed out regions
    draw.rectangle(
        [(3 * SIZE + 1, 6 * SIZE + 1), (7 * SIZE + 1, 7 * SIZE + 1)],
        outline=None, fill=(204, 204, 204), width=1
    )
    draw.rectangle(
        [(6 * SIZE + 1, 1), (7 * SIZE + 1, 2 * SIZE + 1)],
        outline=None, fill=(204, 204, 204), width=1
    )

    # Draw month and day, plus text
    mo_x = SIZE * ((month - 1) % 6) + 1
    mo_y = SIZE * ((month - 1) // 6) + 1
    day_x = SIZE * ((day - 1) % 7) + 1
    day_y = SIZE * ((day - 1) // 7 + 2) + 1

    draw.text((mo_x + SIZE // 2, mo_y + SIZE // 2), MONTHS[month - 1], fill=(0, 0, 0), font=font, align="center", anchor="mm")
    draw.text((day_x + SIZE // 2, day_y + SIZE // 2), str(day), fill=(0, 0, 0), font=font, align="center", anchor="mm")

    # Draw the outlines of the shapes
    for shape_num in range(1, 9):
        pts = np.argwhere(grid == shape_num)
        corners = get_corners(pts)
        draw.polygon(corners, outline=None, fill=COLORS[shape_num - 1])

    # Draw the grid lines
    for i in range(8):
        draw.line([(1 + i * SIZE, 1), (1 + i * SIZE, 7 * SIZE + 1)], fill=(0, 0, 0), width=1)
        draw.line([(1, 1 + i * SIZE), (7 * SIZE + 1, 1 + i * SIZE)], fill=(0, 0, 0), width=1)

    if save:
        img.save(f"{month}-{day}_CO.png")
    else:
        img.show()



if __name__ == "__main__":
    grid = np.array([
        [1, 2, 2, 2, -1, 5, -1],
        [1, 1, 1, 2, 5, 5, -1],
        [8, 8, 1, 2, 5, 4, 4],
        [8, 7, 7, 7, 5, 4, 4],
        [8, 7, 6, 7, 3, 4, 4],
        [8, 6, 6, 3, 3, 3, 3],
        [-1, 6, 6, -1, -1, -1, -1]
    ])
    make_img(grid, 5, 29, save=False)
