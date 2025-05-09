# app.py (con login y autenticación)
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from db import get_connection
from datetime import datetime
import pandas as pd


credentials = {
    "usernames": {
        "usuario1": {
            "name": "Alvaro H",
            "password": st.secrets["HASH_ALVARO"],
            "email": "alvaro@email.com"
        },
        "usuario2": {
            "name": "Maru R",
            "password": st.secrets["HASH_MARU"],
            "email": "maru@email.com"
        }
    }
}

cookie_config = {
    "name": st.secrets["COOKIE_NAME"],
    "key": st.secrets["COOKIE_KEY"],
    "expiry_days": int(st.secrets["COOKIE_EXPIRY"])
}

authenticator = stauth.Authenticate(
    credentials,
    cookie_config["name"],
    cookie_config["key"],
    cookie_config["expiry_days"]
)

name, authentication_status, username = authenticator.login("Login", location="main")

if authentication_status:
    conn = get_connection()
    cursor = conn.cursor()

    st.set_page_config(page_title="Inventario Cafetería", layout="centered")
    st.title("📦 Inventario - Cafetería")

    authenticator.logout("Logout", "sidebar")
    st.sidebar.markdown(f"Bienvenido, {name}")

    menu = st.sidebar.selectbox("Menú", ["Registrar entrada", "Registrar salida", "Ver inventario"])

    def obtener_insumos():
        cursor.execute("SELECT id, nombre, unidad, cantidad_actual FROM insumos ORDER BY nombre ASC")
        return cursor.fetchall()

    def agregar_nuevo_insumo(nombre, unidad):
        cursor.execute("INSERT INTO insumos (nombre, unidad, cantidad_actual) VALUES (%s, %s, %s) RETURNING id", (nombre, unidad, 0))
        conn.commit()
        return cursor.fetchone()[0]

    def registrar_movimiento(tipo, insumo_id, cantidad, operador, observacion=""):
        if tipo == "salida":
            cursor.execute("SELECT cantidad_actual FROM insumos WHERE id = %s", (insumo_id,))
            disponible = cursor.fetchone()[0]
            if cantidad > disponible:
                st.error("❌ No hay suficiente inventario.")
                return
            cursor.execute("UPDATE insumos SET cantidad_actual = cantidad_actual - %s WHERE id = %s", (cantidad, insumo_id))
        else:
            cursor.execute("UPDATE insumos SET cantidad_actual = cantidad_actual + %s WHERE id = %s", (cantidad, insumo_id))

        cursor.execute("""
            INSERT INTO movimientos (tipo, insumo_id, cantidad, observacion)
            VALUES (%s, %s, %s, %s)
        """, (tipo, insumo_id, cantidad, f"{operador}: {observacion}"))
        conn.commit()
        st.success("✅ Movimiento registrado correctamente.")

    if menu == "Registrar entrada":
        st.header("📥 Registrar entrada")
        insumos = obtener_insumos()
        nombres = [i[1] for i in insumos]
        seleccion = st.selectbox("Selecciona insumo", ["(Nuevo insumo)"] + nombres)

        if seleccion == "(Nuevo insumo)":
            nuevo_nombre = st.text_input("Nombre del nuevo insumo")
            unidad = st.text_input("Unidad")
        else:
            nuevo_nombre = seleccion
            unidad = None

        cantidad = st.number_input("Cantidad", min_value=0.01)
        observacion = st.text_input("Observaciones")

        if st.button("Registrar entrada"):
            if not nuevo_nombre or cantidad <= 0:
                st.warning("Completa todos los campos.")
            else:
                if seleccion == "(Nuevo insumo)":
                    insumo_id = agregar_nuevo_insumo(nuevo_nombre, unidad)
                else:
                    insumo_id = [i[0] for i in insumos if i[1] == seleccion][0]
                registrar_movimiento("entrada", insumo_id, cantidad, name, observacion)

    elif menu == "Registrar salida":
        st.header("📤 Registrar salida")
        insumos = obtener_insumos()
        if not insumos:
            st.warning("No hay insumos disponibles.")
        else:
            seleccion = st.selectbox("Selecciona insumo", [i[1] for i in insumos])
            cantidad = st.number_input("Cantidad a retirar", min_value=0.01)
            observacion = st.text_input("Observaciones")
            insumo_id = [i[0] for i in insumos if i[1] == seleccion][0]

            if st.button("Registrar salida"):
                if cantidad <= 0:
                    st.warning("Completa todos los campos.")
                else:
                    registrar_movimiento("salida", insumo_id, cantidad, name, observacion)

    elif menu == "Ver inventario":
        st.header("📊 Inventario actual")
        insumos = obtener_insumos()
        df = pd.DataFrame(insumos, columns=["ID", "Nombre", "Unidad", "Cantidad disponible"])
        st.dataframe(df, use_container_width=True)

elif authentication_status is False:
    st.error("❌ Usuario o contraseña incorrectos")
elif authentication_status is None:
    st.warning("🔒 Ingresa tus credenciales para continuar")
