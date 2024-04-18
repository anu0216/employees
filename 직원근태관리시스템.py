import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pymysql
from pymysql import Error
import datetime

# 데이터베이스 연결 설정 함수
def create_db_connection():
    return pymysql.connect(host='localhost', user='root', password='2379', db='employees_attendance')

# 로그인 검증 함수
def verify_login(email, user_password):
    conn = create_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM Employees WHERE Email = %s AND Password = %s"
            cursor.execute(sql, (email, user_password))
            result = cursor.fetchone()
            return result is not None
    except Error as e:
        messagebox.showerror("Database Error", f"Error: {e}")
        return False
    finally:
        conn.close()
# 사이드바 메뉴 설정 함수
def setup_sidebar(parent):
    sidebar = ttk.Treeview(parent)
    
    # 사이드바 메뉴 항목 설정
    sidebar.heading("#0", text="기능 메뉴", anchor='w')
    
    # 계정 관리 메뉴 항목
    account_mgmt = sidebar.insert("", 1, text="계정 관리", open=True)
    sidebar.insert(account_mgmt, "end", text="계정 생성")
    sidebar.insert(account_mgmt, "end", text="계정 수정")
    sidebar.insert(account_mgmt, "end", text="계정 삭제")
    sidebar.insert(account_mgmt, "end", text="권한 관리")

    # 근태 데이터 관리 메뉴 항목
    attendance_mgmt = sidebar.insert("", 2, text="근태 데이터 관리", open=True)
    sidebar.insert(attendance_mgmt, "end", text="출퇴근 시간 기록")
    sidebar.insert(attendance_mgmt, "end", text="근무 시간 계산")

    # 휴가 및 출장 관리 메뉴 항목
    leave_trip_mgmt = sidebar.insert("", 3, text="휴가 및 출장 관리", open=True)
    sidebar.insert(leave_trip_mgmt, "end", text="휴가 요청")
    sidebar.insert(leave_trip_mgmt, "end", text="휴가 승인")
    sidebar.insert(leave_trip_mgmt, "end", text="출장 관리")

    # 보고서 및 통계 메뉴 항목
    report = sidebar.insert("", 4, text="보고서 및 통계", open=True)
    sidebar.insert(report, "end", text="근태 보고서 생성")
    sidebar.insert(report, "end", text="근무 시간 및 휴가 사용 통계")

    sidebar.pack(side='left', fill='y')

    # 메뉴 선택 이벤트 바인딩
    sidebar.bind("<<TreeviewSelect>>", on_select)

def show_attendance_report_frame(parent):
    clear_frame(parent)

    tk.Label(parent, text="기간 선택").grid(row=0, column=0)
    tk.Label(parent, text="부서 또는 개인 ID").grid(row=1, column=0)

    period_entry = tk.Entry(parent)
    target_entry = tk.Entry(parent)

    period_entry.grid(row=0, column=1)
    target_entry.grid(row=1, column=1)

    report_button = tk.Button(parent, text="근태 보고서 생성", command=lambda: generate_attendance_report(
        period_entry.get(),
        target_entry.get()
    ))
    report_button.grid(row=2, column=0, columnspan=2)

def show_work_hours_and_leave_statistics_frame(parent):
    clear_frame(parent)

    tk.Label(parent, text="기간 선택").grid(row=0, column=0)
    tk.Label(parent, text="부서 또는 개인 ID").grid(row=1, column=0)

    period_entry = tk.Entry(parent)
    target_entry = tk.Entry(parent)

    period_entry.grid(row=0, column=1)
    target_entry.grid(row=1, column=1)

    statistics_button = tk.Button(parent, text="근무 시간 및 휴가 통계", command=lambda: generate_work_hours_and_leave_statistics(
        period_entry.get(),
        target_entry.get()
    ))
    statistics_button.grid(row=2, column=0, columnspan=2)

def show_account_creation_frame(parent):
    clear_frame(parent)

    # 프레임 제목
    tk.Label(parent, text="계정 생성", font=('Arial', 16), bg='white').grid(row=0, columnspan=2, pady=10)

    # 입력 필드와 레이블
    labels_texts = ['이름', '이메일', '비밀번호', '부서', '직위']
    entries = []

    for i, text in enumerate(labels_texts, start=1):
        tk.Label(parent, text=text, font=('Arial', 14), bg='white').grid(row=i, column=0, sticky='e', padx=5, pady=2)
        entry = tk.Entry(parent, font=('Arial', 14), width=25)
        entry.grid(row=i, column=1, padx=5, pady=2)
        entries.append(entry)

    # 입력 필드 검증 함수
    def validate_inputs():
        # 예시: 이메일 형식 검증
        if not "@" in entries[1].get():
            messagebox.showwarning("입력 오류", "유효한 이메일 주소를 입력해주세요.")
            return False
        return True

    # 계정 생성 버튼 클릭 이벤트
    def on_create_account_clicked():
        if validate_inputs():
            name = entries[0].get()
            email = entries[1].get()
            password = entries[2].get()
            department = entries[3].get()
            position = entries[4].get()

        # 데이터베이스에 계정 생성 로직 호출
        success = create_account(name, email, password, department, position)
        if success:
            messagebox.showinfo("성공", "계정이 성공적으로 생성되었습니다.")

    # 계정 생성 버튼
    submit_button = tk.Button(parent, text="계정 생성", font=('Arial', 14), command=on_create_account_clicked)
    submit_button.grid(row=len(labels_texts) + 1, columnspan=2, pady=10)

