"""
    Copyright (c) 2013 Joshua Machol
    MIT, see LICENSE for more details.
"""

import urllib.request
import operator
import json
import bs4
import re




class Hero:
    def __init__(self, hero_id):
        self.hero_id = hero_id
        self.img_url = ''
        self.portrait_img_url = ''
        self.name = ''
        self.title = ''
        self.description = ''
        self.lore = ''
        self.allegiance = ''
        self.primary_attribute = ''
        self.atk_type = ''
        self.roles = ''
        self.int = ''
        self.agi = ''
        self.str = ''
        self.dmg = ''
        self.move_spd = ''
        self.armor = ''
        self.sight_range = ''
        self.atk_range = ''
        self.missile_spd = ''
        self.abilities = []  # list of type Ability


class Ability:
    def __init__(self, hero_id):
        self.ability_id = ''
        self.hero_id = hero_id
        self.img_url = ''
        self.vid_url = ''
        self.name = ''
        self.description = ''
        self.lore = ''
        self.mana_cost = ''
        self.cooldown = ''
        self.details = []  # list of type AbilityDetail


class AbilityDetail:
    def __init__(self, ability_id):
        self.ability_id = ability_id
        self.name = ''
        self.detail = ''


def soupify(url):
    print("soupifying '{}'".format(url))
    page = urllib.request.urlopen(url)
    soup = bs4.BeautifulSoup(page, "html.parser")
    if not soup:
        raise ValueError("soup is '{}'", soup)
    return soup


def get_hero_urls():
    soup = soupify("http://www.dota2.com/heroes/")
    tags = soup(href=re.compile("http://www.dota2.com/hero/"))
    return [t['href'] for t in tags]

def _scrape_hero_ability(ability_soup, hero_id, ability_id):
    a = Ability(hero_id)
    a.ability_id = ability_id
    a.img_url = ability_soup.find(class_='overviewAbilityImg')['src']
    vid_soup = ability_soup.find(class_='abilityVideoContainer')
    if vid_soup:
        iframe = vid_soup.find('iframe')
        a.vid_url = iframe['src']
    ability_row_description = (ability_soup.find(class_='abilityHeaderRowDescription') or
                               ability_soup.find(class_='overviewAbilityRowDescription'))
    a.name = ability_row_description.find('h2').string
    a.description = ability_row_description.find('p').text.rstrip()
    lore_soup = ability_soup.find(class_='abilityLore')
    if lore_soup:
        a.lore = lore_soup.string
    mana_soup = ability_soup.find(class_='mana')
    if mana_soup:
        a.mana_cost = list(mana_soup.stripped_strings)[1]
    cooldown_soup = ability_soup.find(class_='cooldown')
    if cooldown_soup:
        a.cooldown = list(cooldown_soup.stripped_strings)[1]
    details_soup = ability_soup.find(class_='abilityFooterBoxRight')
    details = list(details_soup.stripped_strings)
    for name, detail in zip(details[::2], details[1::2]):
        d = AbilityDetail(a.ability_id)
        d.name = name[:-1]
        d.detail = detail
        a.details.append(d)
    return a


def _scrape_hero_abilities(soup_, hero_id):
    divs = soup_(class_='abilitiesInsetBoxContent')
    output_array = []
    ability_id = 0
    for d in divs:
        output_array.append(_scrape_hero_ability(d, hero_id, ability_id))
        ability_id += 1
    return output_array


def _scrape_hero(soup_, hero_id):
    print(("scraping '{}'"
           .format(soup_.find(id='centerColContent').find('h1').string)))
    h = Hero(hero_id)
    h.img_url = soup_.find(id='heroTopPortraitIMG')['src']
    h.portrait_img_url = soup_.find(id='heroPrimaryPortraitImg')['src']
    h.name = soup_.find(id='centerColContent').find('h1').string
    h.title = ''
    h.lore = list(soup_.find(id='bioInner').stripped_strings)[0]
    prim_style = soup_.find(id='overviewIcon_Primary')['style']
    if prim_style == 'top:83px':
        h.primary_attribute = 'str'
    elif prim_style == 'top:43px':
        h.primary_attribute = 'agi'
    elif prim_style == 'top:1px':
        h.primary_attribute = 'int'
    h.atk_type = soup_.find(class_='bioTextAttack').string
    roles_soup = soup_.find(id='heroBioRoles')
    if len(roles_soup.contents) > 1:
        h.roles = roles_soup.contents[1].strip(' - ')
    h.int = soup_.find(id='overview_IntVal').string
    h.agi = soup_.find(id='overview_AgiVal').string
    h.str = soup_.find(id='overview_StrVal').string
    h.dmg = soup_.find(id='overview_AttackVal').string
    h.move_spd = soup_.find(id='overview_SpeedVal').string
    h.armor = soup_.find(id='overview_DefenseVal').string
    misc_stats = soup_(class_='statRowCol2W')
    h.sight_range = misc_stats[0].string
    h.atk_range = misc_stats[1].string
    h.missile_spd = misc_stats[2].string
    h.abilities = _scrape_hero_abilities(soup_, h.hero_id)
    return h

if __name__ == '__main__':
    heros = []
    urls = get_hero_urls()
    hero_id = 0;
    for url in urls:
        soup = soupify(url)
        heros.append(_scrape_hero(soup, hero_id))
        hero_id += 1
    json = json.dumps(heros, separators=(',', ':'),
                      default=operator.attrgetter("__dict__"))
    f = open('heroes_json.txt', 'w')
    print('writing JSON to file "heroes_json.txt')
    f.write(json)
    f.close()
    print('done')
