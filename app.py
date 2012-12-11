# -*- coding: utf-8 -*-
import os, datetime
import re
from unidecode import unidecode

from flask import Flask, request, render_template, redirect, abort
from flask import jsonify

# import all of mongoengine
from mongoengine import *

# import data models
import models

# Twilio
from twilio.rest import TwilioRestClient

app = Flask(__name__)   # create our flask app
app.config['CSRF_ENABLED'] = False

# --------- Database Connection ---------
# MongoDB connection to MongoLab's database
connect('mydata', host=os.environ.get('MONGOLAB_URI'))
app.logger.debug("Connecting to MongoLabs")

# hardcoded categories for the checkboxes on the form
categories = ['web','physical computing','software','video','music','installation','assistive technology','developing nations','business','social networks']

# --------- Routes ----------

# this is our main page
@app.route("/", methods=['GET','POST'])
def index():

	# get Idea form from models.py
	idea_form = models.IdeaForm(request.form)
	
	# if form was submitted and it is valid...
	if request.method == "POST" and idea_form.validate():

		# somewhere here to create deadline datetime field
		currentTime = datetime.datetime.now()

		# get form data - create new idea
		idea = models.Idea()
		idea.creator = request.form.get('creator','anonymous')
		idea.title = request.form.get('title','no title')
		idea.slug = slugify(idea.title + str(currentTime))
		idea.idea = request.form.get('idea','')
		idea.categories = request.form.getlist('categories') # getlist will pull multiple items
		idea.duration = request.form.get('duration','no duration') # for duration
		idea.timeHour = request.form.get('timeHour','no timeHour') # for timeHour
		idea.timeHour2 = request.form.get('timeHour2','') # for timeHour
		idea.timeMinute = request.form.get('timeMinute','no timeMinute') # for timeMinute
		idea.timeAmPm = request.form.get('timeAmPm','no timeAmPm') # for timeAmPm


		# convert GMT to Eastern Time
		eastToGmtTimeConvert = currentTime - datetime.timedelta(0, 60*60)

		# add user's deadline
		# example add 20 minutes
		userminutes = int(request.form.get("timeHour2")) # convert to int
		#idea.deadline = currentTime + datetime.timedelta(0, userminutes*60)
		#idea.deadline = eastToGmtTimeConvert + datetime.timedelta(0, userminutes*60)
		#trying with conversion
		idea.deadline = currentTime + datetime.timedelta(0, userminutes*60)
		# tried this with Zena: idea.now = idea.deadline-currentTime.seconds/60
		#idea.minutesRemaining = idea.deadline - currentTime

		idea.save() # save it

		# redirect to the new idea page
		return redirect('/hungryfr/%s' % idea.slug)

	else:

		# for form management, checkboxes are weird (in wtforms)
		# prepare checklist items for form
		# you'll need to take the form checkboxes submitted
		# and idea_form.categories list needs to be populated.
		if request.method=="POST" and request.form.getlist('categories'):
			for c in request.form.getlist('categories'):
				idea_form.categories.append_entry(c)

		# render the template
		templateData = {
			'ideas' : models.Idea.objects(deadline__gte= datetime.datetime.now()).order_by('+deadline'),
			'categories' : categories,
			'currentTime' : datetime.datetime.now(),
			'form' : idea_form
			#'timeDisplay' : models.timeDisplay.currentTimeDisplay
		}

		return render_template("main.html", **templateData)

