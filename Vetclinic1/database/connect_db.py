import pyodbc

conn = pyodbc.connect(
    'DRIVER={SQL Server};'
    'SERVER=DESKTOP-7PE36RN;'
    'DATABASE=Vetclinic;'
    'Trusted_Connection=yes;'
)

cursor = conn.cursor()