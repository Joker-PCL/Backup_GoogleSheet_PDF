# Backup_GoogleSheet_PDF

# ตั้งค่า RAID1
    - sudo apt-get update
    - sudo apt-get upgrade
    - sudo apt-get install libudev-dev

    แตกไฟล์ mdadm-4.2.tar
    เข้าไปในไดเรกทอรีที่ถูกสร้างขึ้นจากการแตกไฟล์:
    - cd ไดเรกทอรี
    - ./configure
    - make
    - sudo make install

    สร้าง RAID array
    - sudo mdadm –create /dev/md0 –level=1 –raid-devices=2 /dev/sda /dev/sdb

    Format the RAID array
    - sudo mkfs.ext4 /dev/md0

    Mount the RAID array
    - sudo mkdir /mnt/raid
    - sudo mount /dev/md0 /mnt/raid

    Configure the RAID array to mount at boot
    - sudo nano /etc/fstab      
    - เพิ่ม /dev/md0 /mnt/raid ext4 defaults 0 0 ไปยังบรรทัดสุดท้าย

    ปลี่ยนสิทธิ์ของไดเรกทอรี /mnt/raid เพื่อให้สามารถเข้าถึงและแก้ไขไฟล์ในไดเรกทอรีได้ 
    - sudo chown -R pi:pi /mnt/raid

# คำสั่งต่างๆ
    ตรวจสอบพื้นที่ว่างใน Raspberry Pi
    - df -h

    ตรวจสอบพื้นที่ว่างใน RAID
    - df -h /mnt/raid

    ตรวจสอบสถานะของอาเรย์ RAID ใน Raspberry Pi 
    - sudo mdadm --detail /dev/md0

    หากฮาร์ดดิสก์ในอาเรย์ RAID พังไป และได้ทำการเปลี่ยนฮาร์ดดิสก์ที่เสียแล้ว ทำขั้นตอนต่อไปนี้เพื่อเปลี่ยนฮาร์ดดิสก์ในอาเรย์ RAID
    - mdadm --add /dev/md0 /dev/sda
    /dev/md0 คือตำแหน่งของ RAID 
    /dev/sda คือตำแหน่งของไดร์ที่เพิ่มเข้ามาไหม่

    สร้างทางลัด (shortcut) ไปยังโฟลเดอร์ใน Raspberry Pi
    - ln -s /mnt/raid/PDF /home/pi/Desktop

# ติดตั้ง FileZilla 
    - sudo apt-get update
    - sudo apt-get install filezilla



