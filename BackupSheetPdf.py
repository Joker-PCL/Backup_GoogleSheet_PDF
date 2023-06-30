import os
import os.path
import io
import json
from ftplib import FTP

import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request

from time import sleep

# เก็บ log file ** debug, info, warning, error, critical
import logging
logging.basicConfig(filename='Backup.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S')

# กำหนด path ของ credentials.json ที่คุณดาวน์โหลดมา
SCOPES = ['https://www.googleapis.com/auth/drive']
CREDENTIALS_DIR = 'credentials.json'
TOKEN_DIR = 'token.pickle'

# กำหนด path ของโฟล์เดอร์ที่ต้องการบันทึกไฟล์ PDF
setting_json = "setting.json"
pdf_folder = 'D:\Backup_GGSH_PDF_Linux\PDF'
success_list = 'BackupSuccess.txt'
failed_list = 'BackupFailed.txt'

# ข้อมูลการเชื่อมต่อ FTP
ftp_host = 'pclerp.ddns.net'
ftp_user = 'PD'
ftp_passwd = 'Pd7894560'

# ftp ไดเรกทอรี
ftp_dir = '/BackupPD/PDF'

def main():
    while True:
        print("Connecting...")
        try:
            creds = None
            if os.path.exists(TOKEN_DIR):
                with open(TOKEN_DIR, 'rb') as token:
                    creds = pickle.load(token)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        CREDENTIALS_DIR, SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open(TOKEN_DIR, 'wb') as token:
                    pickle.dump(creds, token)

            # สร้าง Google Drive API service
            service = build('drive', 'v3', credentials=creds)

            with open(setting_json) as json_file:
                # แปลง JSON ไฟล์ เป็น Python Dict
                prog_dict = json.load(json_file)

            for data in prog_dict:
                folder_id = data["folder_id"]

                downloadFile(service, folder_id, pdf_folder)
            
            upload_files_ftp(pdf_folder, ftp_dir)
            print("<<<<<< Data backup completed successfully >>>>>>>")
            print("The program will check and backup the data again in")    
            
            # ตั้งเวลาในการรันรอบโปรแกรม
            breaktime(1, 0, 0)

        except Exception as e:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("<<ERROR>>",e)
            # print("เกิดข้อผิดพลาดระหว่างดาวน์โหลด กำลังเชื่อมต่อไหม่....")
            print("An error occurred during the download. Reconnecting...")
            breaktime(0, 0, 30) 

def backupList(filename, listname, type="add/remove"):
    # อ่านไฟล์ข้อมูล
    with open(filename, 'r') as file:
        data = file.readlines()

    data = [line.strip() for line in data]

    # ค้นหาและลบข้อมูลที่ตรงกันออก
    data = [line for line in data if line != listname]

    # หากไม่พบข้อมูลที่ตรงกัน ให้เพิ่มข้อมูล
    if(type == "add"):
        if listname not in data:
            data.append(listname)

    # เขียนข้อมูลกลับลงในไฟล์
    with open(filename, 'w') as file:
        file.write('\n'.join(data))

def breaktime(Hours=5, Min=0, Sec=0):
    for i in range((Hours*3600)+(Min*60)+Sec, 0, -1):
        hours = i // 3600  # หารเพื่อหาจำนวนชั่วโมง
        minutes = (i % 3600) // 60  # หารเพื่อหาจำนวนนาที
        seconds = i % 60  # หารเพื่อหาจำนวนวินาที

        # print(f"{hours} ชั่วโมง {minutes} นาที {seconds} วินาที", end='\r')
        time_str = f"Timer: {str(hours).zfill(2)}:{str(minutes).zfill(2)}:{str(seconds).zfill(2)}"  # แปลงเป็น string และใช้ zfill() เพื่อเติมศูนย์ด้านหน้าตัวเลข
        print(time_str, end='\r')
        sleep(1)

def downloadFile(service, folder_id, folder_name):
    results = [] # เก็บรายการไฟล์
    page_token = None

    # ดึงรายการไฟล์ทั้งหมดที่อยู่ในโฟล์เดอร์
    while True:
        query = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.spreadsheet'"
        response = service.files().list(
            q=query,
            fields="nextPageToken, files(id, name)",
            pageToken=page_token
        ).execute()

        items = response.get('files', [])
        results.extend(items)
        page_token = response.get('nextPageToken')

        if not page_token:
            break
    
    # วนลูปเพื่อดาวน์โหลดไฟล์และบันทึกเป็นไฟล์ PDF
    for item in results:
        file_id = item['id']
        file_name = item['name']
        file_name = file_name.replace("/", "-").upper()

        try:
            output_path = os.path.join(folder_name, f"{file_name}.pdf")
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(
                file,
                service.files()
                .export_media(
                    fileId=file_id,
                    mimeType='application/pdf'
                )
            )

            done = False

            # ตรวจสอบว่าตำแหน่งและชื่อไฟล์ปลายทางนั้นมีอยู่จริง
            if not os.path.exists(output_path):
                # ดาวน์โหลดไฟล์และบันทึกเป็นไฟล์ PDF
                while done is False:
                    status, done = downloader.next_chunk()
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(f"Download {file_name} {int(status.progress() * 100)}%")
                    print(f"File saved to {output_path}", end='\n')
                # เขียนข้อมูลในไฟล์ PDF
                file.seek(0)

                # สามารถใช้โค้ดต่อไปนี้เพื่อเปิดไฟล์ใหม่ในโหมด binary และทำการบันทึกไฟล์
                with open(output_path, 'wb') as f:
                    # ทำการบันทึกไฟล์ PDF ที่ต้องการดาวน์โหลด
                    f.write(file.read())
                    backupList(failed_list, file_name)
                    backupList(success_list, file_name, "add")
                    logging.info(f"backup_success {output_path}")
            else:
                pass

        except Exception as e:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("Error", e)
            backupList(failed_list, file_name, "add")
            logging.error(f"backup_error {output_path}")
            pass

def check_file_exists(ftp, file_name):
    file_list = []
    ftp.retrlines('NLST', file_list.append)
    return file_name in file_list

def upload_files_ftp(directory_path, target_dir):
    ftp = FTP(ftp_host)
    ftp.login(user=ftp_user, passwd=ftp_passwd)
    ftp.cwd(target_dir)

    file_list = os.listdir(directory_path)
    total_files = len(file_list)
    success_count = 0
    failure_count = 0

    for file_name in file_list:
        file_path = os.path.join(directory_path, file_name)

        if not check_file_exists(ftp, file_name):
            try:
                file = open(file_path, 'rb')
                ftp.storbinary('STOR ' + file_name, file)
                file.close()
                print(f"อัพโหลดไฟล์ {file_name} สำเร็จ")
                success_count += 1
            except Exception as e:
                print(f"เกิดข้อผิดพลาดในการอัพโหลดไฟล์ {file_name}: {str(e)}")
                failure_count += 1
        else:
            print(f"ไฟล์ {file_name} มีอยู่แล้วในไดเรกทอรีเป้าหมาย")
            failure_count += 1

    ftp.quit()

    print("สรุปผลการอัพโหลด:")
    print(f"จำนวนไฟล์ทั้งหมด: {total_files}")
    print(f"อัพโหลดสำเร็จ: {success_count}")
    print(f"อัพโหลดไม่สำเร็จ: {failure_count}")

if __name__ == '__main__':
    main()
