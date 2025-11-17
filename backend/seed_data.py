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
                name="Carpintería Valencia",
                address="Av. del Puerto 245, Valencia",
                phone="963123456",
                email="info@carpivalencia.com",
                location='POINT(-0.3763 39.4699)',
                status="active"
            ),
            Client(
                name="Aluminis Gandia",
                address="Calle Mayor 89, Gandia",
                phone="962456789",
                email="contacto@aluminisgandia.com",
                location='POINT(-0.1828 38.9672)',
                status="active"
            ),
            Client(
                name="Perfiles Alzira",
                address="Industrial Nord, Alzira",
                phone="962789012",
                email="alzira@perfiles.com",
                location='POINT(-0.4351 39.1521)',
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