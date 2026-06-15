import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv("kg_pipeline/.env")
load_dotenv("config/.env")
load_dotenv()

uri = os.getenv("NEO4J_URI")
username = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER")
password = os.getenv("NEO4J_PASSWORD")
database = os.getenv("NEO4J_DATABASE", "neo4j")

print("URI:", uri)
print("USERNAME:", username)
print("DATABASE:", database)
print("PASSWORD SET:", bool(password))

driver = GraphDatabase.driver(uri, auth=(username, password))

with driver.session(database=database) as session:
    result = session.run("RETURN 1 AS ok")
    print("Result:", result.single()["ok"])

driver.verify_connectivity()
print("Neo4j connection OK")

driver.close()