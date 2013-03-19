#! /usr/bin/env python

from flask import Flask, render_template, redirect, request, url_for
from follow import render

app = Flask(__name__) 

@app.route('/')
def hello():
	return render_template('web_button.html')

@app.route('/', methods=['POST'])
def hello_post():
	if request.form.get('login'):
		hs_email = request.form.get('HS-username')
		hs_password = request.form.get('HS-password')
		gh_username = request.form.get('GH-username')
		gh_password = request.form.get('GH-password')
		output = render(hs_email, hs_password, gh_username, gh_password)
		if type(output) == str:
			return render_template('output.html', following=None, already_following=None, error=output)
		else:
			following, already_following = output[0], output[1]
			return render_template('output.html', following=following, already_following=already_following, error=None)

if __name__ == '__main__':
	app.run(debug=True)