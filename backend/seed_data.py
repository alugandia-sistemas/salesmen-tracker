from main import SessionLocal, Seller, Client

def seed_database():
    db = SessionLocal()
    
    try:
        existing = db.query(Seller).first()
        if existing:
            print("⚠️  La base de datos ya tiene datos")
            return
        
        sellers = [
            Seller(name="Ernesto Arocas", email="earoca@alugandia.es", phone="962873543", active=1),
            Seller(name="Jose Manuel Gómez", email="jmgomez@alugandia.es", phone="962873543", active=1)
        ]
        
        clients = [
            Client(
                name="Cristalum Gandia",
                address="C. del Lector Romero, 8, 46702 Gandia, Valencia",
                phone="961953754",
                email="info@cristalumgandia.info",
                location='POINT(38.960107688053455 -0.1876011040296285)',
                status="active"
            ),
            Client(
                name="Aluminguez SL",
                address="c/ Primero de Mayo, 12 Pol. Ind. Les Pedreres, 03610 Petrer, Alicante",
                phone="965376478",
                email="info@aluminguez.com",
                location='POINT(38.50622908918234 -0.7911363828664167)',
                status="active"
            ),
            Client(
                name="MetalGlass Aluminio y Cristal SL",
                address="C. Zurita, 8, 03630 Sax, Alicante",
                phone="636740677",
                email="metalglass@metalglass.es",
                location='POINT(38.54765471839225 -0.8162404364787462)',
                status="active"
            ),
        ]
        
        db.add_all(sellers)
        db.add_all(clients)
        db.commit()
        
        print(f"✅ Insertados {len(sellers)} vendedores y {len(clients)} clientes")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()