def show_update_account_frame(parent):
    clear_frame(parent)

    # 프레임 제목
    tk.Label(parent, text="계정 수정", font=('Arial', 16), bg='white').grid(row=0, columnspan=2, pady=10)

    # 입력 필드와 레이블
    labels_texts = ['직원 ID', '이메일', '비밀번호', '부서', '직위']
    entries = {}

    for i, text in enumerate(labels_texts, start=1):
        tk.Label(parent, text=text, font=('Arial', 12), bg='white').grid(row=i, column=0, sticky='e', padx=5, pady=2)
        entry = tk.Entry(parent, font=('Arial', 12), width=25)
        entry.grid(row=i, column=1, padx=5, pady=2)
        entries[text] = entry

    # 입력 필드 검증 함수
    def validate_inputs():
        # 기본적인 입력 검증 예시
        if not "@" in entries['이메일'].get():
            messagebox.showwarning("입력 오류", "유효한 이메일 주소를 입력해주세요.")
            return False
        return True

    # 계정 수정 버튼 클릭 이벤트
    def on_update_account_clicked():
        if validate_inputs():
            # 데이터베이스에 계정 수정 로직 호출
            # update_account(...)
            success = update_account(
                entries['직원 ID'].get(),
                email=entries['이메일'].get(),
                password=entries['비밀번호'].get(),
                department=entries['부서'].get(),
                position=entries['직위'].get()
            )
            if success:
                messagebox.showinfo("성공", "계정 정보가 성공적으로 수정되었습니다.")
            else:
                messagebox.showerror("실패", "계정 정보 수정에 실패했습니다.")

    # 계정 수정 버튼
    update_button = tk.Button(parent, text="계정 수정", font=('Arial', 12), command=on_update_account_clicked)
    update_button.grid(row=len(labels_texts) + 1, columnspan=2, pady=10)

def show_delete_account_frame(parent):
    clear_frame(parent)

    # 프레임 제목
    tk.Label(parent, text="계정 삭제", font=('Arial', 16), bg='white').grid(row=0, columnspan=2, pady=10)

    # 입력 필드와 레이블
    tk.Label(parent, text="직원 ID", font=('Arial', 12), bg='white').grid(row=1, column=0, sticky='e', padx=5, pady=2)
    employee_id_entry = tk.Entry(parent, font=('Arial', 12), width=25)
    employee_id_entry.grid(row=1, column=1, padx=5, pady=2)

    # 입력 필드 검증 함수
    def validate_inputs():
        # 기본적인 입력 검증 예시, 여기서는 입력 여부만 확인
        if not employee_id_entry.get().strip():
            messagebox.showwarning("입력 오류", "직원 ID를 입력해주세요.")
            return False
        return True

    # 계정 삭제 버튼 클릭 이벤트
    def on_delete_account_clicked():
        if validate_inputs():
            # 데이터베이스에 계정 삭제 로직 호출
            success = delete_account(employee_id_entry.get())
            if success:
                messagebox.showinfo("성공", "계정이 성공적으로 삭제되었습니다.")
                employee_id_entry.delete(0, tk.END)  # 입력 필드 초기화
            else:
                messagebox.showerror("실패", "계정 삭제에 실패했습니다. 직원 ID를 확인해주세요.")

    # 계정 삭제 버튼
    delete_button = tk.Button(parent, text="계정 삭제", font=('Arial', 12), command=on_delete_account_clicked)
    delete_button.grid(row=2, columnspan=2, pady=10)

