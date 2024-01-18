

import json
import urllib
import urllib.request
import csv
import os
import logging


KRKIN=24
# SONO=[2400, 2404, 2411,2415,2420,2423,2437,2439,2440,2442,2443,2444,2447,2448,2450,2452,2453,2454,2455,2456,2457,2459,2460,2461,2462,2463,2464,2465,2466,2467]
INNARR=[]
OKVEDOO="85.14" #Образование среднее общее
OKVEDSPO="85.21" #Образование профессиональное среднее
INNCTRLMUL=[2,4,10,3,5,9,4,6,8]
INNCTRLDEL=11
FILENAME = f"{os.path.dirname(os.path.abspath(__file__))}/inn.csv"
OUTFILE = f"{os.path.dirname(os.path.abspath(__file__))}/output.csv"
logging.basicConfig(
	 handlers=[
		  logging.FileHandler(f"{os.path.dirname(os.path.abspath(__file__))}/LOG.log"),
		  logging.StreamHandler()
	 ], encoding='utf-8', level=logging.DEBUG)
base_url="https://egrul.itsoft.ru/"

basekey=["СвЮЛ", "СвАдресЮЛ"]
keyaddrinfo=["АдресРФ", "СвАдрЮЛФИАС"]

org_status="1"

def main():
	FILENAME=f"{os.path.dirname(os.path.abspath(__file__))}/"+input(f"Введите имя файла в папке {os.path.dirname(os.path.abspath(__file__))}/")
	#Открываем и чистим выходной файл
	fopen()
	body_dict={}
	#Открываем файл с исходными данными (ИНН - в один столбец без заголовка)
	with open(FILENAME, "r", newline="",encoding='utf-8-sig') as file:
		reader = csv.reader(file)
		for row in reader:
			 orginfo(row[0])		#вызов функции парсинга данных из json |https://egrul.itsoft.ru/{inn}.json|

#Генератор валидных ИНН
def genInn():
	sonokrk=[]
	for i in range(1,99):
		tsono=f"{KRKIN}{i:02}"
		sonokrk.append(tsono)
	innarr=[]
	for sono in sonokrk:
		for i in range (0, 99999):
			#print (f"{i:05}")
			t_inn=f"{sono}{i:05}"
			# print(t_inn)
			t_inn=controlInn(t_inn)
			# print(t_inn)
			if testinn(t_inn):
				innarr.append(t_inn)
	for inn in innarr:
		# print(inn)
		try:
			url=base_url+str(inn)+".json"
			with urllib.request.urlopen(url) as response:
				body_json = response.read()
			# body_dict = json.loads(body_json)
			with open (OUTFILE, "a", newline="", encoding='cp1251') as file:
				writer = csv.writer(file)
				writer.writerow(str(inn))
		except urllib.error.HTTPError as HTTPERR:
			logging.error(f"Ошибка #{HTTPERR}# в {inn}")		
			
#Проверка ИНН на валидность
def controlInn(inn):
	sum=0
	i=0
	tinn=inn
	for i in range(0,len(inn)):
		sum+=int(inn[i])*INNCTRLMUL[i]
	# print(sum)
	result = sum//INNCTRLDEL
	result=result*INNCTRLDEL
	result=abs(result-sum)
	if result==10:
		result = 0
	tinn=tinn+str(result)
	return tinn

#Функция для проверки работы разных новых функций
def test():
	fopen()
	#genInn()
	# fopen()
	body_dict={}
	orginfo(input("Введите ИНН организации: ")) #TEST

#Проверка ИНН на корректность
def testinn(inn):
	sum=0
	i=0
	tinn=str(inn).zfill(10)
	tinn=tinn[:-1]
	for digit in tinn:
		sum+=int(digit)*INNCTRLMUL[i]
		i+=1
	# print(f"Контрольная сумма по {inn}: {sum}")
	result=sum//INNCTRLDEL
	result=result*INNCTRLDEL
	result=abs(result-sum)
	# print(f"Контрольное число {result}")
	if result==10:
		result = 0
	if inn.endswith(str(result)):
		#   print(f"{inn} is OKAY!")
		return True
	else:
		return False

#Получение общего кода вида экономической деятельности для проверки организаций на соответствие
def testokved(tdict):
	result=""
	if tdict.get('СвЮЛ').get('СвОКВЭД') is not None:
		if tdict.get('СвЮЛ').get('СвОКВЭД').get('СвОКВЭДОсн').get('@attributes').get('КодОКВЭД') is not None:
			result = tdict.get('СвЮЛ').get('СвОКВЭД').get('СвОКВЭДОсн').get('@attributes').get('КодОКВЭД') #Код ОКВЭД Основной
	return result

def sub_division_q(tdict):
	result=0
	global subDiv
	if tdict.get('СвЮЛ').get('СвПодразд') is not None:
		tempdict=tdict.get('СвЮЛ').get('СвПодразд')
		if tempdict.get('СвФилиал') is not None:
			subDiv="Филиал"
			if isinstance(tempdict.get('СвФилиал'), dict):
				result = 1
				return result
			elif isinstance(tempdict.get('СвФилиал'), list):
				result = len(tempdict.get('СвФилиал'))
				return result
		elif tempdict.get('СвПредстав') is not None:
			subDiv="Представительство"
			if isinstance(tempdict.get('СвПредстав'), dict):
				result = 1
				return result
			elif isinstance(tempdict.get('СвПредстав'), list):
				result = len(tempdict.get('СвПредстав'))
				return result
	else:
		return result


