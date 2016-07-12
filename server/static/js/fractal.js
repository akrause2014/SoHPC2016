fractal = {
    init: function(compute_function, ctx, worker_id,
                   xstart, xstop, ystart, ystop,
                   xmin, xmax, ymin, ymax, cre, cim,
                   grid_size_x, grid_size_y, max_iter) {
      this.worker_id = worker_id;
      this.ctx = ctx;
      this.compute_function = compute_function;
      this.xstart = xstart;
      this.xstop = xstop;
      this.ystart = ystart;
      this.ystop = ystop;
      this.xmin = xmin;
      this.xmax = xmax;
      this.ymin = ymin;
      this.ymax = ymax;
      this.cre = cre;
      this.cim = cim;
      this.grid_size_x = grid_size_x;
      this.grid_size_y = grid_size_y;
      this.max_iter = max_iter;
      this.ncolours = Math.min(255, max_iter);
      this.xsize = xstop - xstart;
      this.ysize = ystop - ystart;
      this.currentY = 0;
      this.currentX = 0;

      console.log("Initialise image (" + this.xsize + ", " + this.ysize + ")");
      this.imagesection = initialise_image(this.xsize, this.ysize);

      drawPoints = function() {
        fractal.repeater = requestAnimationFrame(drawPoints);
        fractal.nextPoint();
      }
      drawPoints();
    },
    nextPoint: function() {
      // calculate one row at a time
      var factorX = ((this.xmax - this.xmin) / this.grid_size_x);
      var factorY = ((this.ymax - this.ymin) / this.grid_size_y);
      for (var i=0; i<this.xsize; i++) {
        x0 = this.xmin + (this.xstart+this.currentX) * factorX;
        y0 = this.ymin + (this.ystart+this.currentY) * factorY;
        var value = this.compute_function(x0, y0, this.cre, this.cim, this.max_iter);
        this.imagesection[this.currentX][this.currentY] = value
        rgb = gray_to_rgb(value, this.ncolours);
        // console.log(rgb);
        this.ctx.fillStyle = rgbToHex(rgb[R], rgb[G], rgb[B]);
        this.ctx.fillRect(this.currentX, this.currentY, 1, 1);

        // console.log('draw point (' + this.currentX + ', ' + this.currentY + ') = ' + rgb);
        // continue iteration
        if (this.currentX < this.xsize-1) {
          this.currentX = this.currentX+1;
        }
        else {
          this.currentX = 0;
          if (this.currentY < this.ysize-1) {
            this.currentY = this.currentY+1;
          }
          else {
            // stop animation
            cancelAnimationFrame(this.repeater);
            console.log('Done!')
            computation_complete();
            $.ajax({url: "/worker/complete/" + this.worker_id,
                    type: 'POST',
                    data: JSON.stringify(this.imagesection)})
              .done(function(){
                transfer_complete();
              });

          }
        }
      }
    },
    cancelComputation: function() {
      cancelAnimationFrame(this.repeater);
    }
}

function compute_task(worker_id, task)
{
  console.log(task);

  var xstart = task['xstart'];
  var xstop = task['xstop'];
  var ystart = task['ystart'];
  var ystop = task['ystop'];
  var xmin = task['xmin'];
  var xmax = task['xmax'];
  var ymin = task['ymin'];
  var ymax = task['ymax'];
  var cim = task['cim'];
  var cre = task['cre'];
  var grid_size_x = task['grid_size_x'];
  var grid_size_y = task['grid_size_y'];
  var max_iter = task['max_iter'];
  var compute_function;
  if (task['compute_function'] == 'mandelbrot') {
    compute_function = point_in_mandelbrot_set;
  }
  else if (task['compute_function'] == 'julia') {
    compute_function = point_in_julia_set;
  }
  try {
      fractal.init(compute_function, ctx, worker_id,
          xstart, xstop, ystart, ystop,
          xmin, xmax, ymin, ymax, cre, cim,
          grid_size_x, grid_size_y, max_iter);
  }catch(err){
    console.log(err);
  }
}

function rgbToHex(r, g, b) {
    return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
}
