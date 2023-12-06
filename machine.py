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
        self.is_full = False

    def find_best_selection(self):

        self.posible_lines = []
        self.independent_lines_case = []

        #가능한 line 가져오기
        for (point1, point2) in list(combinations(self.whole_points, 2)):
            temp_line = [point1, point2]
            if self.check_availability(temp_line):
                self.posible_lines.append(temp_line)
                #if(self.check_triangle(temp_line)):
                #    return temp_line
        
        #삼각형을 만드는 경우가 생기면 무조건 그 선을 우선적으로 그음.
        max_value = 0
        best_line = self.posible_lines[0]
        for line in self.posible_lines:
            temp = self.check_temp_triangle_return_num(self.drawn_lines,line)
            if temp > max_value:
                max_value = temp
                best_line = line

        if max_value != 0:
            print("triangle case")
            return best_line                 
                    
        #print(self.posible_lines)

        #독립선분 긋기 --> DFS 완전탐색, 시간 이슈 발생 
        simul_line_set = self.drawn_lines
        self.minimum_independent_line_num = 1000000000
        self.simulation_independent_line(0,simul_line_set)

        #print(self.independent_lines_case)
        #print(len(self.independent_lines_case))

        #convexHull points 와 convexHull lines 생성
        convex_points = self.ConvexHull(self.whole_points)
        convex_lines = []
        convex_lines.append(sorted([convex_points[0], convex_points[-1]]))
        for i in range(0,len(convex_points)-1):
            convex_lines.append(sorted([convex_points[i],convex_points[i+1]]))
        
        # 독립선분 최소 case에서 convexhull 위의 선분이 아닌 것을 선택 

        min_length, shortest_element = min([(len(x),x) for x in self.independent_lines_case])
        for line_set in self.independent_lines_case:
            if len(line_set) == min_length:
                for line in line_set:
                    if line in self.drawn_lines:
                        continue
                    else:
                        if len(self.whole_points) == len(convex_points):
                            #독립 선분 중에 convex hull 위의 선이 아닌것을 출력
                            if sorted(line) in convex_lines: 
                                continue
                            else:
                                print("return = ", line)
                                print("independent line")
                                return [line[0], line[1]]
                        else:
                            # if line[0] in convex_points and line[1] in convex_points:
                            #     continue
                            # else:
                            #     print("return = ", line)
                            #     print("independent line")
                            #     return [line[0], line[1]]
                            print("return = ", line)
                            print("independent line")
                            return [line[0], line[1]]
        
        # 독립선분이 포화 상태일 때 min-max 적용
        simul_line_set = self.drawn_lines
        print("minmax")
        self.min_max_start(simul_line_set)
        return self.best_line


        # default random return value 
        #available = [[point1, point2] for (point1, point2) in list(combinations(self.whole_points, 2)) if self.check_availability([point1, point2])]
        #return random.choice(available)
                    
    # DFS 완전탐색 for 독립선분 
    def simulation_independent_line(self, i, simul_line_set):
        #print(i)

        # 독립변수 case 조사하는 개수 제한... 20까지 했는데 최적의 수가 21번째 나오면 답 없음... 타협 필요
        if len(self.independent_lines_case) == 12:
            return

        # 독립변수 case 조사할 때, 선분 수가 가장 적은 case 보다 simulation set이 많아지면 즉시 종료
        if(len(simul_line_set) > self.minimum_independent_line_num):
            return

        check = True
        for j in range(i, len(self.posible_lines)):
            if(self.check_temp_availability(simul_line_set, self.posible_lines[j])):
                if(self.check_next_triangle(simul_line_set, self.posible_lines[j])):
                    check = False
                    simul_line_set.append(self.posible_lines[j])
                    #print("posible lines = ", self.posible_lines[j])
                    #print("simul_line_set = ", simul_line_set)
                    self.simulation_independent_line(i,simul_line_set)
                    simul_line_set.remove(self.posible_lines[j])   

        if(check):
            self.organize_points(simul_line_set)
            if(not simul_line_set in self.independent_lines_case):
                self.independent_lines_case.append(simul_line_set.copy())
                if(self.minimum_independent_line_num > len(simul_line_set)):
                    self.minimum_independent_line_num = len(simul_line_set)
                #print("independent_lines_case = ", self.independent_lines_case)
        #print(i, " done")             


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
        #print("1 : ", condition1, " 2 : ", condition2, " 3 : ", condition3, " 4 : ", condition4)

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
        print("min_max running....")
        alpha = -1000000
        beta = 100000 
        evaluation_value =0
        self.best_line = [(0, 0), (1 , 0)]
        depth =0
        self.max_move(depth, simul_line_set, alpha, beta, evaluation_value)  # 무조건 machine의 turn 이니까 max_move 먼저 호출


    def max_move(self, depth, simul_line_set, alpha, beta, evaluation_value):
        if self.check_endgame(simul_line_set):
            #print("simul_line_set = ", simul_line_set)
            #print("evaluation_value = ", evaluation_value)
            return evaluation_value
        elif depth > 5:
            return evaluation_value
        else:
            next_lines = self.GenerateMove(simul_line_set) #line list를 반환
            best_value = -1000000000
            temp_score = self.score
            temp_evaluation_value = evaluation_value
            for next_line in next_lines:
                #print(next_line)
                # machine이 이기면 점수 +1
                if(self.check_temp_triangle(simul_line_set, next_line)):
                    self.score[1] += 1

                #simul_line_set에 next line 넣고, evaluation_value 계산해서, 다음 min_move 보기
                simul_line_set.append(next_line)
                evaluation_value += self.EvalGameStateMax(simul_line_set)
                next_node_value = self.min_move(depth+1, simul_line_set, alpha, beta, evaluation_value)
                # 나온 결과 값의 최댓값만 저장
                if next_node_value > best_value:
                    best_value = next_node_value
                    self.best_line = next_line
                    alpha = max(alpha, best_value)
                # 점수랑 simul_line_set랑 evaluation_value 다시 원래대로 되돌리기
                simul_line_set.remove(next_line)
                self.score = temp_score
                evaluation_value = temp_evaluation_value

                #alpha cuttoff
                if beta <= alpha:
                    break

            return best_value
                

    def min_move(self, depth, simul_line_set, alpha, beta, evaluation_value):
        if self.check_endgame(simul_line_set):
            #print("simul_line_set = ", simul_line_set)
            #print("evaluation_value = ", evaluation_value)
            return evaluation_value
        elif depth > 5:
            return evaluation_value
        else:
            next_lines = self.GenerateMove(simul_line_set) #line list를 반환
            best_value = 1000000000
            temp_score = self.score
            temp_evaluation_value = evaluation_value
            for next_line in next_lines:
                # user가 이기면 점수 +1
                if(self.check_temp_triangle(simul_line_set, next_line)):
                    self.score[0] += 1
                
                #simul_line_set에 next line 넣고, evaluation_value 계산해서, 다음 max_move 보기
                simul_line_set.append(next_line)
                evaluation_value -= self.EvalGameStateMin(simul_line_set)
                next_node_value = self.max_move(depth+1, simul_line_set,alpha,beta, evaluation_value)
                # 나온 결과 값의 최솟값만 저장
                if next_node_value < best_value:
                    best_value = next_node_value
                    beta = min(beta, best_value)
                # 점수랑 simul_line_set랑 evaluation_value 다시 원래대로 되돌리기
                simul_line_set.remove(next_line)
                self.score = temp_score
                evaluation_value = temp_evaluation_value

                #beta cutoff
                if beta <= alpha:
                    break

            return best_value
    

    def EvalGameStateMax(self, simul_line_set):    #상수 파라미터들은 플레이 해보면서 고치기,1안:갯수 따라서 전부 점수 따로 매김
        node_value=0
        
        if(self.check_next_triangle_return_num(simul_line_set[0:len(simul_line_set)-1:],simul_line_set[-1])==2):
            node_value-=30  
        elif(self.check_next_triangle_return_num(simul_line_set[0:len(simul_line_set)-1:],simul_line_set[-1])==1):
            node_value-=10
            
        if(self.check_temp_triangle_return_num(simul_line_set[0:len(simul_line_set)-1:],simul_line_set[-1])==2):
            node_value+=45   
        elif(self.check_temp_triangle_return_num(simul_line_set[0:len(simul_line_set)-1:],simul_line_set[-1])==1):
            node_value+=15
        # else:    #user<score 수비 위주로 평가 
        #     if(self.check_next_triangle_return_num(simul_line_set[0:len(simul_line_set)-1:],simul_line_set[-1])==2):
        #         node_value-=50   
        #     elif(self.check_next_triangle_return_num(simul_line_set[0:len(simul_line_set)-1:],simul_line_set[-1])==1):
        #         node_value-=20
                
        #     if(self.check_temp_triangle_return_num(simul_line_set[0:len(simul_line_set)-1:],simul_line_set[-1])==2):
        #         node_value+=45    
        #     elif(self.check_temp_triangle_return_num(simul_line_set[0:len(simul_line_set)-1:],simul_line_set[-1])==1):
        #         node_value+=15
        
        return node_value

    def EvalGameStateMin(self, simul_line_set):    #상수 파라미터들은 플레이 해보면서 고치기,1안:갯수 따라서 전부 점수 따로 매김
        node_value=0
        
        if(self.check_next_triangle_return_num(simul_line_set[0:len(simul_line_set)-1:],simul_line_set[-1])==2):
            node_value-=45  
        elif(self.check_next_triangle_return_num(simul_line_set[0:len(simul_line_set)-1:],simul_line_set[-1])==1):
            node_value-=15
            
        if(self.check_temp_triangle_return_num(simul_line_set[0:len(simul_line_set)-1:],simul_line_set[-1])==2):
            node_value+=30   
        elif(self.check_temp_triangle_return_num(simul_line_set[0:len(simul_line_set)-1:],simul_line_set[-1])==1):
            node_value+=10
        # else:    #user<score 수비 위주로 평가 
        #     if(self.check_next_triangle_return_num(simul_line_set[0:len(simul_line_set)-1:],simul_line_set[-1])==2):
        #         node_value-=50   
        #     elif(self.check_next_triangle_return_num(simul_line_set[0:len(simul_line_set)-1:],simul_line_set[-1])==1):
        #         node_value-=20
                
        #     if(self.check_temp_triangle_return_num(simul_line_set[0:len(simul_line_set)-1:],simul_line_set[-1])==2):
        #         node_value+=45    
        #     elif(self.check_temp_triangle_return_num(simul_line_set[0:len(simul_line_set)-1:],simul_line_set[-1])==1):
        #         node_value+=15
        
        return node_value
    
    def EvalGameState2(self, simul_line_set):    #상수 파라미터들은 플레이 해보면서 고치기,2안:갯수 차이로만 점수 계산
        node_value=0
        triangle_count=self.check_next_triangle_return_num(simul_line_set[0:len(simul_line_set)-1:],simul_line_set[-1])-self.check_temp_triangle_return_num(simul_line_set[0:len(simul_line_set)-1:],simul_line_set[-1])
        if(triangle_count==-2):
            node_value+=30
        elif(triangle_count==-1):
            node_value+=30
        elif(triangle_count==1):
            node_value-=15
        elif(triangle_count==2):
            node_value-=45
        return node_value


    def GenerateMove(self, simul_line_set):
        
        return_next_lines = []
        posible_lines = []
        evalueted_lines_value = []

        #posible_lines 고르기
        for (point1, point2) in list(combinations(self.whole_points, 2)):
            temp_line = [point1, point2]
            if self.check_temp_availability(simul_line_set, temp_line):
                posible_lines.append(temp_line)

        #posible_lines의 수에 따라서 생성할 child 노드 수 정하기 
        # if len(posible_lines) >= 10:
        #     num_of_child_node = 2
        # else:
        #     num_of_child_node = 5
        num_of_child_node = 3

        #각각 가능한 선분에 대해 heuristic 값 구하기 
        # h(x) = getScore(x) - nextTriangle(x)
        for next_line in posible_lines:
            h_x =0   # heuristic value

            # getScore()
            getScore = self.check_temp_triangle_return_num(simul_line_set, next_line)
            if(getScore != 0):
                h_x += 3*getScore

            # nextTriangle()
            nextTriangle = self.check_next_triangle_return_num(simul_line_set, next_line)
            if nextTriangle == 0:
                h_x -= 0
            elif nextTriangle == 1:
                h_x -= 2
            else:
                h_x -= 1

            evalueted_lines_value.append([h_x, next_line])
            #print("next_line = ", next_line, " h_x = ", h_x)

        
        # for i in range(num_of_child_node):
        #     max_value = [-1000000, [[0,0],[0,1]]]
        #     for candidate in evalueted_lines_value:
        #         if candidate[1] > max_value[1]:
        #             max_value = candidate

        #    return_next_lines.append(max_value[0])
        
        evalueted_lines_value.sort()
        #print("evalueted_lines_value ", evalueted_lines_value)
        if(len(evalueted_lines_value) < num_of_child_node):
            for element in evalueted_lines_value:
                return_next_lines.append(element[1])
        else:
            for i in range(num_of_child_node):
                return_next_lines.append(evalueted_lines_value[i][1])
            
    

        #print("candidate of node", return_next_lines)
        return return_next_lines

    # 현재 내가 긋는 선분이 몇개의 삼각형을 만드는지를 return 하는 function 
    def check_temp_triangle_return_num(self, simul_line_set,line):
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
        
        return_value=0
        
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
                    return_value+=1

        return return_value
        
    # simulation_line_set 에 포함된 선분을 대상으로 상대방에게 삼각형을 몇개 제공하게 되는지를 return 하는 함수
    def check_next_triangle_return_num(self, simul_line_set, line):
        simul_line_set.append(line)

        point1 = line[0]
        point2 = line[1]

        connected_with_line = []
        return_value =0

        posible_lines = []
        for (point1, point2) in list(combinations(self.whole_points, 2)):
            temp_line = [point1, point2]
            if self.check_temp_availability(simul_line_set,temp_line):
                posible_lines.append(temp_line)

        for next_line in posible_lines:
            if next_line in simul_line_set:
                continue
            elif point1 in next_line or point2 in next_line:
                connected_with_line.append(next_line)

        for next_line in connected_with_line:
            if(self.check_temp_triangle(simul_line_set,next_line)):
                return_value += 1

        simul_line_set.remove(line)
        return return_value

    def ConvexHull(self, points):
        upper = []
        lower = []
        for p in sorted(points):
            while len(upper) > 1 and self.ccw(upper[-2], upper[-1], p) > 0:
                upper.pop()
            while len(lower) > 1 and self.ccw(lower[-2], lower[-1], p) < 0:
                lower.pop()
            upper.append(p)
            lower.append(p)
    
        convex_points = upper + lower
        result = []
        [result.append(x) for x in convex_points if x not in result]
        return result

    def ccw(self, a,b,c):
        return a[0]*b[1] + b[0]*c[1] + c[0]*a[1] - (b[0]*a[1] + c[0]*b[1] + a[0]*c[1])


