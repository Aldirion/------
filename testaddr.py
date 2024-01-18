import json
import urllib
import urllib.request
import csv
import os
import logging

basekey=["СвЮЛ", "СвАдресЮЛ"]
keyaddrinfo=["АдресРФ", "СвАдрЮЛФИАС"]
keyaddr=["@attributes","Индекс","Регион","МуниципРайон","Район","НаселенПункт","НаселПункт","Город","Улица","ЭлУлДорСети","Дом","Здание"]
keyatr="@attributes"
keyindex="Индекс"
keycity=["Тип","ТипГород","Наим","НаимГород"]
keyregion=["НаимРегион","Наим","ТипРегион","Тип"]
keydistrict=["НаимРайон","Наим","ТипРайон","Тип"]
keynp=["ТипНаселПункт", "Вид", "НаимНаселПункт","Наим"]
keystreet=["ТипУлица", "Тип", "НаимУлица", "Наим"]
keybuilding=["Тип", "Номер"]

tdistrict=""
ndistrict=""
inn1="2461023606"
inn2="2813005506"
inn3="2459011346"

def main():
	get_address_from_inn(inn3)



def get_address_from_inn(inn):
	url="https://egrul.itsoft.ru/"+str(inn)+".json"
	try:
		with urllib.request.urlopen(url) as response:
			body_json = response.read()
		body_dict = json.loads(body_json)
		tempdict=body_dict['СвЮЛ']['СвАдресЮЛ']
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
			if isinstance(tempdict, dict):
				print(f"{tempdict.get('Район').get('@attributes').get('НаимРайон')} {tempdict.get('Район').get('@attributes').get('ТипРайон')}")
				address.setdefault("Район", f"{tempdict.get('Район').get('@attributes').get('НаимРайон')} {tempdict.get('Район').get('@attributes').get('ТипРайон')}".replace(" None", ""))
			else:
				address.setdefault("Район", tempdict.get('Район'))
		
		if tempdict.get('Город') is not None:
			if isinstance(tempdict,dict):
				print(f"{tempdict.get('Город').get('@attributes').get('ТипГород')} {tempdict.get('Город').get('@attributes').get('НаимГород')}")
				address.setdefault("Город", f"{tempdict.get('Город').get('@attributes').get('ТипГород')} {tempdict.get('Город').get('@attributes').get('НаимГород')}".replace(" None", ""))
			else:
				address.setdefault("Город", tempdict.get('Город'))
		
		if tempdict.get('НаселПункт') is not None:
			if isinstance(tempdict,dict):
				print(f"{tempdict.get('НаселПункт').get('@attributes').get('ТипНаселПункт')} {tempdict.get('НаселПункт').get('@attributes').get('НаимНаселПункт')}")
				address.setdefault("НаселПункт", f"{tempdict.get('НаселПункт').get('@attributes').get('ТипНаселПункт')} {tempdict.get('НаселПункт').get('@attributes').get('НаимНаселПункт')}".replace(" None", ""))
			else:
				address.setdefault("НаселПункт", tempdict.get('НаселПункт'))
		
		if tempdict.get('НаселенПункт') is not None:
			if isinstance(tempdict,dict):
				print(f"{tempdict.get('НаселенПункт').get('@attributes').get('Вид')} {tempdict.get('НаселенПункт').get('@attributes').get('Наим')}")
				address.setdefault("НаселПункт", f"{tempdict.get('НаселенПункт').get('@attributes').get('Вид')} {tempdict.get('НаселенПункт').get('@attributes').get('Наим')}".replace(" None", ""))
			else:
				address.setdefault("НаселПункт", tempdict.get('НаселенПункт'))

		
		if tempdict.get('Улица') is not None:
			if isinstance(tempdict, dict):
				print(f"{tempdict.get('Улица').get('@attributes').get('НаимУлица')} {tempdict.get('Улица').get('@attributes').get('ТипУлица')}")
				address.setdefault("Улица", f"{tempdict.get('Улица').get('@attributes').get('НаимУлица')} {tempdict.get('Улица').get('@attributes').get('ТипУлица')}".replace(" None", ""))
			else:
				address.setdefault("Улица", tempdict.get('Улица'))

		if tempdict.get('ЭлУлДорСети') is not None:
			if isinstance(tempdict, dict):
				print(f"{tempdict.get('ЭлУлДорСети').get('@attributes').get('Наим')} {tempdict.get('ЭлУлДорСети').get('@attributes').get('Тип')}")
				address.setdefault("Улица", f"{tempdict.get('ЭлУлДорСети').get('@attributes').get('Наим')} {tempdict.get('ЭлУлДорСети').get('@attributes').get('Тип')}".replace(" None", ""))
			else:
				address.setdefault("ЭлУлДорСети", tempdict.get('ЭлУлДорСети'))

		if tempdict.get('Здание') is not None:
			if isinstance(tempdict, dict):
				print(f"{tempdict.get('Здание').get('@attributes').get('Тип')} {tempdict.get('Здание').get('@attributes').get('Номер')}")
				address.setdefault("Здание", f"{tempdict.get('Здание').get('@attributes').get('Тип')} {tempdict.get('Здание').get('@attributes').get('Номер')}".replace(" None", ""))
			elif isinstance(tempdict,list):
				print(f"{tempdict.get('Здание')[0].get('@attributes').get('Тип')} {tempdict.get('Здание')[0].get('@attributes').get('Номер')}, {tempdict.get('Здание')[1].get('@attributes').get('Тип')} {tempdict.get('Здание')[1].get('@attributes').get('Номер')}")
				address.setdefault("Здание", f"{tempdict.get('Здание')[0].get('@attributes').get('Тип')}, {tempdict.get('Здание')[0].get('@attributes').get('Номер')}".replace(" None", ""))
				address.setdefault("Строение", f"{tempdict.get('Здание')[1].get('@attributes').get('Тип')}, {tempdict.get('Здание')[1].get('@attributes').get('Номер')}".replace(" None", ""))
			else:
				address.setdefault("Здание", tempdict.get('Здание'))
		
		address.setdefault("Дом", f"{tempdict.get('@attributes').get('Дом')}".replace(" None", ""))
		result=""
		for i in address:
			if address.get(i) != "":
				result+=f"{address.get(i)}, "
		print(result.replace(" None", "").rstrip(", "))
		return result
	except urllib.error.HTTPError as HTTPERR:
		print(f"Ошибка #{HTTPERR}#")
	


main()