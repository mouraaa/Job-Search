import requests 
import smtplib 
import keyring 
from bs4 import BeautifulSoup 
from csv import writer 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from os import path 

url = "https://newyork.craigslist.org/search/etc"
job_counter = 0
page_number = 0

#print data to CSV file
def printData(url,job_counter,page_number):
	response = requests.get(url) 
	soup = BeautifulSoup(response.content, 'html.parser')
	jobs = soup.findAll(class_="result-info") 

	with open('jobs.csv', 'a') as csv_file: 
		csv_writer = writer(csv_file)
		if not path.exists('jobs.csv'): #if the path doesn't exist, add the headers
			headers = ['number','title','date','location','attributes','link'] 
			csv_writer.writerow(headers)
		for job in jobs:
			title = job.find(class_="result-title").getText() 
			date = job.find(class_="result-date").getText()
			location_tag = job.find(class_="result-hood") 
			location = location_tag.getText() if location_tag else "N/A"
			link = job.find('a')['href'] 
																		 

			#NAVIGATE TO THE JOB DESCRIPTION PAGE INSIDE EACH JOB
			job_response = requests.get(link) 
			job_soup = BeautifulSoup(job_response.content,'html.parser') 
			job_attributes_tag = job_soup.find(class_="attrgroup") 
			job_attributes = job_attributes_tag.getText() if job_attributes_tag else "N/A"
			job_counter += 1
			csv_writer.writerow([job_counter,title,date,location,job_attributes,link])	

	page_number += 1
	print("Page " + str(page_number) + " completed")	

	#NAVIGATE TO THE NEXT PAGE
	nextPage = soup.find(class_='button next') 
	if nextPage.get('href'):
		url = 'https://newyork.craigslist.org' + nextPage.get('href')
		printData(url,job_counter,page_number)


def sendMail():
	sender_email = 'youremail@mail.com'
	password = 'email password'
	with open('mailinglist.txt') as f:
		for i in f:	
			try:
				email_receiver = i.lower().rstrip()
				msg = MIMEMultipart()
				msg['From'] = sender_email
				msg['To'] = email_receiver
				msg['Subject'] = "This Week's Job Listing!"

				body = "Dont forget to check out this week's job listing. See attatchment for more details!"
				msg.attach(MIMEText(body,'plain'))

				filename = 'jobs.csv'
				attachment = open(filename,'rb')

				part = MIMEBase('application','octet-stream')
				part.set_payload((attachment).read())
				encoders.encode_base64(part)
				part.add_header('Content-Disposition',"attachment; filename= " + filename)

				msg.attach(part)
				text = msg.as_string()
				server = smtplib.SMTP('smtp-mail.outlook.com', 587)
				server.starttls()
				server.login(sender_email,password)
				server.sendmail(sender_email,email_receiver,text)
				server.quit()

			except:
				print("Mailing went south...")


printData(url,job_counter,page_number)
sendMail()
print("All Emails sent!")




