__G__ = "(G)bd249ce4"

from psycopg2 import sql,connect
from sys import stdout
from time import sleep
from traceback import format_exc

class postgres_class():
	def __init__(self,host=None,port=None,username=None,password=None,db=None,drop=False):
		self.host = host or 'chameleon_postgres' 
		self.port = port or 9999
		self.username = username or 'changeme027a088931d22' 
		self.password = password or 'changeme0f40773877963' 
		self.db = db or 'chameleon' 
		self.mapped_tables = ["errors","servers","sniffer","system"]
		self.wait_until_up()
		if drop:
			self.con = connect(host=self.host,port=self.port,user=self.username,password=self.password)
			self.con.set_isolation_level(0)
			self.cur = self.con.cursor()
			self.drop_db()
			self.drop_tables()
			self.con.close()
		self.con = connect(host=self.host,port=self.port,user=self.username,password=self.password,database=self.db)
		self.con.set_isolation_level(0)
		self.cur = self.con.cursor()
		self.create_tables()

	def wait_until_up(self):
		test = True
		while test:
			try:
				print("Testing postgres connection")
				stdout.flush()
				conn = connect(host=self.host,port=self.port,user=self.username,password=self.password,connect_timeout=1)
				conn.close()
				test = False
			except:
				pass
			sleep(1)

	def addattr(self,x,val):
		self.__dict__[x]=val

	def check_db_if_exists(self):
		self.cur.execute("SELECT exists(SELECT 1 from pg_catalog.pg_database where datname = %s)", (self.db,))
		if self.cur.fetchall()[0][0]:
			return True
		else:
			return False

	def drop_db(self):
		try:
			if self.check_db_if_exists():
				self.cur.execute(sql.SQL("drop DATABASE IF EXISTS {}").format(sql.Identifier(self.db)))
				sleep(2)
				self.cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(self.db)))
			else:
				self.cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(self.db)))
		except:
			pass

	def drop_tables(self,):
		for x in self.mapped_tables:
			self.cur.execute(sql.SQL("drop TABLE IF EXISTS {}").format(sql.Identifier(x+"_table")))

	def create_tables(self):
		for x in self.mapped_tables:
			self.cur.execute(sql.SQL("CREATE TABLE IF NOT EXISTS {} (id SERIAL NOT NULL,date timestamp with time zone DEFAULT now(),data json)").format(sql.Identifier(x+"_table")))

	def insert_into_data_safe(self,table,obj):
		try:
			#stdout.write(str(table))
			self.cur.execute(
				sql.SQL("INSERT INTO {} (id,date, data) VALUES (DEFAULT ,now(), %s)")
					.format(sql.Identifier(table+"_table")),
						[obj])
			#self.cur.execute(sql.SQL("INSERT INTO errors_table (data) VALUES (%s,)"),dumps(serialize_object(obj),cls=ComplexEncoder))
		except Exception:
			stdout.write(str(format_exc()).replace("\n"," "))
		stdout.flush()