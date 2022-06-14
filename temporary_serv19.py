import sqlite3
from socket import *
from threading import *
import time


connection = sqlite3.connect("edu.db", check_same_thread = False)
cur = connection.cursor()

class Serv:
    def __init__(self):
        super(Serv, self).__init__()
        self.clients = []
        self.ip = ''
        self.port = 9036
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sock.bind((self.ip, self.port))
        self.sock.listen(5)
        print(" 접 속 자 대 기 중 . . . ")
        self.accept()

# 클라 연결 요청
    def accept(self):   # -> class init
        while True:
            print("1")
            c_sock, (r_host, r_port) = self.sock.accept()               # 클라를 소켓, ip, port로 분해함
            print(f"{c_sock} 접속함")
            job = c_sock.recv(1024).decode()
            if c_sock not in self.clients:                              # 클라 리스트 안에 없는 소켓이라면
                if job == 'teacher':
                    self.clients.append((c_sock,'t', 0))
                elif job == 'student':
                    self.clients.append((c_sock,'s', 0))                             # 클라 리스트에 소켓 추가
            print(f'{r_host}:{str(r_port)}가 연결되었습니다.')
            print(self.clients)
            c_thd = Thread(target=self.recv_msg, args=(c_sock,job))        # recv_msg 함수를 쓰레드 연결
            c_thd.start()                                               # 쓰레드 스타트

    def recv_msg(self, c_sock, job):
        while True:
            # 클라로부터 받는 모든 것(메세지, 요청 등등)들이 들어오는 부분
            try:
                data = c_sock.recv(1024)
                print(f"받은 메세지 : {data.decode()}")
                if not data:                        # 받은 메세지가 없으면 꺼짐
                    break
            except:
                continue
            # 로그인하는 부분
            else:
                if job == 'student':
                    final_msg = data.decode()           # 받은 메세지를 디코드 하고
                    print("빠이널메쎄쥐", final_msg)
                    if '#' in final_msg:                                            # 클라에서 오는 메세지 안에 '#'이 포함되어 있다면
                        print("#", final_msg)
                        id_and_pw = final_msg.split(" ")                            # " "(공백)으로 split 합니다
                        print("스플릿", id_and_pw)
                        input_id = id_and_pw[1]                                     # 그러면 ['#', 'id', 'password'] 로 나뉘어집니다
                        input_pw = id_and_pw[2]                                     # 그래서 [1]번 인덱스가 id, [2]번 인덱스가 password
                        print("4", id_and_pw, input_id, input_pw)
                        cur.execute(f"select id, password from students where id = '{input_id}'")   # db에서 입력받은 id와 일치하는 id, pw를 불러옵니다
                        id_pw_from_db = cur.fetchall()                              # db에서 가져온다
                        print("4.5", id_pw_from_db)
                        for i in id_pw_from_db:                                     # 불러온 db를 for문으로 돌려서 하나하나 체크해서
                            print("5", i)                                           # 불러온 db는 [(id, pw), (id1, pw1)] 이런 형태이기 때문에
                            if input_id == i[0] and input_pw == i[1]:               # for문으로 리스트를 풀어서 (id, pw) 모양으로 하나하나 체크합니다
                                print(f'6 {input_id}={i[0]}, {input_pw}={i[1]}')    # 입력받은 id와 i[0] (for문 돌린 i[0] db의 아이디) and pw와 i[1] (패스워드) 가 둘 다 일치한다면
                                c_sock.send("OK, GO!".encode())  # 허가 메세지        # ok, go!(변경해도 됨, 변경 후 말만 해주세요) 라는 메세지를 클라이언트에 다시 보내준다
                                break                                               # 그리고 break
                            else :  # 메세지 박스 넣으면 될 듯, 아이디ok, 비번 X 일 때 7번으로 옴
                                print("7 get out !")             # 불허 메세지        # 일치하는게 없다면 특정한 메세지를 보냄
                    elif '?' in final_msg:  # 아이디를 입력하고 중복확인 버튼을 눌렀을 경우
                        print("?", final_msg)  # 넘어온 메세지 출력, 예상되는 메세지는 ? id
                        # 넘어온 문자열이 데이터 베이스에 있는지 확인해야함
                        userid = final_msg.split(" ") # 받은 문자열을 split함수를 통해서 " "단위로 나눌것이다. ['?', 'id']
                        # split함수를 사용해서 나눴기 때문에 인덱스를 사용해서 값을 뽑아볼수있다.
                        cur.execute(f"select count(*) from students where id  = '{userid[1]}'")  # cur.fetchall() 는 id가 userid[1]와 겹치는 줄수를 나타낸다. 예상되는 형태는 [(0)] 이런식으로 나오게 될 것이다.
                        check = int(cur.fetchall()[0][0]) # 리스트 한번 벗기고 튜플 한번 벗기고 int형 씌우면 정수처럼 사용이 될것이다.
                        if check > 0: # 중복된 줄수가 1이상일 경우
                            c_sock.send("중복됨".encode())
                        else: # 아닐경우
                            c_sock.send("사용가능한 아이디".encode())
                    elif '!' in final_msg: # 회원가입 창에서 다 입력하고 회원가입버튼을 눌렀을 때
                        # 넘어올 것으로 예상되는 데이터 [! 아이디 비밀번호 비밀번호확인 이름 이메일]
                        userdata = final_msg.split(" ") # [!,아이디,비밀번호,이름,이메일]
                        # 이 데이터들로 데이터베이스에 추가해야함.
                        # 단, 조건으로 비밀번호와 비밀번호확인이 같을 때
                        cur.execute(f"insert into students(name, id, password, quiz_score, e_mail) values (?, ?, ?, ?, ?)",(userdata[3],userdata[1],userdata[2],0,userdata[4]))
                        c_sock.send("회원가입 성공".encode())
                        connection.commit()
                    elif '^' in final_msg: # ^, 문제, 정답, 채점
                        userquiz = final_msg.split(" ")
                        cur.execute(f"insert into quiz values('{id_and_pw[1]}','{userquiz[1]}','{userquiz[2]}','{userquiz[3]}')")
                        c_sock.send("문제풀기 성공".encode())
                        connection.commit()
                        # 문제 한문제 풀 때마다 데이터베이스 저장
                    elif 'qna' in final_msg:
                        user_question = final_msg.split(" ")
                        for i in range(len(user_question[0])):
                            cur.execute(f"insert into QnA values (?, ?, ?)",(user_question[0][i], user_question[1][i], '답변대기'))
                    elif '@상담진입' in final_msg:
                        # 상담하고 있는 학생이 있으면 막아야함.
                        for i in self.clients:
                            if i[2] == 1 and i[1] == 's':
                                break
                        # 상담요청에 성공했을 때 학생클라이언트의 상태를 1로 전환
                        c_sock = 1
                    elif chr(1003) in final_msg:
                        left = final_msg.split(chr(1003))
                        right = left[1].split(chr(1001))
                        print(right)
                        cur.execute(f"insert into left values (?, ?, ?)",(id_and_pw[1], str(right[0]), str(right[1])))
                        c_sock.send('보냄'.encode())
                        time.sleep(1 / 1000)
                        connection.commit()
                    elif chr(3000) in final_msg: # 불러오기
                        # 데이터베이스에 해당 아이디 문제를 클라이언트로 보내주면서 다 지워야함.
                        cur.execute(f"select * from left where id = '{id_and_pw[1]}'")
                        leftlist = cur.fetchall()
                        for i in leftlist:
                            time.sleep(1 / 100)
                            c_sock.send(f'{chr(1003)}{i[1]}{chr(1001)}{i[0]}'.encode())
                            cur.execute(f"delete from left where id = '{id_and_pw[1]}'")

                    else:
                        self.send_clients(c_sock,final_msg)                     # 그 외의 사항에는 send_all_clients() 함수를 실행한다

                elif job == 'teacher':
                    final_msg = data.decode()  # 받은 메세지를 디코드 하고
                    print("빠이널메쎄쥐", final_msg)
                    if '@문제출제' in final_msg:
                        questions = final_msg.split(" ")
                        cur.execute(f"select count(voca) from english where voca = '{questions[1]}'")
                        if int(cur.fetchall()[0][0]) > 0:
                            c_sock.send("중복된 단어".encode())
                        else:
                            if len(questions[1]) == 0:
                                pass
                            else:
                                cur.execute(f"insert into english(voca,meaning) values(?, ?)",(questions[1],questions[2]))
                                c_sock.send("문제출제 성공".encode())
                                connection.commit()
                    elif '@qna답변' in final_msg:
                        qnalist = []
                        qna = final_msg.split(" ")
                        cur.execute(f"select * from QnA") # 넘어올 것으로 예상되는 데이터 [(id, q, a),(id, q, a), ... ]
                        qnalist = cur.fetchall()
                        idlist = []
                        qlist = []
                        alist = []
                        for i in range(len(qnalist)):
                            idlist.append(qnalist[i][0])
                            qlist.append(qnalist[i][1])
                            alist.append(qnalist[i][2])
                        c_sock.send(f"{[tuple(idlist),tuple(qlist),tuple(alist)]}".encode())
                    elif '@문제확인' in final_msg:
                        cur.execute(f"select * from english")
                        list = cur.fetchall()
                        for i in list:
                            c_sock.send(str(i[1:]).encode())
                            time.sleep(1/100)
                    else:
                        self.send_clients(c_sock,final_msg)                     # 그 외의 사항에는 send_all_clients() 함수를 실행한다


        c_sock.close()


    def send_clients(self, c_sock,final_msg):       # 선생 클라이언에게 채팅을 send 하는 함수
        for client in self.clients:                     # 클라 리스트트를 하나하나 체크해서
            if client[1] == 't' and c_sock[2] == '1':                             # 접속된 소켓과 같은 소켓의 클라라면
                print("2")
                try:                                        # 그 소켓에 메세지를 보낸다
                    print("3")
                    socket.send(final_msg.encode())
                except:
                    self.clients.remove(client)             # 그 외의 사항에는 클라 리스트에서 클라를 삭제한다



if __name__ == "__main__":
    Serv()