def show_manage_role_frame(parent):
    clear_frame(parent)

    # 프레임 제목
    tk.Label(parent, text="권한 관리", font=('Arial', 16), bg='white').grid(row=0, columnspan=2, pady=10)

    # 입력 필드와 레이블
    tk.Label(parent, text="직원 ID", font=('Arial', 12), bg='white').grid(row=1, column=0, sticky='e', padx=5, pady=2)
    tk.Label(parent, text="새로운 권한", font=('Arial', 12), bg='white').grid(row=2, column=0, sticky='e', padx=5, pady=2)
    
    employee_id_entry = tk.Entry(parent, font=('Arial', 12), width=25)
    role_entry = tk.Entry(parent, font=('Arial', 12), width=25)
    
    employee_id_entry.grid(row=1, column=1, padx=5, pady=2)
    role_entry.grid(row=2, column=1, padx=5, pady=2)

    # 입력 필드 검증 함수
    def validate_inputs():
        if not employee_id_entry.get().strip():
            messagebox.showwarning("입력 오류", "직원 ID를 입력해주세요.")
            return False
        # 권한 값의 예시적인 검증: 여기서는 값이 있는지만 확인합니다.
        if not role_entry.get().strip():
            messagebox.showwarning("입력 오류", "새로운 권한을 입력해주세요.")
            return False
        return True

    # 권한 수정 버튼 클릭 이벤트
    def on_update_role_clicked():
        if validate_inputs():
            success = update_role(
                employee_id_entry.get(),
                role_entry.get()
            )
            if success:
                messagebox.showinfo("성공", "직원의 권한이 성공적으로 업데이트되었습니다.")
                employee_id_entry.delete(0, tk.END)  # 입력 필드 초기화
                role_entry.delete(0, tk.END)        # 입력 필드 초기화
            else:
                messagebox.showerror("실패", "직원의 권한 업데이트에 실패했습니다.")

    # 권한 수정 버튼
    update_role_button = tk.Button(parent, text="권한 업데이트", font=('Arial', 12), command=on_update_role_clicked)
    update_role_button.grid(row=3, columnspan=2, pady=10)

def show_approve_leave_frame(parent):
    clear_frame(parent)
    listbox_requests = tk.Listbox(parent, width=60, height=15)
    listbox_requests.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    requests = load_leave_requests()
    for req in requests:
        display_text = f"Request ID: {req[0]}, EmployeeID: {req[1]}, Dates: {req[2]} to {req[3]}, Reason: {req[4]}"
        listbox_requests.insert(tk.END, display_text)

    def approve_leave():
        selected = listbox_requests.curselection()
        if not selected:
            messagebox.showinfo("Info", "Please select a leave request to approve.")
            return
        request_id = requests[selected[0]][0]
        if update_leave_status(request_id, "Approved"):
            messagebox.showinfo("Success", "Leave request approved.")
            listbox_requests.delete(selected[0])

    def reject_leave():
        selected = listbox_requests.curselection()
        if not selected:
            messagebox.showinfo("Info", "Please select a leave request to reject.")
            return
        request_id = requests[selected[0]][0]
        if update_leave_status(request_id, "Rejected"):
            messagebox.showinfo("Success", "Leave request rejected.")
            listbox_requests.delete(selected[0])

    approve_button = tk.Button(parent, text="승인", command=approve_leave)
    approve_button.grid(row=2, column=0, pady=5)

    reject_button = tk.Button(parent, text="거절", command=reject_leave)
    reject_button.grid(row=2, column=1, pady=5)

def show_record_attendance_frame(parent):
    clear_frame(parent)

    # 프레임 제목
    tk.Label(parent, text="출퇴근 시간 기록", font=('Arial', 16), bg='white').grid(row=0, columnspan=2, pady=10)

    # 입력 필드와 레이블
    tk.Label(parent, text="직원 ID", font=('Arial', 12), bg='white').grid(row=1, column=0, sticky='e', padx=5, pady=2)
    tk.Label(parent, text="날짜 (YYYY-MM-DD)", font=('Arial', 12), bg='white').grid(row=2, column=0, sticky='e', padx=5, pady=2)
    tk.Label(parent, text="출근 시간 (HH:MM)", font=('Arial', 12), bg='white').grid(row=3, column=0, sticky='e', padx=5, pady=2)
    tk.Label(parent, text="퇴근 시간 (HH:MM)", font=('Arial', 12), bg='white').grid(row=4, column=0, sticky='e', padx=5, pady=2)

    employee_id_entry = tk.Entry(parent, font=('Arial', 12), width=25)
    date_entry = tk.Entry(parent, font=('Arial', 12), width=25)
    time_in_entry = tk.Entry(parent, font=('Arial', 12), width=25)
    time_out_entry = tk.Entry(parent, font=('Arial', 12), width=25)
    
    employee_id_entry.grid(row=1, column=1, padx=5, pady=2)
    date_entry.grid(row=2, column=1, padx=5, pady=2)
    time_in_entry.grid(row=3, column=1, padx=5, pady=2)
    time_out_entry.grid(row=4, column=1, padx=5, pady=2)

    # 입력 필드 검증 함수
    def validate_inputs():
        try:
            datetime.datetime.strptime(date_entry.get(), '%Y-%m-%d')
            datetime.datetime.strptime(time_in_entry.get(), '%H:%M')
            datetime.datetime.strptime(time_out_entry.get(), '%H:%M')
        except ValueError:
            messagebox.showwarning("입력 오류", "날짜 또는 시간의 형식이 잘못되었습니다.")
            return False
        return True

    # 출퇴근 시간 기록 버튼 클릭 이벤트
    def on_record_attendance_clicked():
        if validate_inputs():
            # 데이터베이스에 출퇴근 시간 기록 로직 호출
            success = record_attendance(
                employee_id_entry.get(),
                f"{date_entry.get()} {time_in_entry.get()}:00",
                f"{date_entry.get()} {time_out_entry.get()}:00"
            )
            if success:
                messagebox.showinfo("성공", "출퇴근 시간이 성공적으로 기록되었습니다.")
                employee_id_entry.delete(0, tk.END)
                date_entry.delete(0, tk.END)
                time_in_entry.delete(0, tk.END)
                time_out_entry.delete(0, tk.END)
            else:
                messagebox.showerror("실패", "시간 기록에 실패했습니다.")

    # 출퇴근 시간 기록 버튼
    record_button = tk.Button(parent, text="시간 기록", font=('Arial', 12), command=on_record_attendance_clicked)
    record_button.grid(row=5, columnspan=2, pady=10)

