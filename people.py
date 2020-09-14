import numpy as np
import matplotlib.pyplot as plt
import hashlib
import names

class Person:
    def __init__(self, born, gender=None, first_name=None, last_name=None, father=None, mother=None, counter=None):
        self.born = born
        self._init_params()
        self.age = 0
        self.civil_status = 'single'
        self.partners = []
        self.children = []
        self.alive = True
        self.died = None
        self.father = father
        self.mother = mother
        self.counter = counter
        self._create_unique_hash()
        self._create_gender(gender)
        self._create_name(first_name, last_name)
        self.biography = [(self.born, "I was born.")]

    def _init_params(self):
        self.x0 = np.random.random()*20 + 50
        self.alpha = (1.+np.random.random())*self.x0/8

    def _create_gender(self, gender=None):
        if gender is None:
            self.gender = np.random.choice(['male', 'female'])
        else:
            assert gender in ('male', 'female')
            self.gender = gender
    
    def _create_name(self, first_name=None, last_name=None):
        self._create_first_name(first_name)
        self._create_last_name(last_name)
        self.name = f"{self.first_name} {self.last_name}"
        
    def _create_first_name(self, first_name):
        if first_name is None:
            name_collision=True
            while name_collision:
                n_first_name = np.random.choice([1, 2, 3], p=[0.85, 0.145, 0.005])
                self.first_name = ' '.join([names.get_first_name(gender=self.gender) for _ in range(n_first_name)])
                if self.father is None:
                    name_collision = False
                else:
                    taken_names = [p.first_name for p in self.father.children]
                    name_collision = self.first_name in taken_names
        else:
            self.first_name = first_name

    def _create_last_name(self, last_name):
        if last_name is None:
            self.last_name = names.get_last_name()
        else:
            self.last_name = last_name

    def _create_unique_hash(self):
        sha = hashlib.sha256()
        sha.update(str(self.counter).encode())
        self.hash = sha.hexdigest()

    def __repr__(self):
        if self.alive:
            return f"{self.name} ({self.born} - )"
        else:
            return f"{self.name} ({self.born} - {self.died})"
    
    def summary(self):
        summary_list = []
        died = "" if self.alive else self.died
        summary_list.append(f"{self.name}. ({self.born} - {died} [age {self.age}])")
        if self.father is not None:
            summary_list.append(f"  father: {self.father.name}, born: {self.father.born}")
        if self.mother is not None:
            summary_list.append(f"  mother: {self.mother.name}, born: {self.mother.born}")
        for year, event in self.biography:
            summary_list.append(f"  {year} [age {year-self.born}]: {event}")
        print('\n'.join(summary_list))

    def year_passed(self):
        if not self.alive:
            return
        f = 0.1/(1.+np.exp(-((self.age+1)-self.x0)/self.alpha))
        if np.random.random() < f: # I died x_x
            self.alive = False
            self.died = self.born + self.age
            if self.civil_status == 'married':
                self.partners[-1].partner_died()
            self.biography.append((self.died, f"I passed away, at age {self.age}"))
        else:
            self.age += 1
    
    def partner_died(self):
        assert self.alive
        self.civil_status = 'widow'
        self.biography.append((self.born+self.age, f"My partner, {self.partners[-1].name} passed away."))

    def willing_to_marry(self):
        """
        Do I want to marry at my age?
        """
        if not self.alive:
            return False
        if self.civil_status == 'married':
            return False
        elif self.civil_status == 'widow':
            p_true = np.clip(.5 - (self.age - 70)*0.03, 0., .6)
            p_false = 1. - p_true
            return np.random.choice([True, False], p=[p_true, p_false])
        else: # single
            p_true = np.clip((self.age - 15)*0.2, 0., 1.)
            p_false = 1. - p_true
            return np.random.choice([True, False], p=[p_true, p_false])

    def marry_candidate(self, other):
        """
        Do I want to marry the other?
        """
        if not self.alive:
            return False
        if self.gender == other.gender:
            return False
        age_diff = abs(self.age - other.age)
        p_true = 0.8*np.exp(-0.05*age_diff**2) + 0.2*np.exp(-0.005*age_diff**2)
        p_false = 1. - p_true
        return np.random.choice([True, False], p=[p_true, p_false])
    
    def do_marry(self, other):
        """
        Let's marry the other
        """
        assert self.alive
        assert self.civil_status != 'married'
        self.civil_status = 'married'
        self.partners.append(other)
        self.married_at_age = self.age
        self.biography.append((self.born+self.age, f"I married {other.name}"))
    
    def want_a_child(self):
        """
        Do I want a child?
        """
        if not self.alive:
            return False
        p_true = np.clip(1. - 0.2*len(self.children), 0., 1.)
        p_false = 1.-p_true
        return np.random.choice([True, False], p=[p_true, p_false])

    def able_to_create_child(self):
        if not self.alive:
            return False
        if self.gender == 'male':
            p_true = np.clip(1. - 0.1*(self.age-40), 0., 1.)
            p_false = 1. - p_true
            return np.random.choice([True, False], p=[p_true, p_false])
        else:
            p_true = np.clip(1. - 0.3*(self.age-30), 0., 1.)
            p_false = 1. - p_true
            return np.random.choice([True, False], p=[p_true, p_false])
        
    def add_new_child(self, child):
        assert self.alive
        self.children.append(child)
        self.biography.append((self.born+self.age, f"{child.name} was born."))