# this is our departures page
@app.route("/cron")
def cron():

		# userminutes = int(timeHour2)

		# # somewhere here to create deadline datetime field
		# currentTime = datetime.datetime.now()

		# # userminutes = int(request.form.get("timeHour2")) # convert to int
		# idea.deadline = currentTime + datetime.timedelta(0, userminutes*60)
		boardingTime = datetime.datetime.now() + datetime.timedelta(0, 10*60)
		
		ideas = models.Idea.objects(  deadline__gte= datetime.datetime.now(),deadline__lte=boardingTime).order_by('+deadline')
		
		account = os.environ.get('TWILIO_ACCOUNT_SID')
		token = os.environ.get('TWILIO_AUTH_TOKEN')
		client = TwilioRestClient(account, token)
		from_telephone = os.environ.get('TWILIO_PHONE_NUMBER') # format +19171234567

		# #syntax for getting telephone number based on posted number
		# if request.method == "POST":
		# 	telephone = request.form.get('telephone')

		# 	# prepare telephone number. regex, only numbers
		# 	telephone_num = re.sub("\D", "", telephone)
		# 	if len(telephone_num) != 11:
		# 		return "your target phone number must be 11 digits. go back and try again."
		# 	else:
		# 		to_number = "+1" + str(telephone_num) #US country only now

		# loop through all soon things
		for i in ideas:

			app.logger.info(i.title )
			app.logger.info(i.sms_sent)



			if i.sms_sent != True:
				# app.logger.info(i.timeHour2)
				# message = client.sms.messages.create(to="+16464709566", from_=from_telephone,body="template text " + i.title)

				i.sms_sent = True
				i.save()

			# if we have a telephone number, send sms to this person
			# if i.telephone:
			# 	app.logger.info('got a number')

			

		# render the template
		templateData = {
			#greater than now but less than ten minutes from now
			#'ideas' : models.Idea.objects(deadline__gte= datetime.datetime.now()).order_by('+deadline'),
			'ideas': ideas,
			'currentTime' : datetime.datetime.now(),
		}

		return render_template("cron.html", **templateData)

# this is our departures page
@app.route("/departures", methods=['GET','POST'])
def departures():

	# get Idea form from models.py
	idea_form = models.IdeaForm(request.form)
	
	# if form was submitted and it is valid...
	if request.method == "POST" and idea_form.validate():
	
		# get form data - create new idea
		idea = models.Idea()
		idea.creator = request.form.get('creator','anonymous')
		idea.title = request.form.get('title','no title')
		idea.slug = slugify(idea.title + " ")
		idea.idea = request.form.get('idea','')
		idea.categories = request.form.getlist('categories') # getlist will pull multiple items
		idea.duration = request.form.get('duration','no duration') # for duration
		idea.timeHour = request.form.get('timeHour','no timeHour') # for timeHour
		idea.timeHour2 = request.form.get('timeHour2','') # for timeHour
		idea.timeMinute = request.form.get('timeMinute','no timeMinute') # for timeMinute
		idea.timeAmPm = request.form.get('timeAmPm','no timeAmPm') # for timeAmPm


		idea.save() # save it

		# redirect to the new idea page
		return redirect('/hungryfr/%s' % idea.slug)

	else:

		# for form management, checkboxes are weird (in wtforms)
		# prepare checklist items for form
		# you'll need to take the form checkboxes submitted
		# and idea_form.categories list needs to be populated.
		if request.method=="POST" and request.form.getlist('categories'):
			for c in request.form.getlist('categories'):
				idea_form.categories.append_entry(c)

		# render the template
		templateData = {
			'ideas' : models.Idea.objects(deadline__gte= datetime.datetime.now()).order_by('+deadline'),
			'categories' : categories,
			'currentTime' : datetime.datetime.now(),
			'form' : idea_form
		}

		return render_template("departures.html", **templateData)