def show_calculate_work_hours_frame(parent):
    clear_frame(parent)

    # 프레임 제목
    tk.Label(parent, text="근무 시간 계산", font=('Arial', 16), bg='white').grid(row=0, columnspan=2, pady=10)

    # 입력 필드와 레이블
    tk.Label(parent, text="직원 ID", font=('Arial', 12), bg='white').grid(row=1, column=0, sticky='e', padx=5, pady=2)
    tk.Label(parent, text="시작 날짜 (YYYY-MM-DD)", font=('Arial', 12), bg='white').grid(row=2, column=0, sticky='e', padx=5, pady=2)
    tk.Label(parent, text="종료 날짜 (YYYY-MM-DD)", font=('Arial', 12), bg='white').grid(row=3, column=0, sticky='e', padx=5, pady=2)

    employee_id_entry = tk.Entry(parent, font=('Arial', 12), width=25)
    start_date_entry = tk.Entry(parent, font=('Arial', 12), width=25)
    end_date_entry = tk.Entry(parent, font=('Arial', 12), width=25)
    
    employee_id_entry.grid(row=1, column=1, padx=5, pady=2)
    start_date_entry.grid(row=2, column=1, padx=5, pady=2)
    end_date_entry.grid(row=3, column=1, padx=5, pady=2)

    # 입력 필드 검증 함수
    def validate_inputs():
        try:
            start = datetime.datetime.strptime(start_date_entry.get(), '%Y-%m-%d')
            end = datetime.datetime.strptime(end_date_entry.get(), '%Y-%m-%d')
            if start > end:
                raise ValueError("시작 날짜가 종료 날짜보다 늦을 수 없습니다.")
        except ValueError as e:
            messagebox.showwarning("입력 오류", str(e))
            return False
        return True

    # 근무 시간 계산 버튼 클릭 이벤트
    def on_calculate_work_hours_clicked():
        if validate_inputs():
            # 데이터베이스에서 근무 시간 계산 로직 호출
            total_hours = calculate_work_hours(
                employee_id_entry.get(),
                start_date_entry.get(),
                end_date_entry.get()
            )
            if total_hours is not None:
                messagebox.showinfo("성공", f"총 근무 시간: {total_hours}시간")
            else:
                messagebox.showerror("실패", "근무 시간 계산에 실패했습니다.")

    # 근무 시간 계산 버튼
    calculate_button = tk.Button(parent, text="근무 시간 계산", font=('Arial', 12), command=on_calculate_work_hours_clicked)
    calculate_button.grid(row=4, columnspan=2, pady=10)

