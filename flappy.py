import random


class Bird:

    def __init__(self, y):
        self.y = y
        self.vy = 0
        self.alive = True
        self.ticks = 0
        self.flaps = 0
        self.angle = 0
        self.input_flap = False

    def tick(self):
        self.y += self.vy
        self.vy -= 0.98
        self.angle = 3.0 * self.vy
        self.angle = max(-90.0, min(90.0, self.angle))
        self.ticks += 1

    def flap(self):
        self.vy = 10
        self.flaps += 1

    def __repr__(self):
        return 'Bird(y=%s, vy=%s, ticks=%s, alive=%s' % (
            self.y, self.vy, self.ticks, self.alive)


class Pipe:
    def __init__(self, x, height, vx):
        self.x = x
        self.vx = vx
        self.height = height
        self.passed = False

    def tick(self):
        self.x -= self.vx


class GameEngine:
    WIDTH         = 576
    HEIGHT        = 768
    #BIRD_WIDTH    = 72
    #BIRD_HEIGHT   = 52
    BIRD_WIDTH    = 62
    BIRD_X        = WIDTH / 3
    FLOOR_WIDTH   = 672
    FLOOR_HEIGHT  = 224
    FLOOR_OFFSET  = 96
    FLOOR_SPEED   = 5
    PIPE_WIDTH    = 104
    PIPE_HEIGHT   = 640
    PIPE_APERTURE = 200

    def __init__(self, n_birds):
        self.width = self.WIDTH
        self.height = self.HEIGHT
        self.pipe_frequency = 75
        self.ticks = 0
        self.ticks_pipes = 0
        self.score = 0
        self.birds = [Bird(self.height / 2) for _ in range(n_birds)]
        self.pipes = []

    def is_end_game(self):
        return all(not bird.alive for bird in self.birds)

    def do_tick(self):
        self.ticks += 1
        self.ticks_pipes += 1

        if self.ticks_pipes == self.pipe_frequency:
            self.spawn_pipe()
            self.ticks_pipes = 0

        for bird in self.birds:
            if bird.alive:
                if bird.input_flap:
                    bird.flap()
                    bird.input_flap = False
                bird.tick()

        for pipe in self.pipes:
            pipe.tick()
            if not pipe.passed and pipe.x + self.PIPE_WIDTH / 2 < self.BIRD_X - self.BIRD_WIDTH / 2:
                self.score += 1
                if self.score % 10 == 0:
                    self.pipe_frequency -= 5
                    self.pipe_frequency = max(25, self.pipe_frequency)
                pipe.passed = True
        self.check_collisions()
        self.clean_pipes()

    def check_collisions(self):
        for bird in self.birds:
            if bird.alive:
                if bird.y < 0 or bird.y >= self.height:
                    #print('dead', bird.y, self.height)
                    bird.alive = False
            for pipe in self.pipes:
                #if 95 <= pipe.x <= 105 and ((bird.y-5) < pipe.hole_y or (bird.y+5) > (pipe.hole_y + pipe.hole_size)):
                if pipe.x - self.PIPE_WIDTH < self.BIRD_X + self.BIRD_WIDTH:
                    if self.intersect_pipe_bird(pipe, bird):
                        #print('dead pipe', bird.y, self.height)
                        bird.alive = False

    def intersect_pipe_bird(self, pipe, bird):
        circle = (self.BIRD_X, bird.y, self.BIRD_WIDTH / 2)
        return self.intersect_vsegment_circle(
            pipe.x - self.PIPE_WIDTH / 2,
            0,
            pipe.height,
            *circle
        ) or \
        self.intersect_vsegment_circle(
            pipe.x + self.PIPE_WIDTH / 2,
            0,
            pipe.height,
            *circle
        ) or \
        self.intersect_hsegment_circle(
            pipe.x - self.PIPE_WIDTH / 2,
            pipe.x + self.PIPE_WIDTH / 2,
            pipe.height,
            *circle
        ) or \
        self.intersect_vsegment_circle(
            pipe.x - self.PIPE_WIDTH / 2,
            pipe.height + self.PIPE_APERTURE,
            self.HEIGHT,
            *circle
        ) or \
        self.intersect_vsegment_circle(
            pipe.x + self.PIPE_WIDTH / 2,
            pipe.height + self.PIPE_APERTURE,
            self.HEIGHT,
            *circle
        ) or \
        self.intersect_hsegment_circle(
            pipe.x - self.PIPE_WIDTH / 2,
            pipe.x + self.PIPE_WIDTH / 2,
            pipe.height + self.PIPE_APERTURE,
            *circle
        )

    def intersect_vsegment_circle(self, x, ay, by, cx, cy, d):
        assert ay <= by
        if abs(x - cx) <= d and ay <= cy <= by:
            return True
        elif self.point_in_circle(x, ay, cx, cy, d):
            return True
        elif self.point_in_circle(x, by, cx, cy, d):
            return True
        else:
            return False

    def intersect_hsegment_circle(self, ax, bx, y, cx, cy, d):
        assert ax <= bx
        if abs(y - cy) <= d and ax <= cx <= bx:
            return True
        elif self.point_in_circle(ax, y, cx, cy, d):
            return True
        elif self.point_in_circle(bx, y, cx, cy, d):
            return True
        else:
            return False

    def point_in_circle(self, x, y, cx, cy, d):
        return (x-cx)**2 + (y-cy)**2 <= d*d

    def spawn_pipe(self):
        height = random.randint(100, self.height - 200 - self.PIPE_APERTURE)
        self.pipes.append(Pipe(self.width + self.PIPE_WIDTH / 2, height, self.FLOOR_SPEED))

    def clean_pipes(self):
        self.pipes = [pipe for pipe in self.pipes if -self.PIPE_WIDTH <= pipe.x <= self.width + self.PIPE_WIDTH]

    def dumpstate(self):
        return {
            'ticks': self.ticks,
            'score': self.score,
            'birds': [bird.y for bird in self.birds if bird.alive],
            'pipes': [{
                'x': pipe.x,
                'height': pipe.height,
            } for pipe in self.pipes],
        }
