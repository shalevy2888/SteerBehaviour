from typing import List
from infra.vmath import Vector
# from steer_behaviour import
from steer.movable_entity import MovableEntity
from steer.formation import Formation
from typing import Callable, Optional

SquadForceFunc = Callable[[], None]

class Squad:
    def __init__(self):
        self.entities: List[MovableEntity] = []
        self.formation: Formation = None
        self.squad_behaviour: Optional[SquadForceFunc] = None
    
    def active_iter(self):
        return (e for e in self.entities if e.is_active is True)

    def get_leader(self):
        return next(self.active_iter(), None)
    
    def count(self):
        return len(list(self.active_iter()))

    def get_index_of_entity(self, entity):
        """ returns the index of entity in the squad based on the active entities. Basically counting the
            number of active entities till reaching the requested one and returning the count """
        return next((i for i, e1 in enumerate(self.active_iter()) if e1 == entity), None)

    def get_entity_by_index(self, index):
        if index<0:
            return None
        return next((e1 for i, e1 in enumerate(self.active_iter()) if i == index), None)

    def _get_position_delta(self, entity):
        if self.formation is None:
            return Vector.zero()
        index = self.get_index_of_entity(entity)
        if index is not None:
            return self.formation.entity_position(index)
        return Vector.zero()
        
    def get_position_delta(self, entity, from_entity=None):
        return self._get_position_delta(entity) - (Vector.zero() if from_entity is None else
                                                   self._get_position_delta(from_entity))

    def get_member_in_front_of(self, entity):
        """ return the entity in front of the given entity, which means the entity in index-1 of the given entity index """
        # not a very efficient implementation since we traverse the list twice inside of just once
        index = self.get_index_of_entity(entity)
        return None if index is None else self.get_entity_by_index(index - 1)

    def update_squad_behaviour(self, dt: float):
        if self.squad_behaviour is None:
            return
        
        self.squad_behaviour()
        for e in self.active_iter():
            e.update_steer_behaviour(dt)
