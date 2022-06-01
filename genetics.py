import numpy as np
import os
import pygame as pg
from variable import Variable
from factor import Factor
from bayes import BayesianNetwork


class FamilyMember:

    def __init__(self, name, sex, mother, father):
        self.name = name
        self.sex = sex
        self.mother = mother
        self.father = father

    def get_name(self):
        return self.name

    def get_sex(self):
        return self.sex


class Male(FamilyMember):

    def __init__(self, name, mother=None, father=None):
        super().__init__(name, "male", mother, father)


class Female(FamilyMember):

    def __init__(self, name, mother=None, father=None):
        super().__init__(name, "female", mother, father)


def create_paternal_inheritance_cpt(person, signature):
    inherited = signature[f'IP_{person.get_name()}']
    if person.father is not None:
        parent_genotype = signature[f'G_{person.father.get_name()}']
        if person.get_sex() == "male":
            probs = {('xy', 'y'): 1.0, ('Xy', 'y'): 1.0}
        else:
            probs = {('xy', 'x'): 1.0, ('xy', 'X'): 0.0,
                     ('Xy', 'x'): 0.0, ('Xy', 'X'): 1.0}
        cpt = Factor([parent_genotype, inherited], probs)
    else:
        if person.get_sex() == "male":
            probs = {('y',): 1.0}
        else:
            probs = {('x',): 0.999, ('X',): 0.001}
        cpt = Factor([inherited], probs)
    return cpt


def create_maternal_inheritance_cpt(person, signature):
    inherited = signature[f'IM_{person.get_name()}']
    if person.mother is not None:
        parent_genotype = signature[f'G_{person.mother.get_name()}']
        probs = {('xx', 'x'): 1.0, ('xx', 'X'): 0.0,
                 ('xX', 'x'): 0.5, ('xX', 'X'): 0.5,
                 ('XX', 'x'): 0.0, ('XX', 'X'): 1.0}
        cpt = Factor([parent_genotype, inherited], probs)
    else:
        probs = {('x',): 0.999, ('X',): 0.001}
        cpt = Factor([inherited], probs)
    return cpt


def create_genotype_cpt(person, signature):
    maternal = signature[f'IM_{person.get_name()}']
    genotype = signature[f'G_{person.get_name()}']
    if person.get_sex() == "male":
        probs = {('x', 'xy'): 1.0, ('x', 'Xy'): 0.0,
                 ('X', 'xy'): 0.0, ('X', 'Xy'): 1.0}
        cpt = Factor([maternal, genotype], probs)
    else:
        paternal = signature[f'IP_{person.get_name()}']
        probs = {('x', 'x', 'xx'): 1.0, ('x', 'x', 'xX'): 0.0, ('x', 'x', 'XX'): 0.0,
                 ('x', 'X', 'xx'): 0.0, ('x', 'X', 'xX'): 1.0, ('x', 'X', 'XX'): 0.0,
                 ('X', 'x', 'xx'): 0.0, ('X', 'x', 'xX'): 1.0, ('X', 'x', 'XX'): 0.0,
                 ('X', 'X', 'xx'): 0.0, ('X', 'X', 'xX'): 0.0, ('X', 'X', 'XX'): 1.0}
        cpt = Factor([paternal, maternal, genotype], probs)
    return cpt


def create_phenotype_cpt(person, signature):
    genotype = signature[f'G_{person.get_name()}']
    phenotype = signature[f'P_{person.get_name()}']
    if person.get_sex() == "male":
        probs = {('xy', '-'): 1.0, ('xy', '+'): 0.0,
                 ('Xy', '-'): 0.0, ('Xy', '+'): 1.0}
    else:
        probs = {('xx', '-'): 1.0, ('xx', '+'): 0.0,
                 ('xX', '-'): 1.0, ('xX', '+'): 0.0,
                 ('XX', '-'): 0.0, ('XX', '+'): 1.0}
    return Factor([genotype, phenotype], probs)


def create_family_bayes_net(family):
    variables = []
    for member in family:
        if member.get_sex() == "male":
            maternal_inheritance = Variable(f'IM_{member.name}', ['x', 'X'])
            genotype = Variable(f'G_{member.name}', ['xy', 'Xy'])
            phenotype = Variable(f'P_{member.name}', ['-', '+'])
            variables = variables + [maternal_inheritance, genotype, phenotype]
        else:
            paternal_inheritance = Variable(f'IP_{member.name}', ['x', 'X'])
            maternal_inheritance = Variable(f'IM_{member.name}', ['x', 'X'])
            genotype = Variable(f'G_{member.name}', ['xx', 'xX', 'XX'])
            phenotype = Variable(f'P_{member.name}', ['-', '+'])
            variables = variables + [paternal_inheritance, maternal_inheritance,
                                     genotype, phenotype]
    signature = {var.get_name(): var for var in variables}
    cpts = []
    for person in family:
        if person.get_sex() == "female":
            cpts.append(create_paternal_inheritance_cpt(person, signature))
        cpts.append(create_maternal_inheritance_cpt(person, signature))
        cpts.append(create_genotype_cpt(person, signature))
        cpts.append(create_phenotype_cpt(person, signature))
    return BayesianNetwork(cpts)


