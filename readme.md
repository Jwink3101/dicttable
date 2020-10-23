# DictTable

A simple *in memory* single-table object. Replace list of dictionaries with a fast, O(1) lookup, data structure. 

Also supports indexing multiple items per attribute by using a list of values.

It is very simple and designed for small to medium databases which can exist purely in memory and where query *speed is prioritized* over memory usage and instantiation time.

I built it because I was querying a list of dictionaries by multiple keys *inside* of a loop. That cause an O(N^2) complexity and made my moderately-sized 30,000 item list intractable!

There are other solutions out there that are more traditionally database focused such as [TinyDB][tinydb], [buzhug][buzhug], etc, but do not offer the O(1) lookups and speed.

[tinydb]:https://tinydb.readthedocs.io/en/latest/
[buzhug]:http://buzhug.sourceforge.net/

A single SQLite table (especially with `:memory:` path) may check all of the boxes, but requires SQL knowledge and doesn't *automatically* index values. It also cannot (easily) handle a mishmash of keys without having to add columns to tables. DictTable handles it just fine!

It passes all tests (with **100% test coverage**) on Python 2.7 and Python 3.7


## Install

Simply 

    $ python -m pip install git+https://github.com/Jwink3101/dicttable

## Usage:

For more full example usage, including the flexible query methods, see the tests.

Consider the following: (please do not argue accuracy. It is an example)

```python
items = [
    {'first':'John', 'last':'Lennon','born':1940,'role':'guitar'},
    {'first':'Paul', 'last':'McCartney','born':1942,'role':'bass'},
    {'first':'George','last':'Harrison','born':1943,'role':'guitar'},
    {'first':'Ringo','last':'Starr','born':1940,'role':'drums'},
    {'first':'George','last':'Martin','born':1926,'role':'producer'}
]
```

If we want to find all members of The Beatles who's name is "George Harrison", we could do the following:

```python
[item for item in items if item['first']=='George' and item['last']=='Harrison']
```

Which is an O(N) operation. If we are only doing it once, it is fine, but if we are doing it multiple times (especially in loops) it can cause a major bottleneck.

Instead do:

```python
from dicttable import DictTable
DB = DictTable(items) # Will index them all

DB.query_one(first='George',last='Harrison')  # Or more. See below for query methods

```

The creation is O(N) but the query is O(1) and can be done many times.

## Queries

There are a few different methods to perform queries. It is designed to be flexible and allow for easy construction

### Basic Queries

Basic queries only test equality with an `and` boolean relationship.

For example, to query band the example DB for band members with the first name 'George', you can do either of the following:

These return an iterator

```python
DB.query(first='George')
DB.query({'first':'George'})
DB(first='George')          # Directly calling the object is a query()
```

This returns a single item:

```python
DB[{'first':'George'}]      # item indecies can be queries or a number
```

To get George Harrison, you can do the following:

```python
DB.query(first='George',last='Harrison')
```

Or again, you can use a dictionary or mix and match. For example:

```    
DB.query({'first':'George'},last='Harrison')
```
    
Again, you are restricted to equality and `all()`.

### Advanced Queries

An advanced query is constructed as follows. **NOTE**: Python gets easily messed up with assignment. Use parentheses to separate statements!

For example, to query all elements with the first name George and the last name **not** Martin, you can do:

```python
DB.query( (DB.Q.first=='George') & (DB.Q.last != 'Martin') )
```

Notice:

* Use of parentheses. The queries must be separated
* We are checking equality so `==` and `!=` are used
    * You can also negate with `~` but again, be careful and deliberate about parentheses
* We used `&` for `and` and `|` for `or`
* `<`, `<=`, `>`, `>=`, and filters are supported but these are O(N) opperations.

You can also do more advanced boolean logic such as:

```python
DB.query( ~( (DB.Q.role=='guitar') | (DB.Q.role=='drums')))
```

#### Filters

A filter allows for more advanced queries of the data but, as noted below, are O(N) (as with `<`, `<=`, `>`, `>=`).

For example, to perform a simple equality, the following return the same entry. But do note that the equality version is *much faster*.

Edge Case: If an attribute's name is 'filter', the filter method may be accessed through `_filter`.

```python
# Traditional lookup:
DB.query(DB.Q.first == 'George') # equality is O(1)

# Filter lookup
filt = lambda item: True if item['first'] == 'George' else False
DB.query(DB.Q.filter(filt))
```

The are flexible for more advanced queries

#### WARNING about speed

Some of the major speed gains in this are due to the use of dictionaries and sets which are O(1) complexity. 

Queries with `<`, `<=`, `>`, `>=`, and `filters` are O(N) opperations and should be avoided if possible.

The time complexity of a query will depend on the number of items that match any part of the query.

## Loading and Saving (Dumping)

There is *intentionally* no built in way to dump these as they are intended to be *in-memory*. 

To save them, convert back to a list with `list(DB)` and save that!

## Lists:
    
All attributes must be hashable. The only exception are lists in which case the list is expanded for each item. For example, an entry may be:

```python
{'first':'George','last':'Harrison','born':1943,'role':['guitar','sitar']}
```

and 

```python
DB.query(role='sitar')
```

will return him.

## Known Issues

None at the moment.

There is 100% (!!!) test coverage. Of course that doesn't mean there aren't bugs. If you find any, please report them.

## Limitations

* The entire DB exists in memory
* The index used in the dictionary is itself a dictionary with keys as any value. Since these are all done as pointers to original list, the memory footprint should be small.
* This has **not** been tested for thread-safety and is very likely *not* threa safe




















