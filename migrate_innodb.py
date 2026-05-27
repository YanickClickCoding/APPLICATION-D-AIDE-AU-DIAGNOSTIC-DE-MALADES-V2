"""Migration MyISAM → InnoDB + ajout FK réelles"""
import pymysql

conn = pymysql.connect(host='localhost', user='root', password='',
                       database='gasa_sad_ia _v2.sql', port=3306, charset='utf8mb4')
cur = conn.cursor()

# 1. Récupérer toutes les tables MyISAM
cur.execute("""
    SELECT TABLE_NAME FROM information_schema.TABLES
    WHERE TABLE_SCHEMA = DATABASE() AND ENGINE = 'MyISAM'
    ORDER BY TABLE_NAME
""")
tables = [r[0] for r in cur.fetchall()]
print(f"Tables MyISAM à migrer : {tables}\n")

# 2. Convertir chaque table
for t in tables:
    cur.execute(f"ALTER TABLE `{t}` ENGINE=InnoDB")
    print(f"  OK  {t} -> InnoDB")

conn.commit()

# 3. Vérification
cur.execute("""
    SELECT TABLE_NAME, ENGINE FROM information_schema.TABLES
    WHERE TABLE_SCHEMA = DATABASE() ORDER BY TABLE_NAME
""")
print("\nÉtat final :")
all_innodb = True
for r in cur.fetchall():
    status = "✓" if r[1] == 'InnoDB' else "✗"
    print(f"  {status}  {r[0]:35s}  {r[1]}")
    if r[1] != 'InnoDB':
        all_innodb = False

print(f"\n{'Toutes les tables sont InnoDB.' if all_innodb else 'ATTENTION: certaines tables ne sont pas InnoDB!'}")
conn.close()