# this is our kiosk page
@app.route("/kiosk", methods=['GET','POST'])
def kiosk():

	# get Idea form from models.py
	idea_form = models.IdeaForm(request.form)
	
	# if form was submitted and it is valid...
	if request.method == "POST" and idea_form.validate():

		# somewhere here to create deadline datetime field
		currentTime = datetime.datetime.now()

		# get form data - create new idea
		idea = models.Idea()
		idea.creator = request.form.get('creator','anonymous')
		idea.title = request.form.get('title','no title')
		idea.slug = slugify(idea.title + str(currentTime))
		idea.idea = request.form.get('idea','')
		idea.categories = request.form.getlist('categories') # getlist will pull multiple items
		idea.duration = request.form.get('duration','no duration') # for duration
		idea.timeHour = request.form.get('timeHour','no timeHour') # for timeHour
		idea.timeHour2 = request.form.get('timeHour2','') # for timeHour
		idea.timeMinute = request.form.get('timeMinute','no timeMinute') # for timeMinute
		idea.timeAmPm = request.form.get('timeAmPm','no timeAmPm') # for timeAmPm


		# convert GMT to Eastern Time
		eastToGmtTimeConvert = currentTime - datetime.timedelta(0, 60*60)

		# add user's deadline
		# example add 20 minutes
		userminutes = int(request.form.get("timeHour2")) # convert to int
		#idea.deadline = currentTime + datetime.timedelta(0, userminutes*60)
		#idea.deadline = eastToGmtTimeConvert + datetime.timedelta(0, userminutes*60)
		#trying with conversion
		idea.deadline = currentTime + datetime.timedelta(0, userminutes*60)
		# tried this with Zena: idea.now = idea.deadline-currentTime.seconds/60
		#idea.minutesRemaining = idea.deadline - currentTime

		idea.save() # save it

		# redirect to the new idea page
		return redirect('/hungryfr/%s' % idea.slug)

	else:

		# for form management, checkboxes are weird (in wtforms)
		# prepare checklist items for form
		# you'll need to take the form checkboxes submitted
		# and idea_form.categories list needs to be populated.
		if request.method=="POST" and request.form.getlist('categories'):
			for c in request.form.getlist('categories'):
				idea_form.categories.append_entry(c)

		# render the template
		templateDataKiosk = {
			'ideas' : models.Idea.objects(deadline__gte= datetime.datetime.now()).order_by('+deadline'),
			'categories' : categories,
			'currentTime' : datetime.datetime.now(),
			'form' : idea_form
			#'timeDisplay' : models.timeDisplay.currentTimeDisplay
		}

		return render_template("kiosk.html", **templateDataKiosk)

# this is our kiosk page
@app.route("/comingsoon", methods=['GET','POST'])
def comingsoon():

	# get Idea form from models.py
	idea_form = models.IdeaForm(request.form)
	
	# if form was submitted and it is valid...
	if request.method == "POST" and idea_form.validate():

		# somewhere here to create deadline datetime field
		currentTime = datetime.datetime.now()

		# get form data - create new idea
		idea = models.Idea()
		idea.creator = request.form.get('creator','anonymous')
		idea.title = request.form.get('title','no title')
		idea.slug = slugify(idea.title + str(currentTime))
		idea.idea = request.form.get('idea','')
		idea.categories = request.form.getlist('categories') # getlist will pull multiple items
		idea.duration = request.form.get('duration','no duration') # for duration
		idea.timeHour = request.form.get('timeHour','no timeHour') # for timeHour
		idea.timeHour2 = request.form.get('timeHour2','') # for timeHour
		idea.timeMinute = request.form.get('timeMinute','no timeMinute') # for timeMinute
		idea.timeAmPm = request.form.get('timeAmPm','no timeAmPm') # for timeAmPm


		# convert GMT to Eastern Time
		eastToGmtTimeConvert = currentTime - datetime.timedelta(0, 60*60)

		# add user's deadline
		# example add 20 minutes
		userminutes = int(request.form.get("timeHour2")) # convert to int
		#idea.deadline = currentTime + datetime.timedelta(0, userminutes*60)
		#idea.deadline = eastToGmtTimeConvert + datetime.timedelta(0, userminutes*60)
		#trying with conversion
		idea.deadline = currentTime + datetime.timedelta(0, userminutes*60)
		# tried this with Zena: idea.now = idea.deadline-currentTime.seconds/60
		#idea.minutesRemaining = idea.deadline - currentTime

		idea.save() # save it

		# redirect to the new idea page
		return redirect('/hungryfr/%s' % idea.slug)

	else:

		# for form management, checkboxes are weird (in wtforms)
		# prepare checklist items for form
		# you'll need to take the form checkboxes submitted
		# and idea_form.categories list needs to be populated.
		if request.method=="POST" and request.form.getlist('categories'):
			for c in request.form.getlist('categories'):
				idea_form.categories.append_entry(c)

		# render the template
		templateData = {
			'ideas' : models.Idea.objects(deadline__gte= datetime.datetime.now()).order_by('+deadline'),
			'categories' : categories,
			'currentTime' : datetime.datetime.now(),
			'form' : idea_form
			#'timeDisplay' : models.timeDisplay.currentTimeDisplay
		}

		return render_template("comingsoon.html", **templateData)


