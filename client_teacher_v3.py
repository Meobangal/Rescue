import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from socket import *

form_class = uic.loadUiType("teacher.ui")[0]
sock = socket(AF_INET, SOCK_STREAM)
sock.connect(('', 9036))
sock.send("teacher".encode())

class Window(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # 버튼 기능
        self.q_upload_btn.clicked.connect(self.move_q_upload_page)
        self.q_send_btn.clicked.connect(self.append_question)
        self.q_send_btn.clicked.connect(self.check)
        self.q_send_btn.setText("문제 출제")
        self.q_upload_btn.setText("문제출제하기")
        self.chat_btn.clicked.connect(self.move_chat_page)
        self.q_list_check.clicked.connect(self.show_question)
        self.q_list_check.setText("문제확인")
        self.chat_btn.setText("실시간 상담")
        self.qna_btn.clicked.connect(self.move_qna_page)
        self.qna_btn.clicked.connect(self.qna_view)
        self.qna_btn.setText("QnA 게시판")
        self.s_info_btn.clicked.connect(self.move_info_page)
        self.s_info_btn.setText("학생정보열람")
        self.upload_back_btn.clicked.connect(self.move_start_page)
        self.upload_back_btn.clicked.connect(self.clear)
        self.upload_back_btn.setText("뒤로가기")
        self.info_back_btn.clicked.connect(self.move_start_page)
        self.info_back_btn.clicked.connect(self.clear)
        self.info_back_btn.setText("뒤로가기")
        self.qna_back_btn.clicked.connect(self.move_start_page)
        self.qna_back_btn.clicked.connect(self.clear)
        self.qna_back_btn.setText("뒤로가기")
        self.chat_back_btn.clicked.connect(self.move_start_page)
        self.chat_back_btn.clicked.connect(self.clear)
        self.chat_back_btn.setText("뒤로가기")
        # 문제출제창 설정
        # 리스트위젯을 써서 현재 존재하는 모든 문제를 출력
        # 입력칸을 만들어서 문제를 입력할까?
        self.q_list.resize(900, 450)
        self.q_upload.resize(300, 40)
        self.a_upload.resize(300, 40)
        self.q_up_label.setText("문제")
        self.a_up_label.setText("답")
        self.rcv = Receive()
        self.rcv.chat.connect(self.recv_chat)
        self.rcv.chat2.connect(self.recv_chat2)
        self.rcv.chat3.connect(self.recv_chat3)
        self.rcv.chat4.connect(self.recv_chat4)
        self.rcv.start()


        # 학생정보열람창 설정
        # self.s_info_browser
        # 학생의 이름을 입력 했을 때 DB내의 그 학생의 값을 전부 출력할 부분
        # 학생이름을 그냥 입력 받을곳
        self.s_info_browser.resize(900, 450)
        self.s_info_inputname.resize(900, 50)
        self.s_info_inputname.returnPressed.connect(self.info_check)


        # Q&A창 설정
        self.qna_list.resize(1100, 500)
        self.qna_list.setColumnCount(3)
        header1 = self.qna_list.horizontalHeader()
        header1.resizeSection(0, 80)
        header2 = self.qna_list.horizontalHeader()
        header2.resizeSection(1, 300)
        header3 = self.qna_list.horizontalHeader()
        header3.resizeSection(2, 600)
        self.qna_list.currentCellChanged.connect(self.cellchanged_event)
        self.qna_check.clicked.connect(self.check)
        # 실시간 상담(체팅기능)
        self.chat_input.returnPressed.connect(self.send_chat)
        self.chat_window.resize(900, 450)
        self.chat_input.resize(900, 50)


    def move_start_page(self):
        self.stackedWidget.setCurrentWidget(self.start_page)

    def move_q_upload_page(self):
        self.stackedWidget.setCurrentWidget(self.q_upload_page)

    def move_info_page(self):
        self.stackedWidget.setCurrentWidget(self.s_info_page)

    def move_qna_page(self):
        self.stackedWidget.setCurrentWidget(self.qna_page)

    def move_chat_page(self):
        self.stackedWidget.setCurrentWidget(self.chat_page)

    # 서버에게 특수문자+문제 를 붙여서 메시지 전송하면 서버가 문제출제 저장요청으로 인식
    def show_question(self):
        question_check = "@문제확인"
        sock.send(question_check.encode())
        self.q_upload.clear()

    def append_question(self):
        # 라인에디터를 하나 더 만들어서 문제와 답안을 따로 입력하고 문제 제출 버튼으로 서버에 둘다 전송할것
        question = f"@문제출제 {self.q_upload.text()} {self.a_upload.text()}"
        print("문제를 출제함", question)
        sock.send(question.encode())
        self.q_upload.clear()
        self.a_upload.clear()

    # 서버에게 특수문자+학생이름 을 붙여서 메시지 전송하면 서버가 학생정보 요청으로 인식
    def info_check(self):
        s_name = "@학생이름"+self.s_info_inputname.text()
        sock.send(s_name.encode())
        # 학생 이름을 전송하면 서버에서 DB를 확인하여 해당하는 학생의 정보를 문자열로 보냄
        # 클라이언트에서 데이터를 잘 풀어서 정보를 출력할 것
        print("학생이름 보냄 :", s_name)
        self.s_info_inputname.clear()

    def qna_view(self):
        rows = []
        student = []
        question = []
        answer = []
        # 리시브 한 데이터를 특정 문자열로 구분해서 저장 분류
        # [(학생 이름만),(질문내용만),(답변만)]
        # 전부 갱신받으면서 답변부분은 답변대기 문자열로 받고, 답변 입력시 그 문자열을 전송할것
        QnA = [student, question, answer]
        print(QnA)
        for i in range(1):
            rows.append(QnA[:])
        i = 0
        for row in range(len(rows)):
            for j in range(len(question)):
                self.qna_list.setRowCount((i + 1))
                QnA_data = rows[row]
                self.qna_list.setItem(i, 0, QTableWidgetItem(str(QnA_data[0][j])))
                self.qna_list.setItem(i, 1, QTableWidgetItem(str(QnA_data[1][j])))
                self.qna_list.setItem(i, 2, QTableWidgetItem(str(QnA_data[2][j])))
                i += 1
                j += 1

    def cellchanged_event(self, row, col):
        qna_change = self.qna_list.item(row, col)
        print(f"{row}열 {col}행 변경 : ", qna_change)
        # 시그널 발생하고 그 셀의 값이 변경되면 그 문자열을 서버에 전송할 것
        # 뒤로가기 후 다시 qna들어오면 서버에서 다시 전송받아서 출력할 것

    def check(self):
        a = "@qna답변"
        sock.send(a.encode())
        print(a)
        print("qna 보냄")

    # 체팅은 그냥 클라이언트끼리니 서버는 구분없이 그냥 사이 중계만 하면 될 듯
    def send_chat(self):
        msg = self.chat_input.text()
        data = "@상담"+self.chat_input.text()
        sock.send(data.encode())
        self.chat_window.append(msg)
        self.chat_input.clear()

    def clear(self):
        self.chat_window.clear()
        self.q_list.clear()
        self.s_info_browser.clear()

    @pyqtSlot(str)
    def recv_chat(self, msg):
        print("상담 메세지 수신", msg)
        self.chat_window.append(msg)

    @pyqtSlot(str)
    def recv_chat2(self, msg):
        print("문제 메세지 수신", msg)
        self.q_list.addItem(msg)

    @pyqtSlot(str)
    def recv_chat3(self, msg):
        print("학생정보 메시지 수신", msg)
        self.s_info_browser.append(msg)

    @pyqtSlot(str)
    def recv_chat4(self, msg):
        print("Q&A 메시지 수신", msg)




class Receive(QThread):
    chat = pyqtSignal(str)
    chat2 = pyqtSignal(str)
    chat3 = pyqtSignal(str)
    chat4 = pyqtSignal(str)
    print("큐쓰레드 수신")

    def run(self):
        while True:
            try:
                msg = sock.recv(1024)
                print("msg.decode()", msg.decode())
                if not msg:
                    break
            except:
                print("리시브 오류")
                break
            else:
                data = msg.decode()
                print("큐쓰레드 메시지 수신됨 ", data)
                self.chat.emit(f"학생 : {data}")
                self.chat2.emit(data)
                self.chat3.emit(data)
                self.chat4.emit(data)
        print("q스레드 종료")
        # sock.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = Window()
    myWindow.show()
    app.exec_()