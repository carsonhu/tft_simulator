import streamlit as st
from champion import Champion
from set13champs import *
import set13buffs
import set13items

class ObjectWrapper:
    def __init__(self, champion):
        self.obj = champion
        self.hash = champion.__hash__()


def hash_func(obj: ObjectWrapper) -> str:
    return obj.hash  # or any other value that uniquely identifies the object


# @st.cache_data(hash_funcs={ObjectWrapper: hash_func})
# def multiply_score(champ1):   
#     return Lux(3)


@st.cache_data(hash_funcs={ObjectWrapper: hash_func})
def multiply_score(champ1, champ2, _items, _buffs):   
    return Lux(3)

item_list = [set13items.LastWhisper(), set13items.Red()]
buff_list = [set13buffs.Rebel(7, [4, 3]), set13buffs.Rebel(5, 5)]

# item_list = [ObjectWrapper(i) for i in item_list]
# buff_list = [ObjectWrapper(i) for i in buff_list]

multiplier = "yes"

lux = Lux(2)

for item in item_list:
    lux.items.append(item)
for buff in buff_list:
    lux.items.append(buff)


yar = ObjectWrapper(lux)
st.write(yar.obj.hashFunction())

st.write(multiply_score(ObjectWrapper(Lux(2)),
                        ObjectWrapper(Lux(3)),
                        item_list,
                        buff_list))