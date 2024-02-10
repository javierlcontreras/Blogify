from glob import glob
import os
import json
import re

class Compiler():
	def __init__(self, input_path, output_path, boilerplate_path, cname):
		self.input_path = input_path
		self.output_path = output_path
		self.boilerplate_path = boilerplate_path
		self.cname = cname
		self.header_boilerplate = open(f"{self.boilerplate_path}/header.html", "r").read()
		self.footer_boilerplate = open(f"{self.boilerplate_path}/footer.html", "r").read()
		self.info_json = "info.json"
		self.sections = self.getSections()

	def getSections(self):
		sections = []
		for section_path in glob(f"{self.input_path}/*"):
			section_id = section_path.split("/")[-1]
			if section_id == self.info_json:
				continue
			sections.append(section_id)
		return sections

	def createOutputCopy(self):
		if os.path.exists(f"{self.output_path}") == True:
			os.system(f"rm {self.output_path} -r")

		os.system(f"cp {self.input_path} {self.output_path} -r")

	def addFiles(self):
		pass

	def generateHeader(self):
		header = None
		with open(f"{self.boilerplate_path}/header.html") as r:
			header = r.read()

		website_info = self.getInfo(f"{self.output_path}")

		header = header.replace("SITE_TITLE", website_info["site-title"])
		header = header.replace("SITE_AUTHOR", website_info["author"])

		button = None
		with open(f"{self.boilerplate_path}/header-button.html") as r:
			button = r.read()

		dropdown_button = None
		with open(f"{self.boilerplate_path}/drop-down-header-button.html") as r:
			dropdown_button = r.read()

		buttons = []
		for section_id in self.sections:
			section_path = f"{self.output_path}/{section_id}"
			info = self.getInfo(f"{section_path}")
			if section_id == "index":
				section_path = f"{self.output_path}/index.html"
			else:
				section_path = f"{self.output_path}/{section_id}.html"
			section_path = section_path.replace(f"{self.output_path}", '.')
			section_name = info["section-name"]
			section_order = info["section-order"]

			section_button = button.replace("SECTION_NAME", section_name).replace("SECTION_PATH", section_path).replace("SECTION_ID", section_id)
			section_ddbutton = dropdown_button.replace("SECTION_NAME", section_name).replace("SECTION_PATH", section_path).replace("SECTION_ID", section_id)

			buttons.append( (section_order, section_button, section_ddbutton) )

		buttons = sorted(buttons)
		for button in buttons:
			section_button = button[1]
			section_ddbutton = button[2]
			header = header.replace("SECTION_BUTTONS", section_button + "\n SECTION_BUTTONS")
			header = header.replace("SECTION_DROPDOWN_BUTTONS", section_ddbutton + "\n SECTION_DROPDOWN_BUTTONS")

		header = header.replace("SECTION_BUTTONS", "")
		header = header.replace("SECTION_DROPDOWN_BUTTONS", "")
		self.header = header

	def moveStylesCSS(self):
		os.system(f"cp {self.boilerplate_path}/style.css {self.output_path}/style.css")

	def prepareHeader(self, section_id, is_index=False):
		header = self.header
		mybutton = f"navigation-button-{section_id}"
		header  = header.replace(mybutton, "navigation-button navigation-button-active")
		for other_section_id in self.sections:
			header = header.replace(f"navigation-button-{other_section_id}", "navigation-button")
		return header

	def prepareFooter(self, section_id):
		footer = ""
		with open(f"{self.boilerplate_path}/footer.html") as r:
			footer = r.read()
		footer = footer.replace("SECTION_ID", section_id)
		return footer

	def addBodySection(self, section_id, section_path, is_index=False):
		body = None
		with open(f"{section_path}/body.html") as r:
			body = r.read()
		self.saveSection(body, section_id, section_path, is_index)
	
	def toMonth(self, n):
		months = [
			"January", 
			"February", 
			"March", 
			"April", 
			"May", 
			"June", 
			"July", 
			"August", 
			"September", 
			"October", 
			"November", 
			"December", 
		]
		if n >= 1 and n <= 12:
			return months[n-1]
		return ""


	def toMonthShort(self, n):
		months = [
			"Jan", 
			"Feb", 
			"Mar", 
			"Apr", 
			"May", 
			"Jun", 
			"Jul", 
			"Aug", 
			"Sep", 
			"Oct", 
			"Nov", 
			"Dec", 
		]
		if n >= 1 and n <= 12:
			return months[n-1]
		return ""

	def addBlogs(self, body, section_id, section_path):
		blogs = []
		for blog_path in glob(f"{section_path}/*"):
			blog_id = blog_path.split("/")[-1]
			if blog_id == self.info_json: continue
			
			info = self.getInfo(f"{blog_path}")

			blog_date = f'{self.toMonth(info["date-month-number"])} of {info["date-year"]}'
			blog_time = info["date-day"]/12/365 + info["date-month-number"]/12 + info["date-year"]
			blogs.append((-blog_time, blog_id, info["blog-title"], info["blog-subtitle"], blog_date, section_id, info["link"]))

		blogs = sorted(blogs)
		for blog in blogs:
			blog_button = ""
			with open(f"{self.boilerplate_path}/blog-section-button.html") as r:
				blog_button = r.read()

			blog_button = blog_button.replace("BLOG_ID", blog[1])
			blog_button = blog_button.replace("BLOG_TITLE", blog[2])
			blog_button = blog_button.replace("BLOG_SUBTITLE", blog[3])
			blog_button = blog_button.replace("BLOG_DATE", blog[4])
			blog_button = blog_button.replace("SECTION_ID", blog[5])
			blog_button = blog_button.replace("BLOG_LINK", blog[6])

			body = body.replace("BLOG_BUTTONS", blog_button + "\n" + "BLOG_BUTTONS")
		return body.replace("BLOG_BUTTONS", "")


	def addBlogSection(self, section_id, section_path, is_index=False):
		body = ""
		with open(f"{self.boilerplate_path}/blog-section.html") as r:
			body = r.read()

		body = self.addBlogs(body, section_id, section_path)
		self.saveSection(body, section_id, section_path, is_index)

	def saveSection(self, body, section_id, section_path, is_index):
		header = self.prepareHeader(section_id, is_index=is_index)
		footer = self.prepareFooter(section_id)
		content = header + "\n" + body + "\n" + footer

		if is_index:
			with open(f"{self.output_path}/index.html", "w+") as w:
				w.write(content)
			os.system(f"cp \"{section_path}\"/* {self.output_path} -r")
		else:
			with open(f"{self.output_path}/{section_id}.html", "w+") as w:
				w.write(content) 

	def addSection(self, section_id, section_path, is_index = False):
		info = self.getInfo(section_path)
		if info["type-of-section"] == "body":
			self.addBodySection(section_id, section_path, is_index)
		elif info["type-of-section"] == "blog":
			self.addBlogSection(section_id, section_path, is_index)

	def addAllSections(self):
		for section_path in glob(f"{self.output_path}/*"):
			section_id = section_path.split("/")[-1]
			if section_id == self.info_json:
				continue
			print(section_id)
			self.addSection(section_id, section_path, is_index = (section_id=="index"))

	def addCNAME(self):
		with open(f"{self.output_path}/CNAME", 'w') as w:
			w.write(self.cname)

	def getInfo(self, path):
		info = None
		with open(f"{path}/{self.info_json}") as r:
			info = json.load(r)
		return info

	def compile(self):
		self.createOutputCopy()

		self.generateHeader()
		self.addAllSections()
		self.addCNAME()
		self.moveStylesCSS()


	def random():
		import re
		navbuttons = re.findall("navigation\-button\-[a-z]*", headerHTML)

		for file in glob(f"./{OUTPUT}/**/*.html", recursive=True):
			print(file)
			filename = file.split("/")[2]
			if filename[-5:] == ".html": filename = filename[:-5]

			myHeaderHTML = headerHTML
			nsubfold = file.count("/")
			if nsubfold >= 3:
				myHeaderHTML = myHeaderHTML.replace("./", "../"*(nsubfold-2))			


			mybutton = f"navigation-button-{filename}"
			if mybutton in myHeaderHTML:
				myHeaderHTML = myHeaderHTML.replace(mybutton, \
								  	"navigation-button navigation-button-active")
			for navbutton in navbuttons:
				if navbutton in myHeaderHTML:
					myHeaderHTML = myHeaderHTML.replace(navbutton, "navigation-button")
			
			myFooterHTML = footerHTML
			if (filename == "index"):
				myFooterHTML = myFooterHTML.replace("<current-page>", "experience")
			else:
				myFooterHTML = myFooterHTML.replace("<current-page>", filename)

			rd = open(file, "r")
			HTML = rd.read()
			rd.close()
			wd = open(file, "w")

			wd.write(myHeaderHTML + HTML + myFooterHTML)
			wd.close()