def sub_division_fname(tdict, q):
	result = ""
	if q>=0:
		if subDiv == "Филиал":
			tempdict=tdict.get('СвЮЛ').get('СвПодразд').get('СвФилиал')[q]
		elif subDiv == "Представительство":
			tempdict=tdict.get('СвЮЛ').get('СвПодразд').get('СвПредстав')[q]
		else:
			return ""
		if tempdict.get('СвНаим') is not None:
			result = tempdict.get('СвНаим').get('@attributes').get('НаимПолн')
		else:
			result = ""
	else:
		if subDiv == "Филиал":
			tempdict=tdict.get('СвЮЛ').get('СвПодразд').get('СвФилиал')
		elif subDiv == "Представительство":
			tempdict=tdict.get('СвЮЛ').get('СвПодразд').get('СвПредстав')
		else:
			return ""
		if tempdict.get('СвНаим') is not None:
			result = tempdict.get('СвНаим').get('@attributes').get('НаимПолн')
		else:
			result = ""
	return result


def sub_division_faddress(tdict, q):
	result = ""
	if q>=0:
		if subDiv == "Филиал":
			tempdict=tdict.get('СвЮЛ').get('СвПодразд').get('СвФилиал')[q]
		elif subDiv == "Представительство":
			tempdict=tdict.get('СвЮЛ').get('СвПодразд').get('СвПредстав')[q]

		if tempdict.get('АдрМНРФ') is not None:
			tempdict=tempdict.get('АдрМНРФ')
		elif tempdict.get('АдрМНФИАС') is not None:
			tempdict=tempdict.get('АдрМНФИАС')
		else:
			result="-"
			return result
	else:
		if subDiv == "Филиал":
			tempdict=tdict.get('СвЮЛ').get('СвПодразд').get('СвФилиал')
		elif subDiv == "Представительство":
			tempdict=tdict.get('СвЮЛ').get('СвПодразд').get('СвПредстав')
		if tempdict.get('АдрМНРФ') is not None:
			tempdict=tempdict.get('АдрМНРФ')
		elif tempdict.get('АдрМНФИАС') is not None:
			tempdict=tempdict.get('АдрМНФИАС')
		else:
			result="-"
			return result
	address={}
	address.setdefault("Индекс",tempdict.get('@attributes').get('Индекс'))
	
	if tempdict.get('НаимРегион') is not None:
		address.setdefault("Регион", tempdict.get('НаимРегион'))
	elif tempdict.get('Регион') is not None:
		if tempdict.get('Регион').get('@attributes').get('ТипРегион') is not None or tempdict.get('Регион').get('@attributes').get('НаимРегион') is not None:
			address.setdefault("Регион",f"{tempdict.get('Регион').get('@attributes').get('НаимРегион')} {tempdict.get('Регион').get('@attributes').get('ТипРегион')}".replace(" None", ""))
	
	if tempdict.get('Район') is not None:
		if isinstance(tempdict.get('Район'), dict):
			#print(f"{tempdict.get('Район').get('@attributes').get('НаимРайон')} {tempdict.get('Район').get('@attributes').get('ТипРайон')}")
			address.setdefault("Район", f"{tempdict.get('Район').get('@attributes').get('НаимРайон')} {tempdict.get('Район').get('@attributes').get('ТипРайон')}".replace(" None", ""))
		else:
			address.setdefault("Район", tempdict.get('Район'))
	
	if tempdict.get('МуниципРайон') is not None:
		if isinstance(tempdict.get('МуниципРайон'), dict):
			#print(f"{tempdict.get('МуниципРайон').get('@attributes').get('Наим')} {tempdict.get('МуниципРайон').get('@attributes').get('Тип')}")
			address.setdefault("Район", f"{tempdict.get('МуниципРайон').get('@attributes').get('Наим')} {tempdict.get('МуниципРайон').get('@attributes').get('Тип')}".replace(" None", ""))
		else:
			address.setdefault("Район", tempdict.get('МуниципРайон'))
	
	if tempdict.get('Город') is not None:
		if isinstance(tempdict.get('Город'),dict):
			#print(f"{tempdict.get('Город').get('@attributes').get('ТипГород')} {tempdict.get('Город').get('@attributes').get('НаимГород')}")
			address.setdefault("Город", f"{tempdict.get('Город').get('@attributes').get('ТипГород')} {tempdict.get('Город').get('@attributes').get('НаимГород')}".replace(" None", ""))
		else:
			address.setdefault("Город", tempdict.get('Город'))
	
	if tempdict.get('НаселПункт') is not None:
		if isinstance(tempdict.get('НаселПункт'),dict):
			#print(f"{tempdict.get('НаселПункт').get('@attributes').get('ТипНаселПункт')} {tempdict.get('НаселПункт').get('@attributes').get('НаимНаселПункт')}")
			address.setdefault("НаселПункт", f"{tempdict.get('НаселПункт').get('@attributes').get('ТипНаселПункт')} {tempdict.get('НаселПункт').get('@attributes').get('НаимНаселПункт')}".replace(" None", ""))
		else:
			address.setdefault("НаселПункт", tempdict.get('НаселПункт'))
	
	if tempdict.get('НаселенПункт') is not None:
		if isinstance(tempdict.get('НаселенПункт'),dict):
			#print(f"{tempdict.get('НаселенПункт').get('@attributes').get('Вид')} {tempdict.get('НаселенПункт').get('@attributes').get('Наим')}")
			address.setdefault("НаселПункт", f"{tempdict.get('НаселенПункт').get('@attributes').get('Вид')} {tempdict.get('НаселенПункт').get('@attributes').get('Наим')}".replace(" None", ""))
		else:
			address.setdefault("НаселПункт", tempdict.get('НаселенПункт'))

	if tempdict.get('Улица') is not None:
		if isinstance(tempdict.get('Улица'), dict):
			#print(f"{tempdict.get('Улица').get('@attributes').get('НаимУлица')} {tempdict.get('Улица').get('@attributes').get('ТипУлица')}")
			address.setdefault("Улица", f"{tempdict.get('Улица').get('@attributes').get('НаимУлица')} {tempdict.get('Улица').get('@attributes').get('ТипУлица')}".replace(" None", ""))
		else:
			address.setdefault("Улица", tempdict.get('Улица'))

	if tempdict.get('ЭлУлДорСети') is not None:
		if isinstance(tempdict.get('ЭлУлДорСети'), dict):
			#print(f"{tempdict.get('ЭлУлДорСети').get('@attributes').get('Наим')} {tempdict.get('ЭлУлДорСети').get('@attributes').get('Тип')}")
			address.setdefault("Улица", f"{tempdict.get('ЭлУлДорСети').get('@attributes').get('Наим')} {tempdict.get('ЭлУлДорСети').get('@attributes').get('Тип')}".replace(" None", ""))
		else:
			address.setdefault("ЭлУлДорСети", tempdict.get('ЭлУлДорСети'))

	if tempdict.get('Здание') is not None:
		if isinstance(tempdict.get('Здание'), dict):
			print(type(tempdict.get('Здание')))
			address.setdefault("Здание", f"{tempdict.get('Здание').get('@attributes').get('Тип')} {tempdict.get('Здание').get('@attributes').get('Номер')}".replace(" None", ""))
		elif isinstance(tempdict.get('Здание'),list):
			#print(f"{tempdict.get('Здание')[0].get('@attributes').get('Тип')} {tempdict.get('Здание')[0].get('@attributes').get('Номер')}, {tempdict.get('Здание')[1].get('@attributes').get('Тип')} {tempdict.get('Здание')[1].get('@attributes').get('Номер')}")
			address.setdefault("Здание", f"{tempdict.get('Здание')[0].get('@attributes').get('Тип')}, {tempdict.get('Здание')[0].get('@attributes').get('Номер')}".replace(" None", ""))
			address.setdefault("Строение", f"{tempdict.get('Здание')[1].get('@attributes').get('Тип')}, {tempdict.get('Здание')[1].get('@attributes').get('Номер')}".replace(" None", ""))
		else:
			address.setdefault("Здание", tempdict.get('Здание'))
	if tempdict.get('@attributes').get('Дом') is not None: 
		address.setdefault("Дом", f"{tempdict.get('@attributes').get('Дом')}".replace(" None", ""))
	result=""
	for i in address:
		if address.get(i) != "" :
			result+=f"{address.get(i)}, "
	#print(result.replace(" None", "").rstrip(", "))
	return result.rstrip(", ")
	
	


