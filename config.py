# config.py
from dotenv import load_dotenv
import os
import oracledb

load_dotenv()

ORACLE_USER = os.getenv("ORACLE_USER")
ORACLE_PASS = os.getenv("ORACLE_PASS")
ORACLE_DSN = os.getenv("ORACLE_DSN")

def get_connection():
    """
    devuelve una conexion a oracle . lanza excepcion si falla .
    """
    if not (ORACLE_USER and ORACLE_PASS and ORACLE_DSN):
        raise RuntimeError("variables oracle_user/oracle_pass/oracle_dsn no configuradas en .env")
    # si ncecesitas usar oracle instant client, realiza oracle.db.init_oracle_client(lib_dir=...) antes.
    return oracledb.connect(user=ORACLE_USER, password=ORACLE_PASS, dsn= ORACLE_DSN, encoding="UTF-8")