def show_request_leave_frame(parent):
    clear_frame(parent)

    # 프레임 제목
    tk.Label(parent, text="휴가 요청", font=('Arial', 16), bg='white').grid(row=0, columnspan=2, pady=10)

    # 입력 필드와 레이블
    tk.Label(parent, text="직원 ID", font=('Arial', 12), bg='white').grid(row=1, column=0, sticky='e', padx=5, pady=2)
    tk.Label(parent, text="휴가 시작 날짜", font=('Arial', 12), bg='white').grid(row=2, column=0, sticky='e', padx=5, pady=2)
    tk.Label(parent, text="휴가 종료 날짜", font=('Arial', 12), bg='white').grid(row=3, column=0, sticky='e', padx=5, pady=2)
    tk.Label(parent, text="휴가 사유", font=('Arial', 12), bg='white').grid(row=4, column=0, sticky='e', padx=5, pady=2)

    employee_id_entry = tk.Entry(parent, font=('Arial', 12), width=25)
    start_date_entry = tk.Entry(parent, font=('Arial', 12), width=25)
    end_date_entry = tk.Entry(parent, font=('Arial', 12), width=25)
    reason_entry = tk.Entry(parent, font=('Arial', 12), width=25)
    
    employee_id_entry.grid(row=1, column=1, padx=5, pady=2)
    start_date_entry.grid(row=2, column=1, padx=5, pady=2)
    end_date_entry.grid(row=3, column=1, padx=5, pady=2)
    reason_entry.grid(row=4, column=1, padx=5, pady=2)

    # 입력 필드 검증 함수
    def validate_inputs():
        # 검증 로직을 여기에 추가
        if not employee_id_entry.get().strip():
            messagebox.showwarning("입력 오류", "직원 ID를 입력해주세요.")
            return False
        # 날짜 형식 및 논리적 일관성 검증 등 추가 검증 로직 필요
        return True

    # 휴가 요청 버튼 클릭 이벤트
    def on_request_leave_clicked():
        if validate_inputs():
            success = request_leave(
                employee_id_entry.get(),
                start_date_entry.get(),
                end_date_entry.get(),
                reason_entry.get()
            )
            if success:
                messagebox.showinfo("성공", "휴가 요청이 성공적으로 등록되었습니다.")
                # 입력 필드 초기화
                employee_id_entry.delete(0, tk.END)
                start_date_entry.delete(0, tk.END)
                end_date_entry.delete(0, tk.END)
                reason_entry.delete(0, tk.END)
            else:
                messagebox.showerror("실패", "휴가 요청에 실패했습니다.")

    # 휴가 요청 버튼
    request_button = tk.Button(parent, text="휴가 요청", font=('Arial', 12), command=on_request_leave_clicked)
    request_button.grid(row=5, columnspan=2, pady=10)

def show_manage_business_trip_frame(parent):
    clear_frame(parent)
    
    tk.Label(parent, text="직원 ID").grid(row=0, column=0)
    tk.Label(parent, text="출장 시작 날짜").grid(row=1, column=0)
    tk.Label(parent, text="출장 종료 날짜").grid(row=2, column=0)
    tk.Label(parent, text="목적지").grid(row=3, column=0)
    tk.Label(parent, text="출장 사유").grid(row=4, column=0)
    tk.Label(parent, text="예산").grid(row=5, column=0)

    employee_id_entry = tk.Entry(parent)
    start_date_entry = tk.Entry(parent)
    end_date_entry = tk.Entry(parent)
    destination_entry = tk.Entry(parent)
    purpose_entry = tk.Entry(parent)
    budget_entry = tk.Entry(parent)

    employee_id_entry.grid(row=0, column=1)
    start_date_entry.grid(row=1, column=1)
    end_date_entry.grid(row=2, column=1)
    destination_entry.grid(row=3, column=1)
    purpose_entry.grid(row=4, column=1)
    budget_entry.grid(row=5, column=1)

    manage_button = tk.Button(parent, text="출장 관리", command=lambda: manage_business_trip(
        employee_id_entry.get(),
        start_date_entry.get(),
        end_date_entry.get(),
        destination_entry.get(),
        purpose_entry.get(),
        budget_entry.get()
    ))
    manage_button.grid(row=6, column=0, columnspan=2)

def record_attendance(employee_id, time_in, time_out):
    # 날짜와 시간 형식을 'YYYY-MM-DD HH:MM:SS'로 가정합니다.
    conn = create_db_connection()
    try:
        with conn.cursor() as cursor:
            # INSERT 쿼리를 사용하여 출퇴근 시간 기록
            sql = """
            INSERT INTO AttendanceRecords (EmployeeID, TimeIn, TimeOut) 
            VALUES (%s, STR_TO_DATE(%s, '%Y-%m-%d %H:%i:%s'), STR_TO_DATE(%s, '%Y-%m-%d %H:%i:%s'))
            """
            cursor.execute(sql, (employee_id, time_in, time_out))
            conn.commit()
            return True  # 기록에 성공한 경우
    except Error as e:
        messagebox.showerror("Database Error", f"Error: {e}")
        return False  # 기록에 실패한 경우
    finally:
        conn.close()

def calculate_work_hours(employee_id, start_date, end_date):
    conn = create_db_connection()
    total_work_hours = 0  # 총 근무 시간을 저장할 변수 초기화
    try:
        with conn.cursor() as cursor:
            # 시작 날짜와 종료 날짜 사이의 출퇴근 기록을 조회합니다.
            sql = """
            SELECT TimeIn, TimeOut FROM AttendanceRecords
            WHERE EmployeeID = %s AND Date BETWEEN %s AND %s
            """
            cursor.execute(sql, (employee_id, start_date, end_date))
            rows = cursor.fetchall()

            for row in rows:
                # 출근 시간과 퇴근 시간을 파싱합니다.
                time_in = row['TimeIn']
                time_out = row['TimeOut']
                if time_in and time_out:
                    # 근무 시간(초 단위)을 계산하고, 총 근무 시간에 더합니다.
                    work_duration = (time_out - time_in).total_seconds()
                    total_work_hours += work_duration / 3600  # 시간 단위로 변환

            return total_work_hours
    except Error as e:
        messagebox.showerror("Database Error", f"Error: {e}")
        return None  # 오류 발생 시 None 반환
    finally:
        conn.close()

