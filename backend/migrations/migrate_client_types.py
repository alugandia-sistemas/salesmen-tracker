#!/usr/bin/env python3
"""
============================================================================
MIGRACIÓN: Actualizar client_type a nueva taxonomía
============================================================================

ANTES (tipos antiguos):
- carpenter
- installer  
- industrial

DESPUÉS (nueva taxonomía Alugandia):
- carpintero_metalico  → Carpinteros metálicos
- cristalero           → Cristaleros / Vidrieros
- taller               → Talleres industriales
- instalador           → Instaladores
- cerrajero            → Cerrajeros
- constructor          → Constructores / Obras
- otros                → Otros

MAPEO DE MIGRACIÓN:
- carpenter   → carpintero_metalico
- installer   → instalador
- industrial  → taller

============================================================================
USO:
    # Ver estado actual (sin cambios)
    python migrate_client_types.py --dry-run
    
    # Ejecutar migración
    python migrate_client_types.py --execute
    
    # Revertir migración
    python migrate_client_types.py --rollback
============================================================================
"""

import os
import sys
import argparse
from datetime import datetime

# Agregar path del backend para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
from psycopg2.extras import RealDictCursor


# ============================================================================
# CONFIGURACIÓN
# ============================================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5433/salesmen_tracker"
)

# Mapeo de tipos antiguos → nuevos
MIGRATION_MAP = {
    "carpenter": "carpintero_metalico",
    "installer": "instalador",
    "industrial": "taller",
}

# Mapeo inverso para rollback
ROLLBACK_MAP = {v: k for k, v in MIGRATION_MAP.items()}

# Tipos válidos después de migración
VALID_TYPES_NEW = [
    "carpintero_metalico",
    "cristalero",
    "taller",
    "instalador",
    "cerrajero",
    "constructor",
    "otros"
]


# ============================================================================
# FUNCIONES DE MIGRACIÓN
# ============================================================================

