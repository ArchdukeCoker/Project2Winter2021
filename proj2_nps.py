#################################
##### Name: Dylan Coakley   #####
##### Uniqname: dcoakley    #####
#################################


from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key
import time


BASE = 'https://www.nps.gov'
API_CONSUMER_KEY = secrets.CONSUMER_KEY
SECRET_CONSUMER_KEY = secrets.CONSUMER_KEY_SECRET


class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.

    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    def __init__(self, name, address, zipcode, phone, category=None):
        self.category = category
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.phone = phone

    def info(self): #this only needs self because self has all the attributes we are looking for
        return(f"{self.name} ({self.category}): {self.address} {self.zipcode}")


class MapQuest_Place:
    '''a mapquest location

    Instance Attributes
    -------------------
    name: string
        the name of the location (e.g. 'TA Monroe')

    category: string
        the category of the location (e.g. 'Scales Public')
        some places have no category

    address: string
        the address of the location (e.g. 'I-75 Exit 15')
        some places have no address

    city: string
        the city in which the location is located (e.g. 'Monroe')
        some places have no city
    '''
    def __init__(self, name, category='no category', address='no address', city='no city'):
        self.name = name
        self.category = category
        self.address = address
        self.city = city
    
    def info(self):
        return(f'- {self.name} ({self.category}): {self.address}, {self.city}')


def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    #base = 'https://www.nps.gov'

    begin = '/index.htm'

    url = BASE + begin

    #response = requests.get(url)

    state_url_cache_dict = open_cache('state_url_cache.json')

    if url in state_url_cache_dict:
        #print('Using cache')
        return(state_url_cache_dict[url])

    else:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        state_parent = soup.find('ul', class_='dropdown-menu SearchBar-keywordSearch')
        state_info = state_parent.find_all('li', recursive=False)

        url_collector = []
        for x in state_info:
            y = x.find('a')
            z = y['href']
            url_collector.append(BASE+z)

        state_name_collector = []
        for a in state_info:
            b = a.find('a')
            c = b.text
            d = c.lower()
            state_name_collector.append(d)

        state_site_dict = {state_name_collector[i]: url_collector[i] for i in range(len(state_name_collector))}
        #https://www.geeksforgeeks.org/python-convert-two-lists-into-a-dictionary/ used this source to learn about dict comprehension

        state_url_dict = {url: state_site_dict}

        save_cache('state_url_cache.json', state_url_dict)

        #print('Fetching')
        return(state_site_dict)


