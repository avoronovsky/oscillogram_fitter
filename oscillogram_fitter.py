import numpy as np
from scipy.optimize import curve_fit
import csv
from os import listdir 
import matplotlib.pyplot as plt
from datetime import datetime

def strftime(x):
    return datetime.now().strftime(x) 

#input
csv_files = []
while csv_files ==[]:
    print('Укажите csv-файл/папку с csv-файлами в ./data')
    input_is_file=0
    while len(csv_files) == 0:
        location = './data'+input('./data')
        if ('.csv' or '.CSV') in location:
            csv_files.append(location)
            input_is_file = 1
        if ('.csv' or '.CSV') not in location:
            for csv_file in listdir(location):
                if (csv_file[-4:]=='.csv' or csv_file[-4:]=='.CSV') and csv_file[:6]!='output':
                    csv_files.append(csv_file)
            list_of_files = ''
            for i in csv_files:
                list_of_files+=str(i)+', '
            list_of_files = list_of_files[:-2]
            print('В указанной директории содержатся такие csv-файлы (за исключением output*): '+list_of_files+'.')
        if len(csv_files)==0:
            print('В указанной директории csv-файлов не обнаружено. Попробуйте ещё раз.')
if input_is_file == 0:
    print('Вы можете убрать файл из списка обрабатываемых, введя его название (с учётом регистра). Можно несколько, через пробел')
    print('Как надоест убирать файлы, просто жмакните энтер')
    file_to_delete = input()
    while file_to_delete!='':
        files_to_delete_list = file_to_delete.split(sep=', ')
        for ffile in files_to_delete_list:
            if ffile not in csv_files:
                print('Файла '+ffile+' и так там нет')
            if ffile in csv_files:
                del csv_files[csv_files.index(ffile)]
        print('')
        list_of_files = 'Что у нас осталось: '
        for i in csv_files:
            list_of_files+=str(i)+', '
        list_of_files = list_of_files[:-2]
        print(list_of_files)
        print('Хотите убрать что-то ещё? Если нет, то просто жмакните энтер')
        file_to_delete = input()

output_file_name = 'output_'+strftime('%d')+strftime('%m')+strftime('%y')+'_'+strftime('%M')+strftime('%S')+'.csv'
if input_is_file == 0:
    output_file_adress = location+'/'+output_file_name
if input_is_file == 1:
    output_file_adress = location[:location.rfind('/')]+output_file_name
print('Значения величин и погрешности будут сохранены в csv-файл '+output_file_adress)
print('')
with open(output_file_adress,'w') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        filewriter.writerow(['Название файла', 'a1','da1','b1','db1','a2','da2','b2','db2','t0','dt0'])

        
print('Наша функция выглядит так:')
print('y = a1 * exp(-(x - t0) / b1) + a2 * exp(-(x - t0) / b2)')
print('')
print('Фиттинг очень чувствителен к изначальному предположению о величинах параметров')
print('Изначальное предположение по умолчанию:')
initial_guess = np.array([1,0.000005,1,0.000005,0.00000005])
parameters_names = ['a1','b1','a2','b2','t0']
initial_guess_string = ''
for parameter in parameters_names:
    index = parameters_names.index(parameter)
    initial_guess_string+=parameter+' = '+str(initial_guess[index])+', '
print(initial_guess_string[:-2])
print('Если вы хотите изменить инишиал гесс для всех файлов, то введите что-то типа "a1 = 1.025, b2 = 0.23"')
initial_guess_change=input()
while initial_guess_change !='':
    initial_guess_change_dict = {}
    initial_guess_change=initial_guess_change.split(sep=', ')
    for parameter in initial_guess_change:
        eq = parameter.find('=')
        if parameter[eq-1]==' ':
            key = parameter[:eq-1]
        if parameter[eq-1]!=' ':
            key = parameter[:eq]
        if parameter[eq+1]==' ':
            data = parameter[eq+2:]
        if parameter[eq+1]!=' ':
            data = parameter[eq+1:]
        initial_guess_change_dict.update({key: data})
    
    for parameter in initial_guess_change_dict.keys():
        if parameter not in parameters_names:
            print('Хм-м, нет такого параметра как '+parameter)
        if parameter in parameters_names:
            index_of_par = parameters_names.index(parameter)
            initial_guess[index_of_par] = initial_guess_change_dict[parameter]

    print('Теперь инишиал гесс таков:')
    initial_guess_string = ''
    for parameter in parameters_names:
        index = parameters_names.index(parameter)
        initial_guess_string+=parameter+' = '+str(initial_guess[index])+', '
    print(initial_guess_string[:-2])
    print('Изменить ещё?')
    initial_guess_change=input()
#print('Если хотите иметь возможность изменить инишиал гесс и профиттить заново для ситуаций, когда')
#print('1 - Значение погрешности любого из параметров на как минимум порядок выше значения параметра')
#print('2 - То же самое, только >=, а не просто >')
#print('Введите соответствующее число. Если не хотите, не вводите ничего')
#reguess_flag = input()
reguess_flag = ''
#print('Выведение графиков, доан, потом доделаю')
print('Работаем...')

