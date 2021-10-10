# Changelog

## 20211010.0

* Adds `del DB[query]` capability.
* Adds `DB.pop(query)` capability.
* Tests for both. Also discovered bug related to `DB.query(attrib=[])` but that is fixed and tested as part of the new tests


## 20200825.0

* Major revision and new name. Now `DictTable`. Indexes everything unless set otherwise
* Updated tests:
    * Includes performance tests to ensure O(1) 
* Still supports python2 but that will likely go away soon

## 20191123

This change is all about how iterators over the table work. In general, it restarts the iterator when you loop over it. This is more in line with how python built-in objects such as a list or dict work.

* Removed the `.items()` method. Just iterate
* When `.__iter__()` is called, it returns a generator