#Полное наименование из выписки ЕГРЮЛ	 
def full_name_from_inn (tdict):
	result=""
	if tdict.get('СвЮЛ').get('СвНаимЮЛ').get('@attributes').get('НаимЮЛПолн') is not None:
		result = tdict.get('СвЮЛ').get('СвНаимЮЛ').get('@attributes').get('НаимЮЛПолн')
	return result
  
#Краткое наименование из выписки ЕГРЮЛ 2 типа
def short_name_from_inn (tdict):
	result=""
	#inn=input("Введите ИНН организации: ")
	if tdict.get('СвЮЛ').get('СвНаимЮЛ').get('СвНаимЮЛСокр') is not None:
		result = tdict.get('СвЮЛ').get('СвНаимЮЛ').get('СвНаимЮЛСокр').get('@attributes').get('НаимСокр')
	elif tdict.get('СвЮЛ').get('СвНаимЮЛ').get('@attributes').get('НаимЮЛСокр') is not None:
		result = tdict.get('СвЮЛ').get('СвНаимЮЛ').get('@attributes').get('НаимЮЛСокр')
	return result

#Получение полного адреса образовательной организации
def get_address_from_inn(tdict):
	
	tempdict=tdict['СвЮЛ']['СвАдресЮЛ']
	for key in keyaddrinfo:
		if key in tempdict.keys():
			tempdict=tempdict.get(key)

	address={}
	address.setdefault("Индекс",tempdict.get('@attributes').get('Индекс'))
	
	if tempdict.get('НаимРегион') is not None:
		address.setdefault("Регион", tempdict.get('НаимРегион'))
	elif tempdict.get('Регион') is not None:
		if tempdict.get('Регион').get('@attributes').get('ТипРегион') is not None or tempdict.get('Регион').get('@attributes').get('НаимРегион') is not None:
			address.setdefault("Регион",f"{tempdict.get('Регион').get('@attributes').get('НаимРегион')} {tempdict.get('Регион').get('@attributes').get('ТипРегион')}".replace(" None", ""))
	
	if tempdict.get('Район') is not None:
		if isinstance(tempdict.get('Район'), dict):
			#print(f"{tempdict.get('Район').get('@attributes').get('НаимРайон')} {tempdict.get('Район').get('@attributes').get('ТипРайон')}")
			address.setdefault("Район", f"{tempdict.get('Район').get('@attributes').get('НаимРайон')} {tempdict.get('Район').get('@attributes').get('ТипРайон')}".replace(" None", ""))
		else:
			address.setdefault("Район", tempdict.get('Район'))
	
	if tempdict.get('МуниципРайон') is not None:
		if isinstance(tempdict.get('МуниципРайон'), dict):
			#print(f"{tempdict.get('МуниципРайон').get('@attributes').get('Наим')} {tempdict.get('МуниципРайон').get('@attributes').get('Тип')}")
			address.setdefault("Район", f"{tempdict.get('МуниципРайон').get('@attributes').get('Наим')} {tempdict.get('МуниципРайон').get('@attributes').get('Тип')}".replace(" None", ""))
		else:
			address.setdefault("Район", tempdict.get('МуниципРайон'))
	
	if tempdict.get('Город') is not None:
		if isinstance(tempdict.get('Город'),dict):
			#print(f"{tempdict.get('Город').get('@attributes').get('ТипГород')} {tempdict.get('Город').get('@attributes').get('НаимГород')}")
			address.setdefault("Город", f"{tempdict.get('Город').get('@attributes').get('ТипГород')} {tempdict.get('Город').get('@attributes').get('НаимГород')}".replace(" None", ""))
		else:
			address.setdefault("Город", tempdict.get('Город'))
	
	if tempdict.get('НаселПункт') is not None:
		if isinstance(tempdict.get('НаселПункт'),dict):
			#print(f"{tempdict.get('НаселПункт').get('@attributes').get('ТипНаселПункт')} {tempdict.get('НаселПункт').get('@attributes').get('НаимНаселПункт')}")
			address.setdefault("НаселПункт", f"{tempdict.get('НаселПункт').get('@attributes').get('ТипНаселПункт')} {tempdict.get('НаселПункт').get('@attributes').get('НаимНаселПункт')}".replace(" None", ""))
		else:
			address.setdefault("НаселПункт", tempdict.get('НаселПункт'))
	
	if tempdict.get('НаселенПункт') is not None:
		if isinstance(tempdict.get('НаселенПункт'),dict):
			#print(f"{tempdict.get('НаселенПункт').get('@attributes').get('Вид')} {tempdict.get('НаселенПункт').get('@attributes').get('Наим')}")
			address.setdefault("НаселПункт", f"{tempdict.get('НаселенПункт').get('@attributes').get('Вид')} {tempdict.get('НаселенПункт').get('@attributes').get('Наим')}".replace(" None", ""))
		else:
			address.setdefault("НаселПункт", tempdict.get('НаселенПункт'))

	if tempdict.get('Улица') is not None:
		if isinstance(tempdict.get('Улица'), dict):
			#print(f"{tempdict.get('Улица').get('@attributes').get('НаимУлица')} {tempdict.get('Улица').get('@attributes').get('ТипУлица')}")
			address.setdefault("Улица", f"{tempdict.get('Улица').get('@attributes').get('НаимУлица')} {tempdict.get('Улица').get('@attributes').get('ТипУлица')}".replace(" None", ""))
		else:
			address.setdefault("Улица", tempdict.get('Улица'))

	if tempdict.get('ЭлУлДорСети') is not None:
		if isinstance(tempdict.get('ЭлУлДорСети'), dict):
			#print(f"{tempdict.get('ЭлУлДорСети').get('@attributes').get('Наим')} {tempdict.get('ЭлУлДорСети').get('@attributes').get('Тип')}")
			address.setdefault("Улица", f"{tempdict.get('ЭлУлДорСети').get('@attributes').get('Наим')} {tempdict.get('ЭлУлДорСети').get('@attributes').get('Тип')}".replace(" None", ""))
		else:
			address.setdefault("ЭлУлДорСети", tempdict.get('ЭлУлДорСети'))

	if tempdict.get('Здание') is not None:
		if isinstance(tempdict.get('Здание'), dict):
			print(type(tempdict.get('Здание')))
			address.setdefault("Здание", f"{tempdict.get('Здание').get('@attributes').get('Тип')} {tempdict.get('Здание').get('@attributes').get('Номер')}".replace(" None", ""))
		elif isinstance(tempdict.get('Здание'),list):
			#print(f"{tempdict.get('Здание')[0].get('@attributes').get('Тип')} {tempdict.get('Здание')[0].get('@attributes').get('Номер')}, {tempdict.get('Здание')[1].get('@attributes').get('Тип')} {tempdict.get('Здание')[1].get('@attributes').get('Номер')}")
			address.setdefault("Здание", f"{tempdict.get('Здание')[0].get('@attributes').get('Тип')}, {tempdict.get('Здание')[0].get('@attributes').get('Номер')}".replace(" None", ""))
			address.setdefault("Строение", f"{tempdict.get('Здание')[1].get('@attributes').get('Тип')}, {tempdict.get('Здание')[1].get('@attributes').get('Номер')}".replace(" None", ""))
		else:
			address.setdefault("Здание", tempdict.get('Здание'))
	if tempdict.get('@attributes').get('Дом') is not None: 
		address.setdefault("Дом", f"{tempdict.get('@attributes').get('Дом')}".replace(" None", ""))
	result=""
	for i in address:
		if address.get(i) != "" :
			result+=f"{address.get(i)}, "
	#print(result.replace(" None", "").rstrip(", "))
	return result.rstrip(", ")