def request_leave(employee_id, start_date, end_date, reason):
    conn = create_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO leave_requests (EmployeeID, StartDate, EndDate, Reason, Status) 
            VALUES (%s, %s, %s, %s, 'Pending')
            """
            cursor.execute(sql, (employee_id, start_date, end_date, reason))
        conn.commit()
        if cursor.rowcount > 0:  # 성공적으로 데이터가 삽입됨
                return True
        else:
                return False
    except Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()

def load_leave_requests():
    conn = create_db_connection()
    leave_requests = []
    try:
        with conn.cursor() as cursor:
            sql = "SELECT RequestID, EmployeeID, StartDate, EndDate, Reason FROM leave_requests WHERE Status = 'Pending'"
            cursor.execute(sql)
            leave_requests = cursor.fetchall()
    except Error as e:
        messagebox.showerror("Database Error", f"Error: {e}")
    finally:
        conn.close()
    return leave_requests

def update_leave_status(request_id, status):
    
    conn = create_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "UPDATE Leave_Requests SET Status = %s WHERE RequestID = %s"
            cursor.execute(sql, (status, request_id))
            conn.commit()
            return cursor.rowcount > 0  # True if the status was updated, False otherwise
    except Error as e:
        messagebox.showerror("Database Error", f"Error: {e}")
        return False
    finally:
        conn.close()

def manage_business_trip(employee_id, start_date, end_date, destination, purpose, budget):
    conn = create_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO BusinessTrips (EmployeeID, StartDate, EndDate, Destination, Purpose, Budget, Status) 
            VALUES (%s, %s, %s, %s, %s, %s, 'Pending')
            """
            cursor.execute(sql, (employee_id, start_date, end_date, destination, purpose, budget))
        conn.commit()
    except Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()

def create_account(name, email, password, department, position):
    conn = create_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO Employees (Name, Email, Password, Department, Position) 
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (name, email, password, department, position))
        conn.commit()
        return True
    except pymysql.IntegrityError as e:
        messagebox.showerror("Error", "이메일이 이미 사용 중입니다.")
        return False
    except Error as e:
        messagebox.showerror("Database Error", f"Error: {e}")
        return False
    finally:
        conn.close()

def update_account(employee_id, email=None, password=None, department=None, position=None):
    conn = create_db_connection()
    try:
        with conn.cursor() as cursor:
            # 동적으로 업데이트할 필드와 값 목록을 생성합니다.
            updates = []
            params = []
            
            if email:
                updates.append("Email = %s")
                params.append(email)
            if password:
                updates.append("Password = %s")
                params.append(password)
            if department:
                updates.append("Department = %s")
                params.append(department)
            if position:
                updates.append("Position = %s")
                params.append(position)
            
            # 쿼리가 비어있지 않은 경우에만 실행합니다.
            if updates:
                params.append(employee_id)  # WHERE 조건에 사용될 EmployeeID
                sql = "UPDATE Employees SET " + ", ".join(updates) + " WHERE EmployeeID = %s"
                cursor.execute(sql, params)
                conn.commit()
                return True
            else:
                # 수정할 내용이 없을 경우
                return False
    except Error as e:
        messagebox.showerror("Database Error", f"Error: {e}")
        return False
    finally:
        conn.close()

def delete_account(employee_id):
    
    conn = create_db_connection()
    try:
        with conn.cursor() as cursor:
            # 삭제할 직원 ID가 유효한지 먼저 확인
            sql_check = "SELECT * FROM Employees WHERE EmployeeID = %s"
            cursor.execute(sql_check, (employee_id,))
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("실패", "해당하는 직원 ID가 존재하지 않습니다.")
                return False
            
            # 직원 ID에 해당하는 계정을 삭제
            sql_delete = "DELETE FROM Employees WHERE EmployeeID = %s"
            cursor.execute(sql_delete, (employee_id,))
            conn.commit()
            
            if cursor.rowcount == 0:  # 삭제된 레코드가 없는 경우
                messagebox.showerror("실패", "계정 삭제에 실패했습니다.")
                return False
            else:
                return True  # 성공적으로 삭제된 경우
    except Error as e:
        messagebox.showerror("Database Error", f"Error: {e}")
        return False
    finally:
        conn.close()

