from bs4 import BeautifulSoup
import requests, json
from threading import Thread
from multiprocessing import Queue
from queue import Empty


request_accepts = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
user_agent = 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'

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
		rsp = requests.get(link, headers={'User-Agent': user_agent, 'Accept': request_accepts})
	except Exception as e:
		print('An exception occured: {}'.format(e))
		return open_file(file_)
	if not rsp.ok:
		print('Invalid response gotten from main page, code: {}'.format(rsp.status_code))
		return open_file(file_)
	return rsp.content


def main_page_scrapper():
	main_url = 'http://top-topics.thefullwiki.org'
	current_site = main_url + '/Cities,_towns_and_villages_in_Nigeria'
	rsp = get_data_or_file(current_site, None)
	if not rsp:
		return
	a = []
	soup = BeautifulSoup(rsp)
	all_ul_tags = soup.findAll('ul', attrs={'class': 'topic_hit_stats_subcategories'})
	if len(all_ul_tags) == 0:
		print( 'No tags found' )
		exit(0)
	for state_links in all_ul_tags:
		links = state_links.findAll('li')
		for link in links:
			for l in link.children:
				a.append( [l.text, main_url + l.attrs['href']] )
	return a[:37]


def file_content(content):
	soup = BeautifulSoup(content)
	all_towns = soup.findAll('td', attrs={'class': 'topic_hit_stats_topic'})
	a = []
	for town in all_towns:
		a.append(town.text)
	return a


def scrapper(urls, result):
	try:
		while True:
			data = urls.get_nowait()
			key, link = data
			rsp = get_data_or_file(link, None)
			result[key] = file_content(rsp)
	except Empty as empty_exception:
		print(empty_exception)


if __name__ == '__main__':
	result = main_page_scrapper()
	if result is None:
		print('No result obtained')
		exit(0)
	queue = Queue()
	for r in result:
		queue.put( r )
	thread_list = []
	result = {}
	for i in range(10):
		new_thread = Thread(target=scrapper, args=[queue, result])
		thread_list.append(new_thread)
		new_thread.start()
	for my_thread in thread_list:
		if my_thread.is_alive():
			my_thread.join()
	queue.close()
	with open('result.json', 'w') as my_file:
		my_file.write(json.dumps(result, indent=2, separators=(',', ': ')))
