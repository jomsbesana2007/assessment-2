# To fetch data from API
import requests

# To load images using URL
import urllib.request
from urllib.error import HTTPError
from io import BytesIO

# For the application's GUI
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image

# Handles the retrieval of data from the API and data processing
class DataHandler:
	def __init__(self):
		# The endpoint URL
		self.url = "https://restcountries.com/v3.1/all?fields=name,flags,capital,languages,continents"

	# Retrieves data of the specific country the user typed in from Restcountries API
	def apicall(self):
		try:
			response = requests.get(self.url)
			print(f"Successful : {response.status_code}")
			data = response.json()
			return data
		except requests.exceptions.RequestException as error:
			print(error)
		
	# Formats and processes data to ensure readability and avoid errors
	def process_data(self):

		raw_data = self.apicall() # Data fetched from API

		all_countries = {} # Stores processed data about each country
		
		for country in raw_data:

			# Deals with nested dictionaries containing native names in different languages
			def retrieve_languages():
				languages = []
				languages_raw = country['languages']

				for _, value in languages_raw.items():
					# Sets a cap for the amount of different names that can be displayed per country
					if len(languages) == 5:
						break
					languages.append(value)

				# Converting list into set to remove duplicates and into list again
				languages = ", ".join(list(set(languages)))
				return languages
			
			# Deals with nested dictionaries containing native names in different languages
			def retrieve_native_names():
				native_names = []
				native_names_raw = country['name']['nativeName']

				for _, value in native_names_raw.items():
					# Sets a cap for the amount of different names that can be displayed per country
					if len(native_names) == 3:
						break
					native_names.append(value['official'])

				# Converting list into set to remove duplicates and into list again
				native_names = ", ".join(list(set(native_names)))
				return native_names
			
			# Retrieves the png filename of the specific country's flag
			def retrieve_flag_img():
				flag_img_raw = country['flags']

				for filetype, filename in flag_img_raw.items():
					if filetype == 'png':
						return filename
			
			# Compiles all relevant information about the chosen country
			country_info = {
				'common': country['name']['common'],
				'official_name': country['name']['official'],
				'native_name': retrieve_native_names(),
				'capital': ', '.join([capital_name for capital_name in country['capital']]),
				'languages': retrieve_languages(),
				'continent': ', '.join(country['continents']),
				'flag': retrieve_flag_img(),
			}

			name = country['name']['common'] # Name for the dictionary key
			all_countries.update({name: country_info})

		all_countries = dict(sorted(all_countries.items()))
		print("Data processing done.") # Print status
		return all_countries
	
# Handles the configuration of the window
class App(tk.Tk):
	def __init__(self):
		super().__init__()
		
		self.title('Country Directory')
		self.geometry('800x1000')
		self.resizable(0,0)
		self.iconphoto(True, ImageTk.PhotoImage(file="media_files/globe.png"))