def get_director_fname (tdict):
	result = ""
	if isinstance(tdict.get('СвЮЛ').get('СведДолжнФЛ'),dict):
		result = f"{tdict.get('СвЮЛ').get('СведДолжнФЛ').get('СвФЛ').get('@attributes').get('Фамилия')} {tdict.get('СвЮЛ').get('СведДолжнФЛ').get('СвФЛ').get('@attributes').get('Имя')} {tdict.get('СвЮЛ').get('СведДолжнФЛ').get('СвФЛ').get('@attributes').get('Отчество')}"
	elif isinstance(tdict.get('СвЮЛ').get('СведДолжнФЛ'),list):
		for i in tdict.get('СвЮЛ').get('СведДолжнФЛ'):
			result += f"{i.get('СвФЛ').get('@attributes').get('Фамилия')} {i.get('СвФЛ').get('@attributes').get('Имя')} {i.get('СвФЛ').get('@attributes').get('Отчество')} \n"
	else:
		result = "00"
	return result

def get_director_post(tdict):
	result=""
	if isinstance(tdict.get('СвЮЛ').get('СведДолжнФЛ'),dict):
		result = f"{tdict.get('СвЮЛ').get('СведДолжнФЛ').get('СвДолжн').get('@attributes').get('НаимДолжн')}"
	elif isinstance(tdict.get('СвЮЛ').get('СведДолжнФЛ'),list):
		for i in tdict.get('СвЮЛ').get('СведДолжнФЛ'):
			result+=f"{i.get('СвДолжн').get('@attributes').get('НаимДолжн')} \n"
	else:
		result = "00"
	return result

