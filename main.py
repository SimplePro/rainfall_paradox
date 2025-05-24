import matplotlib.pyplot as plt
from random import uniform
from math import pi, cos, sin
from vpython import *

# 빗방울 객체
class Raindrop:

    # 초기 위치를 매개변수로 입력받음
    def __init__(self, pos, mode):
        
        self.init_pos = pos
        self.pos = pos

        self.mode = mode

        if self.mode == "simulation":
            self.sphere = sphere(pos=self.pos, radius=0.1, color=color.cyan, opacity=0.2)
        
        self.last_time = 0 # 지난 시간

    # TIME_INTERVAL 동안의 운동 진행
    def step(self):
        # self.x = WIND_SPEED * cos(WIND_DIRECTION) * self.last_time
        self.pos = self.init_pos + (TERMINAL_VELOCITY + WIND_SPEED) * self.last_time
        # self.x = self.init_x + WIND_SPEED * cos(WIND_DIRECTION) * self.last_time
        # self.y = WIND_SPEED * sin(WIND_DIRECTION) * self.last_time + 0.5 * GRAVITATION * self.last_time ** 2
        # self.y = WIND_SPEED * sin(WIND_DIRECTION) * self.last_time + TERMINAL_VELOCITY * self.last_time
        # self.y = self.init_y + WIND_SPEED * cos(WIND_DIRECTION) * self.last_time

        if self.mode == "simulation":
            self.sphere.pos = self.pos

        self.last_time += TIME_INTERVAL

        # print(self.x, self.y)

    # 바로 전 상태를 반환
    def get_last_state(self):
        # return self.x - WIND_SPEED * cos(WIND_DIRECTION) * TIME_INTERVAL, self.y - (WIND_SPEED * sin(WIND_DIRECTION) * TIME_INTERVAL + TERMINAL_VELOCITY * TIME_INTERVAL)
        return self.pos - (TERMINAL_VELOCITY + WIND_SPEED) * TIME_INTERVAL


# 사람 객체
class Human:

    # 이동 속도와 가로, 세로, 초기 위치를 매개변수로 입력받음
    def __init__(self, speed, size, init_pos, mode):

        self.speed = speed
        self.size = size
        self.pos = init_pos

        self.mode = mode

        if self.mode == "simulation":
            self.box = box(pos=self.pos, size=self.size, color=color.orange)

        self.v = self.speed + WIND_SPEED
        self.v.y = 0

        self.last_time = 0
    
    # TIME_INTERVAL 동안의 운동 진행
    def step(self):
        # self.x = self.speed * self.last_time + WIND_SPEED * cos(WIND_DIRECTION) * self.last_time
        # self.pos += (self.speed + WIND_SPEED) * TIME_INTERVAL
        self.pos += self.v * TIME_INTERVAL

        if self.mode == "simulation":
            self.box.pos = self.pos

        self.last_time += TIME_INTERVAL

# 환경 객체
class Environment:

    # 1초당 강수량과 사람 객체, 가로, 세로, 모드를 매개변수로 입력받음
    def __init__(self, rainfall, human, height, depth, width, mode="none"):
        self.rainfall = rainfall # 1초당 강수량
        self.raindrops = [] # 환경에 내리고 있는 빗방울 객체 리스트
        self.human = human
        self.height = height
        self.depth = depth
        self.width = width
        self.mode = mode # mode: "none", "simulation" 이 있음.

        # 맞은 빗방울이 어디에 맞았는지 저장하는 변수
        self.collision_rain_count = {
            "top": 0,
            "side": 0
        }

        if self.mode == "simulation":
            self.box = box(pos=vector(0, -height/3, 0), size=vector(width, 0.5, depth))

        self.last_time = 0

    # TIME_INTERVAL 동안의 운동 진행
    def step(self):
        # TIME_INTERVAL 동안의 새로운 빗방울 생성
        # 빗방울의 x 초기 위치는 균등분포로 결정, y 초기 위치는 모두 동일
        self.raindrops += [Raindrop(pos=vector(uniform(-self.width/2, self.width/2), self.height, uniform(-self.depth/2, self.depth/2)), mode=self.mode) 
                           for _ in range(int(self.rainfall * TIME_INTERVAL))]

        # print(self.raindrops)
        
        # 빗방울 리스트를 맨 뒤에서부터 긁는다. (중간에 빗방울을 지우는 과정이 있는데, 이때 반복문에 영향을 끼치지 않기 위함)
        i = len(self.raindrops) - 1

        # 모든 빗방울 긁음.
        while i > -1:
            # TIME_INTERVAL 동안의 i번째 빗방울 운동 진행
            self.raindrops[i].step()
            
            # 만약 빗방울이 environment를 벗어났다면, 제거
            if self.raindrops[i].pos.y < -self.height/3 \
                or self.raindrops[i].pos.x < -self.width/2 \
                    or self.raindrops[i].pos.x > self.width/2:
                
                if self.mode == "simulation":
                    self.raindrops[i].sphere.visible = False

                del self.raindrops[i]

            # 만약 빗방울이 사람에 부딪혔다면, 제거
            elif self.human.pos.y + self.human.size.y/2 > self.raindrops[i].pos.y > self.human.pos.y - self.human.size.y/2 \
                and self.human.pos.x - self.human.size.x/2 < self.raindrops[i].pos.x < self.human.pos.x + self.human.size.x/2:
            # elif self.human.y + self.human.height > self.raindrops[i].y > self.human.y and self.human.x < self.raindrops[i].x < self.human.x + self.human.width:
                last_state = self.raindrops[i].get_last_state()
                top_ = last_state.y >= self.human.pos.y
                
                if top_:
                    self.collision_rain_count["top"] += 1
                
                else:
                    self.collision_rain_count["side"] += 1
                
                if self.mode == "simulation":
                    self.raindrops[i].sphere.visible = False

                del self.raindrops[i]
            
            i -= 1
        
        # TIME_INTERVAL 동안의 사람 운동 진행
        self.human.step()
        self.last_time += TIME_INTERVAL

    # 모두 실행
    def run(self):
        
        # 사람이 environment를 벗어나기 전까지 진행
        while self.human.pos.x + self.human.size.x/2 <= self.width/2 and self.human.pos.x - self.human.size.x/2 >= -self.width/2:
            rate(60)
            print(self.human.pos)
            self.step()


if __name__ == '__main__':
    # human = Human(speed=2, height=1.7, width=0.3, init_x=0, init_y=0)
    # env = Environment(rainfall=100, human=human, height=30, width=50, mode="none")

    GRAVITATION = vector(0, -9.8, 0) # 중력 가속도 상수 (종단속도 때문에 아마 안 쓸 듯)
    TERMINAL_VELOCITY = vector(0, -9.0, 0) # 종단 속도
    TIME_INTERVAL = 0.02 # 한 step당 시간 (s)
    WIND_SPEED = vector(0, -1, 0) # 바람
    rainfall = 100

    mode = "simulation"
    env_size = vector(20, 20, 20)
    human_speed = vector(1.0, 0, 0)
    human_size = vector(0.3, 1.7, 0.6)

    if mode == "simulation":
        canvas(width=1920, height=1080, background=color.white)

    human = Human(speed=human_speed, size=human_size, init_pos=vector(-env_size.x/2+human_size.x/2, -env_size.y/3 + human_size.y/2 + 0.25, 0), mode=mode)
    env = Environment(rainfall=rainfall, human=human, height=env_size.y, depth=env_size.z, width=env_size.x, mode=mode)
    env.run()

    print(env.collision_rain_count)