def get_site_instance(site_url):
    '''Make an instances from a national site URL.

    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov

    Returns
    -------
    instance
        a national site instance
    '''

    site_instance_cache_dict = open_cache('site_instance.json')

    if site_url in site_instance_cache_dict:
        return(NationalSite(site_instance_cache_dict[site_url][0], site_instance_cache_dict[site_url][1], site_instance_cache_dict[site_url][2], site_instance_cache_dict[site_url][3], site_instance_cache_dict[site_url][4]))

    else:
        response = requests.get(site_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        parent = soup.find('div', class_='Hero-titleContainer clearfix')


        name_parent = parent.find('a', class_='Hero-title')
        name = name_parent.text

        try:
            category_parent = parent.find('span', class_='Hero-designation')
            category = category_parent.text
        except:
            category = None


        address_parent = soup.find('div', class_='mailing-address')

        try:
            city_parent = address_parent.find('span', itemprop='addressLocality')
            city = city_parent.text
        except:
            city = 'Yosemite'

        try:
            state_parent = address_parent.find('span', class_='region')
            state = state_parent.text 
        except AttributeError:
            try:
                state_parent = address_parent.find('span', itemprop='addressRegion')
                state = state_parent.text
            except:
                state = 'CA'

        try:
            zip_parent = address_parent.find('span', itemprop='postalCode')
            zipcode = zip_parent.text
            zipp = zipcode.strip()
        except:
            zipp = '95389'

        phone_parent = soup.find('div', class_='vcard')
        phone_test = phone_parent.find('span', itemprop='telephone')
        phone = phone_test.text
        cut = phone[1:]

        state_city = f'{city}, {state}'
        nat_site_inst = NationalSite(name, state_city, zipp, cut, category)
        site_instance_cache_dict[site_url] = [name, state_city, zipp, cut, category]
        save_cache('site_instance.json', site_instance_cache_dict)

        return nat_site_inst


def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.

    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov

    Returns
    -------
    list
        a list of national site instances
    '''

    state_sites_cache = open_cache('state_site_url_cache.json')

    if state_url in state_sites_cache:
        list_of_state_site_url_bits = state_sites_cache[state_url]
        key_coll = []

        for key in list_of_state_site_url_bits:
            key_coll.append(key)

        national_site_collector = []
        for x in list_of_state_site_url_bits[key_coll[0]]:
            print('Using cache')
            state_nat_site_inst = get_site_instance(BASE+x)
            national_site_collector.append(state_nat_site_inst)

        print('--------------------------------------------------------------------------------')
        print(f'List of National Sites in {key_coll[0]}') # figure out how to get the state names in the cache as well, might have to get a get state name function
        print('--------------------------------------------------------------------------------')
        i = 1
        for x in national_site_collector:
            print(f'[{i}] {x.info()}')
            i+=1
        return(national_site_collector)

    else:
        response = requests.get(state_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        title_obj = soup.find('h1', class_='page-title')
        state_name = title_obj.text
        #print(state_name)

        state_site_parent = soup.find_all('div', class_='col-md-9 col-sm-9 col-xs-12 table-cell list_left')

        state_url_collector = []
        for elements in state_site_parent:
            test = elements.find('a')
            test2 = test['href']
            state_url_collector.append(test2)
        #print(state_url_collector)

        inner_dict = {state_name: state_url_collector}
        outer_dict = {state_url: inner_dict}

        save_cache('state_site_url_cache.json', outer_dict)
        print('Fetching')
        national_site_collector = []
        for x in state_url_collector:
            print('Fetching')
            state_nat_site_inst = get_site_instance(BASE+x)
            national_site_collector.append(state_nat_site_inst)


        print('--------------------------------------------------------------------------------')
        print(f'List of National Sites in {state_name}') # figure out how to get the state names in the cache as well, might have to get a get state name function
        print('--------------------------------------------------------------------------------')
        i = 1
        for x in national_site_collector:
            print(f'[{i}] {x.info()}')
            i+=1
        return(national_site_collector)


def get_nearby_places(site_object):

    '''Obtain API data from MapQuest API.

    Parameters
    ----------
    site_object: object
        an instance of a national site

    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    places_cache = open_cache('mapquest_place.json')
    url = 'http://www.mapquestapi.com/search/v2/radius?'
    key = API_CONSUMER_KEY
    origin = site_object.zipcode
    national_place_name = site_object.name
    rad_max_resp = '10'
    ambiguities = 'ignore'
    out_Format='json'

    api_call_url =  url+'origin='+origin+'&radius='+rad_max_resp+'&maxMatches='+rad_max_resp+'&ambiguities='+ambiguities+'&outFormat='+out_Format+'&key='+API_CONSUMER_KEY

    if origin in places_cache:
        print('Using cache')
        place_inst_coll = []
        for i in range(11):
            try:
                name = places_cache[origin]['searchResults'][i]['name']
                if places_cache[origin]['searchResults'][i]['fields']['group_sic_code_name'] != '':
                    category = places_cache[origin]['searchResults'][i]['fields']['group_sic_code_name']
                else:
                    category = 'no category'
                if places_cache[origin]['searchResults'][i]['fields']['address'] != '':
                    address = places_cache[origin]['searchResults'][i]['fields']['address']
                else:
                    address = 'no address'
                if places_cache[origin]['searchResults'][i]['fields']['city'] != '':
                    city = places_cache[origin]['searchResults'][i]['fields']['city']
                else:
                    city = 'no city'
                place_inst_coll.append(MapQuest_Place(name, category, address, city))
            except IndexError:
                continue

        print('--------------------------------------------------------------------------------')
        print(f'Places near {national_place_name}') # figure out how to get the state names in the cache as well, might have to get a get state name function
        print('--------------------------------------------------------------------------------')
        for x in place_inst_coll:
            print(x.info())

        place_cache_dict = {api_call_url: place_inst_coll}
        return(place_cache_dict)

    else:
        response = requests.get(api_call_url)
        print('Fetching')
        json = response.json()
        place_cache_dict = {origin: json}
        save_cache('mapquest_place.json', place_cache_dict)

        place_inst_coll = []
        for i in range(11):
            try:
                #print(json['searchResults'][i])
                name = json['searchResults'][i]['name']
                if json['searchResults'][i]['fields']['group_sic_code_name'] != '':
                    category = json['searchResults'][i]['fields']['group_sic_code_name']
                else:
                    category = 'no category'
                if json['searchResults'][i]['fields']['address'] != '':
                    address = json['searchResults'][i]['fields']['address']
                else:
                    address = 'no address'
                if json['searchResults'][i]['fields']['city'] != '':
                    city = json['searchResults'][i]['fields']['city']
                else:
                    city = 'no city'
                place_inst_coll.append(MapQuest_Place(name, category, address, city))
            except IndexError:
                continue

        print('--------------------------------------------------------------------------------')
        print(f'Places near {national_place_name}') # figure out how to get the state names in the cache as well, might have to get a get state name function
        print('--------------------------------------------------------------------------------')
        for x in place_inst_coll:
            print(x.info())

        place_cache_dict = {api_call_url: place_inst_coll}
        return(place_cache_dict)


def open_cache(cache_file):
    '''Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary

    Parameters
    ----------
    cache_file: str
        The cache filename

    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(cache_file, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict
    #this code was modified the SI507 lecture file PersistCache.py


def save_cache(cache_file, cache_dict):
    ''' Saves the current state of the cache to disk

    Parameters
    ----------
    cache_file: str
        The cache filename

    cache_dict: dict
        The dictionary to save

    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(cache_file,"w")
    fw.write(dumped_json_cache)
    fw.close()
    #this code was modified the SI507 lecture file PersistCache.py


def main():
    ''' Asks the user to input a state name or exit the
    program. Tells user if their input is unacceptable
    and starts over. Runs the build state url dict and
    checks to see if the users input is in the dictionary.
    Then runs get sites for states and prints out a list
    of the national sites in the the selected state.


    Parameters
    ----------
    None

    Returns
    -------
    None
    '''
    print('Enter a state name (e.g. Michigan or michigan) or "exit"')
    input1 = input(':').lower()
    state_dict = build_state_url_dict()
    #STEP1
    if input1 == 'exit':
        print('Bye!')
    else:
        while True:
            try:
                if input1 in state_dict:
                    site_inst = get_sites_for_state(state_dict[input1])
                    print('--------------------------------------------------------------------------------')
                    print('')
                    print('Choose the number for detail or search "exit" or "back"')
                    input2 = input(':')
                    try:
                        if int(input2):
                            index = int(input2) - 1
                            get_nearby_places(site_inst[index])
                            try:
                                print('')
                                print('Choose the number for detail or search "exit" or "back"') #fix this bit i think just enter exit to finish or back to return to the last level
                                input2 = input(':')
                                if input2.lower() == 'exit':
                                    break
                                elif input2.lower() == 'break':
                                    continue
                                else:
                                    print('[Error] Invalid input')
                                    print('--------------------------------------------------------------------------------')
                                    time.sleep(1)
                                    print('')
                                continue
                            except:
                                print('[Error] Invalid input')
                                print('--------------------------------------------------------------------------------')
                                time.sleep(1)
                                print('')
                            continue
                        else:
                            print('[Error] Invalid input')
                            print('--------------------------------------------------------------------------------')
                            time.sleep(1)
                            print('')
                            continue
                    except:
                        if input2 == 'exit':
                            (print('Bye!'))
                            break
                        elif input2 =='back':
                            print('Enter a state name (e.g. Michigan or michigan) or "exit"')
                            input1 = input(':').lower()
                        else:
                            print('[Error] Invalid input')
                            print('--------------------------------------------------------------------------------')
                            time.sleep(1)
                            print('')
                            continue
                elif input1 == 'exit':
                    print('Bye!')
                    break
                else:
                    print('[Error] Enter proper state name')
                    print('--------------------------------------------------------------------------------')
                    time.sleep(1)
                    print('')
                    print('Enter a state name (e.g. Michigan or michigan) or "exit"')
                    input1 = input(':').lower()
                    continue
            except ValueError:
                print('[Error] Enter proper state name')
                print('--------------------------------------------------------------------------------')
                time.sleep(1)
                print('')
                print('Enter a state name (e.g. Michigan or michigan) or "exit"')
                input1 = input(':').lower()
                continue


if __name__ == "__main__":
    main()