def is_org_closed(tdict):
	global org_status
	if tdict.get('СвЮЛ').get('СвПрекрЮЛ') is not None:
		return True
	elif tdict.get('СвЮЛ').get('СвСтатус')is not None:
		org_status=tdict.get('СвЮЛ').get('СвСтатус').get('СвСтатус').get('@attributes').get('НаимСтатусЮЛ')
		return tdict.get('СвЮЛ').get('СвСтатус').get('СвСтатус').get('@attributes').get('КодСтатусЮЛ')
	else : return False

#2403001755

def write_row(data):
	#Запись выходного массива данных в файл
	with open (OUTFILE, "a", newline="", encoding='cp1251') as file:
		writer = csv.writer(file)
		writer.writerow(data)
	#Конец записи выходного массива данных в файл

#Парсер
def orginfo(inn):
	#Вывод текущего ИНН, объявление переменных строк
	
	print(str(inn).zfill(10))
	# testinn(inn)
	isOrgClosed=False
	org_name=""				# Наименование организации сокращенное
	org_fname=""			# Наименование организации полное
	org_address=""			# Юридический адрес организации
	org_okved=""			# Основной ОКВЭД
	director_fname=""		# Полное имя руководителя юрлица
	director_post=""		# Должность руководителя юрлица
	# subDiv=""				# Вид подразделения (филиал/представительство)
	subDivisionFName=""		# Наименование подразделения
	subDivisionAddress=""	# Адрес подразделения
	global body_dict 	# Словарь json

	#Конец объявления переменных строк
	
	#Проверка валидности URL, Заполнение словаря json ответом
	try:
		url=base_url+str(inn).zfill(10)+".json"
		with urllib.request.urlopen(url) as response:
			body_json = response.read()
		body_dict = json.loads(body_json)
	except urllib.error.HTTPError as HTTPERR:
		logging.error(f"Ошибка #{HTTPERR}# в {inn}")
	#Конец проверки
	# print(json.dumps(body_dict, indent=4))
	
	isOrgClosed=is_org_closed(body_dict)
	
	#Получение искомых данных из словаря
	if isOrgClosed == False:
		# org_okved=testokved(body_dict).upper()
		# org_name=short_name_from_inn(body_dict).upper()
		# org_fname=full_name_from_inn(body_dict).upper()
		# org_address=get_address_from_inn(body_dict).upper()
		# director_fname=get_director_fname(body_dict).upper()
		# director_post=get_director_post(body_dict).upper()
		branch=sub_division_q(body_dict)
		if branch is not None and branch > 1:
			#Вносим информацию о головном учреждении
			org_okved=testokved(body_dict).upper()
			org_name=short_name_from_inn(body_dict).upper()
			org_fname=full_name_from_inn(body_dict).upper()
			org_address=get_address_from_inn(body_dict).upper()
			director_fname=get_director_fname(body_dict).upper()
			director_post=get_director_post(body_dict).upper()
			org_info=[inn,"Головное отделение",org_okved,org_name,org_fname,org_address,branch]
			write_row(org_info)
			#Вносим информацию о подразделениях
			for i in range(branch):
				org_okved=org_name=director_fname=director_post="="
				org_fname=sub_division_fname(body_dict, i)
				org_address=sub_division_faddress(body_dict, i)
				org_info=[inn,subDiv,org_okved,org_name,org_fname,org_address,subDivisionFName,subDivisionAddress,i+1]
				write_row(org_info)
		elif branch is not None and branch == 1:
			# global subDiv
			#Вносим информацию о головном учреждении
			org_okved=testokved(body_dict).upper()
			org_name=short_name_from_inn(body_dict).upper()
			org_fname=full_name_from_inn(body_dict).upper()
			org_address=get_address_from_inn(body_dict).upper()
			director_fname=get_director_fname(body_dict).upper()
			director_post=get_director_post(body_dict).upper()
			org_info=[inn,"Головное отделение",org_okved,org_name,org_fname,org_address,branch]
			write_row(org_info)
			#Вносим информацию о подразделении
			org_okved=org_name=director_fname=director_post="="
			org_fname=sub_division_fname(body_dict, -branch)
			org_address=sub_division_faddress(body_dict, -branch)
			org_info=[inn,subDiv,org_okved,org_name,org_fname,org_address,subDivisionFName,subDivisionAddress]
			write_row(org_info)
		else:
			org_okved=testokved(body_dict).upper()
			org_name=short_name_from_inn(body_dict).upper()
			org_fname=full_name_from_inn(body_dict).upper()
			org_address=get_address_from_inn(body_dict).upper()
			director_fname=get_director_fname(body_dict).upper()
			director_post=get_director_post(body_dict).upper()
			org_info=[inn,"ГУ",org_okved,org_name,org_fname,org_address]
			write_row(org_info)

	elif isOrgClosed == True:
		org_okved=org_name=org_fname=org_address=director_post=director_fname="CLOSED"
		org_info=[inn,"CLOSED",org_okved,org_name,org_fname,org_address]
		write_row(org_info)
	else:
		print(f"ERROR {isOrgClosed} - {org_status}")
		org_okved=org_name=org_fname=f"ERROR {isOrgClosed} - {org_status}"
		org_address=url
		org_info=[inn,"ERR",org_okved,org_name,org_fname,org_address]
		write_row(org_info)
	#Конец получения исходных данных
	
	#Формирование выходного массива данных
	# org_info=[inn,org_okved,org_name,org_fname,org_address,director_post,director_fname]
	#Конец формирования выходного массива данных

	#Запись выходного массива данных в файл
	# with open (OUTFILE, "a", newline="", encoding='cp1251') as file:
	# 	writer = csv.writer(file)
	# 	writer.writerow(org_info)
	#Конец записи выходного массива данных в файл

