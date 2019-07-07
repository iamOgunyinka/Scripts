import requests, json, os

request_accepts = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0'
main_url = 'http://www.geonames.org/childrenJSON?geonameId='
headers = { 'User-Agent': user_agent, 'Accept': request_accepts,
	'Accept-Encoding': 'gzip, deflate',
	'Accept-Language': 'en-US,en;q=0.5', 'Connection':'keep-alive',
	'Host':'www.geonames.org', 'Upgrade-Insecure-Requests': '1'
}

def get_data_or_file(link, file_=None):
	def open_file(file_):
		if not file_:
			return None
		rsp = ''
		with open(file_) as w:
			for wx in w:
				rsp += wx
		return rsp
	try:
		rsp = requests.get(link, headers=headers)
	except Exception as e:
		print('An exception occured: {}'.format(e))
		return open_file(file_)
	if not rsp.ok:
		print('Invalid response gotten from page, code: {}'.format(rsp.status_code))
		return open_file(file_)
	return rsp.content.decode()

class Earth:
	def __init__(self, name, geo_id):
		self._name = name
		self._geoid = geo_id
		self._continents = []
		
	@property
	def children(self):
		return self._continents
	
	@children.setter
	def children(self, items):
		self._continents = items
	
	def to_json(self):
		return {'name': self._name, 'continents': [continent.to_json() for continent in self.children]}

class Continent:
	def __init__(self, name, geo_id):
		self._name = name
		self._geoid = geo_id
		self._countries = []

	def name(self):
		return self._name
	
	@property
	def children(self):
		return self._countries
		
	@children.setter
	def children(self, items):
		self._countries = items
	
	def to_json(self):
		return {'name': self._name, 'countries': [country.to_json() for country in self.children]}

class Country:
	def __init__(self, name, geo_id):
		self._name = name
		self._geoid = geo_id
		self._states = []

	@property
	def children(self):
		return self._states
		
	def set_name(self, name):
		self._name = name
	
	@children.setter
	def children(self, items):
		self._states = items
	
	def to_json(self):
		return {'name': self._name, 'states': [state.to_json() for state in self.children]}

class State:
	def __init__(self, name, geo_id):
		self._name = name
		self._geoid = geo_id
		self._local_gvts = []

	@property
	def children(self):
		return self._local_gvts
		
	@children.setter
	def children(self, items):
		self._local_gvts = items
	
	def to_json(self):
		return {'name': self._name, 'lgs': [lg.to_json() for lg in self._local_gvts]}

class LocalGovernment:
	def __init__(self, name, geo_id):
		self._name = name
		self._geoid = geo_id
		self._cities = []
		
	@property
	def children(self):
		return self._cities
	
	@children.setter
	def children(self, items):
		self._cities = items
	
	def to_json(self):
		return {'name': self._name, 'cities': [city.to_json() for city in self._cities]}

class City:
	def __init__(self, name, geo_id):
		self._name = name
		self._geoid = geo_id
		
	@property
	def children(self):
		return []
	
	@children.setter
	def children(self, items):
		self._name = items
	
	def to_json(self):
		return {'name': self._name}

def file_content(rsp, Type):
	data = json.loads(rsp)
	geonames = data.get('geonames')
	result = []
	if geonames is not None:
		for info in geonames:
			result.append(Type(info.get('name'), info.get('geonameId')))
	return result

def get_info(geo_id, name, ChildType: type):
	link = main_url + str(geo_id)
	lists = []
	rsp = get_data_or_file(link, None)
	if rsp is not None:
		lists = file_content(rsp, ChildType)
	return lists

def scrape(item, ChildType):
	item.children = get_info(item._geoid, item._name, ChildType)

if __name__ == '__main__':
	earth = Earth('World', 6295630)
	scrape(earth, Continent)
	r = tuple(filter(lambda continent: 'Africa' in continent.name(), earth.children))
	if len(r) == 0:
		exit(0)
	african_continent = r[0]
	print('Found continent: {}'.format(african_continent.name()))
	scrape(african_continent, Country)
	for country in african_continent.children:
		scrape(country, State)
		for state in country.children:
			scrape(state, LocalGovernment)
	with open('result.json', 'w') as my_file:
		my_file.write(json.dumps(earth.to_json(), indent=2, separators=(',', ': ')))
