from main import SessionLocal, Seller, Client, Route, Visit, Opportunity
from sqlalchemy import func, text
from datetime import datetime, timedelta
import uuid

def seed_database():
    """
    ✅ SEED CORREGIDO - Inserta datos reales de Alugandia
    
    CAMBIOS REALIZADOS:
    1. active=1 → is_active=True (campo correcto en modelo)
    2. POINT(lat,lng) → POINT(lng,lat) (orden correcto WKT)
    3. Añadidos rutas, visitas y oportunidades de prueba
    """
    db = SessionLocal()
    
    try:
        # Verificar si ya hay datos
        existing = db.query(Seller).first()
        if existing:
            print("⚠️  La base de datos ya tiene datos")
            return
        
        # ============================================================================
        # VENDEDORES - Con tus agentes reales
        # ============================================================================
        sellers = [
            Seller(
                name="Ernesto Arocas",
                email="earoca@alugandia.es",
                phone="962873541",
                is_active=True  # ✅ CORREGIDO
            ),
            Seller(
                name="Jose Manuel Gómez",
                email="jmgomez@alugandia.es",
                phone="962873542",
                is_active=True  # ✅ CORREGIDO
            )
        ]
        
        # ============================================================================
        # CLIENTES - Con ubicaciones correctas (LONGITUDE, LATITUDE)
        # ============================================================================
        clients = [
            # Cliente 1: Cristalum Gandia (Real de Gandia)
            Client(
                name="Cristalum Gandia",
                address="C. del Lector Romero, 8, 46702 Gandia, Valencia",
                phone="961953754",
                email="info@cristalumgandia.info",
                # ✅ CORREGIDO: POINT(LONGITUDE LATITUDE) no (LATITUDE LONGITUDE)
                location=f"POINT(-0.1876011040296285 38.960107688053455)",
                client_type="carpenter",
                status="active"
            ),
            # Cliente 2: Aluminguez SL (Petrer, Alicante)
            Client(
                name="Aluminguez SL",
                address="c/ Primero de Mayo, 12 Pol. Ind. Les Pedreres, 03610 Petrer, Alicante",
                phone="965376478",
                email="info@aluminguez.com",
                location=f"POINT(-0.7911363828664167 38.50622908918234)",
                client_type="installer",
                status="active"
            ),
            # Cliente 3: MetalGlass (Sax, Alicante)
            Client(
                name="MetalGlass Aluminio y Cristal SL",
                address="C. Zurita, 8, 03630 Sax, Alicante",
                phone="636740677",
                email="metalglass@metalglass.es",
                location=f"POINT(-0.8162404364787462 38.54765471839225)",
                client_type="carpenter",
                status="active"
            ),
        ]
        
        # Insertar vendedores y clientes
        db.add_all(sellers)
        db.add_all(clients)
        db.commit()
        
        print(f"✅ Insertados {len(sellers)} vendedores y {len(clients)} clientes")
        
        # ============================================================================
        # RUTAS - Planificadas para los vendedores
        # ============================================================================
        seller_ernesto = db.query(Seller).filter(Seller.name == "Ernesto Arocas").first()
        seller_jose = db.query(Seller).filter(Seller.name == "Jose Manuel Gómez").first()
        
        client_cristalum = db.query(Client).filter(Client.name == "Cristalum Gandia").first()
        client_aluminguez = db.query(Client).filter(Client.name == "Aluminguez SL").first()
        client_metalglass = db.query(Client).filter(Client.name == "MetalGlass Aluminio y Cristal SL").first()

        today = datetime.utcnow()
        
        routes = [
            # Ruta de Ernesto para hoy
            Route(
                seller_id=seller_ernesto.id,
                client_id=client_cristalum.id,
                planned_date=today,
                planned_time="10:00",
                status="pending"
            ),
            Route(
                seller_id=seller_ernesto.id,
                client_id=client_aluminguez.id,
                planned_date=today,
                planned_time="14:30",
                status="pending"
            ),
            # Ruta de José para mañana
            Route(
                seller_id=seller_jose.id,
                client_id=client_metalglass.id,
                planned_date=today + timedelta(days=1),
                planned_time="11:00",
                status="pending"
            ),
        ]
        
        db.add_all(routes)
        db.commit()
        
        print(f"✅ Insertadas {len(routes)} rutas planificadas")
        
        # ============================================================================
        # OPORTUNIDADES - Asociadas a clientes
        # ============================================================================
        opportunities = [
            Opportunity(
                seller_id=seller_ernesto.id,
                client_id=client_cristalum.id,
                title="Sistema de carpintería de aluminio para villa",
                description="Cliente interesado en renovar todas las carpinterías",
                estimated_value=15000.00,
                status="open"
            ),
            Opportunity(
                seller_id=seller_jose.id,
                client_id=client_metalglass.id,
                title="Perfiles para fachada comercial",
                description="Proyecto nuevo en zona industrial",
                estimated_value=8500.00,
                status="open"
            ),
        ]
        
        db.add_all(opportunities)
        db.commit()
        
        print(f"✅ Insertadas {len(opportunities)} oportunidades")
        
        print("\n" + "="*60)
        print("✅ BASE DE DATOS INICIALIZADA CORRECTAMENTE")
        print("="*60)
        print(f"  • {len(sellers)} vendedores")
        print(f"  • {len(clients)} clientes")
        print(f"  • {len(routes)} rutas planificadas")
        print(f"  • {len(opportunities)} oportunidades")
        print("\n🚀 Ya puedes hacer:")
        print("   - POST /check-in/ para registrar visitas")
        print("   - GET /visits/ para ver historial")
        print("   - GET /dashboard/stats/ para métricas")
        print("\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