# #Получение полного адреса образовательной организации
# def get_address_from_inn(tdict):
	
# 	tempdict=tdict['СвЮЛ']['СвАдресЮЛ']
# 	for key in keyaddrinfo:
# 		if key in tempdict.keys():
# 			tempdict=tempdict.get(key)

# 	address={}
# 	address.setdefault("Индекс",tempdict.get('@attributes').get('Индекс'))
	
# 	if tempdict.get('НаимРегион') is not None:
# 		address.setdefault("Регион", tempdict.get('НаимРегион'))
# 	elif tempdict.get('Регион') is not None:
# 		if tempdict.get('Регион').get('@attributes').get('ТипРегион') is not None or tempdict.get('Регион').get('@attributes').get('НаимРегион') is not None:
# 			address.setdefault("Регион",f"{tempdict.get('Регион').get('@attributes').get('НаимРегион')} {tempdict.get('Регион').get('@attributes').get('ТипРегион')}".replace(" None", ""))
	
# 	if tempdict.get('Район') is not None:
# 		if isinstance(tempdict.get('Район'), dict):
# 			#print(f"{tempdict.get('Район').get('@attributes').get('НаимРайон')} {tempdict.get('Район').get('@attributes').get('ТипРайон')}")
# 			address.setdefault("Район", f"{tempdict.get('Район').get('@attributes').get('НаимРайон')} {tempdict.get('Район').get('@attributes').get('ТипРайон')}".replace(" None", ""))
# 		else:
# 			address.setdefault("Район", tempdict.get('Район'))
	
# 	if tempdict.get('МуниципРайон') is not None:
# 		if isinstance(tempdict.get('МуниципРайон'), dict):
# 			#print(f"{tempdict.get('МуниципРайон').get('@attributes').get('Наим')} {tempdict.get('МуниципРайон').get('@attributes').get('Тип')}")
# 			address.setdefault("Район", f"{tempdict.get('МуниципРайон').get('@attributes').get('Наим')} {tempdict.get('МуниципРайон').get('@attributes').get('Тип')}".replace(" None", ""))
# 		else:
# 			address.setdefault("Район", tempdict.get('МуниципРайон'))
	
# 	if tempdict.get('Город') is not None:
# 		if isinstance(tempdict.get('Город'),dict):
# 			#print(f"{tempdict.get('Город').get('@attributes').get('ТипГород')} {tempdict.get('Город').get('@attributes').get('НаимГород')}")
# 			address.setdefault("Город", f"{tempdict.get('Город').get('@attributes').get('ТипГород')} {tempdict.get('Город').get('@attributes').get('НаимГород')}".replace(" None", ""))
# 		else:
# 			address.setdefault("Город", tempdict.get('Город'))
	
# 	if tempdict.get('НаселПункт') is not None:
# 		if isinstance(tempdict.get('НаселПункт'),dict):
# 			#print(f"{tempdict.get('НаселПункт').get('@attributes').get('ТипНаселПункт')} {tempdict.get('НаселПункт').get('@attributes').get('НаимНаселПункт')}")
# 			address.setdefault("НаселПункт", f"{tempdict.get('НаселПункт').get('@attributes').get('ТипНаселПункт')} {tempdict.get('НаселПункт').get('@attributes').get('НаимНаселПункт')}".replace(" None", ""))
# 		else:
# 			address.setdefault("НаселПункт", tempdict.get('НаселПункт'))
	
# 	if tempdict.get('НаселенПункт') is not None:
# 		if isinstance(tempdict.get('НаселенПункт'),dict):
# 			#print(f"{tempdict.get('НаселенПункт').get('@attributes').get('Вид')} {tempdict.get('НаселенПункт').get('@attributes').get('Наим')}")
# 			address.setdefault("НаселПункт", f"{tempdict.get('НаселенПункт').get('@attributes').get('Вид')} {tempdict.get('НаселенПункт').get('@attributes').get('Наим')}".replace(" None", ""))
# 		else:
# 			address.setdefault("НаселПункт", tempdict.get('НаселенПункт'))

# 	if tempdict.get('Улица') is not None:
# 		if isinstance(tempdict.get('Улица'), dict):
# 			#print(f"{tempdict.get('Улица').get('@attributes').get('НаимУлица')} {tempdict.get('Улица').get('@attributes').get('ТипУлица')}")
# 			address.setdefault("Улица", f"{tempdict.get('Улица').get('@attributes').get('НаимУлица')} {tempdict.get('Улица').get('@attributes').get('ТипУлица')}".replace(" None", ""))
# 		else:
# 			address.setdefault("Улица", tempdict.get('Улица'))

