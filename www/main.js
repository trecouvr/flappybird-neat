var WIDTH         = 576;
var HEIGHT        = 768;
//var BIRD_WIDTH    = 72;
//var BIRD_HEIGHT   = 52;
var BIRD_WIDTH    = 62;
var BIRD_X        = WIDTH / 3;
var FLOOR_WIDTH   = 672;
var FLOOR_HEIGHT  = 224;
var FLOOR_OFFSET  = 96;
var FLOOR_SPEED   = 5;
var PIPE_WIDTH    = 104;
var PIPE_HEIGHT   = 640;
var PIPE_APERTURE = 200;
var canvas = document.getElementById('canvas');
var panel = document.getElementById('panel');
var ctx = canvas.getContext('2d');


function createImage(src) {
  var img = new Image();
  img.src = src;
  return img;
}

var imgBackground = createImage('images/bg.png');
var imgBird = createImage('images/bird.png');
var imgGround = createImage('images/ground.png');
var imgTubeTop = createImage('images/tube1.png');
var imgTubeBottom = createImage('images/tube2.png');


function Animation(image, width, height, ticksPerFrame, numberOfFrames) {

  this.image = image;
  this.width = width;
  this.height = height;

  this.frameIndex = 0;
  this.tickCount = 0;
  this.ticksPerFrame = ticksPerFrame;
  this.numberOfFrames = numberOfFrames;

  this.render = function(ctx, x, y, dx, dy) {
    // Draw the animation
    ctx.drawImage(
      this.image,
      this.frameIndex * this.width,
      0,
      this.width,
      this.height,
      x,
      y,
      dx,
      dy);
  };

  this.update = function() {
    this.tickCount += 1;
    if (this.tickCount > this.ticksPerFrame) {
      this.tickCount = 0;
        // Go to the next frame
        this.frameIndex += 1;
        this.frameIndex %= this.numberOfFrames;
    }
  };

}

var birdAnimation = new Animation(imgBird, 36, 26, 5, 3);



function update(ticks, score, birds, pipes) {
  // flush canvas
  //ctx.fillStyle = "white";
  //ctx.fillRect(0, 0, WIDTH, HEIGHT);
  //ctx.strokeStyle = "black";
  //ctx.strokeRect(0, 0, WIDTH, HEIGHT);
  ctx.drawImage(imgBackground, 0, 0, WIDTH, HEIGHT);

  for (var i in birds) {
    var y = birds[i];
    //ctx.beginPath();
    //ctx.arc(BIRD_X, HEIGHT - y, BIRD_WIDTH / 2, 0, 2 * Math.PI, false);
    //ctx.fillStyle = '#ff0000';
    //ctx.fill();
    birdAnimation.render(ctx, BIRD_X - BIRD_WIDTH / 2, HEIGHT - y - BIRD_WIDTH / 2, BIRD_WIDTH, BIRD_WIDTH);
  }
  birdAnimation.update()

  for (var i in pipes) {
    var pipe = pipes[i];
    //ctx.fillStyle = '#00ff00';
    //ctx.fillRect(pipe.x - PIPE_WIDTH / 2, HEIGHT - pipe.height, PIPE_WIDTH, pipe.height);
    //ctx.fillRect(pipe.x - PIPE_WIDTH / 2, 0, PIPE_WIDTH, HEIGHT - pipe.height - PIPE_APERTURE);
    ctx.drawImage(imgTubeBottom, pipe.x - PIPE_WIDTH / 2, HEIGHT - pipe.height, PIPE_WIDTH, pipe.height);
    ctx.drawImage(imgTubeTop, pipe.x - PIPE_WIDTH / 2, 0, PIPE_WIDTH, HEIGHT - pipe.height - PIPE_APERTURE);
  }
  panel.innerHTML = 'Ticks: ' + ticks;
  panel.innerHTML += '<br/>Score: ' + score;
  panel.innerHTML += '<br/>Birds: ' + birds.length;
}

var socket = new WebSocket('ws://localhost:4000/');
//socket.binaryType = "arraybuffer";
socket.onopen = function (event) {
  console.log("Socket open");
};
socket.onclose = function(event) {
  console.log('socket close');
}
socket.onerror = function(event) {
  console.log('socket error');
  socket.close();
}
socket.onmessage = function(event) {
  var data = JSON.parse(event.data);
  update(data.ticks, data.score, data.birds, data.pipes);
};

function socket_send(data) {
  if (socket.readyState === socket.OPEN) {
    socket.send(data);
  }
}
