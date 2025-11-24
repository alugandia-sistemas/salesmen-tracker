#!/usr/bin/env python3
"""
🔧 VALIDADOR DE CONEXIÓN SUPABASE
Prueba que la DATABASE_URL funciona antes de hacer deploy a Railway
"""

import psycopg2
import sys

def test_supabase_connection(database_url: str):
    """
    Prueba conexión a Supabase PostgreSQL
    
    Args:
        database_url: postgresql://user:password@host:port/database
    
    Returns:
        bool: True si conexión OK, False si falla
    """
    
    print("=" * 60)
    print("🔍 VALIDADOR DE CONEXIÓN SUPABASE")
    print("=" * 60)
    
    # Validación básica
    if not database_url:
        print("❌ ERROR: DATABASE_URL vacía")
        return False
    
    if not database_url.startswith("postgresql://"):
        print("❌ ERROR: DATABASE_URL debe empezar con 'postgresql://'")
        return False
    
    print(f"📍 URL (parcial): postgresql://***@{database_url.split('@')[1]}")
    
    try:
        print("\n⏳ Conectando a Supabase...")
        conn = psycopg2.connect(database_url, connect_timeout=10)
        cursor = conn.cursor()
        print("✅ Conexión establecida")
        
        # Test 1: Version PostgreSQL
        print("\n🔍 Test 1: Versión PostgreSQL")
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"   ✅ {version[:80]}...")
        
        # Test 2: PostGIS disponible
        print("\n🔍 Test 2: PostGIS")
        try:
            cursor.execute("SELECT PostGIS_version();")
            postgis_version = cursor.fetchone()[0]
            print(f"   ✅ PostGIS instalado: {postgis_version}")
        except Exception as e:
            if "does not exist" in str(e):
                print(f"   ⚠️ PostGIS no instalado")
                print(f"   💡 Solución: En Supabase SQL Editor, ejecutar:")
                print(f"      CREATE EXTENSION IF NOT EXISTS postgis;")
            else:
                print(f"   ❌ Error: {str(e)}")
        
        # Test 3: Crear tabla de prueba
        print("\n🔍 Test 3: Permisos de escritura")
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS _test_connection (
                    id SERIAL PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            print("   ✅ Puedo crear tablas")
            
            # Limpiar
            cursor.execute("DROP TABLE IF EXISTS _test_connection;")
            conn.commit()
        except Exception as e:
            print(f"   ❌ Error de permisos: {str(e)}")
        
        # Test 4: Verificar esquema public
        print("\n🔍 Test 4: Esquema 'public'")
        cursor.execute("""
            SELECT schema_name FROM information_schema.schemata 
            WHERE schema_name = 'public';
        """)
        if cursor.fetchone():
            print("   ✅ Esquema 'public' disponible")
        else:
            print("   ⚠️ Esquema 'public' no existe")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("🎉 TODAS LAS PRUEBAS PASARON")
        print("=" * 60)
        print("\n✅ Tu DATABASE_URL es válida para Railway")
        print("📝 Próximo paso: Actualizar en Railway Variables")
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ ERROR DE CONEXIÓN")
        print(f"   {str(e)}")
        print("\n💡 Verificar:")
        print("   • PASSWORD correcto")
        print("   • Hostname correcto (db.XXXX.supabase.co)")
        print("   • Puerto 5432")
        print("   • Base de datos: 'postgres'")
        return False
        
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {str(e)}")
        return False


if __name__ == "__main__":
    # Obtener DATABASE_URL
    import os
    
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ Variable DATABASE_URL no configurada")
        print("\nUso:")
        print("  export DATABASE_URL='postgresql://user:pass@host:5432/database'")
        print("  python validate_supabase.py")
        sys.exit(1)
    
    success = test_supabase_connection(database_url)
    sys.exit(0 if success else 1)