# 	if tempdict.get('ЭлУлДорСети') is not None:
# 		if isinstance(tempdict.get('ЭлУлДорСети'), dict):
# 			#print(f"{tempdict.get('ЭлУлДорСети').get('@attributes').get('Наим')} {tempdict.get('ЭлУлДорСети').get('@attributes').get('Тип')}")
# 			address.setdefault("Улица", f"{tempdict.get('ЭлУлДорСети').get('@attributes').get('Наим')} {tempdict.get('ЭлУлДорСети').get('@attributes').get('Тип')}".replace(" None", ""))
# 		else:
# 			address.setdefault("ЭлУлДорСети", tempdict.get('ЭлУлДорСети'))

# 	if tempdict.get('Здание') is not None:
# 		if isinstance(tempdict.get('Здание'), dict):
# 			print(type(tempdict.get('Здание')))
# 			address.setdefault("Здание", f"{tempdict.get('Здание').get('@attributes').get('Тип')} {tempdict.get('Здание').get('@attributes').get('Номер')}".replace(" None", ""))
# 		elif isinstance(tempdict.get('Здание'),list):
# 			#print(f"{tempdict.get('Здание')[0].get('@attributes').get('Тип')} {tempdict.get('Здание')[0].get('@attributes').get('Номер')}, {tempdict.get('Здание')[1].get('@attributes').get('Тип')} {tempdict.get('Здание')[1].get('@attributes').get('Номер')}")
# 			address.setdefault("Здание", f"{tempdict.get('Здание')[0].get('@attributes').get('Тип')}, {tempdict.get('Здание')[0].get('@attributes').get('Номер')}".replace(" None", ""))
# 			address.setdefault("Строение", f"{tempdict.get('Здание')[1].get('@attributes').get('Тип')}, {tempdict.get('Здание')[1].get('@attributes').get('Номер')}".replace(" None", ""))
# 		else:
# 			address.setdefault("Здание", tempdict.get('Здание'))
# 	if tempdict.get('@attributes').get('Дом') is not None: 
# 		address.setdefault("Дом", f"{tempdict.get('@attributes').get('Дом')}".replace(" None", ""))
# 	result=""
# 	for i in address:
# 		if address.get(i) != "" :
# 			result+=f"{address.get(i)}, "
# 	#print(result.replace(" None", "").rstrip(", "))
# 	return result.rstrip(", ")
		  
#Открытие файла output, стирание файла, установка шапки
def fopen():
	data_template=["ИНН", "ТИП", "ОКВЭД", "Наименование организации сокр.", "Наименование организации полн.", "Юридический адрес"]
	with open (OUTFILE, "w", newline="", encoding='cp1251') as file:
		writer = csv.writer(file)
		writer.writerow(data_template)

main()
test()


# #Краткое наименование из выписки ЕГРЮЛ 2 типа	
# def short2_name_from_inn (inn):
#	 #inn=input("Введите ИНН организации: ")
#	 url=base_url+str(inn)+".json"
#	 try:
#		  with urllib.request.urlopen(url) as response:
#			   body_json = response.read()
#		  body_dict = json.loads(body_json)
#		  name = body_dict['СвЮЛ']['СвНаимЮЛ']['@attributes']['НаимЮЛСокр'] #Сокращенное наименование организации
#		  #print(name)
#		  return name
#	 except urllib.error.HTTPError as HTTPERR:
#		  #print(f"Ошибка #{HTTPERR}# в {inn}")
#		  logging.error(f"Ошибка #{HTTPERR}# в {inn}")
#		  result = f"Ошибка #{HTTPERR}#"
#		  return result
	   
# #Полный адрес из выписки ЕГРЮЛ 1 типа
# def address_from_inn(inn):
#	 url=base_url+str(inn)+".json"
#	 try:
#		  with urllib.request.urlopen(url) as response:
#			   body_json = response.read()
#		  body_dict = json.loads(body_json)
#		  dict=body_dict['СвЮЛ']['СвАдресЮЛ']['АдресРФ']
#		  address={
#		 "Индекс" : dict['@attributes']['Индекс'],
#		 "Регион" :dict['Регион']['@attributes']['НаимРегион'],
#		 "Район" : dict['Район']['@attributes']['НаимРайон'] + " " + dict['Район']['@attributes']['ТипРайон'],
#		 "НаселПункт" : dict['НаселПункт']['@attributes']['ТипНаселПункт'] + 
#		 " " + 
#		 dict['НаселПункт']['@attributes']['НаимНаселПункт'], 
#		 "Улица" : dict['Улица']['@attributes']['ТипУлица'] + " " + dict['Улица']['@attributes']['НаимУлица'],
#		 "Дом" : dict['@attributes']['Дом']
#		   }
#		  result = f"{address['Индекс']}, {address['Регион']}, {address['Район']}, {address['НаселПункт']}, {address['Улица']}, {address['Дом']}"
#		  #print(result)
#		  return result
#	 except urllib.error.HTTPError as HTTPERR:
#		  #print(f"Ошибка #{HTTPERR}# в {inn}")
#		  logging.error(f"Ошибка #{HTTPERR}# в {inn}") 

