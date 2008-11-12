import time

from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, Boolean
from sqlalchemy.orm import mapper, sessionmaker, relation

#for user in session.query(User).filter(User.name=='ed'):
#	print user

#print session.query(User).\
#	join('addresses', aliased=True).filter(Address.ip_address=='216.7.57.1').all()

#session.query(Address).filter_by(user=user).all()

#engine = create_engine('sqlite:///:memory:')#, echo=True)
#engine = create_engine('sqlite:///database.txt')

#### IMPLEMENT THIS #### ...maybe not...
#import sqlalchemy.pool as pool
#import sqlite

#def getconn():
#    return sqlite.connect(filename='myfile.db')

## SQLite connections require the SingletonThreadPool    
#p = pool.SingletonThreadPool(getconn)
#### END ####

#engine = create_engine('mysql://uberserver:A2Pb2p3M547EuE47@localhost/uberserver')
metadata = MetaData()

class User(object):
	def __init__(self, name, password, last_ip):
		self.name = name
		self.password = password
		self.last_login = int(time.time())
		self.register_date = int(time.time())
		self.last_ip = last_ip
		self.ingame_time = 0
		self.bot = 0
		self.access = 'user' # moderator, admin

	def __repr__(self):
		return "<User('%s', '%s')>" % (self.name, self.password)

class Address(object):
	def __init__(self, ip_address):
		self.time = int(time.time())
		self.ip_address = ip_address

	def __repr__(self):
		return "<Address('%s')>" % self.ip_address

class Rename(object):
	def __init__(self, original, new):
		self.original = original
		self.new = new
		self.time = int(time.time())
		
	def __repr__(self):
		return "<Rename('%s')>" % self.ip_address

class Channel(object):
	def __init__(self, name, password='', chanserv=False, owner='', topic='', topic_time=0, topic_owner='', antispam='', admins='', autokick='ban', censor=False, antishock=False):
		self.name = name
		self.password = password
		self.chanserv = chanserv
		self.owner = owner
		self.topic = topic
		self.topic_time = topic_time
		self.topic_owner = topic_owner
		self.antispam = antispam
		self.admins = admins
		self.allow = allow
		self.autokick = autokick
		self.censor = censor
		self.antishock = antishock

	def __repr__(self):
		return "<Channel('%s')>" % self.name

class ChanUser(object):
	def __init__(self, name, channel, admin=False, banned='', allowed=False, mute=0):
		self.name = name
		self.channel = channel
		self.admin = admin
		self.banned = banned
		self.allowed = allowed
		self.mute = mute

	def __repr__(self):
		return "<ChanUser('%s')>" % self.name

class Antispam(object):
	def __init__(self, enabled, quiet, duration, timeout, bonus, unique, bonuslength):
		self.enabled = enabled
		self.quiet = quiet
		self.duration = duration
		self.timeout = timeout
		self.bonus = bonus
		self.unique = unique
		self.bonuslength = bonuslength

	def __repr__(self):
		return "<Antispam('%s')>" % self.channel

class Ban(object):
	def __init__(self, reason, end_time):
		self.reason = reason
		self.end_time = end_time
	
	def __repr__(self):
		return "<Ban('%s')>" % self.end_time

class AggregateBan(object):
	def __init__(self, ban_type, data):
		self.ban_type = ban_type
		self.data = data
	
	def __repr__(self):
		return "<AggregateBan('%s')('%s')>" % (self.ban_type, self.data)

users_table = Table('users', metadata,
	Column('id', Integer, primary_key=True),
	Column('name', String(40)),
	Column('password', String(32)),
	Column('register_date', Integer)),
	Column('last_login', Integer), # use seconds since unix epoch
	Column('last_ip', String(15)), # would need update for ipv6
	Column('ingame', Integer),
	Column('access', String(32)),
	Column('bot', Integer),
	)

addresses_table = Table('addresses', metadata, 
	Column('id', Integer, primary_key=True),
	Column('ip_address', String(15), nullable=False),
	Column('time', Integer),
	Column('user_id', Integer, ForeignKey('users.id')),
	)

renames_table = Table('renames', metadata,
	Column('user_id', Integer, ForeignKey('users.id')),
	Column('original', String(40)),
	Column('new', String(40)),
	Column('time', Integer),
	)

channels_table = Table('channels', metadata,
	Column('id', Integer, primary_key=True),
	Column('name', String(40)),
	Column('password', String(32)),
	Column('owner', String(40)),
	Column('topic', Integer),
	Column('topic_time', Integer),
	Column('topic_owner', String(40)),
	Column('antispam', ForeignKey('antispam.id')),
	Column('autokick', String(5)),
	Column('censor', Boolean),
	Column('antishock', Boolean),
	)

chanuser_table = Table('chanuser', metadata,
	Column('id', Integer, primary_key=True),
	Column('name', String(40)),
	Column('channel', String(40)),
	Column('admin', Boolean),
	Column('banned', String),
	Column('allowed', Boolean),
	Column('mute', Integer),
	)

