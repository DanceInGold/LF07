import serial
import pymysql

ser = serial.Serial('/dev/ttyACM0', 9600)

db = pymysql.connect(
    user="mhtf_app",
    password="D4t4B4s3!",
    database="mhtf",
    unix_socket="/run/mysqld/mysqld.sock"
)

cursor = db.cursor()

print("RFID Reader gestartet")

while True:

    line = ser.readline().decode(errors="ignore").strip()

    if "UID erkannt:" not in line:
        continue

    uid = line.replace("UID erkannt:", "").strip()

    cursor.execute(
        """
        SELECT id,label,person_name
        FROM rfid_cards
        WHERE uid=%s
        AND active=1
        """,
        (uid,)
    )

    result = cursor.fetchone()

    if result:

        ser.write(b"ALLOW\n")

        card_id, label, person = result

        print(f"✅ Zugriff erlaubt: {person}")

        cursor.execute(
            """
            INSERT INTO event_logs
            (action, entity_type, entity_id, result)
            VALUES (%s,%s,%s,%s)
            """,
            (
                f"RFID Scan {uid}",
                "rfid_card",
                card_id,
                "success"
            )
        )

        db.commit()

    else:

        ser.write(b"DENY\n")

        print(f"❌ Zugriff verweigert: {uid}")

        cursor.execute(
            """
            INSERT INTO event_logs
            (action, entity_type, result)
            VALUES (%s,%s,%s)
            """,
            (
                f"RFID Scan {uid}",
                "rfid_card",
                "failed"
            )
        )

        db.commit()
