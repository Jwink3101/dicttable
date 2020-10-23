#!/usr/bin/env python
import sys
import time
import copy
import os

import pytest

import dicttable

# This is a hack but it makes sure we're not using the installed one
if not (os.path.abspath(os.path.dirname(__file__)) 
        == 
        os.path.abspath(os.path.dirname(dicttable.__file__)) ):
    raise ValueError("not using local version")


_emptyList = dicttable._emptyList
DictTable = dicttable.DictTable



def test_list_val():
    items = [
        {'first':'John', 'last':'Lennon','born':1940,'role':['guitar','strings']},      # 0
        {'first':'Paul', 'last':'McCartney','born':1942,'role':['bass','strings']},     # 1
        {'first':'George','last':'Harrison','born':1943,'role':['guitar','strings']},   # 2
        {'first':'Ringo','last':'Starr','born':1940,'role':'drums'},        # 3
        {'first':'George','last':'Martin','born':1926,'role':'producer'}    # 4
    ]
    DB = DictTable(items)    
    
    assert DB.count(role='strings') == 3
    assert DB.count({'role':'strings'},{'role':'bass'}) == 1
    assert DB.count({'role':'strings'},role='bass') == 1
    assert DB.count(role=['strings','bass']) == 1
    assert DB.count( (DB.Q.role==['strings','bass'])  ) == 1
    assert DB.count( (DB.Q.role==['strings','bass']) & (DB.Q.first=='Paul') ) == 1
    assert DB.count( (DB.Q.role=='strings') & (DB.Q.role=='bass') ) == 1
    
    return DB

