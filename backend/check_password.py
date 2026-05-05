import bcrypt
from sqlalchemy import create_engine, text

engine = create_engine('mysql+pymysql://root:@localhost:3306/sante_plus_ia')
conn = engine.connect()

result = conn.execute(text("SELECT email, mot_de_passe FROM utilisateurs WHERE email = 'aya.kouassi@sante.com'"))
row = result.fetchone()

if row:
    email, hashed = row
    print(f"Email: {email}")
    print(f"Hash stocké: {hashed[:60]}...")
    
    # Tester le mot de passe
    password = "admin123"
    try:
        is_valid = bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        print(f"\nTest avec '{password}': {'✅ VALIDE' if is_valid else '❌ INVALIDE'}")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
else:
    print("Utilisateur non trouvé")

conn.close()
