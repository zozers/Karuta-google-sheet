import os, json
from dotenv import load_dotenv
import pygsheets

load_dotenv()

#authorization
gc = pygsheets.authorize(service_account_env_var = 'GOOGLE_JSON')
wks = gc.open('Karuta storage example for my bot')[0]

def getRowbyId(cardId, sheet):
	for i in range(1, sheet.rows):
		if(sheet.cell((i,3)).value == cardId):
			row = i
			return i
	return 0

def getLastRow(sheet):
	for i in range(1, sheet.rows):
		print(sheet.cell((i, 3)).value)
		if(len(sheet.cell((i,3)).value) == 0):
			return i
	return 0

def getCellByIdAndType(cardId, attributeType, sheet, row=1):
	col = 1
	for i in range(1, sheet.cols):
		if(sheet.cell((1, i)).value == attributeType):
			col = i
			break
	if(row <= 1):
		row = getRowbyId(cardId, sheet)
	return (row, col)


def updateSheet(cardId, attributeType, attributeValue, sheet):
	row = getRowbyId(cardId, sheet)
	if row == 0:
		row = getLastRow(sheet)
		location = getCellByIdAndType(cardId, "Id", sheet, row=row)
		wks.cell(location).set_value(cardId)
		location = getCellByIdAndType(cardId, attributeType, sheet, row=row)
		wks.cell(location).set_value(attributeValue)
	else:
		location = getCellByIdAndType(cardId, attributeType, sheet, row=row)
		wks.cell(location).set_value(attributeValue)