# The country directory frame containing the GUI and methods
class CountryDirectory(ttk.Frame):
	def __init__(self, container):
		super().__init__(container)
		self.all_countries = DataHandler().process_data() # Retrieves data of all countries

		# Exit button
		self.exit_btn = ttk.Button(self, text='Exit', command=self.exit_applicaton, width=5)
		self.exit_btn.place(anchor='nw')

		# Displays the title heading
		self.title_frame = ttk.Frame(self)
		self.title_frame.grid(column=1, row=0, columnspan=2, pady=10)

		# Image of the app logo
		self.img = ImageTk.PhotoImage(Image.open("media_files/globe.png").resize((150,150)))
		self.title_img = ttk.Label(self.title_frame, image=self.img)
		self.title_img.grid(column=1, row=0)
		
		# The title heading at the top of the application
		self.title = ttk.Label(self.title_frame, text="Country Directory", style='Title.TLabel')
		self.title.grid(column=2, row=0)

		# Section that displays the flag
		self.flag_frame = ttk.Frame(self, height=400, width=600, relief='solid')
		self.flag_frame.grid(column=1, row=1, columnspan=3, pady=20)
		self.flag_frame.grid_propagate(False) # Keeps dimensions without changes caused by height and width properties of other widgets

		# To configure the spacing and center the flag image
		self.flag_frame.columnconfigure(1, weight=1)	
		self.flag_frame.columnconfigure(2, weight=1)
		self.flag_frame.columnconfigure(3, weight=1)
		self.flag_frame.rowconfigure(0, weight=1)

		# Displays the flag
		self.flag = ttk.Label(self.flag_frame, anchor='center')
		self.flag.grid(column=1, row=0, columnspan=3)

		# Section for dropdown selection
		self.dropdown_frame = ttk.Frame(self, width=400)
		self.dropdown_frame.grid(column=1, row=2, columnspan=2)

		# Displays dropdown of all countries
		self.selected_country = tk.StringVar()
		self.dropdown = ttk.Combobox(self.dropdown_frame, textvariable=self.selected_country, width=50, style='Dropdown.TCombobox')
		self.dropdown['state'] = 'readonly'
		self.dropdown['values'] = [country for country, _ in self.all_countries.items()]
		self.dropdown.grid(padx=20, column=1, row=0)

		# Button that executes the methods to show information about the chosen country
		self.searchbtn = ttk.Button(self.dropdown_frame, text="Search", command=self.fetch_country_data, style='Search.TButton')
		self.searchbtn.grid(column=2, row=0)

		# Display section
		self.info_frame = ttk.Labelframe(self, text="Country Information", height=200, width=750, relief='solid', labelanchor='n')
		self.info_frame.grid(column=1, row=3, columnspan=2, pady=20)
		self.info_frame.grid_propagate(False) # Keeps dimensions without changes caused by height and width properties of other widgets

		self.info_frame.columnconfigure(1, weight=1)	
		self.info_frame.columnconfigure(2, weight=1)

		# Information to be displayed in this section
		self.name = ttk.Label(self.info_frame)
		self.official_name = ttk.Label(self.info_frame)
		self.native_name = ttk.Label(self.info_frame)
		self.capital = ttk.Label(self.info_frame)
		self.languages = ttk.Label(self.info_frame)
		self.continents = ttk.Label(self.info_frame)
		
		self.name.grid(column=1, row=0, sticky='W', pady=5)
		self.official_name.grid(column=1, row=1, sticky='W', pady=5)
		self.native_name.grid(column=1, row=2, sticky='W', pady=5)
		self.capital.grid(column=1, row=3, sticky='W', pady=5)
		self.languages.grid(column=1, row=4, sticky='W', pady=5)
		self.continents.grid(column=1, row=5, sticky='W', pady=5)

		# Labels in the display section
		self.name_label = ttk.Label(self.info_frame, text="Name", style="Bold.TLabel")
		self.official_name_label = ttk.Label(self.info_frame, text="Official Name", style="Bold.TLabel")
		self.native_name_label = ttk.Label(self.info_frame, text="Native Name", style="Bold.TLabel")
		self.languages_label = ttk.Label(self.info_frame, text="Languages", style="Bold.TLabel")
		self.capital_label = ttk.Label(self.info_frame, text="Capital", style="Bold.TLabel")
		self.continents_label = ttk.Label(self.info_frame, text="Continent", style="Bold.TLabel")

		self.name_label.grid(column=2, row=0, sticky='E', pady=5)
		self.official_name_label.grid(column=2, row=1, sticky='E', pady=5)
		self.native_name_label.grid(column=2, row=2, sticky='E', pady=5)
		self.capital_label.grid(column=2, row=3, sticky='E', pady=5)
		self.languages_label.grid(column=2, row=4, sticky='E', pady=5)
		self.continents_label.grid(column=2, row=5, sticky='E', pady=5)

		# Tkinter styles
		self.s = ttk.Style()
		self.s.configure('Title.TLabel', font=('Helvetica', 30, 'bold'))
		self.s.configure('Search.TButton', font=('Helvetica', 11))
		self.s.configure('Dropdown.TCombobox', font=('Helvetica', 11))
		self.s.configure('TLabel', font=('Helvetica', 9))
		self.s.configure('Bold.TLabel', font=('Helvetica', 10, 'bold'))

		# Displays the frame
		self.pack(pady=50, anchor='center')

		print("GUI built successfully.") # Print status

	# Fetches data of the chosen country
	def fetch_country_data(self):
		try:
			# Gets the name of the country from StringVar()
			chosen_country = self.selected_country.get()

			# Loops through the dictionary of all countries until a match had been found
			for country, country_data in self.all_countries.items():
				if chosen_country == country:
					# After data of the country has been found, the methods then run
					self.show_flag(country_data)
					self.show_country_info(country_data)

			print("Data of chosen country retrieved successfully.") # Print status
		except KeyError as error:
			print(error)

	# Method that handles displaying the flag of the chosen country
	def show_flag(self, country_data):
		try:
			# Gets the image file from the dictionary of the chosen country
			flag_file = country_data['flag']

			# Makes a request to retrieve the image file online, which usually has the URL as "https://filename.png"
			with urllib.request.urlopen(flag_file) as flag:
				self.flag_bytes = flag.read() # Gets the raw data in bytes as Tkinter cannot open images from the web
				self.flag_img = ImageTk.PhotoImage(Image.open(BytesIO(self.flag_bytes)))
			self.flag.config(image=self.flag_img) # Configures the image widget with the flag image of the chosen country

			print("Flag displayed successfully.") # Print status
		except HTTPError as error:
			print(error)
	
	# Method that handles displaying information about the chosen country
	def show_country_info(self, country_data):
		try:
			# Configures all the Label widgets
			self.name.configure(text=country_data['common'])
			self.official_name.configure(text=country_data['official_name'])
			self.native_name.configure(text=country_data['native_name'])
			self.capital.configure(text=country_data['capital'])
			self.languages.configure(text=country_data['languages'])
			self.continents.configure(text=country_data['continent'])

			print("Labels have been configured successfully.") # Print status
		except KeyError as error:
			print(error)

	# Exits the application
	def exit_applicaton(self):
		self.master.destroy() # "master" refers to the main window
		print("Application exited successfully.") # Print status

# Runs the application
app = App() # Creates an instance of the App function
CountryDirectory(app) # The "app" object is passed as an argument in order to apply configurations to the other frames
app.mainloop() # Allows the app to run