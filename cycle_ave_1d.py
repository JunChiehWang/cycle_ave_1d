#!/bin/env python
import numpy as np
import math, sys, datetime
#
script = "cycle_ave_1d.py"
usage= script + " usage:\n"                                                   \
       "This script reads a time series 1d plt (Y vs time) for different \n"  \
       "cases, computes the cycle ave. quantity and output to a plt file.\n"  \
       "For example, the input file contains sheath voltage vs time \n"       \
       "for duty cycle of 10%, 30% and 50% (3 cases).\n"                      \
       "The average quantity within a cycle=[max_quantity+min_quantity]/2 \n" \
       "-F=  inpout file \n"                                                  \
       "-O=  output file \n"                                                  \
       "-FRE= frequency for cycles" 
version="20180202"
#
now=datetime.datetime.now()
#
#   user default
#
inputFile = "crtrs_1d.plt"
outputFile = "crtrs_1d_cycle_ave.plt"
freq = 2*10**6
#
#   if no argument is present    
#
if len(sys.argv) ==1:
    print "No valid arguments are provided."
    print usage
    print version       
#
#   Parse command line arguments
#
for arg in sys.argv:
    if arg.upper().find("-F=") > -1:
        temp = arg.find("=")
        inputFile  = arg[temp+1:]
    elif arg.upper().find("-O=") > -1:
        temp = arg.find("=")
        outputFile  = arg[temp+1:]
    elif arg.upper().find("-FRE=") > -1:
        temp = arg.find("=")
        freq  = float(arg[temp+1:])
#
#   Show input argument
#
print ""
print "Arguments provided or used in the script:"
print "Input file =", inputFile
print "Output file =", outputFile
print "Frequency for cycles =", str(freq)
print ""
#
try:
    fin = open(inputFile,'r')
except:
    print ''
    print "File cannot be opened:", inputFile
    exit()
#
#   Find number of cases, then
#
num_case=0
case=[]
for iline, wk_line in enumerate(fin):
    wk_line=wk_line.strip()
    if wk_line.startswith('ZONE T='):
        case_name=wk_line.split('"')[1]
        case.append(case_name)
        num_case=num_case+1
#        
print 'number of case=', num_case
print 'case=', case
#
#   Rewind back to head of file
#
fin.seek(0)        
#
#   Find size of array (num of timepoints for a case)
#   and rewind back to head of file
#
for iline, wk_line in enumerate(fin):
    wk_line=wk_line.strip()
    if wk_line.startswith('I='):
        size=int(wk_line.split(',')[0].split('=')[1])
        break
print 'timepoints for a case=', size
fin.seek(0)            
#
#   Create an initialize array (size, num_case+2)
#   => 
#   time cycle  case_1  case_2 .. 
#
xy_array=np.zeros((size,num_case+2))
print 'shape of xy_array:', xy_array.shape
#
#   read data into the array  
#
print "Read data into array:"
icase=0
for iline, wk_line in enumerate(fin):
    wk_line=wk_line.strip()
    if wk_line.startswith('ZONE T='):
        indx=0
        icase=icase+1
#        if icase==3:
#            break
        print 'process data on ' + str(icase) + 'th case: ' + case[icase-1]
        continue
    if icase>0:
        try:
            time=float(wk_line.split()[0])
            y=float(wk_line.split()[1])
            if icase==1:
                cycle=time*freq
                xy_array[indx,0] = time
                xy_array[indx,1] = cycle
            xy_array[indx,icase+1] = y
            indx=indx+1
        except:
            continue
#
#print xy_array[0:4,:]
#print ''
#print xy_array[size-2:size,:]
#exit()
#
#   cycle average data
#   voltage = [ cycle voltage_case1  voltage_case2 .. ]
#
print "Compute cycle averae quantity:"
max_cycle=int(np.ceil(np.max(xy_array[:,1])))
print 'max_cycle:', max_cycle
voltage=np.zeros((max_cycle,num_case+1))
for indx in range(max_cycle):
#    
#    0, 1, 2, .... max_cycle-1
#
#    print 'indx=',indx
    icycle=indx+1
    print "Cycle:", icycle    
    voltage[indx,0]=icycle
#
#   if ceiling of xy_array[:,1] has number == icycle, then copy over to 
#   array_tmp, use this trick to find the data for a certain cycle and compute
#   cycle average quantity
#
    array_tmp=xy_array[[np.ceil(xy_array[:,1])==icycle]]
    tmp=( np.max(array_tmp[:,2:num_case+2],axis=0) + \
          np.min(array_tmp[:,2:num_case+2],axis=0) ) / 2
    voltage[indx,1:num_case+1]=tmp
#    print voltage[indx,:]
#    if indx==2:
#        break
#exit()

#
#   Create plt file 
#
print "Create " + outputFile + ":" 
fout = open(outputFile,'w')
line = '# Created by ' + script + ' ' + str(now) + '\n'
fout.write(line)
line = 'Title="cycle ave data" \n'
fout.write(line)
line ='Variables="cycle",\n'  
fout.write(line)    
delim = '\t'
#
#   case name
#
for ii in case:
    line = '"'+ii+'",\n'  
    fout.write(line)
#   
for indx in range(max_cycle):
    line=""
    for value in voltage[indx,:]: 
        line = line + '{:12.6e}'.format(value) + delim
    fout.write(line+'\n')
#for indx in range(max_cycle):
#    line = str(voltage[indx,:])[1:-1]
#    fout.write(line+'\n')
