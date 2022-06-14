import sys
import time
import random
import pymysql
import sqlite3
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from socket import *

connection = sqlite3.connect("edu.db", check_same_thread = False)
cur = connection.cursor()
# db에서 출력시킬 문제를 불러옴

eduappwin = uic.loadUiType("eduapp.ui")[0]
sock = socket(AF_INET, SOCK_STREAM)
sock.connect(('', 9036))
sock.send("student".encode())

# 메인화면
class Eduapp(QMainWindow, eduappwin):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 문제 관련 변수
        self.quiz_count = 0             # 퀴즈 카운트
        self.row_count = -1             # 퀴즈 개수만큼 테이블 행 만들기위한 카운트
        self.correct_quiz_answer = 0    # 맞힌 퀴즈 개수
        self.incorrect_quiz_answer = 0  # 틀린 퀴즈 개수
        self.quiz_list = []             # 퀴즈 불러와서 저장할 리스트 ( 이게 0이 되면 퀴즈 끝 )

# 파이큐티 슬롯, Q쓰레드 실행
        self.rcv = Receive()
        self.rcv.signal1.connect(self.recv_msg)         # 리시브
        self.rcv.signal2.connect(self.id_check_recv)    # 로그인
        self.rcv.signal3.connect(self.id_double_check)  # 아이디 중복확인
        self.rcv.start()

        # 학습하기 출력
        cur.execute("select * from english")
        result1 = cur.fetchall()
        for i in result1:
            self.textBrowser.append(f'{i[0]} ) {i[1]}  -  {i[2]}')

# 시그널
        self.backbtn.clicked.connect(self.movetopage0)                  # 메인페이지
        self.pushButton1.clicked.connect(self.movetopage1)              # 학습하기
        self.pushButton2.clicked.connect(self.movetopage2)              # 문제풀기
        self.pushButton3.clicked.connect(self.movetopage3)              # 점수보기
        self.pushButton4.clicked.connect(self.movetopage4)              # QnA
        self.pushButton5.clicked.connect(self.movetopage6)              # 상담하기
        self.move_signup_page_btn.clicked.connect(self.movetopage5)     # 회원가입하기
        self.counsel_input_chat.returnPressed.connect(self.append_text) # 상담창에서 엔터로 메세지 보내기
        self.send_btn.clicked.connect(self.append_text)                 # 상담창에서 보내기 버튼으로 메세지 보내기
        self.exit_btn.clicked.connect(self.exit_counsel_page)           # 상담창에서 나가기 버튼으로 나가기
        self.quiz_lineedit.returnPressed.connect(self.quiz_reset)       # 문제풀이 창에서 엔터로 답 입력하기
        self.login_btn.clicked.connect(self.id_check)                   # 로그인 확인하기
        self.add_quiz_btn.clicked.connect(self.add_quiz)                # 문제 추가
        self.id_check_btn.clicked.connect(self.id_double_check1)        # 중복확인 클릭 시 아이디 서버로 전송
        self.signup_btn.clicked.connect(self.pw_double_check)           # 회원가입 버튼 클릭 시 회원가입 가능 or 불가능
        self.save_quiz_btn.clicked.connect(self.ExtraQuiz)              # 남은 퀴즈 서버에 보내기