antispam_table = Table('antispam', metadata,
	Column('id', Integer, primary_key=True),
	Column('enabled', Boolean),
	Column('quiet', Boolean),
	Column('duration', Integer),
	Column('timeout', Integer),
	Column('bonus', Integer),
	Column('unique', Integer),
	Column('bonuslength', Integer),
	)

bans_table = Table('ban_groups', metadata, # server bans
	Column('id', Integer, primary_key=True),
	Column('reason', String(120)),
	Column('end_time', Integer), # seconds since unix epoch
	)

aggregatebans_table = Table('ban_items', metadata, # server bans
	Column('id', Integer, primary_key=True),
	Column('type', String(10)), # what exactly is banned (user, ip, subnet, hostname, ip range, etc)
	Column('data', String(60)), # regex would be cool
	Column('ban_id', ForeignKey('bans.id')),
	)

mapper(User, users_table, properties={
	'addresses':relation(Address, backref='user', cascade="all, delete, delete-orphan"),
	'renames':relation(Rename, backref='user', cascade="all, delete, delete-orphan"),
	})
mapper(Address, addresses_table)
mapper(Rename, renames_table)
mapper(Channel, channels_table, properties={
	'antispam':relation(AntiSpam, backref='channel', cascade="all, delete, delete-orphan")
	})
mapper(ChanUser, chanuser_table)
mapper(AntiSpam, antispam_table)
mapper(Ban, bans_table)
mapper(AggregateBan, aggregatebans_table, properties={
	'ban':relation(Ban, backref='item', cascade="all, delete, delete-orphan")
	})

#metadata.create_all(engine)

class UsersHandler:
	def __init__(self, root, engine):
		self._root = root
		metadata.create_all(engine)
		Session = sessionmaker(bind=engine, autoflush=True, transactional=True)
		self.session = Session()
	
	def check_ban(self, user=None, ip=None, userid=None):
		results = self.session.query(AggregateBan)
		subnetbans = results.filter(AggregateBan.type=='subnet')
		userban = results.filter(AggregateBan.type=='user').filter(AggregateBan.data==user)
		ipban = results.filter(AggregateBan.type=='ip').filter(AggregateBan.data=ip)
		useridban = results.filter(AggregateBan.type=='userid').filter(AggregateBan.data==userid)
		
	def login_user(self, user, password, ip, userid=None):
		good = True
		now = int(time.time())
		entry = self.session.query(User).filter(User.name==user).first() # should only ever be one user with each name so we can just grab the first one :)
		reason = entry
		if not entry:
			return False, 'No user named %s'%user
		if not password == entry.password:
			good = False
			reason = 'Invalid password'
		#if entry.banned > 0:
			#if entry.banned > now:
				#good = False
				#timeleft = entry.banned - now
				#daysleft = '%.2f'%(float(seconds) / 60 / 60 / 24)
				#if daysleft >= 1:
					#reason = 'You are banned: (%s) days remaining.' % daysleft
				#else:
					#reason = 'You are banned: (%s) hours remaining.' % (float(seconds) / 60 / 60)
		exists = self.session.query(Address).filter(Address.user_id==entry.id).first()
		if not exists:
			entry.addresses.append(Address(ip_address=ip))
		entry.last_login = now
		entry.last_ip = ip
		self.session.commit()
		return good, reason

	def register_user(self, user, password, ip): # need to add better ban checks so it can check if an ip address is banned when registering an account :)
		results = self.session.query(User).filter(User.name==user).first()
		if results:
			return False, 'Username already exists.'
		entry = User(user, password, ip)
        entry.addresses.append(Address(ip_address=ip))
		self.session.save(entry)
		self.session.commit()
		return True, 'Account registered successfully.'

	def rename_user(self, user, newname):
		results = self.session.query(User).filter(User.name==newname).first()
		if results:
			return False, 'Username already exists.'
		entry = self.session.query(User).filter(User.name==user).first()
		entry.name = newname
		self.session.save(entry)
		self.session.commit()
		return True, 'Account renamed successfully.'

	def remove_user(self, user):
		entry = self.session.query(User).filter(User.name==user).first()
		if not entry:
			return False, 'User not found.'
		self.session.delete(entry)
		self.session.commit()
		return True, 'Success.'
	
	def load_channels(self):
		response = self.session.query(Channel)
		for channel in response:
			channels.append({})
		return channels
	
	def save_channel(self, channel):
		entry = self.session.query(Channel)
		entry.password = channel[
		entry.owner = channel[
		entry.topic = channel[
		entry.topic_time = channel[
		entry.topic_owner = channel[
		entry.antispam = channel[
		entry.autokick = channel[
		entry.censor = channel[
		entry.antishock = channel[
		entry.censor = channel[

	def save_channels(self, channels):
		for channel in channels:
			self.save_channel(channel)
