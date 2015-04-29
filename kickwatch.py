#!/usr/bin/env python

from bs4 import BeautifulSoup

import requests
import time
import sys
import webbrowser

class Reward:
	def __init__(self, name='', desc='', amount=0, backerLimit=-1, backers=0):
		self.name = name
		self.desc = desc
		self.amount = amount
		self.backerLimit = backerLimit
		self.backers = backers

	def display(self):
	   	print("Name : " + self.name +  ", amount: " + str(self.amount) +  ", backers: " + str(self.backers) +  "/" + str(self.backerLimit) + "Desc : " + self.desc + ".")

	def shortDescription(self):
		return str(self.amount) + '$\t' + self.name  + ' ' + str(self.backers) + '/' + str(self.backerLimit) + ' backers'

	def hasBackerLimit(self):
		return self.backerLimit > 0

	def isSoldOut(self):
		return self.backers == self.backerLimit

	def isAvailable(self):
		return not self.hasBackerLimit() or (self.hasBackerLimit() and not reward.isSoldOut())

def log(text):
	print("[" + time.strftime('%X %x %Z') + "] " + text)

def decrement(number):
	return int(number)-1

def numberize(textToNumberize, toFloat=0):
	number = textToNumberize.encode('ascii','ignore')
	nondigits = number.translate(None, '0123456789.')
	number = number.translate(None, nondigits)
	if toFloat:
		return float(number)
	else:
		return number

def showRewardsMenu():
	rewards = []
	populateRewards(rewards)
	i = 1
	for reward in rewards:
		if reward.hasBackerLimit():
			print('[' + str(i) + '] ' + str(reward.amount) + '$\t' + reward.name  + ' ' + reward.backers + '/' + reward.backerLimit + ' backers')
		i += 1
	return len(rewards)

def checkReward(reward):
	if reward.hasBackerLimit() and not reward.isSoldOut():
		log("\n------\nREWARD IS AVAILABLE:\n")
		log(reward.shortDescription())
		log("\n------\n")
		webbrowser.open_new_tab(url+"/pledge/new?ref=manage_pledge")
		time.sleep(10)
		sys.exit(0)
	else:
		log("No luck yet...")

def populateRewards(rewardsArray):
	
	log("Fetching data...")
	r  = requests.get(url)

	data = r.text
	log("Parsing data...")
	soup = BeautifulSoup(data)

	rewards_html = soup.find_all('li',class_='NS-projects-reward')
	getOneRewardInfo = lambda x : x.find_all('div',class_='NS_backer_rewards__reward')[0]
	rewards_html = map(getOneRewardInfo,rewards_html)

	skip = 0
	for reward_html in rewards_html:
		if skip:
			log("Skipped reward")
			skip -= 1
			continue

		reward = Reward()
			# amount
		amount = reward_html.h5.contents[0]
		reward.amount = numberize(amount,1)

		backerLimits_html = reward_html.find_all('p',class_='backers-limits')[0]
		backersData = backerLimits_html.find('span', class_='num-backers')
		# backers
		reward.backers = numberize(backersData.string)
		# backer limit
		if backerLimits_html.find('span', class_='sold-out'):
			reward.backerLimit = reward.backers
		else:
			backersLimitData = backerLimits_html.find('span', class_='limited-number')
			if backersLimitData:
				reward.backerLimit = numberize(backersLimitData.string.split('left of')[1])	
		
		description = reward_html.find_all('div',class_='desc')[0].text.lstrip()
		# name
		reward.name = description.split('\n')[0].encode("utf8")
		# description
		reward.desc = description.encode("utf8")
		rewardsArray.append(reward)

interval = raw_input('\nEnter interval for checks in seconds (eg. 60): ')
interval = int(interval)
url = raw_input('\nEnter kickstarter campaign url (eg. https://www.kickstarter.com/projects/tiko3d/tiko-the-unibody-3d-printer): ')

rewardCount = showRewardsMenu()
userRewardsInput = raw_input('Enter one or more reward number separated by spaces (eg. 1 6 8) or none for any limited reward:')
rewardIndexes = map(decrement, userRewardsInput.split());
if len(rewardIndexes) == 0:
	rewardIndexes = xrange(1,rewardCount)

while True:
	rewards = []
	populateRewards(rewards)
	for index in rewardIndexes:
		reward = rewards[index]
		log("Reward [" + str(index+1) + "]")
		log(reward.shortDescription())
		checkReward(reward)
	time.sleep(interval)
