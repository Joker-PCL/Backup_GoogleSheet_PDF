# Backup_GoogleSheet_PDF

# format harddisk
    - sudo fdisk /dev/sda
    เมื่อคำสั่ง fdisk ถูกเรียกใช้งานคุณจะได้รับโปรแกรมส่วนของ fdisk prompt. กด "d" เพื่อลบพาร์ติชันที่ต้องการฟอร์แมต โปรแกรมจะถามคุณว่าต้องการลบพาร์ติชันใด โปรดใส่หมายเลขพาร์ติชันที่ต้องการลบ.
    หากคุณต้องการสร้างพาร์ติชันใหม่คุณสามารถกด "n"  เพื่อสร้างพาร์ติชันใหม่แล้วตามคำแนะนำในโปรแกรม.
    เมื่อคุณได้ทำการลบหรือสร้างพาร์ติชันตามที่ต้องการ กด "w"     เพื่อบันทึกการเปลี่ยนแปลงและออกจากโปรแกรม fdisk.
    หลังจากที่คุณฟอร์แมตดิสก์เสร็จสิ้น  คุณจะสามารถสร้างระบบไฟล์ใหม่บนพาร์ติชันดังกล่าวโดยใช้คำสั่งเช่น "mkfs. ext4" สำหรับระบบไฟล์ ext4 หรือ "mkfs.fat" สำหรับระบบไฟล์ FAT32.

    โปรดทราบว่าการฟอร์แมตฮาร์ดดิสก์จะทำให้ข้อมูลบนดิสก์ที่ถูกฟอร์แมตหายไปและไ  ม่สามารถกู้คืนได้  ดังนั้นโปรดระมัดระวังและสำรองข้อมูลที่สำคัญก่อนทำการฟอร์แมต.

# ตั้งค่า RAID1
    * sudo apt-get update
    * sudo apt-get upgrade
    * sudo apt-get install libudev-dev

    แตกไฟล์ mdadm-4.2.tar
    เข้าไปในไดเรกทอรีที่ถูกสร้างขึ้นจากการแตกไฟล์:
    * cd ไดเรกทอรี
    * ./configure
    * make
    * sudo make install

    ตรวจสอบการเชื่อมต่อฮาร์ดดิสclear
    * lsblk

    สร้าง RAID array
    * sudo mdadm --create /dev/md0 --level=1 --raid-devices=2 --metadata=1.0 /dev/sda /dev/sdb

    Format the RAID array
    * sudo mkfs.ext4 /dev/md0

    Mount the RAID array
    * sudo mkdir /mnt/raid
    * sudo mount /dev/md0 /mnt/raid

    Configure the RAID array to mount at boot
    * sudo nano /etc/fstab      
    * เพิ่ม /dev/md0 /mnt/raid ext4 defaults 0 0 ไปยังบรรทัดสุดท้าย

    ปลี่ยนสิทธิ์ของไดเรกทอรี /mnt/raid เพื่อให้สามารถเข้าถึงและแก้ไขไฟล์ในไดเรกทอรีได้ 
    * sudo chmod -R a+rw /mnt/raid

# คำสั่งต่างๆ
    ตรวจสอบพื้นที่ว่างใน Raspberry Pi
    * df -h

    ตรวจสอบพื้นที่ว่างใน RAID
    * df -h /mnt/raid

    ตรวจสอบสถานะของอาเรย์ RAID ใน Raspberry Pi 
    * sudo mdadm --detail /dev/md0

    หากฮาร์ดดิสก์ในอาเรย์ RAID พังไป และได้ทำการเปลี่ยนฮาร์ดดิสก์ที่เสียแล้ว ทำขั้นตอนต่อไปนี้เพื่อเปลี่ยนฮาร์ดดิสก์ในอาเรย์ RAID
    * sudo mdadm --add /dev/md0 /dev/sda
    /dev/md0 คือตำแหน่งของ RAID 
    /dev/sda คือตำแหน่งของไดร์ที่เพิ่มเข้ามาไหม่

    สร้างทางลัด (shortcut) ไปยังโฟลเดอร์ใน Raspberry Pi
    * ln -s /mnt/raid/PDF /home/pi/Desktop

# ติดตั้ง FileZilla 
    * sudo apt-get update
    * sudo apt-get install filezilla

# ทดสอบ RAID1
    ใช้คำสั่งต่อไปนี้เพื่อทำให้ฮาร์ดดิสก์ตัวหนึ่งในพาร์ติชัน RAID 1 พัง:
    * sudo mdadm --manage /dev/md0 --fail /dev/sda1
    * sudo mdadm --manage /dev/md0 --remove /dev/sda1

    ตรวจสอบสถานะของพาร์ติชัน RAID 1 โดยใช้คำสั่ง:
    * sudo mdadm --detail /dev/md0

    ตัดการทำงานของพาร์ติชัน RAID 1 โดยใช้คำสั่ง:
    * sudo mdadm --stop /dev/md0

    ยกเลิกการทำฮาร์ดดิสก์ที่เสียหายออกจากพาร์ติชัน RAID 1 โดยใช้คำสั่ง:
    * sudo mdadm --manage /dev/md0 --add /dev/sda1