problems = []
unsure = []

for csv_file in csv_files:
    csv_file_opened=np.loadtxt('./data/'+csv_file,unpack=False,delimiter=',',dtype=str)
    x_values = [float(i[-3]) for i in csv_file_opened]
    y_values = [-1*float(i[-2]) for i in csv_file_opened]

    max_y = max(y_values)
    remove_to = y_values.index(max_y)
    y_values_fit = y_values[remove_to:]
    x_values_fit = x_values[remove_to:]
    while y_values_fit[0]>=max_y*0.9:
        del y_values_fit[0]
        del x_values_fit[0]
    x_array = np.array([*x_values_fit])
    y_array = np.array([*y_values_fit])

#data processing
    def double_exp(x,a1,b1,a2,b2,t0):
        return a1*np.exp((np.array(x)-t0)*-1*1/b1) + a2*np.exp((np.array(x)-t0)*-1*1/b2)

    reguess = 1
    skip_or = 0

    #if skip_or == 1:
    #    initial_guess = initial_guess_global
        
    while reguess!=0:

        pars, cov = curve_fit(double_exp, x_values_fit, y_array,p0=initial_guess, method='trf')
        stdevs = np.sqrt(np.diag(cov))

        reguess = 0
        
        for i in range(len(pars)):
            #if pars[i] != 0 and abs(stdevs[i]/pars[i])>=10:
            #    if reguess_flag == '':
            #        problems.append(csv_file)
            #    if reguess_flag != '':
            #        reguess = 1
            if pars[i]!= 0 and abs(stdevs[i]/pars[i])>=0.1:
                if reguess_flag!='2': 
                    unsure.append(csv_file)
                if reguess_flag=='2':
                    reguess = 1

        if reguess == 1:
            print('Что-то не так с фиттингом '+csv_file)
            print('1 - меняем инишиал гесс для одного файла')
            print('2 - меняем инишиал гесс и для всех последующих')
            print('ничего  - пропускаем')
            skip_or = input()
            if skip_or == '':
                reguess = 0
            if skip_or == '1':
                initial_guess_global = initial_guess
            if skip_or != '':
                print('Процедура та же -  введите что-то типа "a1 = 1.025, b2 = 0.23"')
                initial_guess_change=input()
                initial_guess_change_dict={}
                while initial_guess_change !='':
                    initial_guess_change=initial_guess_change.split(sep=', ')
                    for parameter in initial_guess_change:
                        eq = parameter.find('=')
                        if parameter[eq-1]==' ':
                            key = parameter[:eq-2]
                        if parameter[eq-1]!=' ':
                            key = parameter[:eq-1]
                        if parameter[eq+1]==' ':
                            data = parameter[eq+2:]
                        if parameter[eq+1]!=' ':
                            data = parameter[eq+1:]
                        initial_guess_change_dict.update({key: data})
    
                    for parameter in initial_guess_change_dict.keys():
                        if parameter not in parameters_names:
                            print('Хм-м, нет такого параметра как '+parameter)
                        if parameter in parameters_names:
                            index_of_par = parameters_names.index(parameter)
                            initial_guess[index_of_par] = initial_guess_change_dict[parameter]

                    print('Теперь инишиал гесс таков:')
                    initial_guess_string = ''
                    for i in parameters_names:
                        index = parameters_names.index(i)
                        initial_guess_string+=str(initial_guess[index])+' = '+i+', '
                    print(initial_guess_string)
                    print('Изменить что-то ещё?')
                    initial_guess_change=input()    

    with open(output_file_adress,'a') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        string = []
        for i in range(11):
            if i == 0:
                string.append(csv_file)
            if i%2 == 0 and i != 0:
                string.append(stdevs[i//2-1])
            if i%2 == 1:
                string.append(pars[i//2])
        filewriter.writerow(string)
    y_fit = double_exp(x_values_fit, *pars)
print('Похоже, всё прошло хорошо.')
if unsure != [] or problems !=[]:
    print('Только вот')
    if unsure != []:
        unsure_str=''
        for file in unsure:
            if unsure_str.count(file)==0:
                unsure_str+=file+', '
        print('В '+unsure_str[:-2]+' порядок погрешности равен или выше') 
        print('порядка абсолютного значения величины какого-то параметра.')
    if problems != []:
        problems_str=''
        for file in problems:
            if problems_str.count(file)==0:
                problems_str+=file+', '
        print('В '+problems_str[:-2]+ ' погрешность выше асолютного значения величины какого-то параметра.')
#data plotting
show_graph=0
if show_graph == 1:
    plt.plot(x_values_fit, y_values_fit, 'bo', label="y-original")
    plt.plot(x_values_fit, y_fit, label="fitted")
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend(loc='best', fancybox=True, shadow=True)
    plt.grid(True)
    plt.show() 
