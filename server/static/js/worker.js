R = 0;
G = 1;
B = 2;

function heart_to_master(worker_id) {
  $.ajax({url: "/heartbeat/" + worker_id, type: 'GET'})
    .done(function(data) {
      console.log( "sent heartbeat" );
      console.log(data);
      json = json.parseJSON(data);
    });
}

function point_in_mandelbrot_set(x0, y0, cre, cim, max_iter)
{
  /*
   * Note that cre and cim are not needed for Mandelbrot set.
   * They are only needed for Julia set, but both functions must have same
   * prototype.
   */
    var x = x0;
    var y = y0;
    for (var i = 0; i < max_iter; i++ ) {
        var x2 = x * x;
        var y2 = y * y;
        /* z = (z*z) + c */
        if ( x2 + y2 > 4.0 )
        {
            return i;
        } else
        {
            y = y0 + (2.0 * x * y);
            x = x0 + x2 - y2;
        }
    }
    return max_iter;
}

function point_in_julia_set(x0, y0, cre, cim, max_iter)
{
    var x = x0;
    var y = y0;
    for (var i = 0; i < max_iter; i++ ) {
        if ( x * x + y * y > 4.0 ) {
            return i;
        } else
        {
            var tmp = y * y;
            y = 2 * x * y + cim;
            x = x * x - tmp + cre;
        }
    }
    return max_iter;
}

function compute_pixels(compute_function, ctx,
                        xstart, xstop, ystart, ystop,
                        xmin, xmax, ymin, ymax, cre, cim,
                        grid_size_x, grid_size_y, max_iter)
{
    var ncolours = Math.min(255, max_iter);
    var xsize = xstop - xstart + 1;
    var ysize = ystop - ystart + 1;

    var imagesection = initialise_image(xsize, ysize);
    // var imageData = getImageData();

    for ( i = ysize-1; i >= 0; i-- ) {
      for ( j = 0; j < xsize; j++ ) {
            /* calculate coordinates x0,y0 of current pixel */
            x0 = xmin + (xstart+j) * ((xmax - xmin) / grid_size_x);
            y0 = ymin + (ystart+i) * ((ymax - ymin) / grid_size_y);
            var value = compute_function(x0, y0, cre, cim, max_iter);
            imagesection[i][j] = value
            rgb = gray_to_rgb(value, ncolours);
            // console.log(rgb);
            ctx.fillStyle = rgbToHex(rgb[R], rgb[G], rgb[B]);
            ctx.fillRect(j, i, 1, 1);
            // setPixel(imageData, j, i, rgb[R], rgb[G], rgb[B], 1.0);
        }
    }
    // updateImage(imageData);
    console.log('Finished computing');
    return imagesection;
}

function initialise_image(xsize, ysize)
{
  var imagesection = [];
  for(var i=0; i<ysize; i++) {
      imagesection[i] = [];
      for(var j=0; j<ysize; j++) {
          imagesection[i][j] = -1;
      }
  }
  return imagesection;
}

function gray_to_rgb(gray, ncolours)
{
    var s = 1;
    var v = 255;
    var f, p, q, t;
    var rgb = [0, 0, 0];

    var h = (360.0 * gray) / (60 * ncolours);
    if ( h < 0 ) {
        /* Invalid colour, set to black */
        rgb[R] = 0;
        rgb[G] = 0;
        rgb[B] = 0;
        return;
    }
    f = h - Math.floor(h);
    // console.log(h)

    p = Math.floor(v * (1 - s));
    q = Math.floor(v * (1 - s * f));
    t = Math.floor(v * (1 - s * (1 - f)));
    switch ( Math.floor(h) ) {
    case 0:
        rgb[R] = v;
        rgb[G] = t;
        rgb[B] = p;
        break;
    case 1:
        rgb[R] = q;
        rgb[G] = v;
        rgb[B] = p;
        break;
    case 2:
        rgb[R] = p;
        rgb[G] = v;
        rgb[B] = t;
        break;
    case 3:
        rgb[R] = p;
        rgb[G] = q;
        rgb[B] = v;
        break;
    case 4:
        rgb[R] = t;
        rgb[G] = p;
        rgb[B] = v;
        break;
    case 5:
        rgb[R] = v;
        rgb[G] = p;
        rgb[B] = q;
        break;
    default:
        rgb[R] = 0;
        rgb[G] = 0;
        rgb[B] = 0;
    }
    return rgb;
}

function rgbToHex(r, g, b) {
    return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
}