def update_role(employee_id, new_role):
    conn = create_db_connection()
    try:
        with conn.cursor() as cursor:
            # 해당 직원의 권한을 업데이트합니다.
            sql = "UPDATE Employees SET Role = %s WHERE EmployeeID = %s"
            cursor.execute(sql, (new_role, employee_id))
            conn.commit()
            
            if cursor.rowcount > 0:  # 실제로 업데이트된 레코드가 있는 경우
                return True
            else:  # 업데이트된 레코드가 없는 경우(잘못된 직원 ID 등)
                return False
    except Error as e:
        # 데이터베이스 오류가 발생한 경우
        messagebox.showerror("Database Error", f"Error: {e}")
        return False
    finally:
        conn.close()

def generate_attendance_report(start_date, end_date, employee_id=None, department=None):
    conn = create_db_connection()
    try:
        with conn.cursor() as cursor:
            if employee_id:
                sql = """
                SELECT EmployeeID, COUNT(*) AS PresentDays,
                SUM(CASE WHEN Status='Absent' THEN 1 ELSE 0 END) AS AbsentDays,
                SUM(CASE WHEN Status='Late' THEN 1 ELSE 0 END) AS LateDays
                FROM AttendanceRecords
                WHERE EmployeeID=%s AND Date BETWEEN %s AND %s
                GROUP BY EmployeeID
                """
                cursor.execute(sql, (employee_id, start_date, end_date))
            elif department:
                sql = """
                SELECT Department, COUNT(*) AS PresentDays,
                SUM(CASE WHEN Status='Absent' THEN 1 ELSE 0 END) AS AbsentDays,
                SUM(CASE WHEN Status='Late' THEN 1 ELSE 0 END) AS LateDays
                FROM AttendanceRecords
                JOIN Employees ON AttendanceRecords.EmployeeID = Employees.EmployeeID
                WHERE Department=%s AND Date BETWEEN %s AND %s
                GROUP BY Department
                """
                cursor.execute(sql, (department, start_date, end_date))
            else:
                return None
            report = cursor.fetchall()
            return report
    except Error as e:
        print(f"Error: {e}")
        return None
    finally:
        conn.close()

def generate_work_hours_and_leave_statistics(start_date, end_date, employee_id=None, department=None):
    conn = create_db_connection()
    work_hours = None
    leave_statistics = None
    try:
        with conn.cursor() as cursor:
            # 근무 시간 집계
            if employee_id:
                sql_work_hours = """
                SELECT EmployeeID, 
                SUM(TIMESTAMPDIFF(HOUR, TimeIn, TimeOut)) AS TotalWorkHours
                FROM AttendanceRecords
                WHERE EmployeeID=%s AND Date BETWEEN %s AND %s
                GROUP BY EmployeeID
                """
                cursor.execute(sql_work_hours, (employee_id, start_date, end_date))
            elif department:
                sql_work_hours = """
                SELECT Department, 
                SUM(TIMESTAMPDIFF(HOUR, TimeIn, TimeOut)) AS TotalWorkHours
                FROM AttendanceRecords
                JOIN Employees ON AttendanceRecords.EmployeeID = Employees.EmployeeID
                WHERE Department=%s AND Date BETWEEN %s AND %s
                GROUP BY Department
                """
                cursor.execute(sql_work_hours, (department, start_date, end_date))
            work_hours = cursor.fetchall()

            # 휴가 사용량 집계
            if employee_id:
                sql_leave = """
                SELECT EmployeeID, COUNT(*) AS LeaveDays
                FROM Leave_Requests
                WHERE EmployeeID=%s AND StartDate >= %s AND EndDate <= %s AND Status = 'Approved'
                GROUP BY EmployeeID
                """
                cursor.execute(sql_leave, (employee_id, start_date, end_date))
            elif department:
                sql_leave = """
                SELECT Department, COUNT(*) AS LeaveDays
                FROM Leave_Requests
                JOIN Employees ON Leave_Requests.EmployeeID = Employees.EmployeeID
                WHERE Department=%s AND StartDate >= %s AND EndDate <= %s AND Status = 'Approved'
                GROUP BY Department
                """
                cursor.execute(sql_leave, (department, start_date, end_date))
            leave_statistics = cursor.fetchall()

    except Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()
    
    return work_hours, leave_statistics

def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def on_select(event):
    selected_item = event.widget.selection()[0]  # 선택한 메뉴 항목의 ID
    menu_text = event.widget.item(selected_item, 'text')
    global content_area
    
    # 선택한 메뉴에 따른 함수 호출
    if menu_text == "계정 생성":
        show_account_creation_frame(content_area)
    elif menu_text == "계정 수정":
        show_update_account_frame(content_area)
    elif menu_text == "계정 삭제":
        show_delete_account_frame(content_area)
    elif menu_text == "권한 관리":
        show_manage_role_frame(content_area)
    elif menu_text == "출퇴근 시간 기록":
        show_record_attendance_frame(content_area)
    elif menu_text == "근무 시간 계산":
        show_calculate_work_hours_frame(content_area)
    elif menu_text == "휴가 요청":
        show_request_leave_frame(content_area)
    elif menu_text == "휴가 승인":
        show_approve_leave_frame(content_area)
    elif menu_text == "출장 관리":
        show_manage_business_trip_frame(content_area)
    elif menu_text == "근태 보고서 생성":
        show_attendance_report_frame(content_area)
    elif menu_text == "근무 시간 및 휴가 사용 통계":
        show_work_hours_and_leave_statistics_frame(content_area)

