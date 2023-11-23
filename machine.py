import random
from itertools import combinations
from shapely.geometry import LineString, Point
from itertools import product, chain, combinations
from shapely.geometry import LineString, Point, Polygon

class MACHINE():
    """
        [ MACHINE ]
        MinMax Algorithm을 통해 수를 선택하는 객체.
        - 모든 Machine Turn마다 변수들이 업데이트 됨

        ** To Do **
        MinMax Algorithm을 이용하여 최적의 수를 찾는 알고리즘 생성
           - class 내에 함수를 추가할 수 있음
           - 최종 결과는 find_best_selection을 통해 Line 형태로 도출
               * Line: [(x1, y1), (x2, y2)] -> MACHINE class에서는 x값이 작은 점이 항상 왼쪽에 위치할 필요는 없음 (System이 organize 함)
    """
    def __init__(self, score=[0, 0], drawn_lines=[], whole_lines=[], whole_points=[], location=[]):
        self.id = "MACHINE"
        self.score = [0, 0] # USER, MACHINE
        self.drawn_lines = [] # Drawn Lines
        self.board_size = 7 # 7 x 7 Matrix
        self.num_dots = 0
        self.whole_points = [] #
        self.location = []
        self.triangles = [] # [(a, b), (c, d), (e, f)]
        self.independent_lines_case =[]
        self.posible_lines = []

    def find_best_selection(self):

        self.posible_lines = []
        self.independent_lines_case = []

        #삼각형을 만드는 경우가 생기면 무조건 그 선을 우선적으로 그음.
        for (point1, point2) in list(combinations(self.whole_points, 2)):
            temp_line = [point1, point2]
            if self.check_availability(temp_line):
                self.posible_lines.append(temp_line)
                if(self.check_triangle(temp_line)):
                    return temp_line

        print(self.posible_lines)

        #독립선분 긋기 --> DFS 완전탐색, 시간 이슈 발생 
        simul_line_set = self.drawn_lines
        self.simulation_independent_line(0,simul_line_set)

        #print(self.independent_lines_case)
        max_length, longest_element = min([(len(x),x) for x in self.independent_lines_case])
        for line in longest_element:
            if line in self.drawn_lines:
                continue
            else:
                print("return = ", line)
                return line

        #독립선분이 포화 상태일 때 min-max 적용
        simul_line_set = self.drawn_lines
        self.min_max_start(simul_line_set)
        return self.best_line

        # default random return value 
        available = [[point1, point2] for (point1, point2) in list(combinations(self.whole_points, 2)) if self.check_availability([point1, point2])]
        return random.choice(available)
                    
    # DFS 완전탐색 for 독립선분 
    def simulation_independent_line(self, i, simul_line_set):
        print(i)
        # if i == len(self.posible_lines)-1:
        #     print("imworking")
        #     self.independent_lines_case.append(simul_line_set)
        check = True
        for j in range(i, len(self.posible_lines)):
            if(self.check_temp_availability(simul_line_set, self.posible_lines[j])):
                if(self.check_next_triangle(simul_line_set, self.posible_lines[j])):
                    check = False
                    simul_line_set.append(self.posible_lines[j])
                    print("posible lines = ", self.posible_lines[j])
                    print("simul_line_set = ", simul_line_set)
                    self.simulation_independent_line(i,simul_line_set)
                    simul_line_set.remove(self.posible_lines[j])   

        if(check):
            self.organize_points(simul_line_set)
            if(not simul_line_set in self.independent_lines_case):
                self.independent_lines_case.append(simul_line_set.copy())
                print("independent_lines_case = ", self.independent_lines_case)
        print(i, " done")             


    # 선분 정렬 (오름차순) from system.py
    def organize_points(self, point_list):
        point_list.sort(key=lambda x: (x[0], x[1]))
        return point_list
    
    # 그릴 수 있는 선분인지 판별 from system.py
    def check_availability(self, line):
        line_string = LineString(line)

        # Must be one of the whole points
        condition1 = (line[0] in self.whole_points) and (line[1] in self.whole_points)
        
        # Must not skip a dot
        condition2 = True
        for point in self.whole_points:
            if point==line[0] or point==line[1]:
                continue
            else:
                if bool(line_string.intersection(Point(point))):
                    condition2 = False

        # Must not cross another line
        condition3 = True
        for l in self.drawn_lines:
            if len(list(set([line[0], line[1], l[0], l[1]]))) == 3:
                continue
            elif bool(line_string.intersection(LineString(l))):
                condition3 = False

        # Must be a new line
        condition4 = (line not in self.drawn_lines)

        if condition1 and condition2 and condition3 and condition4:
            return True
        else:
            return False    

    # 삼각형인지 판별 from system.py
    # True/False 만 반환하게 custom
    def check_triangle(self, line):
        #self.get_score = False

        point1 = line[0]
        point2 = line[1]

        point1_connected = []
        point2_connected = []

        for l in self.drawn_lines:
            if l==line: # 자기 자신 제외
                continue
            if point1 in l:
                point1_connected.append(l)
            if point2 in l:
                point2_connected.append(l)

        if point1_connected and point2_connected: # 최소한 2점 모두 다른 선분과 연결되어 있어야 함
            for line1, line2 in product(point1_connected, point2_connected):
                
                # Check if it is a triangle & Skip the triangle has occupied
                triangle = self.organize_points(list(set(chain(*[line, line1, line2]))))
                if len(triangle) != 3 or triangle in self.triangles:
                    continue

                empty = True
                for point in self.whole_points:
                    if point in triangle:
                        continue
                    if bool(Polygon(triangle).intersection(Point(point))):
                        empty = False

                if empty:
                    #self.triangles.append(triangle)
                    #self.score[PLAYERS.index(self.turn)]+=1

                    #color = USER_COLOR if self.turn=="USER" else MACHINE_COLOR
                    #self.occupy_triangle(triangle, color=color)
                    #self.get_score = True
                    return True

        return False

    # simulation_line_set 에 포함된 선분을 대상으로 그릴 수 있는 선분인지를 판단
    def check_temp_availability(self, simul_line_set ,line):
        line_string = LineString(line)

        # Must be one of the whole points
        condition1 = (line[0] in self.whole_points) and (line[1] in self.whole_points)
        
        # Must not skip a dot
        condition2 = True
        for point in self.whole_points:
            if point==line[0] or point==line[1]:
                continue
            else:
                if bool(line_string.intersection(Point(point))):
                    condition2 = False

        # Must not cross another line
        condition3 = True
        for l in simul_line_set:
            if len(list(set([line[0], line[1], l[0], l[1]]))) == 3:
                continue
            elif bool(line_string.intersection(LineString(l))):
                condition3 = False

        # Must be a new line
        condition4 = (line not in simul_line_set)

        if condition1 and condition2 and condition3 and condition4:
            return True
        else:
            return False    

    # simulation_line_set 에 포함된 선분을 대상으로 상대방에게 삼각형을 만드는 경우를 제공하는 선분인지를 판단
    def check_next_triangle(self, simul_line_set, line):
        simul_line_set.append(line)

        point1 = line[0]
        point2 = line[1]

        connected_with_line = []

        for next_line in self.posible_lines:
            if next_line in simul_line_set:
                continue
            elif point1 in next_line or point2 in next_line:
                connected_with_line.append(next_line)

        for next_line in connected_with_line:
            if(self.check_temp_triangle(simul_line_set,next_line)):
                simul_line_set.remove(line)
                return False
                
        simul_line_set.remove(line)
        return True


    # simulation_line_set 에 포함된 선분을 대상으로 삼각형을 만드는 선분인지를 판단
    def check_temp_triangle(self, simul_line_set,line):
        #self.get_score = False

        point1 = line[0]
        point2 = line[1]

        point1_connected = []
        point2_connected = []

        for l in simul_line_set:
            if l==line: # 자기 자신 제외
                continue
            if point1 in l:
                point1_connected.append(l)
            if point2 in l:
                point2_connected.append(l)

        if point1_connected and point2_connected: # 최소한 2점 모두 다른 선분과 연결되어 있어야 함
            for line1, line2 in product(point1_connected, point2_connected):
                
                # Check if it is a triangle & Skip the triangle has occupied
                triangle = self.organize_points(list(set(chain(*[line, line1, line2]))))
                if len(triangle) != 3 or triangle in self.triangles:
                    continue

                empty = True
                for point in self.whole_points:
                    if point in triangle:
                        continue
                    if bool(Polygon(triangle).intersection(Point(point))):
                        empty = False

                if empty:
                    #self.triangles.append(triangle)
                    #self.score[PLAYERS.index(self.turn)]+=1

                    #color = USER_COLOR if self.turn=="USER" else MACHINE_COLOR
                    #self.occupy_triangle(triangle, color=color)
                    #self.get_score = True
                    return True

        return False

    # simulation_line_set 에 포함된 선분을 대상으로 게임이 끝났는지를 판단
    def check_endgame(self, simul_line_set):
        remain_to_draw = [[point1, point2] for (point1, point2) in list(combinations(self.whole_points, 2)) if self.check_temp_availability(simul_line_set, [point1, point2])]
        return False if remain_to_draw else True

    # min_max function
    def min_max_start(self, simul_line_set):
        self.best_line = [(0, 0), (1 , 0)]
        self.max_move(simul_line_set)


    def max_move(self, simul_line_set):
        if self.check_endgame(simul_line_set):
            return self.EvalGameState(simul_line_set)
        else:
            next_lines = self.GenerateMove() #line list를 반환
            best_value = -1000000000
            for next_line in next_lines:
                simul_line_set.append(next_line)
                next_node_value = self.min_move(simul_line_set)
                if next_node_value > best_value:
                    best_value = next_node_value
                    self.best_line = next_line
                simul_line_set.remove(next_line)
            return best_value
                

    def min_move(self, simul_line_set):
        if self.check_endgame(simul_line_set):
            return self.EvalGameState(simul_line_set)
        else:
            next_lines = self.GenerateMove() #line list를 반환
            best_value = 1000000000
            for next_line in next_lines:
                simul_line_set.append(next_line)
                next_node_value = self.max_move(simul_line_set)
                if next_node_value < best_value:
                    best_value = next_node_value
                simul_line_set.remove(next_line)
            return best_value
    



