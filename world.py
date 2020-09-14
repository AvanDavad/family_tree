import numpy as np
import pickle

from people import Person

class World:
    def __init__(self, n_people):
        self._init_people(n_people)
        self.couples = []
        self.year = 0

    def _init_people(self, n_people):
        self.person_counter = 0
        self.living_people = []
        for _ in range(n_people):
            self.living_people.append(Person(0, counter=self.person_counter))
            self.person_counter += 1
        self.died_people = []
    
    def years_passed(self, n_years, verbose=True):
        for _ in range(n_years):
            self.year_passed()
            print(self)

    def year_passed(self):
        self.year += 1
        for person in self.living_people:
            person.year_passed()
        self._update_living()
        self._new_borns()
        self._marriages()
        
    def _update_living(self):
        self._update_living_people()
        self._update_living_couples()

    def _update_living_people(self):
        new_living_people = []
        for p in self.living_people:
            if p.alive:
                new_living_people.append(p)
            else:
                self.died_people.append(p)
        self.living_people = new_living_people
    
    def _update_living_couples(self):
        new_couples = []
        for pair in self.couples:
            p1, p2 = tuple(pair)
            if p1.alive and p2.alive:
                new_couples.append(set([p1, p2]))
        self.couples = new_couples
    
    def _new_borns(self):
        newborns = []
        for pair in self.couples:
            p1, p2 = tuple(pair)
            if p1.want_a_child() and p2.want_a_child():
                if p1.able_to_create_child() and p2.able_to_create_child():
                    if p1.gender == 'male':
                        father = p1
                        mother = p2
                    else:
                        father = p2
                        mother = p1
                    last_name = father.last_name
                    if np.random.random() < 0.001: # with low probability, choose a new last name
                        last_name = None
                    child = Person(self.year, last_name=last_name,
                                   father=father, mother=mother,
                                   counter=self.person_counter)
                    self.person_counter += 1
                    self.living_people.append(child)
                    p1.add_new_child(child)
                    p2.add_new_child(child)

    def _marriages(self):
        for p in self.living_people:
            if p.willing_to_marry():
                size = min(np.random.randint(5,50), len(self.living_people))
                candidates = np.random.choice(self.living_people, size=size, replace=False)
                for candid in candidates:
                    if not candid.willing_to_marry():
                        continue
                    want1 = p.marry_candidate(candid)
                    want2 = candid.marry_candidate(p)
                    if want1 and want2:
                        p.do_marry(candid)
                        candid.do_marry(p)
                        self.couples.append(set([p, candid]))
                        break
                    

    def __repr__(self):
        return f"Year {self.year}, {len(self.living_people)} people living."
    
    def save(self, name):
        pass