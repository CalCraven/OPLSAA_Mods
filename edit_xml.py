# This is a python file to help you edit your xml files
# Contains all of the necessary functions to easily do the editing from a jupyter noteboo

import numpy as np
import warnings
import foyer
import os
import mbuild as mb
import subprocess

def Check_Forcefield(mbuild_structure, 
                     forcefield_path,list_types=False,verbose=False):
    parmed_structure = mbuild_structure.to_parmed()
    opls = foyer.Forcefield(forcefield_files=[forcefield_path])
    typed_surface = opls.apply(parmed_structure,verbose=verbose,assert_bond_params=False,assert_angle_params=False,
                                assert_improper_params=False,assert_dihedral_params=False)
    if list_types:
        for i,atom in enumerate(list(typed_surface.atoms)):
            print(i,atom.type)

    #typed_surface.save("test_molecules/building_blocks/molecule.mol2",overwrite=True)
    #typed_surface.save("test_molecules/building_blocks/molecule.top",overwrite=True)
    failed_atoms=[]
    for i,atom in enumerate(list(typed_surface.atoms)):
        #print(atom.type)
        if atom.type== 'opls_1010':
            failed_atoms.append(i)
    tested_molecule = mb.compound.Compound()
    tested_molecule.from_parmed(structure=typed_surface) 
    for molecule in failed_atoms:    
        list(tested_molecule.particles())[molecule].name='Z'
        #print(list(tested_molecule.particles())[molecule].name)
    return(tested_molecule.visualize())

def Compare_Standard_Mol(test_molecule_path,test_forcefield_path):
    molecule=mb.load(test_molecule_path)
    parmed_structure = molecule.to_parmed()
    opls = foyer.Forcefield(forcefield_files=[test_forcefield_path])
    typed_molecule = opls.apply(parmed_structure)
    filepath=os.path.join("./test_molecules/test_molecule_comp.top")
    typed_molecule.save(filepath,overwrite=True)
    originalfilepath=os.path.join(test_molecule_path[:-4]+'top')
    count=0
    total=0
    halt=0
    with open(filepath,'r') as openfile:
        with open(originalfilepath,'r') as compfile:
            comp_lines=compfile.readlines()[17:]
            lines=openfile.readlines()[17:]
            #print(len(comp_lines),len(lines))
            for i,line in enumerate(lines):
                #print(line)
                if line == '[ bonds ]\n':
                    halt = 1
                if line == '[ pairs ]\n':
                    halt = 0
                if not(halt):
                    total+=1
                    if line == comp_lines[i]:
                        count+=1

    if count/total==1.0:
        print(test_molecule_path[:-5] +' Passed')
    else:
        print(test_molecule_path[:-5] +' Failed')
        
def Replace_Line(file_name, line_num, text):
    lines = open(file_name, 'r').readlines()
    lines[line_num] = text
    out = open(file_name, 'w')
    out.writelines(lines)
    out.close()
    
def Find_line_to_Modify(xmlpath, modify_type, name):
    with open(xmlpath,'r') as file:
        #replace line with given opls number
        line = file.readlines()
        cnt=0
        for i in np.arange(0,len(line)):
            i=int(i)
            if modify_type == 'AtomType':
                if line[i][3:7]=='Type':
                    #print(line[i][14:21])
                    if line[i][14:22] == name:
                        edit_line=cnt
            cnt+=1
    return(edit_line)

def Check_Standard_Molecules(xmlpath,moleculedir):
    xmlpath="../switchable_interfaces/atools/atools/forcefields/edited.xml"
    for filename in os.listdir(moleculedir):
        if filename.endswith(".mol2"): 
            file=os.path.join(moleculedir,filename)
            Compare_Standard_Mol(file,xmlpath)

def Edit_xml(path,filename,name,clas,element,mass,definition,desc,doi,overrides,overwrite=False):
    #if modify is AtomType:
    # inputs
    path = "../switchable_interfaces/atools/atools/forcefields/"
    filename = "edited.xml"
    xmlpath = os.path.join(path,filename)
    if not(overwrite):
        cppath = os.path.join(path,'#backup_'+filename)
        print(cppath)
        subprocess.call(['cp', xmlpath, cppath], shell=False)
    modify_type = 'AtomType' #could be AtomType, Bond, Angle Proper
    #name = 'opls_010'
    #clas = 'class'
    #element = 'element'
    #mass = 'mass'
    #definition = 'definition'
    #desc = 'description'
    #doi = 'doi'
    #overrides = 'overrides'
    #charge = 'charge'
    #sigma = 'sigma'
    #epsilon = 'epsilon'
    #find line to edit
    text_to_add = ('  <Type name="' + name + '" class="' + clas 
                + '" element="' + element + '" mass="' + mass 
                + '"   def="' + definition + '" desc="' + desc 
                + '" overrides="' + overrides + '" doi="' + doi + '"/>\n')

    Replace_Line(xmlpath, Find_line_to_Modify(xmlpath, modify_type, name), text_to_add)
    print(filename + ' has been modified.')