# #Полный адрес из выписки ЕГРЮЛ 2 типа
# def address2_from_inn(inn):
#	 url=base_url+str(inn)+".json"
#	 try:
#		  with urllib.request.urlopen(url) as response:
#			   body_json = response.read()
#		  body_dict = json.loads(body_json)
#		  dict=body_dict['СвЮЛ']['СвАдресЮЛ']['АдресРФ']
#		  address={
#		 "Индекс" : dict['@attributes']['Индекс'],
#		 "Регион" :dict['Регион']['@attributes']['НаимРегион'] + " " + dict['Регион']['@attributes']['ТипРегион'],
#		 #"Район" : dict['Район']['@attributes']['НаимРайон'] + " " + dict['Район']['@attributes']['ТипРайон'],
#		 "Город" : dict['Город']['@attributes']['ТипГород'] + " " + dict['Город']['@attributes']['НаимГород'], 
#		 "Улица" : dict['Улица']['@attributes']['ТипУлица'] + " " + dict['Улица']['@attributes']['НаимУлица'],
#		 "Дом" : dict['@attributes']['Дом']
#		   }
#		  result=f"{address['Индекс']}, {address['Регион']}, {address['Город']}, {address['Улица']}, {address['Дом']}"
#		  #print(result)
#		  return result
#	 except urllib.error.HTTPError as HTTPERR:
#		  #print(f"Ошибка #{HTTPERR}# в {inn}")
#		  logging.error(f"Ошибка #{HTTPERR}# в {inn}")

# #Полный адрес из выписки ЕГРЮЛ 3 типа
# def address3_from_inn(inn):
#	 url=base_url+str(inn)+".json"
#	 try:
#		  with urllib.request.urlopen(url) as response:
#			   body_json = response.read()
#		  body_dict = json.loads(body_json)
#		  dict=body_dict['СвЮЛ']['СвАдресЮЛ']['АдресРФ']
#		  address={
#		 "Индекс" : dict['@attributes']['Индекс'],
#		 "Регион" :dict['Регион']['@attributes']['НаимРегион'],
#		 #"Район" : dict['Район']['@attributes']['НаимРайон'] + " " + dict['Район']['@attributes']['ТипРайон'],
#		 "Город" : dict['Город']['@attributes']['ТипГород'] + " " + dict['Город']['@attributes']['НаимГород'], 
#		 "Улица" : dict['Улица']['@attributes']['ТипУлица'] + " " + dict['Улица']['@attributes']['НаимУлица'],
#		 "Дом" : dict['@attributes']['Дом']}
#		  result=f"{address['Индекс']}, {address['Регион']}, {address['Город']}, {address['Улица']}, {address['Дом']}"
#		  #print(result)
#		  return result
#	 except urllib.error.HTTPError as HTTPERR:
#		  #print(f"Ошибка #{HTTPERR}# в {inn}")
#		  logging.error(f"Ошибка #{HTTPERR}# в {inn}")

# #Полный адрес из выписки ЕГРЮЛ 4 типа		 
# def address4_from_inn(inn):
#	 url=base_url+str(inn)+".json"
#	 try:
#		  with urllib.request.urlopen(url) as response:
#			   body_json = response.read()
#		  body_dict = json.loads(body_json)
#		  dict=body_dict['СвЮЛ']['СвАдресЮЛ']['СвАдрЮЛФИАС']
#		  address={
#		 "Индекс" : dict['@attributes']['Индекс'],
#		 "Регион" : dict.get('НаимРегион'),
#		 "НаселПункт" : dict['НаселенПункт']['@attributes']['Вид'] + 
#		 " " + dict['НаселенПункт']['@attributes']['Наим'],
# 		"Улица" : dict['ЭлУлДорСети']['@attributes']['Тип'] + " " + dict['ЭлУлДорСети']['@attributes']['Наим'],
#		 "Дом" : dict['Здание']['@attributes']['Тип'] + " " + dict['Здание']['@attributes']['Номер']}
#		  result=f"{address['Индекс']}, {address['Регион']}, {address['НаселПункт']}, {address['Улица']}, {address['Дом']}"
#		  #print(result)
#		  return result
#	 except urllib.error.HTTPError as HTTPERR:
#		  logging.error(f"Ошибка #{HTTPERR}# в {inn}")

# #Полный адрес из выписки ЕГРЮЛ 5 типа
# def address5_from_inn(inn):
#	 url=base_url+str(inn)+".json"
#	 try:
#		  with urllib.request.urlopen(url) as response:
#			   body_json = response.read()
#		  body_dict = json.loads(body_json)
#		  dict=body_dict['СвЮЛ']['СвАдресЮЛ']['СвАдрЮЛФИАС']
#		  address={
#		 "Индекс" : dict['@attributes']['Индекс'],
#		 "Регион" :dict['НаимРегион'],
#		 #"Район" : dict['Район']['@attributes']['НаимРайон'] + " " + dict['Район']['@attributes']['ТипРайон'],
#		 #"Город" : dict['Город']['@attributes']['ТипГород'] + " " + dict['Город']['@attributes']['НаимГород'], 
#		 "НаселПункт" : dict['НаселенПункт']['@attributes']['Вид'] + 
#		 " " + dict['НаселенПункт']['@attributes']['Наим'],
# 		"Улица" : dict['ЭлУлДорСети']['@attributes']['Тип'] + " " + dict['ЭлУлДорСети']['@attributes']['Наим'],
#		 "Дом" : dict['Здание'][0]['@attributes']['Тип'] + " " + dict['Здание'][0]['@attributes']['Номер'],
#		 "Строение" : dict['Здание'][1]['@attributes']['Тип'] + " " + dict['Здание'][1]['@attributes']['Номер']
#			 }
#		  result=f"{address['Индекс']}, {address['Регион']}, {address['НаселПункт']}, {address['Улица']}, {address['Дом']}, {address['Строение']}"
#		  #print(result)
#		  return result
#	 except urllib.error.HTTPError as HTTPERR:
#		  #print(f"Ошибка #{HTTPERR}# в {inn}")
#		  logging.error(f"Ошибка #{HTTPERR}# в {inn}")
	