# Display all ideas for a specific category
@app.route("/category/<cat_name>")
def by_category(cat_name):

	# try and get ideas where cat_name is inside the categories list
	try:
		ideas = models.Idea.objects(categories=cat_name)

	# not found, abort w/ 404 page
	except:
		abort(404)

	# prepare data for template
	templateData = {
		'current_category' : {
			'slug' : cat_name,
			'name' : cat_name.replace('_',' ')
		},
		'ideas' : ideas,
		'categories' : categories
	}

	# render and return template
	return render_template('category_listing.html', **templateData)


#@app.route("/hungryfr/<idea_slug>")
@app.route("/hungryfr/<idea_slug>", methods=['GET','POST'])
def idea_display(idea_slug):

	# get idea by idea_slug
	try:
		idea = models.Idea.objects.get(slug=idea_slug)
	except:
		abort(404)

	# if request.method == "GET":
	# 	return render_template('idea_entry.html')

	if request.method == "POST":

		telephone = request.form.get('telephone')
		sms_text = request.form.get('sms_text')

		# prepare telephone number. regex, only numbers
		telephone_num = re.sub("\D", "", telephone)
		if len(telephone_num) != 11:
			return "your target phone number must be 11 digits. go back and try again."
		else:
			to_number = "+1" + str(telephone_num) #US country only now


		# trim message to 120
		if len(sms_text) > 120:
			sms_text = sms_text[0:119]

		account = os.environ.get('TWILIO_ACCOUNT_SID')
		token = os.environ.get('TWILIO_AUTH_TOKEN')

		client = TwilioRestClient(account, token)

		from_telephone = os.environ.get('TWILIO_PHONE_NUMBER') # format +19171234567

		message = client.sms.messages.create(to=to_number, from_=from_telephone,
	                                     body="DWD DEMO: " + sms_text)

		return "message '%s' sent" % sms_text

	# prepare template data
	templateData = {
		'idea' : idea,
		'currentTime' : datetime.datetime.now()
	}

	# render and return the template
	return render_template('idea_entry.html', **templateData)

@app.route("/hungryfr/<idea_slug>/edit", methods=['GET','POST'])
def idea_edit(idea_slug):

	
	# try and get the Idea from the database / 404 if not found
	try:
		idea = models.Idea.objects.get(slug=idea_slug)
		
		# get Idea form from models.py
		# if http post, populate with user submitted form data
		# else, populate the form with the database record
		idea_form = models.IdeaForm(request.form, obj=idea)	
	except:
		abort(404)

	# was post received and was the form valid?
	if request.method == "POST" and idea_form.validate():
	
		# get form data - update a few fields
		# note we're skipping the update of slug (incase anyone has previously bookmarked)
		idea.creator = request.form.get('creator','anonymous')
		idea.title = request.form.get('title','no title')
		idea.idea = request.form.get('idea','')
		idea.categories = request.form.getlist('categories')
		idea.duration = request.form.get('duration','no duration') # for duration
		idea.timeHour = request.form.get('timeHour','no timeHour') # for timeHour
		idea.timeHour2 = request.form.get('timeHour2','') # for timeHour
		idea.timeMinute = request.form.get('timeMinute','no timeMinute') # for timeMinute
		idea.timeAmPm = request.form.get('timeAmPm','no timeAmPm') # for timeAmPm

		idea.save() # save changes

		return redirect('/hungryfr/%s/edit' % idea.slug)

	else:

		# for form management, checkboxes are weird (in wtforms)
		# prepare checklist items for form
		# you'll need to take the form checkboxes submitted
		# and idea_form.categories list needs to be populated.
		if request.method=="POST" and request.form.getlist('categories'):
			for c in request.form.getlist('categories'):
				idea_form.categories.append_entry(c)

		templateData = {
			'categories' : categories,
			'form' : idea_form,
			'idea' : idea
		}

		return render_template("idea_edit.html", **templateData)


