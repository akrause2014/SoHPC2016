def point_in_mandelbrot_set(x0, y0, cre, cim, max_iter):
    #
    # Note that cre and cim are not needed for Mandelbrot set.
    # They are only needed for Julia set, but both functions must have same
    # prototype.
    #

    x = x0
    y = y0
    for i in range(max_iter):
        x2 = x * x
        y2 = y * y
        if x2 + y2 > 4.0:
            return i
        else:
            y = y0 + (2.0 * x * y)
            x = x0 + x2 - y2
    return max_iter


def point_in_julia_set(x0, y0, cre, cim, max_iter):
    x = x0
    y = y0
    for i in range(max_iter):
        if x * x + y * y > 4.0:
            return i
        else:
            tmp = y * y
            y = 2 * x * y + cim
            x = x * x - tmp + cre
    return max_iter


def worker_loop(in_set_fn,
                xmin, xmax, ymin, ymax, cre, cim,
                grid_size_x, grid_size_y, max_iter):
    while True:
        # receive task description
        xstart, xstop, ystart, ystop = receive_task()
        data = compute_pixels(in_set_fn,
                              xstart, xstop, ystart, ystop,
                              xmin, xmax, ymin, ymax, cre, cim,
                              grid_size_x, grid_size_y, max_iter)
        send_image_pixels(data, xstart, xstop, ystart, ystop)


def receive_task():
    return None


def compute_pixels(in_set_fn,
                   xstart, xstop, ystart, ystop,
                   xmin, xmax, ymin, ymax, cre, cim,
                   grid_size_x, grid_size_y, max_iter):
    None


def send_image_pixels(data, xstart, xstop, ystart, ystop):
    None