def test_excluded_attributes():
    def _test():
        assert 'i**2' not in DB.attributes,'Should not have been added'
        assert DB.count({'i**2':4}) == 0
    
    # Create with an excluded one
    DB = DictTable(exclude_attributes=['i**2'])

    # Try to add with an exclusion
    DB.add({'i':i,'i//2':i//2,'i**2':i**2} for i in range(10))
    _test()
    
    
    # Reindex
    DB.reindex() # Should do it silently since it is implicit
    _test()
    with pytest.raises(ValueError):
        DB.reindex('i**2')
    _test()

    # Try to add a new item
    i = 10
    DB.add({'i':i,'i//2':i//2,'i**2':i**2})
    _test()
    
    # Update that value on an item
    DB.update({'i**2':21.1},DB.Q.i==1)
    _test()
    assert DB.query_one(i=1)['i**2'] == 21.1,'Should still have updated value'

    # This tests an internal method that is a last guard against not 
    # allowed attributes
    with pytest.raises(ValueError):
        DB._append('i**2',0,0)

    return DB

def test_empty():
    """Operations on empty DB. Mostly testing for errors"""
    # Empty with attributes
    DB = DictTable()

    # Query    
    assert not {'a':'i'} in DB # should also not cause an error
    assert list(DB.query(DB.Q.a=='i')) == []
    
    # Add something
    DB.add({'a':1,'bb':2,'x':3})
    
    assert 'a' in DB.attributes
    assert 'x' in DB.attributes
    
    # Just test the _empty object
    empty = _emptyList()
    assert empty == []
    assert not empty == [1]
    
def test_adv_queries():
    items = [
        {'first':'John', 'last':'Lennon','born':1940,'role':'guitar'},      # 0
        {'first':'Paul', 'last':'McCartney','born':1942,'role':'bass'},     # 1
        {'first':'George','last':'Harrison','born':1943,'role':'guitar'},   # 2
        {'first':'Ringo','last':'Starr','born':1940,'role':'drums'},        # 3
        {'first':'George','last':'Martin','born':1926,'role':'producer'}    # 4
    ]
    
    DB = DictTable(items)
    
    # Remove an item so we can also test with removed items not showing
    DB.remove(first='Paul') # Paul is dead
    assert len(DB) == 4
    
    assert len(list( DB.query(DB.Q._index==0))) == 1
    assert len(list( DB.query(DB.Q._index==1))) == 0
    
    assert DB.count(DB.Q.born <= 1940) == 3
    assert DB.count( (DB.Q._index == 2)  & (DB.Q.born <= 1940) ) == 0
    assert DB.count( (DB.Q.born <= 1940) & (DB.Q._index == 2)  ) == 0
    assert DB.count( (DB.Q.first == 'George') & (DB.Q._index == 1)  ) == 0
    
    assert DB.count(DB.Q.born < 1940) == 1
    assert DB.count( (DB.Q._index == 2) & (DB.Q.born < 1940) ) == 0
    assert DB.count( (DB.Q.born < 1950) & (DB.Q._index == 2)  ) == 1
    
    assert DB.count( DB.Q.born >= 1940) == 3
    assert DB.count( (DB.Q._index == 2) & (DB.Q.born >= 1940) ) == 1
    assert DB.count( (DB.Q.born >= 1940) & (DB.Q._index == 2) ) == 1
    
    assert DB.count(  DB.Q.born > 1940) == 1
    assert DB.count( (DB.Q._index == 1) & (DB.Q.born > 1940) ) == 0
    assert DB.count( (DB.Q.born > 1940)& (DB.Q._index == 1)  ) == 0

    assert DB.count( (DB.Q.first == 'Ringo') | ~(DB.Q.first == 'George')) == 2
    assert DB.count( (DB.Q.first == 'Ringo') |  (DB.Q.first != 'George')) == 2
    
    assert set(item['last'] for item in DB.query(DB.Q.role == 'guitar')) == {'Lennon','Harrison'}
    assert set(item['last'] for item in DB.query(DB.Q.role != 'guitar')) == {'Martin', 'Starr'} # McCartney was removed!
    assert set(item['last'] for item in DB.query(~(DB.Q.role == 'guitar'))) == {'Martin', 'Starr'}
    
    # Add an item so we can use it for incomplete listing
    DB.add({'first':'Brian','last':'Epstein','born':'1934','status':0}) # Missing 'role' and adds 'status'
    
    assert DB.count(DB.Q.status) == 1
    assert DB.count(~DB.Q.status) == 4
    assert DB.count(DB.Q.role) == 4
    
    assert DB.count(DB.Q) == len(DB) == 5

def test_items_iteritems():
    items = [
        {'first':'John', 'last':'Lennon','born':1940,'role':'guitar'},      # 0
        {'first':'Paul', 'last':'McCartney','born':1942,'role':'bass'},     # 1
        {'first':'George','last':'Harrison','born':1943,'role':'guitar'},   # 2
        {'first':'Ringo','last':'Starr','born':1940,'role':'drums'},        # 3
        {'first':'George','last':'Martin','born':1926,'role':'producer'}    # 4
    ]
    
    DB = DictTable(items)
    DB.alwaysReturnList = False
    
    for ii,item in enumerate(DB.items()):
        assert item == items[ii]
    
    for ii,item in enumerate(DB):
        assert item == items[ii]
    
    # Generators don't have lengths
    with pytest.raises(TypeError):
        len(DB.items())
        
    import types
    assert isinstance(DB.items(),types.GeneratorType)
    

def test_index():    
    items = [
        {'first':'John', 'last':'Lennon','born':1940,'role':'guitar'},      # 0
        {'first':'Paul', 'last':'McCartney','born':1942,'role':'bass'},     # 1
        {'first':'George','last':'Harrison','born':1943,'role':'guitar'},   # 2
        {'first':'Ringo','last':'Starr','born':1940,'role':'drums'},        # 3
        {'first':'George','last':'Martin','born':1926,'role':'producer'}    # 4
    ]
    
    DB = DictTable(items)
    
    for ii in range(len(DB)):
        assert DB[ii] == items[ii] # [ ] is yield one
        assert list(DB.items())[ii] == items[ii]
        assert DB.query_one(_index=ii) == items[ii]
        assert DB.query_one(DB.Q._index==ii) == items[ii]
    
    assert list(DB( (DB.Q._index==0) & (DB.Q._index==1) ) ) == []  
#     assert list(DB(DB.Q._index==[0,1]) ) == [] # deprecated
    assert list(DB(_index=100) ) == []
    
    DB._index(9999)
    DB._index(0)
    DB.remove(DB.Q.last == 'Lennon')
    DB._index(0)
    
def test_removal():
    items = [
        {'first':'John', 'last':'Lennon','born':1940,'role':'guitar'},      # 0
        {'first':'Paul', 'last':'McCartney','born':1942,'role':'bass'},     # 1
        {'first':'George','last':'Harrison','born':1943,'role':'guitar'},   # 2
        {'first':'Ringo','last':'Starr','born':1940,'role':'drums'},        # 3
        {'first':'George','last':'Martin','born':1926,'role':'producer'}    # 4
    ]
    
    DB = DictTable(items)
    
    assert DB[3] == items[3]
    
    # This also tests the `_index` term
    DB.remove(_index=3)

    with pytest.raises(ValueError): # it won't let you get this item
        DB[3]
    
    # Can get the third element since it only returns non deleted
    assert list(DB.items())[3] == items[4] 
    
    assert len(list(DB.query(_index=3))) == 0 # Nothing there
    assert len(list(DB.query(first='Ringo'))) == 0 # Nothing there
    
    assert len(list(DB.items())) == 4
    assert len(DB) == 4
    assert DB.N == 4
    
    with pytest.raises(ValueError): # No matches
        DB.remove(first='Peter')
    
    # Remove an empty list element
    DB.query_one(first='Paul')['role'] = []
    DB.reindex('role')
    assert DB.query_one(role=[])['first'] == 'Paul' # Test it
    DB.remove(role=[])
    assert DB.query_one(role=[]) is None
    
    # Try to delete after a change without reindex
    DB.query_one(born=1940)['last'] = 'no last name'
    #... do not reindex
    with pytest.raises(ValueError): # No matches
        DB.remove(born=1940)

def test_reindex_update():
    items = [
        {'first':'John', 'last':'Lennon','born':1940,'role':'guitar'},      # 0
        {'first':'Paul', 'last':'McCartney','born':1942,'role':'bass'},     # 1
        {'first':'George','last':'Harrison','born':1943,'role':'guitar'},   # 2
        {'first':'Ringo','last':'Starr','born':1940,'role':'drums'},        # 3
        {'first':'George','last':'Martin','born':1926,'role':'producer'}    # 4
    ]
    
    DB = DictTable(items)
    
    
    assert DB.query_one(born=1926) == items[4]
    
    # Change it
    DB.query_one(born=1926)['born'] = 1927
    
    # This should fail but it doesn't since we didn't reindex
    assert DB.query_one(born=1926) == items[4]
    
    # This shouldn't fail but it does since we didn't reindex (add a `not` to pass)
    assert not DB.query_one(born=1927) == items[4]
    
    # This should also fail since the Query's aren't updated
    assert not DB.query_one(DB.Q.born==1927) == items[4]
    assert DB.query_one(DB.Q.born==1926) == items[4]
    
    # To show it *was* updated
    assert DB.query_one(last='Martin')['born'] == 1927
    
    # Reindex
    DB.reindex('born')
    
    # now it all flips
    assert not DB.query_one(born=1926) == items[4]
    assert DB.query_one(born=1927) == items[4]
    assert DB.query_one(DB.Q.born==1927) == items[4]
    assert not DB.query_one(DB.Q.born==1926) == items[4]
    
    assert DB.query_one(last='Martin')['born'] == 1927
    
    
    # Now, switch it back with update but do not reindex
    DB.update({'born':1926},DB.Q.born==1927)
    assert DB.query_one(born=1926) == items[4]
    assert not DB.query_one(born=1927) == items[4]
    
    # other update style
    DB.update({'born':1926},born=1926) # This doesn't change anything in reality
    
    # Add a `not` to this one
    assert not DB.query_one(last='Martin')['born'] == 1927
    
    # Multiple
    DB.update({'first':'Ringo'},{'first':'George'})
    assert len(list(DB.query(first='Ringo'))) == 3
    
    ## Errors
    
    # Test bad syntax
    with pytest.raises(ValueError):
        DB.update({'born':1940},{'first':'Ringo'},{'role':'drums'})     # Should fail
    
    # Test bad syntax 2
    with pytest.raises(ValueError):
        DB.update(DB.Q.born==1940,{'first':'Ringo'})
    
    # Test no results
    with pytest.raises(ValueError):
        DB.update({'born':1940},{'first':'ringo'})
    
    with pytest.raises(ValueError):
        DB.update({'born':1940},[{'first':'ringo'}])
    
    
    
def test_all_query_methods():
    items = [
        {'first':'John', 'last':'Lennon','born':1940,'role':'guitar'},      # 0
        {'first':'Paul', 'last':'McCartney','born':1942,'role':'bass'},     # 1
        {'first':'George','last':'Harrison','born':1943,'role':'guitar'},   # 2
        {'first':'Ringo','last':'Starr','born':1940,'role':'drums'},        # 3
        {'first':'George','last':'Martin','born':1926,'role':'producer'}    # 4
    ]
    
    DB = DictTable(items)
        
    ## Single Queries 
    # * Dict vs attrib=val, 
    assert DB.query_one(first='John') == items[0]
    assert DB.query_one({'first':'John'}) == items[0]
    assert DB.query_one(DB.Q.first=='John') == items[0]
    
    # * __call__ maps to query()
    assert next( DB(first='John') ) == items[0]
    assert next( DB(DB.Q.first=='John') ) == items[0]
    assert next( DB({'first':'John'}) ) == items[0]
    
    # * __getitem__ of non integer is also queryone
    assert DB[{'first':'John'}] == items[0]    
    for ii in range(5):
        assert DB[ii] == items[ii]
    
    with pytest.raises(ValueError):
        assert DB['Paul']['last'] == 'McCartney' 
    
    
    ## Multi Queries
    assert DB.query_one( first='George',last='Harrison') == items[2]
    assert DB.query_one( DB.Q.first=='George',last='Harrison') == items[2]
    assert DB.query_one( (DB.Q.first=='George') & (DB.Q.last=='Harrison') ) == items[2]
    assert DB.query_one( {'first':'George'}, last='Harrison' ) == items[2]
    assert DB.query_one( {'first':'George','last':'Harrison'}) == items[2]
    
    ## in queries
    assert {'first':'George','last':'Harrison'} in DB
    assert (DB.Q.first=='George') in DB
    assert DB.isin(first='John')
    assert {'first':'George','last':'Starr'} not in DB
    with pytest.raises(ValueError):
        assert 'George' in DB
    
    
    ## Three queries
    assert DB.query_one( (DB.Q.first=='George') & (DB.Q.born<2000),last='Harrison' ) == items[2]
    

def test_add_attribute():
    items = [
        {'first':'John', 'last':'Lennon','born':1940,'role':'guitar'},
        {'first':'Paul', 'last':'McCartney','born':1942,'role':'bass'},
        {'first':'George','last':'Harrison','born':1943,'role':'guitar'},
        {'first':'Ringo','last':'Starr','born':1940,'role':'drums'},
        {'first':'George','last':'Martin','born':1926,'role':'producer','extra':'test'} # Additional
    ]
    
    ## Fixed
    DB = DictTable(items,fixed_attributes=['first','last','born'],exclude_attributes=['No'])
    
    with pytest.raises(ValueError):
        DB.add_fixed_attribute('No')
    
    assert set(DB.attributes) == {'first','last','born'}
    
    # Make sure the other attributes are still there
    assert 'extra' in DB.query_one(last='Martin')
    

    DB.add_fixed_attribute('role')
    assert set(DB.attributes) == {'first','last','born','role'}
    assert DB.query_one(role='bass')['first'] == 'Paul'
   
    DB.add_fixed_attribute('extra')
    assert set(DB.attributes) == {'first','last','born','role','extra'}
    assert DB.query_one(extra='test')['last'] == 'Martin'

    ## Dynamic
    DB = DictTable(items[:-1])
    assert set(DB.attributes) == {'first','last','born','role'}
    
    # Add the last item with something extra
    DB.add(items[-1])
    assert set(DB.attributes) == {'first','last','born','role','extra'}
    
    # Make sure the other items were not added
    assert 'extra' not in DB.query_one(last='Lennon') 
    assert DB.query_one(extra='test')['last'] == 'Martin'
    
    ## Dynamic with it excluded
    DB = DictTable(items[:-1],exclude_attributes='extra')
    assert set(DB.attributes) == {'first','last','born','role'}
    
    # Add the last item with something extra
    DB.add(items[-1])
    assert set(DB.attributes) == {'first','last','born','role'} # Should *still* not have extra
    assert DB.query_one(extra='test') is None # Should still not recognize it


def test_Query_expiry():
    items = [
        {'first':'John', 'last':'Lennon','born':1940,'role':'guitar'},
        {'first':'Paul', 'last':'McCartney','born':1942,'role':'bass'},
        {'first':'George','last':'Harrison','born':1943,'role':'guitar'},
        {'first':'Ringo','last':'Starr','born':1940,'role':'drums'},
        {'first':'George','last':'Martin','born':1926,'role':'producer','extra':'test'}
    ]    
    
    DB = DictTable(items)
    DB.alwaysReturnList = False
    
    assert DB.query_one( DB.Q.first=='John' ) == items[0]
    Q = DB.Query # or DB.Q
    DB.reindex()    
    with pytest.raises(ValueError): # Should be out of date
        assert DB.query( Q.first=='John' ) == items[0]
    
    
    DB.reindex()
    Q = DB.Query
    assert DB.query_one( Q.first=='John' ) == items[0]
    
    # This should pass since we create the Query in line at the time of query
    DB.reindex()
    assert DB.query_one( DB.Q.first=='John' ) == items[0]
    
    Q = DB.Q.first
    with pytest.raises(ValueError): 
        Q.last == 0
    
    DB2 = DictTable()
    with pytest.raises(ValueError):  
        DB[DB2.Q.name == 'no']
    
def test_init_empty_v_full():
    items = [
        {'first':'John', 'last':'Lennon','born':1940,'role':'guitar'},
        {'first':'Paul', 'last':'McCartney','born':1942,'role':'bass'},
        {'first':'George','last':'Harrison','born':1943,'role':'guitar'},
        {'first':'Ringo','last':'Starr','born':1940,'role':'drums'},
        {'first':'George','last':'Martin','born':1926,'role':'producer','extra':'test'}
    ]
    
    DB1 = DictTable()
    for item in items:
        DB1.add(item)
    assert len(DB1) == 5
    
    DB2 = DictTable(items)
    assert len(DB1) == 5

    
def test_queries():
    items = [
        {'first':'John', 'last':'Lennon','born':1940,'role':'guitar'},
        {'first':'Paul', 'last':'McCartney','born':1942,'role':'bass'},
        {'first':'George','last':'Harrison','born':1943,'role':'guitar'},
        {'first':'Ringo','last':'Starr','born':1940,'role':'drums'},
        {'first':'George','last':'Martin','born':1926,'role':'producer'}
    ]
    
    DB = DictTable(items)
    
    DB.alwaysReturnList = True
    
    # Single item
    result = DB.query(first='George')
    assert items[2] in result
    assert items[4] in result
    
    # Multiple query
    result = DB.query(first='George',role='guitar')
    assert items[2] in result
    assert items[4] not in result
    
    # advanced query 1
    Q = DB.Q
    
    result = DB.query(Q.born <= 1940)
    for ii in [0,3,4]:
        assert items[ii] in result
    
    # advanced query 2
    result = list( DB.query( (DB.Q.born <= 1940) & (DB.Q.role == 'producer')) )
    assert items[0] not in result
    assert items[3] not in result
    assert items[4] in result
    
    # Test no results
    assert list(DB.query(role='computer scientist')) == []

    # Error on queries
    with pytest.raises(ValueError):
        DB.query_one([{'first':'John'}]) # Cannot query a list

def test_filters():
    """ Test things relating to filters. Also tests other parts of the code"""
    items = [
        {'first':'John', 'last':'Lennon','born':1940,'role':'guitar'},
        {'first':'Paul', 'last':'McCartney','born':1942,'role':'bass'},
        {'first':'George','last':'Harrison','born':1943,'role':'guitar'},
        {'first':'Ringo','last':'Starr','born':1940,'role':'drums'},
        {'first':'George','last':'Martin','born':1926,'role':'producer'}
    ]
    
    DB = DictTable(items)
        
    # This is of course the same as an equality
    filt = lambda item: True if item.get('first','') == 'George' and item.get('born',float('inf')) < 1940 else False
    assert DB[DB.Q.filter(filt)]['last'] == 'Martin'
    assert DB[DB.Q._filter(filt)]['last'] == 'Martin'
    
    
    # Add an random object
    DB.add({'filter':'bla'})
    with pytest.raises(TypeError):
        assert DB[DB.Q.filter(filt)]['last'] == 'Martin'
    
    assert DB[DB.Q._filter(filt)]['last'] == 'Martin'
    
    # Now remove it
    DB.remove(filter='bla')
    assert DB[DB.Q.filter(filt)]['last'] == 'Martin' # Can test this again!
    assert DB[DB.Q._filter(filt)]['last'] == 'Martin'
    

@pytest.mark.parametrize("mode", ['function','method'])
def test_copy(mode):
    items = [
        {'first':'John', 'last':'Lennon','born':1940,'role':['guitar','strings']},      # 0
        {'first':'Paul', 'last':'McCartney','born':1942,'role':['bass','strings']},     # 1
        {'first':'George','last':'Harrison','born':1943,'role':['guitar','strings']},   # 2
        {'first':'Ringo','last':'Starr','born':1940,'role':'drums'},        # 3
        {'first':'George','last':'Martin','born':1926,'role':'producer'}    # 4
    ]
    
    # Test with some settings too 
    DB0 = DictTable(items[:2],
                    exclude_attributes=['role'])       
    if mode == 'function':
        DB1 = copy.copy(DB0)
    else:
        DB1 = DB0.copy()
    
    assert DB0 is not DB1
    assert DB0.attributes == DB1.attributes, "Different attributes"
    
    # Add them to both. Make sure the exclude_attributes do not get set
    DB0.add(items[2:])
    DB1.add(items[2:])
    
    assert DB0.attributes == DB1.attributes, "Different attributes"
    assert 'role' not in DB0.attributes
 
    # Need to add an item with an additional attribute to see what the zero goes to
    DB0.add({'test':0})
    assert len(DB0) != len(DB1),"Items should *not* have been added to both"
    DB1.add({'test':1})

    assert DB0.attributes == DB1.attributes, "Different attributes"

    assert DB0[DB0.Q.test==0] == {'test':0}
    assert DB0[DB0.Q.test==1] is None
    
    assert DB1[DB1.Q.test==1] == {'test':1}
    assert DB1[DB1.Q.test==0] is None
     
    DB0.remove(DB0.Q.born > 0)
    assert len(DB0) == 1 # The test
    assert len(DB1) >1
   
    # Test that fixed_attribiutes gets copied
    DB2 = DictTable(items[:2],fixed_attributes='last')
    if mode == 'function':
        DB3 = copy.copy(DB2)
    else:
        DB3 = DB2.copy()
    assert DB2.attributes == DB3.attributes, "Different attributes"
    
    DB2.add(items[2:])
    DB3.add(items[2:])
    
    assert DB2.attributes == DB3.attributes, "Different attributes"
    assert set(DB2.attributes) == {'last'}
    
    
    # Test making a new one from this one. It should NOT have the same settings
    DB4 = DictTable(DB3)       
    assert 'role' not in DB3.attributes # This *not* a copy so it got 'role' attribute
    assert 'role' in DB4.attributes # This *not* a copy so it got 'role' attribute

def test_uncommon_attributes():
    """
    Items all have different attributes
    """
    DB = DictTable()
    for k in range(50):
        DB.add({'k{}'.format(k):k}) # use strings so I can do queries
        
    
    # Make sure comparisons work. 
    for k in range(50):
        
        assert DB.count({'k{}'.format(k):k}) == 1
        
        # Fancy queries. Use eval so I can dynamically form a string
        assert eval('DB.count(DB.Q.k{0} == {0})'.format(k)) == 1
        
        # These are all 0 becuase only one attribute has the value but it
        # will still test them all
        assert eval('DB.count(DB.Q.k{0} <  {0})'.format(k)) == 0
        assert eval('DB.count(DB.Q.k{0} >  {0})'.format(k)) == 0

        # These are all 1 becuase only one attribute has the value but it
        # will still test them all
        assert eval('DB.count(DB.Q.k{0} <= {0})'.format(k)) == 1
        assert eval('DB.count(DB.Q.k{0} >= {0})'.format(k)) == 1

    # See what happens when you delete some
    assert len(DB.attributes) == 50
    
    DB.remove(DB.Q.k10) # All items that specify k10
    assert len(DB.attributes) == 49
    
    # This is just to test the line
    DB._lookup['asfdsdf'] # Will be an empty list
    DB.attributes

def test_adding_fixed_attrib_to_dynamic():
    """Make sure this DOESN'T add to a dynamic list"""
    items = [{'a':i,'b':i**2,'c':i**3} for i in range(10)]
    DB = DictTable(items)
    assert set(DB.attributes) == set('abc')
    
    # Add something to each item
    for item in DB:
        i = item['a']
        item['d'] = i//2
    
    assert set(DB.attributes) == set('abc')
    DB.add_fixed_attribute('d')
    assert set(DB.attributes) == set('abcd')
    
    for item in DB:
        i = item['a']
        item['e'] = i//3
    
    assert set(DB.attributes) == set('abcd')
    DB.add_fixed_attribute('e',force=True)
    assert set(DB.attributes) == set('e')
    
def test_performance():
    """
    This test is far from perfect but the goal is to make sure that
    it does not obviously degrade performance with larger databases
    
    It is an approximation and will not be perfect
    """
    nt = 500
    N = 100000
    n = 1000
    objs = [dict(ii=ii,
                 ii2=ii%200,
                 iis='{ii:08d}'.format(ii=ii)) for ii in range(N)]
    A = dicttable.DictTable(objs)
    B = dicttable.DictTable(objs[-n:])

    q = {'ii':N-1}
    tA = []
    tB = []
    for _ in range(nt):
        t0 = time.time()
        A[q]
        tA.append(time.time() - t0)
    
        t0 = time.time()
        B[q]
        tB.append(time.time() - t0)

    tA = sum(tA)/nt
    tB = sum(tB)/nt
    reldiff = abs(tA - tB)/min([tA,tB])
    print('Time Differences:',reldiff)
    assert reldiff < 0.1, 'Time differences should not be more than 10%'
    

if __name__ == '__main__':
    test_list_val()
    test_excluded_attributes()
    test_empty()
    test_adv_queries()
    test_items_iteritems()
    test_index()
    test_removal()
    test_reindex_update()
    test_all_query_methods()
    test_add_attribute()
    test_Query_expiry()
    test_init_empty_v_full()
    test_queries()
    test_filters()
    test_copy('method')
    test_copy('function')
    test_uncommon_attributes()
    test_adding_fixed_attrib_to_dynamic()
    test_performance()
    
    print('-='*25)
    print('=-'*25)
    print('ALL TESTS PASSED') 