# 시그널 함수
    def movetopage1(self):  # 학습하기 창
        self.stackedWidget.setCurrentWidget(self.page2)

    # 페이지 이동 + 문제 제출하는 함수
    def movetopage2(self):  # 문제풀기 창
        self.stackedWidget.setCurrentWidget(self.page3)

        # 테이블 위젯 설정
        cur.execute("select count(*) count from english")
        row_count = cur.fetchall()[0][0]
        print("0", row_count)
        self.quiztable.setRowCount(row_count)
        self.quiztable.setColumnWidth(0, 95)

        self.quiztable.clearContents()  # 테이블 위젯 다 삭제
        self.quiz_label.clear()         # 텍스트 라벨 클리어
        self.OXlabel.clear()            # OX 그림 라벨 클리어
        self.correct_answer.display(0)         # 맞은 퀴즈 개수 초기화
        self.incorrec_answer.display(0)        # 틀린 퀴즈 개수 초기화
        self.quiz_list.clear()          # 퀴즈 리스트 초기화
        print("왜 왜 왜 왜 왜왜오애ㅗ애", len(self.quiz_list))
        if len(self.quiz_list) == 0:
            self.add_quiz_btn.setEnabled(True)
        else :
            print("길이 길이", len(self.quiz_list))
            self.add_quiz_btn.setEnabled(False)

    def movetopage3(self):  # 점수확인 창
        self.stackedWidget.setCurrentWidget(self.page4)
    def movetopage4(self):  # QnA 창
        self.stackedWidget.setCurrentWidget(self.page5)
    def movetopage5(self):  # 회원가입 창
        self.make_id_line.clear()       # 회원가입 창 드갈 때마다
        self.make_pw_line.clear()
        self.check_pw_line.clear()
        self.make_name_line.clear()     # 싹 다
        self.make_mail_line.clear()
        self.id_check_label.clear()
        self.pw_check_label.clear()     # 비워주기
        self.signup_btn.setEnabled(False)  # 회원가입 버튼 비활성화 시켜놓기
        self.stackedWidget.setCurrentWidget(self.page6)
    def movetopage6(self):  # 상담하기 창
        self.stackedWidget.setCurrentWidget(self.page7)
    def movetopage0(self):  # 메인 페이지로 돌아가기 창
        self.stackedWidget.setCurrentWidget(self.page1)

    # 제일 처음 문제 출제하기
    def add_quiz(self):     # -> 커넥트 시그널
        # DB에서 문제 뽑아오기
        cur.execute("select * from english")
        allquiz = cur.fetchall()
        # # 뽑아온 문제들 리스트에 저장
        for i in allquiz:
            self.quiz_list.append(i[1:])
        random.shuffle(self.quiz_list)  # 섞어주고
        print("2", self.quiz_list, "\n", len(self.quiz_list))

        # 리스트 길이가 0이면 문제풀이 시작하기 버튼 on, 아니면 off
        if len(self.quiz_list) == 0:
            self.add_quiz_btn.setEnabled(True)
        else :
            print("길이 길이", len(self.quiz_list))
            self.add_quiz_btn.setEnabled(False)

        # 화면에 문제 출력
        self.quiz_label.setText(f'{self.quiz_list[0][1]}')

    # 다음 문제로 넘어가기위한 함수
    def quiz_reset(self):   # -> 커넥트 시그널
        self.quiz_label.setText("")
        self.make_quiz()
        self.quiz_lineedit.clear()

    # 계속해서 문제를 만들어주는 함수
    def make_quiz(self):    # -> quiz_reset
        quiz_text = self.quiz_lineedit.text()

        # 문제 카운트가 20이되면 0으로 초기화
        if self.quiz_count == 20:
            self.quiz_count = 0

        # 그 외에는 계속 진행
        else :  # 카운트 세면서 카운트 띄워주기
            print("3", self.row_count)
            self.row_count += 1
            self.quiz_count += 1
            self.quiz_counter.display(self.quiz_count)

            # 정답 입력 시
            if self.quiz_lineedit.text() == self.quiz_list[0][0]:
                print("4")
                print(f"정답 : {self.quiz_list[0][0]} 문제 : {self.quiz_list[0][1]}")
                print("정답")
                a = self.OXlabel.setPixmap(QPixmap("O7070.png"))
                self.correct_quiz_answer += 1
                self.correct_answer.display(self.correct_quiz_answer)
                # 테이블 위젯에 정보들 입력, 0-출제된 문제, 1-내가 쓴 답, 2-문제의 정답, 3-O,X표시
                self.quiztable.setItem(self.row_count, 0, QTableWidgetItem(str(self.quiz_list[0][1])))
                self.quiztable.setItem(self.row_count, 1, QTableWidgetItem(str(quiz_text)))
                self.quiztable.setItem(self.row_count, 2, QTableWidgetItem(str(self.quiz_list[0][0])))
                self.quiztable.setItem(self.row_count, 3, QTableWidgetItem(str('O')))
                sock.send(f'^ {self.quiz_list[0][1]} {self.quiz_list[0][0]} O'.encode())

            # 오답 입력 시
            elif self.quiz_lineedit.text() != self.quiz_list[0][0]:
                print(f"정답 : {self.quiz_list[0][0]} 문제 : {self.quiz_list[0][1]}")
                print("틀렸네")
                self.OXlabel.setPixmap(QPixmap("X7070.png"))
                self.incorrect_quiz_answer += 1
                self.incorrec_answer.display(self.incorrect_quiz_answer)
                self.quiztable.setItem(self.row_count, 0, QTableWidgetItem(str(self.quiz_list[0][1])))
                self.quiztable.setItem(self.row_count, 1, QTableWidgetItem(str(quiz_text)))
                self.quiztable.setItem(self.row_count, 2, QTableWidgetItem(str(self.quiz_list[0][0])))
                self.quiztable.setItem(self.row_count, 3, QTableWidgetItem(str('X')))
                sock.send(f'^ {self.quiz_list[0][1]} {self.quiz_list[0][0]} X'.encode())

        # 리스트에서 출제된 문제 삭제 후 다음 문제 표시해주기
        del self.quiz_list[0]
        print("삭제됐니 리스트야 ?", self.quiz_list, len(self.quiz_list))
        self.quiz_label.setText(f'{self.quiz_list[0][1]}')

    def ExtraQuiz(self):
        print("남은 문제 보내기")
        for i in self.quiz_list:
            print("다 잘 가주기를 바란다 제발", f'{chr(1003)}{i[1]}{chr(1001)}{i[0]}')
            sock.send(f'{chr(1003)}{i[1]}{chr(1001)}{i[0]}'.encode())
        self.quiz_list.clear()               # 퀴즈 리스트 초기화
        print("퀴즈 리스트야 좀 뒤지렴", len(self.quiz_list))
        self.row_count = -1
        self.stackedWidget.setCurrentWidget(self.page1)

    # 상담 채팅 창에 채팅 띄우기, 서버에 메세지 보내기
    def append_text(self):      # -> 커넥트 시그널
        inputchat = self.counsel_input_chat.text()
        sock.send(('&' + inputchat).encode())
        self.counsel_chat_box.append(f'학생 : {inputchat}')
        self.counsel_input_chat.clear()

    # 상담 페이지 벗어나는 함수
    def exit_counsel_page(self):    # -> 커넥트 시그널
        self.counsel_chat_box.clear()
        self.stackedWidget.setCurrentWidget(self.page0)

    # 아이디 비번 확인 절차를 위해 서버에 전송
    def id_check(self):     # -> 커넥트 시그널
        input_id = self.id_lineedit.text()
        input_pw = self.pw_lineedit.text()
        sock.send(f'# {input_id} {input_pw}'.encode())

    # 아이디 중복확인 절차 함수복
    def id_double_check1(self):     # -> 커넥트 시그널
        print("6.5")
        make_id_line = self.make_id_line.text()
        sock.send(f'? {make_id_line}'.encode())

    # 회원가입 함수
    def pw_double_check(self):      # -> 커넥트 시그널
        print("회원가입 성공하니 ?")
        if self.id_check_label.text() == "사용가능 아이디":
            print(" 회원가입 성공 1 ")
            if self.make_pw_line.text() == self.check_pw_line.text():
                print(" 회원가입 성공 2 ")
                if self.make_name_line.text():
                    print(" 회원가입 성공 3 ")
                    if bool(self.make_mail_line.text()):
                        print(" 회원가입 성공 4 ")
                        sock.send(f'! {self.make_id_line.text()} {self.make_pw_line.text()} {self.make_name_line.text()} {self.make_mail_line.text()}'.encode())
                        self.stackedWidget.setCurrentWidget(self.page0)

            elif self.make_pw_line.text() != self.check_pw_line.text():
                self.pw_check_label.setText("")
                self.pw_check_label.setText("비번이 서로 다름")



    # 받은 메세지 상담 창에 띄워주기
    @pyqtSlot(str)
    def recv_msg(self, msg):
        print("7")
        if '선생님 :' in msg:
            self.counsel_chat_box.append(msg)

    # 아이디, 비번 맞을 시 로그인 성공
    @pyqtSlot(str)
    def id_check_recv(self, msg):
        print("8", msg)
        if "OK, GO!" == msg:
            self.stackedWidget.setCurrentWidget(self.page1)

    # 아이디 중복 확인
    @pyqtSlot(str)
    def id_double_check(self, msg):
        if msg == "중복됨":
            self.id_check_label.setText("")
            print("중복됨")
            self.id_check_label.setText("중복된 아이디")
        elif msg == "사용가능한 아이디":
            self.id_check_label.setText("")
            print("사용 가능")
            self.id_check_label.setText("사용가능 아이디")
            self.signup_btn.setEnabled(True)
            self.make_id_line.setEnabled(False)

# 받기, 큐 쓰레드
class Receive(QThread):
    signal1 = pyqtSignal(str)   # 리시브
    signal2 = pyqtSignal(str)   # 로그인
    signal3 = pyqtSignal(str)   # 아이디 중복 확인
    print("9")

    def run(self):
        while True:
            print("10", sock)
            msg = sock.recv(1024)
            data = msg.decode()
            print("11", data)
            if not data:
                print("메세지 없어서 종료")
                break
            if "OK, GO!" == data:
                self.signal2.emit(f'OK, GO!')
            elif "중복됨" or "사용가능한 아이디" == data:
                if data == "중복됨":
                    self.signal3.emit(f'중복됨')
                elif data == "사용가능한 아이디":
                    self.signal3.emit("사용가능한 아이디")
            else:
                self.signal1.emit(f'선생님 : {data}')
        try:
            self.sock.close()
        except:
            print("소켓이 이미 꺼져있음")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    eduapp = Eduapp()
    eduapp.show()
    app.exec_()