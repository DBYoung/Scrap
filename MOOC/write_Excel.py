from pandas import  ExcelWriter
writer = ExcelWriter("MOOC.xlsx")
data.to_excel(writer,"mooc")
writer.save()
