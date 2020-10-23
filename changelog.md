# Changelog

## 20200825.0

* Major revision and new name. Now `DictTable`. Indexes everything unless set otherwise
* Updated tests:
    * Includes performance tests to ensure O(1) 
* Still supports python2 but that will likely go away soon

## 20191123

This change is all about how iterators over the table work. In general, it restarts the iterator when you loop over it. This is more in line with how python built-in objects such as a list or dict work.

* Removed the `.items()` method. Just iterate
* When `.__iter__()` is called, it returns a generator