# 로그인 성공 시 메인 화면을 보여주는 함수
def show_main_window():
    root.withdraw()  # 로그인 창 숨기기
    setup_main_window()  # 메인 화면의 내용 구성 함수 호출

def create_content_area(parent):
    content_area = tk.Frame(parent, bg='white')
    

    # 상단 정보 바
    info_bar = tk.Frame(content_area, bg='lightgray', height=50)
    info_bar.pack(side='top', fill='x')

    # 메인 영역 - 예를 들어 여기에는 사용자의 세부 정보나 달력 등이 표시될 수 있습니다.
    main_area = tk.Frame(content_area, bg='white')
    main_area.pack(expand=True, fill='both')

    # 상단 정보 바에 정보 표시 - 예를 들어 사용자 이름 또는 부서명
    tk.Label(info_bar, text="사용자 이름: ", bg='lightgray').pack(side='left', padx=10)
    tk.Label(info_bar, text="부서명: ", bg='lightgray').pack(side='left')

    # 예시로 달력을 메인 영역에 추가 - 실제 달력 위젯을 사용하려면 추가적인 구현이 필요합니다.
    tk.Label(main_area, text="여기에 달력이나 다른 내용을 표시합니다.", bg='white').pack()

    # 하단 상태 바
    status_bar = tk.Frame(content_area, bg='lightgray', height=30)
    status_bar.pack(side='bottom', fill='x')

    # 상태 바에 정보 표시 - 예를 들어 현재 상태 메시지
    tk.Label(status_bar, text="현재 상태: 준비", bg='lightgray').pack(side='left', padx=10)

    content_area.pack(expand=True, fill='both', padx=1, pady=1)  # 패딩으로 레이아웃 조정
    return content_area

def setup_main_window():
    # 메인 화면 창 생성
    global content_area
    main_window = tk.Toplevel()
    main_window.title('메인 화면')
    main_window.geometry('1024x768')

    setup_sidebar(main_window)

    # # 왼쪽 사이드바
    # sidebar = tk.Frame(main_window, width=200, bg='#333333')
    # sidebar.pack(side='left', fill='y', padx=(0, 1))

    # 메인 콘텐츠 영역
    content_area = create_content_area(main_window)

    # 메인 화면이 닫힐 때 로그인 창도 같이 종료되도록 설정
    main_window.protocol("WM_DELETE_WINDOW", on_close_main_window)

def on_close_main_window():
    root.destroy()  # 로그인 창과 메인 화면 창 모두 닫기

# 로그인 함수
def login():
    email = entry_user.get()
    user_password = entry_pass.get()
    if verify_login(email, user_password):
        show_main_window()  # 메인 화면 표시
    else:
        messagebox.showerror("로그인 실패", "잘못된 이메일 또는 비밀번호입니다.")

# 사용자 입력 필드 초기화 함수
def clear_placeholder(event):
    if event.widget.get() in ('USER_Email', 'PASSWORD'):
        event.widget.delete(0, tk.END)
        if event.widget == entry_pass:
            entry_pass.config(show='*')  # 비밀번호 숨김 처리 활성화

# Tkinter 창 생성 및 설정
root = tk.Tk()
root.title('인사관리시스템 로그인')
root.geometry('400x300+500+200')
root.configure(bg='white')

# 로그인 헤더 레이블
header_label = tk.Label(root, text='인사관리시스템\nLOG-IN', font=('Sans-serif', 20, 'bold'), bg='white', fg='orange')
header_label.pack(pady=30)

# 사용자 ID 입력 필드
entry_user = ttk.Entry(root, width=20, font=('Sans-serif', 14))
entry_user.pack(ipady=7)
entry_user.insert(0, 'USER_ID')
entry_user.bind("<FocusIn>", clear_placeholder)

# 사용자 비밀번호 입력 필드
entry_pass = ttk.Entry(root, width=20, font=('Sans-serif', 14), show='*')
entry_pass.pack(ipady=7, pady=10)
entry_pass.insert(0, 'PASSWORD')
entry_pass.bind("<FocusIn>", clear_placeholder)

# 로그인 버튼
login_button = tk.Button(root, text='로그인', bg='#0052cc', fg='white', font=('Sans-serif', 14), command=login)
login_button.pack(ipady=5, pady=10, fill='x', expand=True)

root.mainloop()