@app.route("/hungryfr/<idea_id>/comment", methods=['POST'])
def idea_comment(idea_id):

	name = request.form.get('name')
	comment = request.form.get('comment')

	if name == '' or comment == '':
		# no name or comment, return to page
		return redirect(request.referrer)


	#get the idea by id
	try:
		idea = models.Idea.objects.get(id=idea_id)
	except:
		# error, return to where you came from
		return redirect(request.referrer)


	# create comment
	comment = models.Comment()
	comment.name = request.form.get('name')
	comment.comment = request.form.get('comment')
	
	# append comment to idea
	idea.comments.append(comment)

	# save it
	idea.save()

	return redirect('/hungryfr/%s' % idea.slug)

@app.route('/data/json')
def data_ideas():

	# query for the ideas - return oldest first, limit 10
	ideas = models.Idea.objects().order_by('+timestamp').limit(100)

	if ideas:

		# list to hold ideas
		public_ideas = []

		#prep data for json
		for i in ideas:

			tmpIdea = {
				'creator' : i.creator,
				'title' : i.title,
				'idea' : i.idea,
				'timestamp' : str( i.timestamp )
			}

			# comments / our embedded documents
			tmpIdea['comments'] = [] # list - will hold all comment dictionaries

			# loop through idea comments
			for c in i.comments:
				comment_dict = {
					'name' : c.name,
					'comment' : c.comment,
					'timestamp' : str( c.timestamp )
				}

				# append comment_dict to ['comments']
				tmpIdea['comments'].append(comment_dict)

			# insert idea dictionary into public_ideas list
			public_ideas.append( tmpIdea )

		# prepare dictionary for JSON return
		data = {
			'status' : 'OK',
			'ideas' : public_ideas
		}

		# jsonify (imported from Flask above)
		# will convert 'data' dictionary and set mime type to 'application/json'
		return jsonify(data)

	else:
		error = {
			'status' : 'error',
			'msg' : 'unable to retrieve ideas'
		}
		return jsonify(error)

@app.route('/twilio', methods=['GET','POST'])
def twilio():
	if request.method == "GET":
		return render_template('twilio.html')

	elif request.method == "POST":

		telephone = request.form.get('telephone')
		sms_text = request.form.get('sms_text')

		# prepare telephone number. regex, only numbers
		telephone_num = re.sub("\D", "", telephone)
		if len(telephone_num) != 11:
			return "your target phone number must be 11 digits. go back and try again."
		else:
			to_number = "+1" + str(telephone_num) #US country only now


		# trim message to 120
		if len(sms_text) > 120:
			sms_text = sms_text[0:119]

		account = os.environ.get('TWILIO_ACCOUNT_SID')
		token = os.environ.get('TWILIO_AUTH_TOKEN')

		client = TwilioRestClient(account, token)

		from_telephone = os.environ.get('TWILIO_PHONE_NUMBER') # format +19171234567

		message = client.sms.messages.create(to=to_number, from_=from_telephone,
	                                     body="DWD DEMO: " + sms_text)

		return "message '%s' sent" % sms_text



@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


# slugify the title 
# via http://flask.pocoo.org/snippets/5/
_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
def slugify(text, delim=u'-'):
	"""Generates an ASCII-only slug."""
	result = []
	for word in _punct_re.split(text.lower()):
		result.extend(unidecode(word).split())
	return unicode(delim.join(result))


# --------- Server On ----------
# start the webserver
if __name__ == "__main__":
	app.debug = True
	
	port = int(os.environ.get('PORT', 5000)) # locally PORT 5000, Heroku will assign its own port
	app.run(host='0.0.0.0', port=port)



	