def get_connection():
    """Conectar a PostgreSQL"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        sys.exit(1)


def show_current_state(conn):
    """Mostrar distribución actual de client_type"""
    print("\n" + "=" * 60)
    print("📊 ESTADO ACTUAL DE client_type")
    print("=" * 60)
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Contar por tipo
        cur.execute("""
            SELECT 
                client_type,
                COUNT(*) as count
            FROM clients
            GROUP BY client_type
            ORDER BY count DESC
        """)
        
        rows = cur.fetchall()
        total = sum(r['count'] for r in rows)
        
        print(f"\n{'Tipo':<25} {'Cantidad':>10} {'%':>8}")
        print("-" * 45)
        
        for row in rows:
            tipo = row['client_type'] or '(null)'
            count = row['count']
            pct = (count / total * 100) if total > 0 else 0
            
            # Marcar tipos antiguos que necesitan migración
            marker = " ⚠️" if tipo in MIGRATION_MAP else ""
            print(f"{tipo:<25} {count:>10} {pct:>7.1f}%{marker}")
        
        print("-" * 45)
        print(f"{'TOTAL':<25} {total:>10}")
        
        # Contar cuántos necesitan migración
        cur.execute("""
            SELECT COUNT(*) as count
            FROM clients
            WHERE client_type IN %s
        """, (tuple(MIGRATION_MAP.keys()),))
        
        need_migration = cur.fetchone()['count']
        
        print(f"\n📌 Clientes que necesitan migración: {need_migration}")
        
        return need_migration


def dry_run(conn):
    """Simular migración sin ejecutar cambios"""
    print("\n" + "=" * 60)
    print("🔍 DRY RUN - Simulación de migración")
    print("=" * 60)
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        for old_type, new_type in MIGRATION_MAP.items():
            cur.execute("""
                SELECT id, name, client_type
                FROM clients
                WHERE client_type = %s
                LIMIT 5
            """, (old_type,))
            
            rows = cur.fetchall()
            
            cur.execute("""
                SELECT COUNT(*) as count
                FROM clients
                WHERE client_type = %s
            """, (old_type,))
            
            total = cur.fetchone()['count']
            
            print(f"\n📦 {old_type} → {new_type} ({total} clientes)")
            
            if rows:
                print("   Ejemplos:")
                for row in rows:
                    print(f"   • {row['name'][:40]}")
            
            if total > 5:
                print(f"   ... y {total - 5} más")
    
    print("\n" + "=" * 60)
    print("✅ Simulación completada. Ningún cambio realizado.")
    print("   Para ejecutar la migración, usa: --execute")
    print("=" * 60)


def execute_migration(conn):
    """Ejecutar migración de tipos"""
    print("\n" + "=" * 60)
    print("🚀 EJECUTANDO MIGRACIÓN")
    print("=" * 60)
    
    # Crear backup log
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"migration_backup_{timestamp}.sql"
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Guardar estado previo para rollback
        print(f"\n📝 Guardando backup en {backup_file}...")
        
        cur.execute("""
            SELECT id, name, client_type
            FROM clients
            WHERE client_type IN %s
        """, (tuple(MIGRATION_MAP.keys()),))
        
        backup_rows = cur.fetchall()
        
        with open(backup_file, 'w') as f:
            f.write(f"-- Backup de migración: {timestamp}\n")
            f.write(f"-- Total registros: {len(backup_rows)}\n\n")
            
            for row in backup_rows:
                f.write(f"UPDATE clients SET client_type = '{row['client_type']}' WHERE id = '{row['id']}';\n")
        
        print(f"   ✅ Backup guardado: {len(backup_rows)} registros")
        
        # Ejecutar migración
        total_updated = 0
        
        for old_type, new_type in MIGRATION_MAP.items():
            cur.execute("""
                UPDATE clients
                SET client_type = %s
                WHERE client_type = %s
            """, (new_type, old_type))
            
            updated = cur.rowcount
            total_updated += updated
            
            print(f"\n   {old_type} → {new_type}: {updated} clientes actualizados")
        
        # Confirmar transacción
        conn.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ MIGRACIÓN COMPLETADA")
        print(f"   Total actualizados: {total_updated} clientes")
        print(f"   Backup guardado en: {backup_file}")
        print("=" * 60)
        
        return total_updated


def rollback_migration(conn):
    """Revertir migración (nuevos tipos → antiguos)"""
    print("\n" + "=" * 60)
    print("⏪ ROLLBACK - Revirtiendo migración")
    print("=" * 60)
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        total_reverted = 0
        
        for new_type, old_type in ROLLBACK_MAP.items():
            cur.execute("""
                UPDATE clients
                SET client_type = %s
                WHERE client_type = %s
            """, (old_type, new_type))
            
            reverted = cur.rowcount
            total_reverted += reverted
            
            print(f"   {new_type} → {old_type}: {reverted} clientes revertidos")
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ ROLLBACK COMPLETADO")
        print(f"   Total revertidos: {total_reverted} clientes")
        print("=" * 60)
        
        return total_reverted


def validate_after_migration(conn):
    """Validar estado después de migración"""
    print("\n" + "=" * 60)
    print("🔎 VALIDACIÓN POST-MIGRACIÓN")
    print("=" * 60)
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Verificar que no quedan tipos antiguos
        cur.execute("""
            SELECT COUNT(*) as count
            FROM clients
            WHERE client_type IN %s
        """, (tuple(MIGRATION_MAP.keys()),))
        
        old_remaining = cur.fetchone()['count']
        
        if old_remaining > 0:
            print(f"   ⚠️ Aún quedan {old_remaining} clientes con tipos antiguos")
        else:
            print(f"   ✅ No quedan tipos antiguos")
        
        # Verificar tipos válidos
        cur.execute("""
            SELECT client_type, COUNT(*) as count
            FROM clients
            WHERE client_type NOT IN %s
            GROUP BY client_type
        """, (tuple(VALID_TYPES_NEW),))
        
        invalid = cur.fetchall()
        
        if invalid:
            print(f"   ⚠️ Tipos no reconocidos encontrados:")
            for row in invalid:
                print(f"      • {row['client_type']}: {row['count']} clientes")
        else:
            print(f"   ✅ Todos los tipos son válidos")
        
        # Resumen final
        cur.execute("""
            SELECT client_type, COUNT(*) as count
            FROM clients
            GROUP BY client_type
            ORDER BY count DESC
        """)
        
        print(f"\n📊 Distribución final:")
        for row in cur.fetchall():
            print(f"   • {row['client_type']}: {row['count']}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Migrar client_type a nueva taxonomía Alugandia",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python migrate_client_types.py --dry-run    # Ver qué se va a cambiar
  python migrate_client_types.py --execute    # Ejecutar migración
  python migrate_client_types.py --rollback   # Revertir migración
  python migrate_client_types.py --status     # Ver estado actual
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--dry-run', action='store_true', help='Simular migración sin cambios')
    group.add_argument('--execute', action='store_true', help='Ejecutar migración')
    group.add_argument('--rollback', action='store_true', help='Revertir migración')
    group.add_argument('--status', action='store_true', help='Ver estado actual')
    
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("🔧 MIGRACIÓN DE CLIENT_TYPE - Alugandia")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🗄️ Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL}")
    
    conn = get_connection()
    print("✅ Conexión establecida")
    
    try:
        # Siempre mostrar estado actual
        need_migration = show_current_state(conn)
        
        if args.status:
            pass  # Solo mostrar estado
        
        elif args.dry_run:
            if need_migration > 0:
                dry_run(conn)
            else:
                print("\n✅ No hay clientes que necesiten migración")
        
        elif args.execute:
            if need_migration > 0:
                confirm = input(f"\n⚠️ ¿Ejecutar migración de {need_migration} clientes? (y/N): ")
                if confirm.lower() == 'y':
                    execute_migration(conn)
                    validate_after_migration(conn)
                else:
                    print("❌ Migración cancelada")
            else:
                print("\n✅ No hay clientes que necesiten migración")
        
        elif args.rollback:
            confirm = input("\n⚠️ ¿Revertir migración? (y/N): ")
            if confirm.lower() == 'y':
                rollback_migration(conn)
                show_current_state(conn)
            else:
                print("❌ Rollback cancelado")
    
    finally:
        conn.close()
        print("\n🔒 Conexión cerrada")


if __name__ == "__main__":
    main()
