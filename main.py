import matplotlib.pyplot as plt
from random import uniform
from math import pi, cos, sin

GRAVITATION = -9.8 # 중력 가속도 상수 (종단속도 때문에 아마 안 쓸 듯)
TERMINAL_VELOCITY = -9.0 # 종단 속도
TIME_INTERVAL = 0.1 # 한 step당 시간
WIND_SPEED = 1 # 풍속
WIND_DIRECTION = 5/4 * pi # 풍향

# 빗방울 객체
class Raindrop:

    # 초기 위치를 매개변수로 입력받음
    def __init__(self, init_x, init_y):
        self.x = init_x # x 위치
        self.y = init_y # y 위치
        
        self.last_time = 0 # 지난 시간

    # TIME_INTERVAL 동안의 운동 진행
    def step(self):
        self.x = WIND_SPEED * cos(WIND_DIRECTION) * self.last_time
        # self.y = WIND_SPEED * sin(WIND_DIRECTION) * self.last_time + 0.5 * GRAVITATION * self.last_time ** 2
        self.y = WIND_SPEED * sin(WIND_DIRECTION) * self.last_time + TERMINAL_VELOCITY * self.last_time

        self.last_time += TIME_INTERVAL

# 사람 객체
class Human:

    # 이동 속도와 가로, 세로, 초기 위치를 매개변수로 입력받음
    def __init__(self, speed, height, width, init_x, init_y):

        self.speed = speed
        self.height = height
        self.width = width

        self.x = init_x
        self.y = init_y

        self.last_time = 0
    
    # TIME_INTERVAL 동안의 운동 진행
    def step(self):
        self.x = self.speed * self.last_time + WIND_SPEED * self.last_time
        self.last_time += TIME_INTERVAL

# 환경 객체
class Environment:

    # 1초당 강수량과 사람 객체, 가로, 세로, 모드를 매개변수로 입력받음
    def __init__(self, rainfall, human, height, width, mode="none"):
        self.rainfall = rainfall # 1초당 강수량
        self.raindrops = [] # 환경에 내리고 있는 빗방울 객체 리스트
        self.human = human
        self.height = height
        self.width = width
        self.mode = mode # mode: "none", "simulation" 이 있음.

        # 맞은 빗방울이 어디에 맞았는지 저장하는 변수
        self.collision_rain_count = {
            "top": 0,
            "front": 0,
            "back": 0
        }

    # TIME_INTERVAL 동안의 운동 진행
    def step(self):
        # TIME_INTERVAL 동안의 새로운 빗방울 생성
        # 빗방울의 x 초기 위치는 균등분포로 결정, y 초기 위치는 모두 동일
        self.raindrops += [Raindrop(init_x=uniform(0, self.width), init_y=self.height) 
                           for _ in range(int(self.rainfall * TIME_INTERVAL))]
        
        # 빗방울 리스트를 맨 뒤에서부터 긁는다. (중간에 빗방울을 지우는 과정이 있는데, 이때 반복문에 영향을 끼치지 않기 위함)
        i = len(self.raindrops) - 1

        # 모든 빗방울 긁음.
        while i > -1:
            # TIME_INTERVAL 동안의 i번째 빗방울 운동 진행
            self.raindrops[i].step()
            
            # 만약 빗방울이 environment를 벗어났다면, 제거
            if self.raindrops[i].y < 0 or self.raindrops[i].x < 0 or self.raindrops[i].x > self.width:
                del self.raindrops[i]

            # 만약 빗방울이 사람에 부딪혔다면, 제거
            elif self.human.y + self.human.height > self.raindrops[i].y > self.human.y and self.human.x < self.raindrops[i].x < self.human.x + self.human.width:
                ##### 이쪽에 빗방울이 사람의 어느쪽에 부딪혔는지와 self.collision_rain_count를 갱신해주는 코드를 작성해야함.
                del self.raindrops[i]
            
            i -= 1
        
        # TIME_INTERVAL 동안의 사람 운동 진행
        self.human.step()

    # 모두 실행
    def run(self):
        
        # 사람이 environment를 벗어나기 전까지 진행
        while self.human.x + self.human.width <= self.width:
            self.step()