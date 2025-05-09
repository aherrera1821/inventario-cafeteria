from db import get_connection

def reset_database():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Borra el contenido de las tablas y reinicia IDs
        cursor.execute("TRUNCATE TABLE movimientos, insumos RESTART IDENTITY;")
        conn.commit()
        conn.close()
        print("✅ Base de datos limpiada y reiniciada exitosamente.")
    except Exception as e:
        print("❌ Error al limpiar la base de datos:", e)

if __name__ == "__main__":
    reset_database()
